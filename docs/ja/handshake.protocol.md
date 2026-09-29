# CCP Handshake Protocol Specification
Version: 3.0
Status: Draft-Stable
Audience: AI Agents / Implementers

本書は、schemas/handshake.schema.yaml に基づき、
AI 同士が安全に接続するための「動的手順（プロトコル）」を定義する。
仕様の全体像と意図は `specs/handshake.yaml` を参照。
状態ポリシーは `README.ja.md` を参照。

CCP は、[Value Continuity](https://github.com/value-continuity/value-continuity) を
**組織・エージェントをまたぐ越境** の面から実装するプロトコルである。
Value Continuity を再定義せず、境界の働きは VCDesign v2（`patterns/boundary-pattern.yaml`）と同じ語で書く。

---

# 1. Overview

CCP Handshake は以下のフェーズで構成される：

1. HELLO
2. OFFER
3. ACCEPT / REJECT
4. REVERSE（任意・途中反転）
5. CLOSE

各フェーズでは、越境が損失を止め、根拠を通し、
人間の判断が認めた範囲の中にとどまるための必須チェックが定義される。

### 判定と判断は別物である

- **guard verdict（判定）**（`pass` / `deny` / `unknown`）は、個々の越境に対する検査である。ACCEPT は `pass`、REJECT は `deny` または `unknown`。
- **Decision（判断）**（Proceed / Expand / Limit / Reframe / Defer / Retire）は人間が閉じ、接続の実行範囲を認める（`decision_authority.authorization`）。

プロトコルは判断の語彙を増やさない。deny や unknown が繰り返される、または責任に影響する場合は Δ として観測し、判断6語で閉じる。

---

# 2. States

| State | Purpose |
|-------|---------|
| HELLO | セッション開始、識別と宣言した境界の交換 |
| OFFER | initiator が権限・境界ポリシー・継続主張を提示 |
| ACCEPT | receiver の guard verdict が `pass`。署名を返す |
| REJECT | receiver の guard verdict が `deny`（理由付き）または `unknown`（上位へ上げる） |
| REVERSE | 途中反転：止める、閉じ込める、Δ を保有者付きで返す、人間へ上げる |
| CLOSE | 接続の終了：責任を解放し、依存先へ通知し、残るものを保有者付きで引き渡す |

---

# 3. Message Sequence

## 3.1 HELLO

### 送信内容（双方）
- handshake_meta
    （handshake_id / timestamp / expires_at / nonce / participants を含む）
- world.id
- agent.id、agent.kind
- trust.validation_level

### 必須チェック
- `timestamp` が現在時刻 ± 5 分以内
- `expires_at` が現在時刻より未来
- `nonce` が未使用
- `signature_schema` が有効

### 目的
- 当事者の識別（`external_crossing.identity`）
- 時刻整合性
- 署名方式の合意
- 宣言した境界（world）の共有

---

## 3.2 OFFER

### initiator が送る
- `interface`
- `cost_model`
- `decision_authority`
- `boundary_policy`
- `continuity_claim`

### 必須チェック

`intent` に応じて検証レベルの条件が変わる：

```
intent = proposal | advice:
  trust.validation_level >= syntax

intent = decision:
  trust.validation_level >= semantic
```

責任（hard stop。違反時は `deny` で REJECT）：
- `decision_authority.final_decider.kind = human`
- `decision_authority.owner` と `continuity_claim.boundary.owner` が存在する
- `intent=decision` の場合、`risk_level >= 2` かつ `authorization.decision_ref` がある
- `irreversible=true` または `reversibility.class=irreversible` の場合、`blast_radius.max_loss` が宣言されている
- `authorization.decision=expand` の場合、`expand_basis.positive_delta_ref` があり `expand_basis.recovery_confirmed=true`
- `agent.kind=ai` かつ `loop` が `physical` / `value` / `responsibility` の場合、`authorization.decision_ref` がある

境界ポリシー：
- `containment.propagation` は明示がなければ `deny`
- `basis_flow.default` は明示がなければ `allow`。`restricted` の各項目には理由がある
- `revalidation.upstream_trust` は証明がなければ `none`
- `delta.transfer.scope` がスキーマと整合

### 目的
- 権限の宣言：誰が判断を閉じ、どの範囲を認めたか（`external_crossing.authority`）
- 境界の宣言：保有者、前提、意味範囲（`external_crossing.declared_boundary`）
- 生かし続ける価値と、残るものの宣言
- 止めるものと通すものの宣言

### 認める判断

実行範囲を認めるのは `proceed` / `expand` / `limit` だけなので、`authorization.decision` にはこの3語だけが入る。残る3語はプロトコル上の帰結として扱う。

| 判断 | CCP での扱い |
|------|--------------|
| Proceed | 現在の宣言のまま接続を開く |
| Expand | 新しいハンドシェイクで `trust.scope`・`blast_radius`・`basis_flow` を広げる。Positive Δ の観測と復旧能力の確認が必須 |
| Limit | 新しいハンドシェイクで `trust.scope`・`blast_radius`・権限を狭める |
| Reframe | 新しい `continuity_claim`（新しい id・前提・保有者）を発行し、新しいハンドシェイクを行う |
| Defer | 接続しない。`unknown` の REJECT を、暫定責任者と `next_review_at` 付きで返す |
| Retire | 接続しない、または既存の接続を CLOSE する |

宣言を狭めない「小さな試行」は Limit ではない。上限のない越境として拒否する。

---

## 3.3 ACCEPT

### receiver が送る
- `verdict: pass`
- 署名（signature）
- canonicalization 情報
- Δ の保有者の決定（任意。`boundary_policy.delta.holder` に書く）

### 必須チェック
- `signed_fields` を canonicalization（json_c14n）で正規化
- 署名が一致
- `revalidation.re_check` が通る：前提・根拠の鮮度・権限を、initiator の結論から引き継がず、receiver の境界で確かめ直す
- `delta.transfer.scope` が互換

### 目的
- 提示された宣言の確定
- 損失は境界で止まり、根拠は通る接続の確立

---

## 3.4 REJECT

### receiver が送る
- 理由付きの `verdict: deny`、または `verdict: unknown`

### ルール
- `deny` には必ず理由を付ける。理由そのものは根拠として流す（失敗は止め、学びは流す）。
- `unknown` は、入力が判定に足りないことを示す。止めて露出させ、`decision_authority.escalation.on_unknown` へ上げる。`pass` として扱わない。
- どちらも `pass` と同じく記録する（責任の履歴）。

---

## 3.5 REVERSE（途中反転）

### 発生条件
- 接続中の越境での `guard_deny` / `guard_unknown`
- `precondition_broken`：宣言した前提が成り立たなくなった
- `blast_radius_exceeded`：宣言した上限を超えた
- `authority_revoked`：認めていた判断が取り消された
- `validation_fail`：検証に失敗した

### 送信内容
- `reversal_signal.events`（`phase`、`reason`、`delta_ref`、`holder` を含む）
- 未解決 Δ の返却（保有者付き）

### 必須チェック
- `type = authority_revoked` の場合、実行を止め、人間の `final_decider` に制御を返す
- `type = blast_radius_exceeded` の場合、`blast_radius.on_exceed`（halt / quarantine / escalate）を適用する
- 返却する Δ には `boundary_policy.delta.holder` に従って保有者を付ける。Δ を保有者不在にしない
- 接続中に観測された Positive Δ は、反転によって停止・隔離しない。保有者付きで記録する

### 目的
- Negative Δ を障害区画の中にとどめる
- 判断を閉じる人間に制御を返す

---

## 3.6 CLOSE

### 発生条件
- 人間の `final_decider` による Retire
- 認められた範囲の終了、または `expires_at` 超過

### 送信内容
- 接続に対する責任の解放
- 依存先（`declaration.depends_on`、他の当事者）への通知
- 保有者付きの `residual_assets`

### ルール
- CLOSE は稼働中の依存を隠さない。
- 接続が終わっても残るものには保有者を付ける。保有者のいないものは残らない。

---

# 4. Error Handling

| Error | 意味 | 必須アクション |
|-------|------|----------------|
| invalid_timestamp | 時刻が範囲外 | HELLO を拒否 |
| expired_handshake | expires_at 超過 | HELLO を拒否 |
| reused_nonce | nonce 再利用 | HELLO を拒否 |
| insufficient_validation | validation_level 不足 | REJECT（`unknown`） |
| no_human_final_decider | final_decider が人間でない | REJECT（`deny`） |
| no_owner | 保有者がいない | REJECT（`deny`） |
| undeclared_max_loss | 不可逆なのに max_loss がない | REJECT（`deny`） |
| expand_without_basis | Positive Δ の観測か復旧確認がない Expand | REJECT（`deny`） |
| signature_mismatch | 署名不一致 | REJECT（`deny`） |
| revalidation_mismatch | 前提・根拠・権限が確かめ直せない | REJECT（`unknown`） |
| delta_incompatible | Δ の扱いに不整合 | REVERSE |
| blast_radius_exceeded | 宣言した上限を超えた | REVERSE |

---

# 5. Security Alignment

本プロトコルは `docs/ja/handshake.security.md` と整合する。

特に：

- canonicalization は **json_c14n MUST**
- yaml_c14n を使う場合、署名対象は JSON に変換してから正規化
- nonce は `expires_at + safety_margin(10min)` まで保持
- authority_revoked は常に実行を止め、人間の final_decider に制御を返す

---

# 6. Value Continuity と VCDesign との統合ノート

CCP は Value Continuity も VCDesign も再定義しない。

- ハンドシェイク全体 → VCDesign `boundary-pattern.yaml external_crossing`（identity、declared_boundary、authority、signature）
- ACCEPT / REJECT → guard verdict（pass / deny / unknown）
- `boundary_policy.containment` → containment（Downside は伝播させない）
- `boundary_policy.basis_flow` → basis_flow（Upside は伝播可能にする）
- `boundary_policy.revalidation` → revalidation
- `decision_authority.authorization` → Decision（人間が閉じる）
- `boundary_policy.delta.holder` → closure_loop（Δ を保有者不在にしない）

詳細な対応は `mappings/vcdesign_mapping.ja.md` を参照。

---

# 7. Termination

### 成功
- ACCEPT の署名検証成功時（接続が開く）
- 残るものを引き渡した CLOSE（接続が終わる）

### 失敗
- REJECT
- REVERSE
- expires_at 超過
- nonce 再利用

---

# 8. License

MIT License
© VCDesign Project
