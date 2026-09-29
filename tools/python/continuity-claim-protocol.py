"""
Continuity Claim Protocol (CCP) 3.0 — reference demo

Artifact が Claim（SIGNED / DENIED / SILENCE）を出す仕組みのデモ。
Claim は越境に対する guard verdict（pass / deny / unknown）である（docs/*/continuity-claim.md）。

- The Core   : value_intent に照らして生成物を作る
- The Sensor : 宣言した前提と価値からの Δ を、両方の向きで観測する
- The Loop   : Negative Δ のとき、blast_radius の範囲で修正を試みる
- The Holder : 確定した Δ には必ず保有者を付ける
- Circuit Breaker : ループが尽きた失敗が続いたら閉じ込める（containment）

署名はモックであり、暗号的な安全性はない。
"""

import enum
import hashlib
import time  # クールダウン管理用
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

# ==========================================
# Claim と境界
# ==========================================

@dataclass(frozen=True)
class ClaimBoundary:
    """continuity_claim.boundary + declaration.value_intent"""
    owner: str            # 境界を保有し続ける主体（tenure）
    precondition: str     # Δ の基準線（前提）
    meaning_scope: str
    value_intent: str     # Δ の基準線（価値）

    def to_string(self) -> str:
        return f"{self.owner}::{self.meaning_scope}::{self.precondition}"


class ClaimSignal(enum.Enum):
    SIGNED = "✅ SIGNED"    # pass
    DENIED = "🚫 DENIED"    # deny（理由必須。理由は根拠として流す）
    SILENCE = "💀 SILENCE"  # unknown（止めて露出させ、人間へ上げる。pass として扱わない）

    @property
    def verdict(self) -> str:
        return {"SIGNED": "pass", "DENIED": "deny", "SILENCE": "unknown"}[self.name]


class Polarity(enum.Enum):
    NEGATIVE = "negative"  # 伝播させない
    POSITIVE = "positive"  # 伝播可能にする（観測と保有は止めない。広げるのは Expand）


@dataclass(frozen=True)
class Delta:
    polarity: Polarity
    description: str
    holder: str  # 判断で閉じるまで Δ を保有する主体（closure_loop）


@dataclass(frozen=True)
class Claim:
    signal: ClaimSignal
    reason: str
    boundary: ClaimBoundary
    content_digest: Optional[str]
    signature: Optional[str]


# ==========================================
# 署名（モック）
# ==========================================

class MockNotary:
    """鍵ペアを模した署名器。実装では ed25519 等に置き換える"""

    def __init__(self, secret: str):
        self._secret = secret

    def sign(self, digest: str, boundary: ClaimBoundary) -> str:
        return hashlib.sha256(f"{self._secret}|{digest}|{boundary.to_string()}".encode()).hexdigest()


class MockVerifier:
    def __init__(self, notary: MockNotary):
        self._notary = notary

    def verify(self, claim: Claim) -> bool:
        if claim.signal != ClaimSignal.SIGNED or not claim.content_digest:
            return False
        return claim.signature == self._notary.sign(claim.content_digest, claim.boundary)


# ==========================================
# Sensor（Δ の観測）
# ==========================================

class CodeSensor:
    """value_intent = 実行可能な Python コードを返す、という宣言に照らして Δ を観測する"""

    def observe(self, content: str, boundary: ClaimBoundary) -> List[Delta]:
        deltas: List[Delta] = []
        if not content.startswith("def "):
            deltas.append(Delta(Polarity.NEGATIVE, "output is not code", boundary.owner))
        elif "# reusable" in content:
            # 宣言を上回る差。異常として扱わず、保有者付きで記録する
            deltas.append(Delta(Polarity.POSITIVE, "output is reusable beyond the task", boundary.owner))
        return deltas


# ==========================================
# Circuit Breaker（containment）
# ==========================================

@dataclass
class BreakerConfig:
    max_retries_per_task: int = 3   # 1タスク内の The Loop リトライ上限（blast_radius の範囲）
    failure_threshold: int = 5      # 連続何回タスク失敗でヒューズを飛ばすか
    cooldown_seconds: float = 10.0  # ヒューズが飛んだ後の冷却時間


