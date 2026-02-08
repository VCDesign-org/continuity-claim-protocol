# CCP Handshake Security Specification
Version: 2.1
Status: Draft-Stable
Audience: AI Agents / Implementers

本書は、schemas/handshake.schema.yaml および docs/ja/handshake.protocol.md に適用される  
「安全性の最低要件」を定義する。
仕様の全体像と意図は `specs/handshake.yaml` を参照。
状態ポリシーは `README.ja.md` を参照。

VCDesign Core は不動であり、本書は CCP 側の技術層として存在する。

---

# 1. Threat Model（脅威モデル）

CCP Handshake は以下の脅威を想定する：

- リプレイ攻撃（過去の handshake を再送して合意を偽装）
- 中間者攻撃（内容の改ざん）
- 署名の不一致（正規化方式の違いによるハッシュ不一致）
- 参加者のなりすまし
- Δ（未解決領域）の不正転送
- decision_authority の不正昇格（AI→Human の逆転）
- VCDesign Core の責任境界の破壊

本仕様は、これらを最小コストで防ぐための要件を定義する。

---

# 2. Handshake Meta の安全要件

`handshake_meta` は以下の 5 要素を必須とする。

## 2.1 handshake_id
- 一意な識別子（UUIDv4 推奨）
- 署名対象に含めること

## 2.2 timestamp
- ISO 8601
- 受信側は **現在時刻 ±5 分以内** であることを検証する

## 2.3 expires_at
- ISO 8601
- **現在時刻より未来であること**（Protocol 側と整合）

## 2.4 nonce
- 128bit 以上のランダム値
- **未使用であることを検証する**

## 2.5 participants
- initiator / receiver の ID を明示
- 署名対象に含めること

---

# 3. Canonicalization（正規化）

署名の前に canonicalization を適用する。

## 3.1 MUST / MAY の明確化（修正版）

MUST: json_c14n
MAY: yaml_c14n（ただし署名対象は JSON に変換してから canonicalize すること）


### 理由
- YAML は実装差が大きく、署名互換性が壊れやすい  
- JSON 化 → canonicalization により、表現差を完全排除できる  

## 3.2 canonicalization の要件
- フィールド順序を固定
- 空白・改行の揺れを排除
- 数値と文字列の型を固定
- YAML のアンカー・エイリアスを禁止

---

# 4. Signed Fields（署名対象）

`continuity_claim.signature_schema.signed_fields` に列挙された  
フィールドのみを署名対象とする。

推奨セット：
signed_fields:
handshake_meta
world
agent
trust
interface
decision_authority
resolution_policy

※ signature_schema 自体は技術層であるため signed_fields に含める必要はないが、
continuity_claim の “boundary_def（主張部分）” を signed_fields に含める運用も許容される。

### 補足：continuity_claim の署名対象について

`signature_schema` 自体（アルゴリズム、鍵参照、正規化方式など）は
技術的メタデータであるため、必ずしも `signed_fields` に含める必要はない。

一方で、以下のような **合意の意味・境界を規定する主張部分**については、
実装または運用ポリシーに応じて `signed_fields` に含めることを許容する：

- continuity_claim.boundary_def
- continuity_claim.claim_text
- その他、合意内容として将来の検証対象となる主張フィールド

これにより、
- 「どの境界について合意したか」
- 「その主張が後から書き換えられていないか」

を、署名によって検証可能とする。


### 意味
- VCDesign の境界・責任・意味を固定する  
- 技術層（署名）が哲学層（VCDesign）を破壊しないようにする  

---

# 5. Replay Protection（リプレイ防止）

リプレイ攻撃を防ぐため、以下の 3 要素を組み合わせる。

## 5.1 nonce の保持期間（修正版）
nonce は expires_at + safety_margin まで保持すること
safety_margin は 10 分を推奨（SHOULD）


## 5.2 timestamp の許容範囲
- ±5 分以内

## 5.3 expires_at の強制
- 有効期限切れの handshake は無効

---

# 6. Authority Safety（判断権限の安全性）

decision_authority の誤用を防ぐため、以下を必須とする。

## 6.1 intent=decision の場合
- `trust.risk_level >= 2`
- `trust.validation_level >= semantic`
- `irreversible=true` の場合、`initial_state=Human-Closed`

## 6.2 AI→Human の強制
以下の条件では必ず AI→Human に遷移する：

- DCS validation_fail  
- reversal_signal.type = authority_revoked  
- trust.validation_level < semantic  
- Δ の不整合  

---

# 7. Delta Safety（Δ の安全性）

Δ（未解決領域）の扱いは以下を満たすこと。

## 7.1 delta_transfer.scope
- `prompt` / `artifact` / `state` / `tool_call`

## 7.2 redaction
- `required` の場合、個人情報・秘密情報を削除

## 7.3 Δ の署名
- Δ を転送する場合、送信側は Δ のハッシュを付与する

---

# 8. Reversal Safety（途中反転の安全性）

途中反転（REVERSE）は以下の条件で発生する。

## 8.1 発生条件
- DCS validation_fail  
- decision_authority の矛盾  
- trust 条件の破綻  
- Δ の不整合  
- VCDesign の境界を破る可能性が検出された場合  

## 8.2 通知内容
- `reversal_signal.events`
- `phase`（HELLO / OFFER / ACCEPT / REVERSE）
- `reason`

## 8.3 権限巻き戻し
- `authority_revoked` の場合、AI→Human を強制

---

# 9. VCDesign Integration Safety

CCP は VCDesign Core の責任境界を上書きしてはならない。

特に：
decision_authority.domain は VCDesign の責任領域を参照するだけであり、
その意味を変更してはならない。

resolution_policy は RC（Δ と R）の技術的写像であり、
Δ の哲学的意味を変更してはならない。


---

# 10. Termination Safety

## 10.1 成立
- ACCEPT が署名検証に成功したとき

## 10.2 不成立
- REJECT  
- REVERSE  
- expires_at 超過  
- nonce 再利用  

---

# 11. License

MIT License  
© VCDesign Project
