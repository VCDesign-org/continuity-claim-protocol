# CCP Handshake Protocol Specification
Version: 2.1
Status: Draft-Stable
Audience: AI Agents / Implementers

本書は、schemas/handshake.schema.yaml に基づき、
AI 同士が安全に接続するための「動的手順（プロトコル）」を定義する。
仕様の全体像と意図は `specs/handshake.yaml` を参照。
状態ポリシーは `README.ja.md` を参照。

VCDesign Core は不動であり、本書は CCP 側の技術層として存在する。

---

# 1. Overview

CCP Handshake は以下の 4 フェーズで構成される：

1. HELLO  
2. OFFER  
3. ACCEPT  
4. REVERSE（任意・途中反転）

各フェーズでは、VCDesign の境界・責任・意味を破壊しないための
必須チェックが定義される。

---

# 2. States

| State | Purpose |
|-------|---------|
| HELLO | セッション開始、境界と検証レベルの交換 |
| OFFER | initiator が提案（責任・意味・Δ の扱い）を提示 |
| ACCEPT | receiver が提案を承認し、署名を返す |
| REJECT | receiver が提案を拒否 |
| REVERSE | DCS/RC/BOA に基づく途中反転 |

---

# 3. Message Sequence

## 3.1 HELLO

### 送信内容（双方）:
- handshake_meta 
    （handshake_id / timestamp / expires_at / nonce / participants を含む）
- world.id
- agent.id
- trust.validation_level


### 必須チェック（修正版）
- `timestamp` が現在時刻 ± 5 分以内  
- `expires_at` が現在時刻より未来であること（※追加）  
- `nonce` が未使用であること  
- `signature_schema` が有効であること  

### 目的
- セッションの一意性  
- 時刻整合性  
- 署名方式の合意  
- VCDesign の境界（world）の共有  

---

## 3.2 OFFER

### initiator が送信
- `interface`
- `cost_model`
- `decision_authority`
- `resolution_policy`
- `continuity_claim`

### 必須チェック
intent に応じて validation_level の条件が変わる：
intent = proposal | advice:
trust.validation_level >= syntax

intent = decision:
trust.validation_level >= semantic


追加チェック：
- `intent=decision` の場合、`risk_level >= 2`
- `irreversible=true` の場合、`initial_state=Human-Closed`
- `delta_transfer.scope` が schema と整合

### 目的
- 意味の範囲（Meaning Scope）の宣言  
- 責任の位置（BOA）の宣言  
- Δ と R の扱い（RC）の宣言  
- 章の外部写像（continuity_claim）の提示  

---

## 3.3 ACCEPT

### receiver が送信
- 署名（signature）
- canonicalization 情報
- resolver 決定（任意）

resolver の決定は resolution_policy.resolver に記述し、
ACCEPT 時に receiver が最終値を返す（任意）。

esolution_policy.resolver に書く

### 必須チェック
- `signed_fields` を canonicalization（json_c14n）で正規化  
- 署名が一致すること  
- `delta_transfer.scope` が互換であること  
- `decision_authority.domain` が VCDesign Core の責任境界と矛盾しないこと  

### 目的
- 提案内容の固定  
- VCDesign の膜を破らない接続の確立  

---

## 3.4 REVERSE（途中反転）

### 発生条件
- DCS validation_fail  
- trust 条件の破綻  
- decision_authority の矛盾  
- Δ の不整合  
- VCDesign の境界を破る可能性が検出された場合  

### 送信内容
- `reversal_signal.events`
- 未解決 Δ の返却

### 必須チェック
- `type = authority_revoked` の場合、`AI→Human` を強制  
- Δ は resolution_policy に従って返却  

### 目的
- VCDesign の責任境界を守る  
- AI が誤って判断を閉じることを防ぐ  

---

# 4. Error Handling

| Error | Meaning | Required Action |
|-------|---------|-----------------|
| invalid_timestamp | 時刻が範囲外 | HELLO を拒否 |
| expired_handshake | expires_at 超過 | HELLO を拒否 |
| reused_nonce | nonce 再利用 | HELLO を拒否 |
| insufficient_validation | validation_level 不足 | OFFER を拒否 |
| signature_mismatch | 署名不一致 | ACCEPT を拒否 |
| delta_incompatible | Δ の扱いが不整合 | REVERSE |

---

# 5. Security Alignment

本プロトコルは `docs/ja/handshake.security.md` と整合する。

特に：

- canonicalization は **json_c14n MUST**  
- yaml_c14n を使う場合、署名対象は JSON に変換してから正規化  
- nonce は `expires_at + safety_margin(10min)` まで保持  
- authority_revoked は必ず AI→Human  

---

# 6. VCDesign Integration Notes

本プロトコルは VCDesign Core を変更しない。

- world.id → VCDesign の境界  
- continuity_claim.boundary_def → 章の外部写像  
- decision_authority.domain → BOA の責任領域  
- resolution_policy → RC（Δ と R）  
- reversal_signal → DCS（途中反転）  

**CCP は VCDesign の責任境界を上書きしてはならない。**

---

# 7. Termination

### 成立
- ACCEPT が署名検証に成功したとき

### 不成立
- REJECT  
- REVERSE  
- expires_at 超過  
- nonce 再利用  

---

# 8. License

MIT License  
© VCDesign Project
