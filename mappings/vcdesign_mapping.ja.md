# CCP ↔ Value Continuity / VCDesign Integration Mapping
Version: 2.0
Status: Stable
Audience: AI Agents / Implementers
Human‑facing: No（Value Continuity と VCDesign はここで再定義しない）

---

# 1. Purpose

本書は、**CCP Handshake** と、CCP が依拠する次の2つとの間にある
**概念的な対応関係（Mapping）** を定義する。

- **[Value Continuity](https://github.com/value-continuity/value-continuity)** —— 思想（定義と原則の正本）
- **[VCDesign v2](https://github.com/VCDesign-org/vcdesign)** —— 判断と責任の面からの、兄弟となる実装

Value Continuity の下に、VCDesign・BEAM・CCP が並ぶ。CCP は Value Continuity を組織・エージェントをまたぐ越境の面から実装する。
本書は CCP 側にのみ置かれ、AI がどちらの文書も誤読しないための翻訳レイヤである。

---

# Contents

1. Purpose
2. Design Principles
3. Non-Goals（非目的）
4. Value Continuity Mapping
5. VCDesign v2 Mapping
6. Non-Mapping
7. Integration Rules
8. Legacy（2.1）Terms
9. Versioning

---

# 2. Design Principles

1. 定義の正本は Value Continuity である。CCP はそれを再定義しない
2. VCDesign と CCP は兄弟である。CCP は VCDesign の語を再定義せず、VCDesign も CCP のフィールドを再定義しない
3. VCDesign がすでに名前を付けている仕組みは、CCP でも同じ語・同じ意味で使う
4. CCP が加えるのは、当事者間の越境に固有のもの（識別、署名、リプレイ防止、ハンドシェイクの状態）だけである
5. 本書は AI のための翻訳レイヤである
6. 人間は本書を読む必要がない（AI 向け）

---

# 3. Non-Goals（非目的）

- Value Continuity や VCDesign の置き換え・変更
- 暗号的・法的保証の形式化
- ガバナンス・倫理・価値判断の定義
- Value Continuity や VCDesign の網羅的オントロジーの提供

---

# 4. Value Continuity Mapping

## 4.1 中心原則

| Value Continuity | CCP | ルール |
|------------------|-----|--------|
| Value Asymmetry Principle —— Downside は伝播させない | `boundary_policy.containment`（propagation の既定は deny） | 損失は境界を越えない |
| Value Asymmetry Principle —— Upside は伝播可能にする | `boundary_policy.basis_flow`（既定は allow） | 根拠・証跡・残るもの・Positive Δ は越える。結論は越えない |
| 「伝播可能」は「自動的に広がる」ではない | `expand_basis` 付きの `authorization.decision = expand` | 接続を広げるのは人間の判断 |
| Δ（宣言した期待との差） | `boundary_policy.delta`。基準線 = `continuity_claim.boundary.precondition` + `continuity_claim.declaration.value_intent` | CCP は Δ の意味を変えない |
| Negative Δ / Positive Δ | containment / basis_flow。`delta.unrecorded_polarity: negative` | Positive Δ は反転によって停止・隔離しない |

## 4.2 5つの原則

| 原則 | CCP |
|------|-----|
| 残す | `continuity_claim.declaration.residual_assets`（保有者付き）、`decision_authority.owner`、`continuity_claim.boundary.owner`、CLOSE |
| 見つける | `continuity_claim.declaration.spread_signals`、`basis_flow.passes: positive_delta` |
| 閉じる | `boundary_policy.containment`、`authorization.blast_radius`、REJECT、REVERSE |
| 試す | `authorization.reversibility`、`escalation.halt_owner`、復旧できる範囲でだけ Expand |
| 伝える | `boundary_policy.basis_flow`、`boundary_policy.revalidation`、deny の理由 |

## 4.3 Decision

| 判断 | CCP |
|------|-----|
| Proceed | `authorization.decision = proceed` —— 現在の宣言のまま接続を開く |
| Expand | `authorization.decision = expand` —— 広げた宣言で新しいハンドシェイク。`expand_basis` が必須 |
| Limit | `authorization.decision = limit` —— 狭めた宣言で新しいハンドシェイク |
| Reframe | 新しい `continuity_claim`（新しい id・前提・保有者）と新しいハンドシェイク |
| Defer | 接続しない。`unknown` の REJECT を、暫定責任者と `next_review_at` 付きで返す |
| Retire | 接続しない、または残るものを引き渡して CLOSE する |

**ルール:** CCP は判断の語彙を増やさない。ハンドシェイクの状態（HELLO、OFFER、ACCEPT、REJECT、REVERSE、CLOSE）はプロトコルの状態であり、判断ではない。

---

# 5. VCDesign v2 Mapping

## 5.1 対応表

| CCP Component | VCDesign v2 | 意味 |
|---------------|-------------|------|
| ハンドシェイク全体 | `boundary-pattern.yaml external_crossing` | identity、declared_boundary、authority、signature |
| `handshake_meta`、`agent` | `external_crossing.identity` | 誰が越境するか |
| `world`、`continuity_claim.boundary`、`continuity_claim.declaration` | `external_crossing.declared_boundary` | どこへ、どの前提で、何の価値のために |
| `decision_authority` | `external_crossing.authority`、`core.yaml decision` | 誰が判断を閉じ、どの範囲か |
| `continuity_claim.signature_schema` | `external_crossing.signature` | 技術層 |
| ACCEPT / REJECT、主張シグナル | `boundary.guard.verdicts`（pass / deny / unknown） | 越境に対する検査。判断ではない |
| `trust.validation_level` | `boundary.guard.determinability`（の入力） | 入力が判定に足りるか。guard の代替ではない |
| `boundary_policy.containment` | `boundary.containment` | 失敗と指令を止める |
| `boundary_policy.basis_flow` | `boundary.basis_flow` | 根拠と残るものを通す |
| `boundary_policy.revalidation` | `boundary.revalidation` | 上流の結論を確かめ直す |
| `continuity_claim.boundary.owner` | `boundary.tenure.owner` | 境界を誰が持ち続けるか |
| `boundary_policy.delta.holder` | `core.yaml closure_loop` | Δ を保有者不在にしない |
| `authorization.blast_radius`、`authorization.reversibility` | `schema_case.yaml blast_radius`、`reversibility` | 事前に宣言した上限と撤回の手段 |
| `decision_authority.final_decider` | `schema_case.yaml final_decider`、axioms A3 | 常に人間 |
| `decision_authority.loop` | `policies.yaml ai_extension.loops` | 越境がどのループに作用するか |
| `decision_authority.escalation.halt_owner` | `policies.yaml haltability` | 誰が止められるか |
| `continuity_claim.boundary.responsibility_boundary` | `catalog/boundaries`（B1〜B17） | 該当する責任境界の型 |

## 5.2 詳細ルール

### Guard verdict
**VCDesign:** 判定は判断ではない。unknown は止めて露出させ、上へ上げる。決して pass ではない。
**CCP:** ACCEPT は `pass`。REJECT は `deny`（理由付き）または `unknown`（`escalation.on_unknown` へ上げる）。`Claim: Silence` は `unknown`。
**ルール:** CCP は沈黙や unknown を pass として扱ってはならない。

### Containment と basis_flow
**VCDesign:** 失敗は既定で止め、根拠と残るものは既定で通す。これが境界の非対称である。
**CCP:** `containment.propagation` の既定は `deny`、`basis_flow.default` の既定は `allow`。deny の理由は根拠として流す。
**ルール:** CCP は、署名された `boundary_policy` で明示せずに、これらの既定を逆転させてはならない。

### Revalidation
**VCDesign:** 上流の結論は引き継がず、確かめ直す。
**CCP:** `revalidation.upstream_trust` の既定は `none`。ACCEPT で前提・根拠の鮮度・権限を確かめ直す。
**ルール:** 署名が証明するのは誰が言ったかであって、それが今も成り立つことではない。

### Decision authority
**VCDesign:** 判断は人間の最終判断者が閉じ、閉じた判断は宣言を通じて範囲を認める（axioms A2、A3）。
**CCP:** `decision_authority.authorization` は、判断、その参照、閉じた人間、その宣言を運ぶ。
**ルール:** CCP は AI を最終判断者として提示してはならず、越境が認められた範囲を超えることを許してはならない。

### Δ
**VCDesign:** 確定した Δ は、判断で閉じるまで責任の下にある。Positive Δ は観測・保有され、止められない。
**CCP:** REVERSE で返す Δ、接続の中で移送する Δ には、すべて保有者を明示する。
**ルール:** CCP は Δ の意味を変えてはならず、Δ を保有者不在にしてはならない。

---

# 6. Non-Mapping（対応させない領域）

以下は Value Continuity にも VCDesign にも **対応するものがない**。CCP の技術層にのみ存在する。

- signature_schema（暗号層）
- canonicalization（正規化）
- nonce / timestamp / expires_at（時間）
- cost_model（計算資源）
- participants（AI 識別子）

---

# 7. Integration Rules

以下は **必須ルール** である。

1. CCP は Value Continuity、Value Asymmetry Principle、5原則、Decision を再定義してはならない。
2. CCP は VCDesign の語を再定義してはならない。同じ意味で使う。
3. CCP は判断の語彙を増やしてはならない。
4. CCP の技術層（署名、正規化、nonce、コスト）は価値の意味を持たない。
5. すべての認可の最終判断者は人間である。
6. unknown は決して pass ではない。

最も重要なルールは次である：**損失は越えず、根拠は越え、どこまで広げるかは人間が決める。**

---

# 8. Legacy（2.1）Terms

CCP 2.1 は、VCDesign v2 で廃止された v1 の概念に対応づけていた。次のように読み替える。

| 2.1 の対応 | 3.0 |
|------------|-----|
| Chapter（膜）→ `continuity_claim.boundary_def` | `continuity_claim.boundary` + `declaration` |
| Boundary → `world.id` | `world`（宣言した境界） |
| BOA（意味 / 責任 / 実行）→ `decision_authority.domain` | `decision_authority.loop` |
| RC（Δ と R）→ `resolution_policy` | `boundary_policy`（delta.holder、containment、basis_flow） |
| DCS（途中反転）→ `reversal_signal` | guard verdict、前提の崩れ、上限超過、権限取り消しによる `reversal_signal` |
| IDG（決定可能性）→ `trust.validation_level` | guard の determinability。`trust.validation_level` はその入力 |

フィールド単位の変更は `README.ja.md` の移行表を参照。

---

# 9. Versioning

- Value Continuity は独立してバージョン管理される
- VCDesign は独立してバージョン管理される（本書は VCDesign v2.0 を対象とする）
- CCP は Value Continuity に依拠し、VCDesign を参照するが、どちらも変更しない
- 本 Mapping は CCP のバージョンに従う（CCP 3.0）

---

# 10. License

MIT License
© VCDesign Project
