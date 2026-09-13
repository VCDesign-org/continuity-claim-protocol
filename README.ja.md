# CCP Handshake Specification
CCP = Continuity Claim Protocol（連続性主張プロトコル）
Version: 2.1  
Status: Draft-Stable  
Maintainer: VCDesign Project

**位置づけ（2026-09 改訂）:** CCP は VCDesign の派生・関連プロジェクトではない。VCDesign が定める
[隣接境界観測ルールの相互性条件](https://github.com/VCDesign-org/vcdesign/blob/main/specs/policies/adjacent-boundary-observation.yaml)
（「隣も同じ規則を守っていることを確認する」という対の要件）の実装形であり、基底層として位置づける。
詳細は §7「VCDesignとの関係」を参照。

---

> **Protocol Manifesto**
>
> 判断は、肯定・否定・不明のいずれかで必ず閉じられ、
> その判定規則は、その判断の実行中に変更されない。
>
> 価値を継続するために、コンティニュアーは
> 判定規則と環境の変化を観測し、判定規則を変更する。
>
> 判断に連鎖・合成が必要なとき、
> それぞれの判断は、責任境界を明示し、
> 相互に「閉じられていること」を前提としてのみ接続される。
>
> 接続の途中で、
> その境界や前提が破綻すると判断された場合には、
> 途中反転を行い、判断を閉じてはならない。
>
> そして価値を維持できなくなった時は、
> その判断を継続する前提を失ったと認め、
> 判断を放棄しなければならない。

---

## 1. Overview

CCP Handshake は、**責任の受け渡しが起きる接続を、その場で安全に成立させるための最小プロトコル**である。

先行事例として実在し、検証済みなのは人の工程間の接続である。引き継ぎ書、FMEA、変更管理の承認フローは、
すでにこのハンドシェイクの一部を——多くは暗黙のうちに——実装している。CCP はそれを構造として取り出し、
何が既に揃っていて、何が欠けているかを明示する。

AI 同士の接続は、この同じ最小形の**特殊例**である。AI を適用先として最初に選んだのは、
擬人化が成立したからではない。責任の受け渡しという操作が、AI 間では他のどこよりも
むき出しになるため、抜けが最も見つけやすいからである。

現代の AI システムは、固定された API や一方的な I/F に従う構造を前提としている。  
しかし、価値の連続性（Continuity）は、**境界（World）と責任（Responsibility）が整合した状態でのみ維持される**。

CCP Handshake は、VCDesign / BOA / RC / DCS の原則に基づき、

- 力関係ではなく「責任の膜（Membrane）」  
- 推測ではなく「境界の宣言」  
- 暗黙ではなく「判断権限の明示」  
- 自動化ではなく「連続性の保証」  

を基準に、責任の受け渡しを伴うあらゆる接続を安全に開始するための **最小ハンドシェイク** を定義する。

---

## 2. なぜ同じ形式が層や規模を超えて使えるか

CCP の3本柱（Identity / Boundary / Authority）は、いずれも**接続の形式のみ**を宣言しており、
接続される主体の性質（人間か、AIか、部門か）を一切含まない。

- Identity は「誰が接続するか」を宣言する。それが人物であるかAIであるかは問わない。
- Boundary は「どの世界（責任範囲）で接続するか」を宣言する。
- Authority は「誰が判断を閉じるか」を宣言する。

主体の性質を含まない形式だからこそ、層や規模が変わっても同一の形式が使い回せる。
AI に最初に適用できたのは、この最小形がそこで最も検証しやすかったからであり、
CCP の本体が AI 向けだからではない。

---

## 3. 人の工程への適用にあたっての注意

HELLO → OFFER → ACCEPT → REVERSE の状態遷移を、そのまま人の工程間ハンドオフに持ち込まないこと。
AI 間接続向けに設計された手順そのものは、人の工程にはオーバースペックであり、かつ形が合わない。

人の工程間では、引き継ぎ書や FMEA の形で、このハンドシェイクの一部——Identity（担当者の宣言）や
Boundary（作業範囲の宣言）に相当するもの——がすでに存在している。

欠けているのは、たいてい **REVERSE**、すなわち**差し戻し条件の宣言**である。
「何が起きたら、この引き継ぎ・この承認を差し戻すか」が、事前に宣言されている引き継ぎ書は稀である。

したがって、製造業現場をはじめとする人の工程への**最小適用**は、新しい書式を導入することではなく、
既存の引き継ぎ・承認フローに「差し戻し条件が宣言されているか」という一点だけを重ねる形になる。
これを人の工程・製造業現場への入口として位置づける。AI 間接続の完全なプロトコル（4本柱すべて）は、
この最小適用を経たあとに必要になる場面でのみ導入する。

---

## 4. Design Principles

CCP Handshake は以下の原則に基づく。

### **4.1 Boundary First（境界優先）**
接続する当事者は用途を推測しない。  
まず「どの世界（World）で会話するか」を宣言し、境界を揃える。

### **4.2 Responsibility Continuity（責任の連続性）**
判断は一方が勝手に閉じてはならない。  
RC（Responsibility Closure）に従い、Δ と R の位置を明確にする。

### **4.3 Determinability Gate（決めてよい／いけないの境界）**
BOA/RCA に基づき、判断を閉じてよい条件を構造的に判定する。

### **4.4 Decision Closure Safety（判断の安全性）**
DCS により、判断を閉じてよいかを  
**5つの Validation Steps** でチェックする。

### **4.5 Minimality（最小性）**
ハンドシェイクは「最小限の情報」で成立する。  
余計な意味推論や暗黙の前提を排除する。

---

## 5. Terminology（用語）

- **Spec**: 仕様の全体像と意図（`specs/handshake.yaml`）
- **Schema**: 構造と検証ルール（`schemas/handshake.schema.yaml`）
- **Protocol**: 動的手順と状態遷移（`docs/ja/handshake.protocol.md`）
- **Security**: 最低限の安全要件（`docs/ja/handshake.security.md`）

---

## 6. Components of the Specification

本パッケージは以下の 4 つの文書で構成される。

### **6.1 specs/handshake.yaml（仕様）**
- ハンドシェイク仕様の全体像と設計意図

### **6.2 schemas/handshake.schema.yaml（構造）**
- ハンドシェイクに必要な **型・構造・検証ルール** を定義
- JSON Schema 互換
- BOA の 3 要素（responsibility_id / meaning_scope / context_assumption）を構造化
- trust を validation_level と risk_level に分離
- decision_authority / resolution_policy / reversal_signal を厳密化
- バージョンは `specs/handshake.yaml` と揃える（現行 2.1）

### **6.3 docs/ja/handshake.protocol.md（手順）**
- HELLO → OFFER → ACCEPT → REVERSE の状態遷移（AI間接続を含む完全形）
- 各フェーズでの必須チェック
- DCS による途中反転（mid-conversation reversal）
- Δ の返却と権限の巻き戻し

### **6.4 docs/ja/handshake.security.md（安全性）**
- canonicalization（正規化）
- 署名対象（signed_fields）
- リプレイ防止（nonce / timestamp / expires_at）
- authority_revoked の強制遷移
- Δ の安全な転送

---

## 7. VCDesignとの関係

CCP Handshake は VCDesign の外側に置かれた付属プロトコルでも、派生プロジェクトでもない。

VCDesign の運用ポリシー集は、境界の検証範囲について「隣接境界観測ルール」を定める。
その規則が成立する条件は、**隣接ノードも同じ規則を守っていることを確認する**という
相互性条件であり、単独では不完全で、必ず対で運用しなければならない
（詳細: [`adjacent-boundary-observation.yaml` / `article_1.mutuality_condition`](https://github.com/VCDesign-org/vcdesign/blob/main/specs/policies/adjacent-boundary-observation.yaml)）。

CCP Handshake の HELLO → OFFER → ACCEPT は、この相互性条件——「自分が境界を宣言し、
相手も境界を宣言していることを確認してから接続する」——を、実行可能な手順として
書き下したものである。REVERSE は、相互性が事後に破綻した場合の離脱手順にあたる。

つまり CCP Handshake は VCDesign の外部接続オプションではなく、
**VCDesign の境界規則が要求する相互性そのものの実装形**である。AI間接続はその中でも
相互性の欠落が最も速く症状化する、最も検証しやすいケースにすぎない。

概念対応の詳細は `mappings/vcdesign_mapping.ja.md` を参照。

| VCDesign Concept | CCP Handshake Component |
|------------------|-------------------------|
| 章（Membrane） | continuity_claim.boundary_def |
| 境界（World） | world.id |
| 責任（Responsibility） | decision_authority.domain |
| Δ と R（RC） | resolution_policy |
| 判断の閉じ方（DCS） | reversal_signal |
| 決めてよい／いけない（BOA/RCA） | trust.validation_level / semantics.intent |
| 隣接境界観測ルールの相互性条件 | HELLO → OFFER → ACCEPT（相互宣言の確認） |

---

## 8. Intended Use

CCP Handshake は以下の用途を想定する。

- 人の工程間の引き継ぎ・承認における差し戻し条件の明示
- AI 同士の安全な接続
- 自動コード生成エージェント間の協調
- 境界を跨ぐ責任の受け渡し
- 意味の整合性を保った I/F の自動生成
- サプライチェーンとしての AI プロセスの透明化

---

## 9. Non-Goals

以下は CCP Handshake のスコープ外である。

- モデルの正しさ・性能の保証
- 倫理判断・価値判断
- AI の人格・意図の推定
- 完全な暗号プロトコルの代替

CCP Handshake は **責任と境界の連続性を保証するための最小プロトコル** である。

---

## 10. Getting Started

最初に読むべき順序：

1. **specs/handshake.yaml**  
   → 仕様の全体像と設計意図を把握する

2. **schemas/handshake.schema.yaml**  
   → どのフィールドが必要か理解する

3. **docs/ja/handshake.protocol.md**  
   → ハンドシェイクの流れを理解する

4. **docs/ja/handshake.security.md**  
   → なぜ安全なのか理解する



---

## 11. License

MIT License  
© VCDesign Project

---

## Status Policy（状態ポリシー）

- すべての派生文書が同一バージョン・同一構造になるまで `Draft-Stable` を維持する  
- スキーマとプロトコルの変更がリリースサイクルで凍結された時のみ `Stable` に移行する
