# CCP ↔ VCDesign Integration Mapping
Version: 1.1
Status: Stable
Audience: 本書自体は AI Agents / Implementers 向け（実装者向けの対応表であり、CCP 自体が
AI専用というわけではない。README.ja.md §1〜§2 参照）
Human‑facing: この対応表に限っては No（VCDesign Core は不動のまま）

---

# 1. Purpose

本書は、**CCP Handshake** と **VCDesign Core** の間に存在する
**概念的な対応関係（Mapping）** を定義する。CCP Handshake は VCDesign の
「隣接境界観測ルール」の相互性条件の実装形であり（README.ja.md §7 参照）、
その対象は AI 同士の接続に限らず、責任の受け渡しを伴うあらゆる接続である。
本書自体は、CCP のフィールドと VCDesign の概念を結びつける実装者向けの
現場向けリファレンスにすぎない。

VCDesign Core は不動であり、  
本書は CCP 側に置かれる実装者向けの技術対応表であって、Core を再定義しない。

---

# Contents

1. Purpose
2. Design Principles
3. Non-Goals（非目的）
4. High‑Level Mapping Table
5. Detailed Mapping

---

# 2. Design Principles

1. VCDesign Core は変更しない  
2. CCP は VCDesign Core が要求する相互性条件の技術的実装であり、Core の外側に
   付属した膜ではない（README.ja.md §7 参照）  
3. CCP は Core の概念を“参照”するだけ  
4. Core の意味を CCP が再定義してはならない  
5. 本書は実装者が CCP のフィールドを VCDesign の概念に正しく結びつけるための翻訳レイヤ  
6. この対応表自体は実装者向けの現場資料である——これは CCP 全体が誰のためのものかの
   宣言ではなく、本書一点の読者範囲についての記述にすぎない  

---

# 3. Non-Goals（非目的）

- VCDesign Core を置き換えたり変更したりしない  
- 暗号学的／法的な保証の定義はしない  
- ガバナンスや倫理・価値判断を定義しない  
- VCDesign の完全なオントロジー化はしない  

---

# 4. High‑Level Mapping Table

| CCP Component | VCDesign Concept | Meaning |
|---------------|------------------|---------|
| `world.id` | Boundary（境界） | 会話が行われる“世界”の宣言 |
| `continuity_claim.boundary_def` | 章（Membrane） | 責任の膜の外部写像 |
| `decision_authority.domain` | BOA（Meaning / Responsibility / Execution） | 判断権限の位置 |
| `resolution_policy` | RC（Δ と R） | 未解決領域と解決の扱い |
| `reversal_signal` | DCS（途中反転） | 判断権限の巻き戻し |
| `trust.validation_level` | IDG（決めてよい／いけない） | 判断の昇格条件 |
| `interface.semantics.intent` | Meaning Scope | 出力の意味の範囲 |
| `signature_schema` | VCDesign外（技術層） | Core には存在しない暗号膜 |

---

# 5. Detailed Mapping

## 5.1 Boundary（境界）
**VCDesign:**  
境界は「世界の物理法則」を定義する。

**CCP:**  
`world.id` は VCDesign の境界を参照する。

**Rule:**  
CCP は境界の意味を再定義してはならない。

---

## 5.2 Membrane（章）
**VCDesign:**  
章は「責任の膜」であり、価値の連続性を保持する単位。

**CCP:**  
`continuity_claim.boundary_def` は BOA の 3 要素を構造化した  
“章の外部写像”である。

**Rule:**  
CCP は章を生成しない。  
章の定義は VCDesign Core のみが行う。

---

## 5.3 Responsibility（責任）
**VCDesign:**  
責任は「どこで判断を閉じるか」を決める。

**CCP:**  
`decision_authority.domain` は BOA の三分割を参照する。

**Rule:**  
CCP は責任の意味を変更してはならない。

---

## 4.4 Δ と R（RC）
**VCDesign:**  
Δ は未解決領域、R は解決。

**CCP:**  
`resolution_policy` は Δ の転送・解決者・削除範囲を定義する。

**Rule:**  
CCP は Δ の哲学的意味を変更してはならない。

---

## 4.5 Decision Closure（DCS）
**VCDesign:**  
AI が判断を閉じてよいかを 5 つの Validation Steps で判定。

**CCP:**  
`reversal_signal` は DCS の途中反転を技術的に通知する。

**Rule:**  
CCP は DCS の判定ロジックを変更してはならない。

---

## 4.6 Determinability Gate（BOA/IDG）
**VCDesign:**  
決めてよい／いけないを構造的に判定する。

**CCP:**  
`trust.validation_level` は IDG の“技術的写像”。

**Rule:**  
validation_level は IDG の代替ではない。

---

## 4.7 Meaning Scope
**VCDesign:**  
意味の範囲は章の内部で定義される。

**CCP:**  
`interface.semantics.intent` は意味の範囲を通信上で宣言する。

**Rule:**  
intent は VCDesign の Meaning Scope を上書きしない。

---

# 5. Non‑Mapping（対応しない領域）

以下は VCDesign Core と CCP の間で **対応させてはならない**。

- signature_schema（暗号層）  
- canonicalization（正規化）  
- nonce / timestamp（時刻）  
- cost_model（計算資源）  
- participants（AI識別子）  

これらは VCDesign の哲学的膜とは無関係であり、  
**CCP の技術層にのみ存在する概念**。

---

# 6. Integration Rules

以下は **VCDesign Core を守るための強制ルール** である。

1. VCDesign Core は不動であり、CCP は Core を変更してはならない。  
2. CCP は Core の概念を“参照”するだけであり、意味を再定義してはならない。  
3. CCP の技術層（署名・正規化・nonce 等）は Core に影響を与えない。  
4. 実装者は本書を読み、CCP のフィールドを Core の概念と取り違えないようにする。  
5. 本対応表は実装者向けであり、VCDesign Core 自体の文書が人間向けの入口であり続ける。  
6. CCP は decision_authority や resolution_policy を通じて、
VCDesign Core の責任境界（Meaning / Responsibility / Execution）を
上書きしてはならない。


これは **VCDesign の膜を守るための最重要ルール** である。

---

# 7. Intended Audience

- AI Agents  
- CCP Implementers  
- Multi‑Agent System Designers  
- Boundary‑aware AI Frameworks  
- 差し戻し条件の最小適用（README.ja.md §3）を人の工程に適用する担当者は、本書を
  読む必要はない——本書は実装者向けのフィールド対応表であり、引き継ぎ・承認フローに
  CCP を適用するための必読文書ではない。

---

# 8. Versioning

- VCDesign Core は独立してバージョン管理される  
- CCP Handshake は Core が要求する規則を実装するが、Core を変更しない  
- 本 Mapping は CCP のバージョンに従う  

---

# 9. License

MIT License  
© VCDesign Project
