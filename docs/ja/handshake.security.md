# CCP Handshake Security Specification
Version: 3.0
Status: Draft-Stable
Audience: AI Agents / Implementers

本書は、`schemas/handshake.schema.yaml` と `docs/ja/handshake.protocol.md` に適用される
「最低限の安全要件」を定義する。
仕様の全体像と意図は `specs/handshake.yaml` を参照。
状態ポリシーは `README.ja.md` を参照。

CCP は、[Value Continuity](https://github.com/value-continuity/value-continuity) を
組織・エージェントをまたぐ越境の面から実装する。
以下の署名・正規化・リプレイ防止は技術的な手段であり、Value Continuity や VCDesign の意味を変えない。

---

# 1. Threat Model

CCP Handshake は以下の脅威を想定する：

- リプレイ攻撃（過去のハンドシェイクを再送して合意を偽装）
- 中間者攻撃（内容の改ざん）
- 署名不一致（正規化方式の違いによるハッシュ不一致）
- 参加者のなりすまし
- Δ の不正な移送（保有者のない Δ、または障害区画をまたぐ Δ の移送）
- 不正な権限（AI を final_decider として提示する、認められた範囲を超えて実行する）
- 不正な Expand（Positive Δ の観測と復旧確認なしに範囲を広げる）
- basis_flow を通じた漏えい（機密情報や過剰な権限など、根拠そのものが損失を運ぶ場合）
- 推移的な信頼（相手の結論を確かめ直さずに引き継ぐ）

本仕様は、これらを最小コストで防ぐための要件を定める。

---

# 2. Handshake Meta の安全要件

`handshake_meta` は以下の 5 要素を必ず含む。

## 2.1 handshake_id
- 一意識別子（UUIDv4 推奨）
- 署名対象に含める

## 2.2 timestamp
- ISO 8601
- 受信側は **現在時刻 ±5 分以内** であることを検証する

## 2.3 expires_at
- ISO 8601
- **現在時刻より未来であること**（プロトコル側と整合）

## 2.4 nonce
- 128bit 以上のランダム値
- **未使用であることを検証する**

## 2.5 participants
- initiator / receiver の ID を明示
- 署名対象に含める

---

# 3. Canonicalization（正規化）

署名前に正規化を適用する。

## 3.1 MUST / MAY

```
MUST: json_c14n
MAY:  yaml_c14n（ただし署名対象は JSON に変換してから正規化する）
```

### 理由
- YAML は実装差が大きく、署名互換が壊れやすい。
- JSON に変換 → 正規化することで、表現差を完全に排除できる。

## 3.2 正規化の要件
- フィールド順序の固定
- 空白・改行の揺れの排除
- 数値・文字列の型の固定
- YAML アンカー / エイリアスの禁止

---

# 4. Signed Fields（署名対象）

`continuity_claim.signature_schema.signed_fields` に列挙されたフィールドのみが署名対象となる。

推奨セット：

```
signed_fields:
  - handshake_meta
  - world
  - agent
  - trust
  - interface
  - decision_authority
  - boundary_policy
  - continuity_claim.boundary
  - continuity_claim.declaration
```

`signature_schema` 自体（アルゴリズム、鍵参照、正規化方式）は技術メタデータであり、署名対象に含める必要はない。

`decision_authority`、`boundary_policy`、`continuity_claim` の主張部分は合意内容そのものなので、署名対象に含めることを推奨する。これにより次を署名で検証できる：

- 誰が判断を閉じ、どの範囲で接続が動くか
- この境界で何を止め、何を通すか
- どの境界・前提・価値について合意したか、後から書き換えられていないか

---

# 5. Replay Protection

以下の 3 要素を組み合わせてリプレイ攻撃を防ぐ。

## 5.1 nonce の保持期間
nonce は `expires_at + safety_margin` まで保持しなければならない。
safety_margin は 10 分を推奨する（SHOULD）。

## 5.2 timestamp の許容範囲
- ±5 分以内

## 5.3 expires_at の強制
- 期限切れのハンドシェイクは無効

---

# 6. Authority Safety（判断権限の安全）

AI は判断を支援するが、責任を持たない（VCDesign axioms A3）。以下を必須とする。

## 6.1 人間の final_decider
- `decision_authority.final_decider.kind = human`
- `authorization.decided_by` が final_decider と一致する、またはその権限委譲を `trust.evidence` で示す

## 6.2 intent=decision の場合
- `trust.risk_level >= 2`
- `trust.validation_level >= semantic`
- `authorization.decision_ref` がある（越境の前に人間が判断を閉じている）
- `irreversible=true` の場合、`blast_radius.max_loss` を宣言している

## 6.3 Expand
- `authorization.expand_basis.positive_delta_ref` がある（平均的な効果だけでは根拠にしない）
- `authorization.expand_basis.recovery_confirmed = true`（広げた範囲でも復旧できる）

## 6.4 遅いループに作用する AI
- `agent.kind = ai` かつ `decision_authority.loop` が `physical` / `value` / `responsibility` の場合、越境には `authorization.decision_ref` が必要。LLM の出力が現実に作用する前には明示的なゲートを置く。

## 6.5 制御の返却
以下の条件では実行を止め、人間の final_decider に制御を返す：

- `reversal_signal.type = authority_revoked`
- 接続の中で解消できない `guard_unknown`
- `on_exceed = halt` または `escalate` の `blast_radius_exceeded`
- Δ の不整合

---

# 7. Boundary Safety（境界の安全）

## 7.1 containment（Downside は伝播させない）
- `propagation` の既定は `deny`。`attested_only` と `allow` は明示する。
- `on_breach`（quarantine / halt / deny）を宣言する。
- `shared_dependencies` を宣言する。これは隔壁の穴である。

## 7.2 basis_flow（Upside は伝播可能にする）
- `default` の既定は `allow`。根拠・証跡・残るもの・Positive Δ は通す。結論は通さない。
- 根拠そのものが損失を運ぶ場合に限り `restricted` とし、各項目に理由を付ける。
- `redaction = required` の場合、通す前に個人情報・機密情報を削除する。
- `deny` の理由は根拠として通す。
- 通すことは広げることではない。接続を広げるには Expand が要る。

## 7.3 revalidation
- `upstream_trust` の既定は `none`。相手の結論を引き継がない。
- 前提・根拠の鮮度・権限を、受け取る側の境界で確かめ直す。
- 一致しない場合は `unknown`。

## 7.4 Δ
- `delta.transfer.scope`：`prompt` / `artifact` / `state` / `tool_call`
- Δ を移送する場合、送信側は Δ のハッシュを付け、保有者を明示する。
- 向きの記録がない Δ は negative として扱う。

---

# 8. Reversal Safety（途中反転の安全）

## 8.1 発生条件
- `guard_deny` / `guard_unknown`
- `precondition_broken`
- `blast_radius_exceeded`
- `authority_revoked`
- `validation_fail`

## 8.2 通知内容
- `reversal_signal.events`
- `phase`（HELLO / OFFER / ACCEPT / REVERSE / CLOSE）
- `reason`
- 返却する Δ の `delta_ref` と `holder`

## 8.3 権限の巻き戻し
- `authority_revoked` の場合、実行を止め、人間の final_decider に制御を返す。
- 状態は戻してよいが、責任記録（判定、反転、Δ の保有者）は追記のみとする。

---

# 9. Value Continuity と VCDesign との統合の安全

- CCP は Value Continuity、Value Asymmetry Principle、5原則、Decision を再定義しない。
- CCP は VCDesign の語を再定義しない。`decision_authority.loop`、`boundary_policy`、`boundary_policy.delta` はそれらをそのまま参照する。
- 技術的なフィールド（署名、正規化、nonce、cost_model）は価値の意味を持たない。

---

# 10. Termination Safety

## 10.1 成功
- ACCEPT の署名検証成功時
- 残るものを保有者に引き渡した CLOSE

## 10.2 失敗
- REJECT
- REVERSE
- expires_at 超過
- nonce 再利用

---

# 11. License

MIT License
© VCDesign Project
