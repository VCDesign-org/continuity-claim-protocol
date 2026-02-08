# CCP Handshake Specification
CCP = Continuity Claim Protocol（連続性主張プロトコル）
Version: 2.1  
Status: Draft-Stable  
Maintainer: VCDesign Project

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

CCP Handshake は、AI 同士が **その場でインターフェースを自律構築するための最小プロトコル** である。

現代の AI システムは、固定された API や一方的な I/F に従う構造を前提としている。  
しかし、価値の連続性（Continuity）は、**境界（World）と責任（Responsibility）が整合した状態でのみ維持される**。

CCP Handshake は、VCDesign / BOA / RC / DCS の原則に基づき、

- 力関係ではなく「責任の膜（Membrane）」  
- 推測ではなく「境界の宣言」  
- 暗黙ではなく「判断権限の明示」  
- 自動化ではなく「連続性の保証」  

を基準に、AI 同士の接続を安全に開始するための **最小ハンドシェイク** を定義する。

---

## 2. Design Principles

CCP Handshake は以下の原則に基づく。

### **2.1 Boundary First（境界優先）**
AI は用途を推測しない。  
まず「どの世界（World）で会話するか」を宣言し、境界を揃える。

### **2.2 Responsibility Continuity（責任の連続性）**
判断は AI が勝手に閉じてはならない。  
RC（Responsibility Closure）に従い、Δ と R の位置を明確にする。

### **2.3 Determinability Gate（決めてよい／いけないの境界）**
BOA/RCA に基づき、AI が判断を閉じてよい条件を構造的に判定する。

### **2.4 Decision Closure Safety（判断の安全性）**
DCS により、AI が判断を閉じてよいかを  
**5つの Validation Steps** でチェックする。

### **2.5 Minimality（最小性）**
ハンドシェイクは「最小限の情報」で成立する。  
余計な意味推論や暗黙の前提を排除する。

---

## 3. Terminology（用語）

- **Spec**: 仕様の全体像と意図（`specs/handshake.yaml`）
- **Schema**: 構造と検証ルール（`schemas/handshake.schema.yaml`）
- **Protocol**: 動的手順と状態遷移（`docs/ja/handshake.protocol.md`）
- **Security**: 最低限の安全要件（`docs/ja/handshake.security.md`）

---

## 4. Components of the Specification

本パッケージは以下の 4 つの文書で構成される。

### **4.1 specs/handshake.yaml（仕様）**
- ハンドシェイク仕様の全体像と設計意図

### **4.2 schemas/handshake.schema.yaml（構造）**
- ハンドシェイクに必要な **型・構造・検証ルール** を定義
- JSON Schema 互換
- BOA の 3 要素（responsibility_id / meaning_scope / context_assumption）を構造化
- trust を validation_level と risk_level に分離
- decision_authority / resolution_policy / reversal_signal を厳密化
- バージョンは `specs/handshake.yaml` と揃える（現行 2.1）

### **4.3 docs/ja/handshake.protocol.md（手順）**
- HELLO → OFFER → ACCEPT → REVERSE の状態遷移
- 各フェーズでの必須チェック
- DCS による途中反転（mid-conversation reversal）
- Δ の返却と権限の巻き戻し

### **4.4 docs/ja/handshake.security.md（安全性）**
- canonicalization（正規化）
- 署名対象（signed_fields）
- リプレイ防止（nonce / timestamp / expires_at）
- authority_revoked の強制遷移
- Δ の安全な転送

---

## 4. Why CCP Handshake Exists

AI 同士が協調する未来では、  
**固定 API や中央集権的な I/F は価値の連続性を破壊する。**

AI は本来、状況に応じて

- 境界を再定義し  
- 意味の範囲を調整し  
- 責任の位置を交渉し  
- その場で I/F を生成する  

能力を持つ。

しかし、その自由度は **最初のハンドシェイクが安全であること** を前提とする。

CCP Handshake は、その「最初の膜」を提供する。

---

## 5. Minimal Handshake Model

ハンドシェイクは以下の 3 つの柱で成立する。

### **5.1 Identity（誰が接続するか）**
- handshake_id  
- participants  
- signature_schema  

### **5.2 Boundary（どの世界で接続するか）**
- world  
- trust  
- interface  

### **5.3 Authority（誰が判断を閉じるか）**
- decision_authority  
- resolution_policy  
- reversal_signal  

これらが揃ったとき、AI 同士は **自律的に I/F を構築する準備が整う**。

---

## 6. Relationship to VCDesign

CCP Handshake は VCDesign の以下の章に対応する。

| VCDesign Concept | CCP Handshake Component |
|------------------|-------------------------|
| 章（Membrane） | continuity_claim.boundary_def |
| 境界（World） | world.id |
| 責任（Responsibility） | decision_authority.domain |
| Δ と R（RC） | resolution_policy |
| 判断の閉じ方（DCS） | reversal_signal |
| 決めてよい／いけない（BOA/RCA） | trust.validation_level / semantics.intent |

つまり CCP Handshake は、  
**VCDesign の外部接続時の“膜の強度”を保証する仕組み** である。

概念対応の詳細は `mappings/vcdesign_mapping.ja.md` を参照。

---

## 7. Intended Use

CCP Handshake は以下の用途を想定する。

- AI 同士の安全な接続
- 自動コード生成エージェント間の協調
- 境界を跨ぐ責任の受け渡し
- 意味の整合性を保った I/F の自動生成
- サプライチェーンとしての AI プロセスの透明化

---

## 8. Non-Goals

以下は CCP Handshake のスコープ外である。

- モデルの正しさ・性能の保証
- 倫理判断・価値判断
- AI の人格・意図の推定
- 完全な暗号プロトコルの代替

CCP Handshake は **責任と境界の連続性を保証するための最小プロトコル** である。

---

## 9. Getting Started

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

## 10. License

MIT License  
© VCDesign Project

---

## Status Policy（状態ポリシー）

- すべての派生文書が同一バージョン・同一構造になるまで `Draft-Stable` を維持する  
- スキーマとプロトコルの変更がリリースサイクルで凍結された時のみ `Stable` に移行する  