class CircuitBreaker:
    def __init__(self, config: BreakerConfig):
        self.config = config
        self.consecutive_failures = 0
        self.state = "CLOSED"  # CLOSED=正常, OPEN=遮断中
        self.last_trip_time = 0.0

    def can_execute(self) -> bool:
        """実行許可判定"""
        if self.state == "CLOSED":
            return True

        # OPEN(遮断)中の場合、冷却時間が過ぎたかチェック
        elapsed = time.time() - self.last_trip_time
        if elapsed > self.config.cooldown_seconds:
            print("   [Breaker] 🔄 Cooldown complete. Resetting to CLOSED.")
            self.reset()
            return True

        return False

    def reset(self):
        self.state = "CLOSED"
        self.consecutive_failures = 0

    def record_success(self):
        """成功時は失敗カウントをリセット"""
        self.consecutive_failures = 0

    def record_failure(self):
        """タスク失敗を記録し、閾値を超えたらTripさせる"""
        self.consecutive_failures += 1
        print(f"   [Breaker] ⚠️ Failure Count: {self.consecutive_failures}/{self.config.failure_threshold}")

        if self.consecutive_failures >= self.config.failure_threshold:
            self.trip()

    def trip(self):
        """ヒューズを飛ばす（失敗を区画の外へ伝播させない）"""
        self.state = "OPEN"
        self.last_trip_time = time.time()
        print(f"   [Breaker] 💥 TRIPPED! Circuit is now OPEN. Cooldown for {self.config.cooldown_seconds}s.")


# ==========================================
# Artifact
# ==========================================

class ClaimArtifact:
    def __init__(self, name, boundary: ClaimBoundary, core, sensor, breaker_config: BreakerConfig):
        self.name = name
        self.boundary = boundary
        self._core = core
        self._sensor = sensor

        self._notary = MockNotary(secret=f"key-of-{name}")
        self._verifier = MockVerifier(self._notary)
        self._breaker = CircuitBreaker(breaker_config)

        self._last_result: Tuple[Optional[Claim], Optional[str]] = (None, None)
        self.held_deltas: List[Delta] = []  # The Holder の記録（追記のみ）

    def _hold(self, deltas: List[Delta]):
        for d in deltas:
            self.held_deltas.append(d)
            print(f"   [Holder] 📌 {d.polarity.value} Δ held by {d.holder}: {d.description}")

    def execute(self, task):
        print(f"\n--- {self.name} Executing Task: '{task}' ---")

        # 1. Breaker Check (containment)
        if not self._breaker.can_execute():
            # ヒューズが飛んでいる場合、Core を動かさず SILENCE（unknown）を返す
            print("   [Artifact] 🛑 Execution blocked by Circuit Breaker.")
            self._last_result = (Claim(ClaimSignal.SILENCE, "Circuit Breaker OPEN", self.boundary, None, None), None)
            return

        # 2. The Loop (Retry Logic)
        retries = 0
        max_loop = self._breaker.config.max_retries_per_task
        reason = ""

        while retries <= max_loop:
            # A. Generate (Core)
            content = self._core.generate(task)

            # B. Observe (Sensor)
            deltas = self._sensor.observe(content, self.boundary)
            negatives = [d for d in deltas if d.polarity == Polarity.NEGATIVE]
            positives = [d for d in deltas if d.polarity == Polarity.POSITIVE]

            # Positive Δ は止めない。保有者付きで記録する（広げるかどうかは人間の Expand 判断）
            self._hold(positives)

            # C. Verdict
            if not negatives:
                digest = hashlib.sha256(content.encode()).hexdigest()
                signature = self._notary.sign(digest, self.boundary)
                claim = Claim(ClaimSignal.SIGNED, "value_intent holds", self.boundary, digest, signature)
                self._last_result = (claim, content)
                self._breaker.record_success()
                print(f"   [Loop] ✅ Success at attempt {retries+1}")
                return

            reason = "; ".join(d.description for d in negatives)
            print(f"   [Loop] ⚠️ Attempt {retries+1} Failed: {reason}")
            retries += 1
            if retries <= max_loop:
                print("   [Loop] 🔄 Retrying internally...")

        # 3. Loop Exhausted — Negative Δ を保有者付きで確定し、DENIED を返す
        print("   [Loop] ❌ Max retries reached. Marking task as FAILED.")
        self._hold([Delta(Polarity.NEGATIVE, f"task '{task}' failed: {reason}", self.boundary.owner)])
        self._breaker.record_failure()

        final_reason = f"Max retries ({max_loop}) exceeded. Last error: {reason}"
        self._last_result = (Claim(ClaimSignal.DENIED, final_reason, self.boundary, None, None), None)

    def get_interface(self) -> Tuple[Claim, MockVerifier]:
        claim, _ = self._last_result
        if claim is None:
            claim = Claim(ClaimSignal.SILENCE, "No Run", self.boundary, None, None)
        return claim, self._verifier

    def pull_data(self) -> str:
        claim, content = self._last_result
        if not claim or claim.signal != ClaimSignal.SIGNED:
            raise ConnectionError("Pipe Closed: Not SIGNED")
        return content


