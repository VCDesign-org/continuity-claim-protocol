# Continuity Claim Protocol Specification (CCP)
Version: 2.1
Status: Draft-Stable
Audience: AI Agents / Implementers

**注意:** このドキュメントは、AI生成物（Artifacts）同士が自律的に接続判断を行うためのプロトコル定義である。人間による解釈よりも、シグナルの論理的な処理を優先する。
ハンドシェイク仕様の全体像は `specs/handshake.yaml` を参照。
状態ポリシーは `README.ja.md` を参照。

## 1. Protocol Definition

VCDesign における「接続（Connection）」とは、インターフェースの互換性確認ではなく、**「価値の継続性（Continuity Claim）」の合意**によって確立される。

### Value Definition (価値の定義)
ここでいう「価値」とは、機能や性能ではない。
その生成物が**「生まれた理由（Reason for existence）」**および**「継続している理由（Reason for continuation）」**そのものである。

### Connection Logic
クライアント（接続元）は、ホスト（接続先）の中身を精査する必要はない。
ホストが掲げる **Claim（継続主張）** のステータスのみを監視し、以下のロジックに従って「何も考えずに（Without thinking）」接続または切断を行う。

## 2. Signal States (3つのシグナル)

| Status | Signal Representation | Meaning (Artifact Context) | Action Required |
| :--- | :--- | :--- | :--- |
| **VALID** | `Claim: Signed` | **Not Garbage.**<br>生まれた理由を維持している。<br>責任境界は閉じている。 | **Connect / Keep Alive**<br>(接続・維持) |
| **INVALID** | `Claim: Denied` | **Drifted.**<br>文脈乖離が発生した。<br>もはや期待された存在ではない。 | **Disconnect Immediately**<br>(即時切断) |
| **SILENCE** | `(No Signal)` | **Unsafe / Unknown.**<br>判断保留、または消失。<br>責任を持てない状態。 | **Disconnect Gracefully**<br>(静かに切断) |

**"Silence is Safety" (沈黙は安全)**
沈黙はエラーではない。それは「責任を持てない」という正直な意思表示である。
いかなる理由があろうと、Claim を出さない（沈黙した）相手と接続し続けてはならない。

## 3. Implementation Requirements

このステータスを生成するために、Artifact は内部に以下の3層構造を持たねばならない。

1.  **The Core:** 設計内価値（Logic）の整合性を検証する。
2.  **The Sensor:** 現時点価値（Context）との乖離を検知する。
3.  **The Loop:** 乖離検知時に、自己を停止または修正プロセスへ回す。

これら全てが正常である場合のみ、Artifact は `Claim: Signed` を出力する。

## 4. Protocol Constraint (最終制約)

> **NON-OPTIMIZATION PLEDGE:**
> This protocol MUST NOT be used to optimize performance or metrics.
> It exists solely to prevent the propagation of invalid value.

（このプロトコルを、性能向上や数値目標のために使用してはならない。これは、価値のないものが伝播するのを防ぐためだけに存在する。）
