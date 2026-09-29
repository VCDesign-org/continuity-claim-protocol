# Continuity Claim Protocol Specification (CCP)
Version: 3.0
Status: Draft-Stable
Audience: AI Agents / Implementers

**注意:** このドキュメントは、AI生成物（Artifacts）同士が自律的に接続判断を行うためのプロトコル定義である。人間による解釈よりも、シグナルの論理的な処理を優先する。
ハンドシェイク仕様の全体像は `specs/handshake.yaml` を参照。
状態ポリシーは `README.ja.md` を参照。

## 1. Protocol Definition

CCP における「接続（Connection）」とは、インターフェースの互換性確認ではなく、**継続主張（Continuity Claim）の合意**によって確立される。

CCP は、[Value Continuity](https://github.com/value-continuity/value-continuity) を組織・エージェントをまたぐ越境の面から実装する。
その中心原則である Value Asymmetry Principle ——*Upside は伝播可能にする。Downside は伝播させない。*—— を、接続ごとに適用する。

### Value Definition (価値の定義)
ここでいう「価値」とは、機能や性能ではない。
その生成物が `precondition`（前提）の上で `value_intent` として宣言した、**次の価値を生み出し続ける能力** である。この2つが Δ の基準線になる。

### Connection Logic
クライアント（接続元）は、ホスト（接続先）の中身を精査する必要はない。
ホストが掲げる **Claim（継続主張）** のステータスを監視し、その前提（署名・鮮度・権限）を自分の境界で確かめ直す。ホストの結論は引き継がない。
そのうえで、以下のロジックに従って接続または切断を行う。

## 2. Signal States (3つのシグナル)

各シグナルは、越境に対する guard verdict（VCDesign `boundary-pattern.yaml`）である。

| Status | Signal Representation | Guard Verdict | Meaning (Artifact Context) | Action Required |
| :--- | :--- | :--- | :--- | :--- |
| **VALID** | `Claim: Signed` | `pass` | **Not Garbage.**<br>前提の上で価値を維持している。<br>境界に保有者がいて、人間が閉じた判断が接続を認めている。 | **Connect / Keep Alive**<br>(認められた範囲で接続・維持) |
| **INVALID** | `Claim: Denied` | `deny` | **Drifted.**<br>Negative Δ が確定した。<br>もはや期待された存在ではない。 | **Disconnect Immediately**<br>(即時切断。失敗は閉じ込め、理由は根拠として流す) |
| **SILENCE** | `(No Signal)` | `unknown` | **Unsafe / Unknown.**<br>判断保留、または消失。<br>責任を持てない状態。 | **Disconnect Gracefully**<br>(静かに切断。露出させ、人間の最終判断者へ上げる) |

**"Silence is Safety" (沈黙は安全)**
沈黙はエラーではない。それは「責任を持てない」という正直な意思表示である。
沈黙は `unknown` であり、`unknown` は決して `pass` として扱わない。
いかなる理由があろうと、Claim を出さない（沈黙した）相手と接続し続けてはならない。

**シグナルの非対称**
- `Denied` が止めるのは失敗であって、学びではない。拒否の理由は根拠として相手へ流す。
- Positive Δ（ホストが宣言を上回ること）はシグナルを変えず、切断の理由にもならない。保有者付きで記録する。それを理由に接続を広げるには、人間が閉じる Expand の判断が要る。

## 3. Implementation Requirements

このステータスを生成するために、Artifact は内部に以下の構造を持たねばならない。

1.  **The Core:** 設計内価値（Logic）を `value_intent` に照らして検証する。
2.  **The Sensor:** 宣言した前提と価値からの Δ を、両方の向きで観測する（Context）。
    - Negative Δ → The Loop へ回す。
    - Positive Δ → 保有者付きで記録する。止めない。
3.  **The Loop:** Negative Δ の検知時に、宣言した `blast_radius` の範囲で自己を停止または修正プロセスへ回す。ループが尽きたら、上限なく再試行せず、失敗を閉じ込める（サーキットブレーカー）。
4.  **The Holder:** 確定した Δ ごとに、人間の判断が閉じるまで名前のある保有者を置く。保有者のいない Artifact は `Claim: Signed` を出力できない。

これら全てが正常である場合のみ、Artifact は `Claim: Signed` を出力する。

## 4. Protocol Constraint (最終制約)

> **NON-OPTIMIZATION PLEDGE:**
> This protocol MUST NOT be used to optimize performance or metrics.
> It exists solely to stop the propagation of losses at the boundary
> while keeping basis propagable.

（このプロトコルを、性能向上や数値目標のために使用してはならない。これは、損失の広がりを境界で止め、次の価値のための根拠を流し続けるためだけに存在する。）
