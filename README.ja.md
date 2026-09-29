# CCP Handshake Specification
CCP = Continuity Claim Protocol（連続性主張プロトコル）
Version: 3.0
Status: Draft-Stable
Maintainer: VCDesign Project

CCP は、[Value Continuity](https://github.com/value-continuity/value-continuity) を
**組織・エージェントをまたぐ越境** の面から実装するプロトコルである。

Value Continuity とは、*変化や失敗があっても、次の価値を生み出せる状態を継続すること* です。
その中心原則である **Value Asymmetry Principle** は、*Upside は伝播可能にする。Downside は伝播させない。* です。
これらの定義は正本にあり、ここでは再定義しない。
CCP は、越境の前に当事者が何を宣言し、越境をどう検査し、
何を止めて何を通し、接続をどう反転・終了するかを定める。

---

> **Protocol Manifesto**
>
> すべての越境は検査され、その判定は pass・deny・unknown のいずれかで閉じる。
> unknown は決して pass として扱わない。止めて、露出させ、人間へ上げる。
>
> 判断は、Value Continuity の6語で、人間が閉じる。
> 閉じた判断は範囲を認め、その範囲の中ではエージェントは自律して動いてよい。
> その範囲を超える変更は Δ であり、判断し直す。
>
> 境界では、損失を止め、根拠を通す。
> 相手の結論は引き継がず、確かめ直す。
>
> 接続の途中で、
> 宣言した前提や上限が破れた場合には、
> 途中反転を行い、すべての Δ を保有者付きで返す。
>
> そして接続が次の価値につながらなくなった時は、
> それを終了し、残るものを保有し続ける者へ引き渡す。

---

## 0. Value Continuity Family

```
Value Continuity  — 思想（定義と原則の正本）
├── VCDesign      — 判断と責任
├── BEAM          — （それぞれのリポジトリで定義）
└── CCP           — 組織・エージェントをまたぐ越境
```

| | 役割 | リポジトリ |
|---|---|---|
| Value Continuity | 定義、Value Asymmetry Principle、5原則、Decision | [value-continuity/value-continuity](https://github.com/value-continuity/value-continuity) |
| VCDesign | Value Continuity を判断と責任の面から実装する | [VCDesign-org/vcdesign](https://github.com/VCDesign-org/vcdesign) |
| BEAM | Value Continuity の兄弟となる実装 | — |
| CCP | Value Continuity を組織・エージェントをまたぐ越境の面から実装する | 本リポジトリ |

CCP は Value Continuity を再定義せず、兄弟の語も再定義しない。
VCDesign がすでに名前を付けている仕組み（guard、containment、basis_flow、revalidation、判断6語）は、
CCP でも同じ語・同じ意味で使う。VCDesign の境界パターンは、`external_crossing` として CCP を参照している。

---

## 1. Overview

CCP Handshake は、組織・エージェントをまたいで、AI 同士が **その場でインターフェースを自律構築するための最小プロトコル** である。

現代の AI システムは、固定された API や一方的な I/F に従う構造を前提としている。
しかし、越境をまたいで価値が続くのは、**境界・責任・認められた範囲が越境の前に宣言されている場合だけ** である。

CCP Handshake は、

- 力関係ではなく「**保有者のいる、宣言された境界**」
- 推測ではなく「**宣言された前提と価値**」
- 暗黙の権限ではなく「**人間が閉じた判断とその範囲**」
- 対称な信頼ではなく「**損失は止め、根拠は通す**」

を基準に、AI 同士の接続を安全に開始するための **最小ハンドシェイク** を定義する。

---

## 2. Design Principles

CCP Handshake は以下の原則に基づく。

### **2.1 Boundary First（境界優先）**
AI は用途を推測しない。
まず、どの世界（World）へ越境するか、境界を誰が保有するか、どの前提の上かを宣言する。

### **2.2 Humans Close Decisions（判断は人間が閉じる）**
AI は判断を支援するが、責任を持たない。
最終判断者は常に人間であり、判断は Proceed / Expand / Limit / Reframe / Defer / Retire の6語のいずれかである。

### **2.3 Scope Authorized by a Decision（判断が認めた範囲）**
越境は、人間の判断（proceed / expand / limit）が宣言した範囲（blast radius、reversibility）の中で動く。
それを超えることは Δ であり、判断し直す。

### **2.4 Asymmetry at the Boundary（境界での非対称）**
Negative Δ は閉じ込める。根拠・証跡・残るもの・Positive Δ は伝播可能にする。
それ以上に広げる —— 接続を広げる —— には、Positive Δ の観測と復旧能力の確認を伴う Expand が要る。

### **2.5 Unknown Fails Safe（unknown は安全側に倒す）**
入力が判定に足りなければ、判定は unknown。止めて、露出させ、上へ上げる。推測しない。

### **2.6 Minimality（最小性）**
ハンドシェイクは「最小限の情報」で成立させる。
不要な意味推論や暗黙の前提を排除する。

---

## 3. Terminology（用語）

- **Spec**: 上位意図とスコープ（`specs/handshake.yaml`）
- **Schema**: 形式構造と検証ルール（`schemas/handshake.schema.yaml`）
- **Protocol**: 動的手順と状態遷移（`docs/ja/handshake.protocol.md`）
- **Security**: 最低限の安全要件と制約（`docs/ja/handshake.security.md`）
- **Guard verdict（判定）**: 個々の越境に対する `pass` / `deny` / `unknown`。判断ではない。
- **Decision（判断）**: Value Continuity の6語のいずれか。人間が閉じる。

---

## 4. Components of the Specification

### **4.1 specs/handshake.yaml（仕様）**
- ハンドシェイクの上位仕様、設計意図、Value Continuity と VCDesign との整合

### **4.2 schemas/handshake.schema.yaml（構造）**
- ハンドシェイクに必要な **型・構造・検証ルール** を定義
- JSON Schema 互換
- `decision_authority`：人間の最終判断者、保有者、ループ、認可（判断・blast radius・reversibility）、エスカレーション
- `boundary_policy`：containment、basis_flow、revalidation、Δ の保有者
- `continuity_claim`：境界（保有者・前提・意味範囲）、宣言（価値・残るもの・広がりの兆候）、署名
- バージョンは `specs/handshake.yaml` と一致（現在 3.0）

### **4.3 docs/ja/handshake.protocol.md（手順）**
- 状態遷移：HELLO → OFFER → ACCEPT / REJECT → REVERSE → CLOSE
- 各フェーズの必須チェック
- guard verdict と、判断6語のプロトコル上の扱い
- 保有者付きの Δ の返却と、人間への制御の返却

### **4.4 docs/ja/handshake.security.md（安全性）**
- canonicalization
- signed_fields
- リプレイ防止（nonce / timestamp / expires_at）
- 権限の安全（人間の最終判断者、Expand の条件、遅いループに作用する AI）
- 境界の安全（containment、basis_flow、revalidation、Δ）

### **4.5 docs/ja/continuity-claim.md（主張シグナル）**
- `Signed` / `Denied` / `Silence` を guard verdict の `pass` / `deny` / `unknown` として読む

---

## 5. Why CCP Handshake Exists

AI が協調する未来において、
**固定 API や中央集権的 I/F は、一つの失敗を広げ、学びを通さない。**

AI は本来、

- 境界を再定義し
- 意味の範囲を調整し
- 責任の所在を交渉し
- その場でインターフェースを生成する

能力を持つ。

しかし、この自由度は **最初の越境が宣言され、検査されていること** を前提とする。

CCP Handshake は、その最初の境界 —— 損失が止まり、根拠が通り、人間が閉じた判断が範囲を決める場所 —— を提供する。

---

## 6. Minimal Handshake Model

ハンドシェイクは、VCDesign の `external_crossing` の要件 —— **識別・境界・権限・署名** —— を満たす。

### **6.1 Identity（誰が接続するか）**
- handshake_meta（handshake_id、participants）
- agent（id、provider、kind）

### **6.2 Declared Boundary（どの世界で、どの前提の上か）**
- world
- continuity_claim.boundary（owner、precondition、meaning_scope）
- continuity_claim.declaration（value_intent、residual_assets）
- boundary_policy（containment、basis_flow、revalidation、delta）

### **6.3 Authority（誰が判断を閉じ、どの範囲か）**
- decision_authority（final_decider、owner、loop、authorization、escalation）
- reversal_signal

### **6.4 Signature**
- continuity_claim.signature_schema

これらが揃ったとき、AI 同士は認められた範囲の中で **自律的にインターフェースを構築できる状態** になる。

---

## 7. Relationship to Value Continuity and VCDesign

| Value Continuity / VCDesign | CCP Handshake Component |
|-----------------------------|-------------------------|
| Value Asymmetry Principle（Downside）/ containment | `boundary_policy.containment` |
| Value Asymmetry Principle（Upside）/ basis_flow | `boundary_policy.basis_flow` |
| revalidation | `boundary_policy.revalidation` |
| guard verdict（pass / deny / unknown） | ACCEPT / REJECT、主張シグナル |
| Decision（6語） | `decision_authority.authorization.decision` とプロトコル上の帰結 |
| Δ（基準線：前提 + 価値） | `continuity_claim.boundary.precondition`、`continuity_claim.declaration.value_intent` |
| closure_loop（Δ を保有者不在にしない） | `boundary_policy.delta.holder` |
| tenure（境界を誰が持ち続けるか） | `continuity_claim.boundary.owner` |
| AI 拡張（A3、ループ、停止可能性） | `agent.kind`、`decision_authority.loop`、`escalation.halt_owner` |
| 境界パターン `external_crossing` | ハンドシェイク全体 |

概念レベルの詳細な対応は `mappings/vcdesign_mapping.ja.md` を参照。

---

## 8. Migration from 2.1（2.1 からの移行）

VCDesign v2 にならい、3.0 は 2.1 との互換性を切っている。2.1 の語彙は次のように読み替える。

| 2.1 | 3.0 |
|-----|-----|
| 位置づけ：不動の VCDesign Core の外側にある技術膜 | Value Continuity を越境の面から実装するもの。VCDesign・BEAM の兄弟 |
| BOA / RC / DCS / IDG / RCA | guard（determinability を含む）、containment、basis_flow、revalidation、判断6語 |
| `decision_authority.initial_state: Human-Closed / AI-Closed` | `decision_authority.final_decider`（常に `human`）。AI-Closed は削除（AI は最終責任を持たない） |
| `decision_authority.allowed_transitions`、`escalation_rules`（AI→Human） | `decision_authority.escalation`（`on_unknown`、`halt_owner`）。制御は常に人間の最終判断者へ戻る |
| `decision_authority.domain: meaning / responsibility / execution` | `decision_authority.loop: physical / semantic / value / responsibility` |
| — | `decision_authority.owner`、`decision_authority.authorization`（decision、decision_ref、decided_by、blast_radius、reversibility、expand_basis） |
| `resolution_policy`（Δ と R） | `boundary_policy` |
| `resolution_policy.delta_transfer.{allowed, scope}` | `boundary_policy.delta.transfer.{allowed, scope}` |
| `resolution_policy.delta_transfer.redaction` | `boundary_policy.basis_flow.redaction` |
| `resolution_policy.resolver` | `boundary_policy.delta.holder`（判断で閉じるまで Δ を保有する） |
| — | `boundary_policy.containment`、`boundary_policy.basis_flow`、`boundary_policy.revalidation` |
| `reversal_signal.events.type: validation_fail / authority_revoked` | `guard_deny`、`guard_unknown`、`precondition_broken`、`blast_radius_exceeded` を追加。payload に `delta_ref`、`holder` を追加 |
| `continuity_claim.boundary_def`（BOA の3要素） | `continuity_claim.boundary` + `continuity_claim.declaration` |
| `boundary_def.responsibility_id` | `boundary.owner`（任意で `boundary.responsibility_boundary`、B1〜B17） |
| `boundary_def.context_assumption` | `boundary.precondition` |
| `boundary_def.meaning_scope` | `boundary.meaning_scope` |
| — | `declaration.value_intent`、`residual_assets`、`spread_signals`、`review_triggers`、`depends_on` |
| — | `agent.kind: ai / human / system` |
| 状態 HELLO / OFFER / ACCEPT / REJECT / REVERSE | CLOSE を追加。ACCEPT = `pass`、REJECT = `deny` または `unknown` |
| 「DCS に基づく途中反転」 | guard verdict、前提の崩れ、上限超過、権限取り消しによる REVERSE |
| 主張シグナル Signed / Denied / Silence | 変更なし。guard verdict の pass / deny / unknown として読む |
| `specs/handshake.yaml schema_definition`（インラインの複製） | `specs/handshake.yaml schema.ref` → `schemas/handshake.schema.yaml` |

`docs/` 配下の2つの PDF は 2.1 を説明したもので、履歴として残している。

---

## 9. Intended Use

CCP Handshake は以下の用途を想定する：

- 組織をまたぐ AI 同士の安全な接続
- 自動コード生成エージェント同士の協調
- 境界を越えた責任と Δ の引き渡し
- 意味整合性を保ったインターフェースの自動生成
- サプライチェーンとしての AI 処理の透明化

---

## 10. Non-Goals

以下は CCP Handshake の範囲外である：

- Value Continuity や VCDesign の再定義
- モデルの正しさ・性能の保証
- 倫理判断・価値判断
- AI の人格・意図の推定
- 完全な暗号プロトコルの代替

CCP Handshake は、**損失は越境させず、根拠は越境させるための最小プロトコル** である。

---

## 11. Getting Started

最初に読む順序：

1. **[Value Continuity](https://github.com/value-continuity/value-continuity)**
   → CCP が実装する思想

2. **specs/handshake.yaml**
   → 上位意図と構造を理解する

3. **schemas/handshake.schema.yaml**
   → どのフィールドが必須かを理解する

4. **docs/ja/handshake.protocol.md**
   → ハンドシェイクの流れを理解する

5. **docs/ja/handshake.security.md**
   → なぜ安全なのかを理解する

---

## 12. License

MIT License
© VCDesign Project

---

## Status Policy（状態ポリシー）

- すべての派生文書が同一バージョン・同一構造になるまで `Draft-Stable` を維持する
- スキーマとプロトコルの変更がリリースサイクルで凍結された時のみ `Stable` に移行する