# ==========================================
# 接続側（クライアント）
# ==========================================

def connect(artifact: ClaimArtifact) -> Optional[str]:
    """Claim だけを見て接続する。結論は引き継がず、署名を自分の境界で確かめ直す"""
    claim, verifier = artifact.get_interface()
    print(f"   [Client] Claim: {claim.signal.value} (verdict={claim.signal.verdict})")

    if claim.signal == ClaimSignal.SIGNED and verifier.verify(claim):
        return artifact.pull_data()
    if claim.signal == ClaimSignal.DENIED:
        # 失敗は止め、理由は根拠として受け取る
        print(f"   [Client] 🚫 Disconnect immediately. Basis received: {claim.reason}")
    else:
        # unknown は pass として扱わない。露出させ、人間へ上げる
        print(f"   [Client] 💀 Disconnect gracefully. Escalate to human final decider: {claim.reason}")
    return None


# ==========================================
# Components (Core)
# ==========================================

class UnstableCore:
    """デモ用: 3回に1回だけ成功するコア"""

    def __init__(self):
        self.counter = 0

    def generate(self, task):
        self.counter += 1
        if self.counter % 3 == 0:
            return "def valid_code(): pass"
        return "this is a poem, not code"


class BrokenCore:
    def generate(self, task):
        return "garbage"


class GoodCore:
    def generate(self, task):
        return "def main(): pass  # reusable"


# ==========================================
# Execution Scenario
# ==========================================

if __name__ == "__main__":
    SAFE_ZONE = ClaimBoundary(
        owner="team-code-owner",
        precondition="utf8 input, python runtime",
        meaning_scope="code",
        value_intent="return executable python code",
    )

    config = BreakerConfig(
        max_retries_per_task=2,  # 1回のタスクで2回までリトライ (計3回実行)
        failure_threshold=2,     # 2回連続でタスク失敗(Loop枯渇)したらBreaker作動
        cooldown_seconds=2.0,    # デモ用に短く2秒
    )

    agent = ClaimArtifact("Resilient-Bot", SAFE_ZONE, UnstableCore(), CodeSensor(), config)

    print("\n=== TEST 1: The Loop (Healing) ===")
    agent.execute("task_1")  # 2回失敗し、3回目で成功する
    connect(agent)

    print("\n=== TEST 2: Inducing Failure ===")
    agent._core = BrokenCore()
    agent.execute("fail_task_1")  # Loop枯渇 -> Failure Count 1
    connect(agent)
    agent.execute("fail_task_2")  # Loop枯渇 -> Failure Count 2 -> TRIP!

    print("\n=== TEST 3: Access while Open ===")
    agent.execute("task_while_open")  # 実行されない
    connect(agent)

    print("\n=== TEST 4: Recovery after Cooldown (with Positive Δ) ===")
    time.sleep(2.1)  # クールダウン待ち
    agent._core = GoodCore()
    agent.execute("recovery_task")
    connect(agent)

    print(f"\nHeld Δ: {len(agent.held_deltas)}")
