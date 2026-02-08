import enum
import hashlib
import secrets
import time  # 【追加】クールダウン管理用
from dataclasses import dataclass
from typing import Optional, Tuple
from abc import ABC, abstractmethod

# ... (Previous Definitions: BOABoundary, Ed25519Mock, PublicVerifier, PrivateNotary remain the same) ...
# ... (ClaimSignal, Claim, Interfaces remain the same) ...

# ==========================================
# (既存コードの再掲省略部分はそのまま使用してください)
# ここでは変更・追加されたクラスのみ抜粋して記述します
# ==========================================

# --- [再掲用ダミー定義: 実際は元のコードを使用] ---
@dataclass(frozen=True)
class BOABoundary:
    responsibility_boundary_id: str
    meaning_scope_id: str
    context_assumption_id: str
    def to_string(self): return f"{self.responsibility_boundary_id}::{self.meaning_scope_id}"

class ClaimSignal(enum.Enum):
    SIGNED = "✅ SIGNED"
    DENIED = "🚫 DENIED"
    SILENCE = "💀 SILENCE"

@dataclass(frozen=True)
class Claim:
    signal: ClaimSignal
    audit_log: str
    boundary: BOABoundary
    content_digest: Optional[str]
    signature: Optional[str]

class Ed25519Mock:
    @staticmethod
    def keygen(): return "priv", "pub"
class PrivateNotary:
    def __init__(self, p, P): pass
    def sign(self, d, l, b): return "sig"
class PublicVerifier:
    def __init__(self, p): pass
    def verify(self, c): return True

# ==========================================
# NEW: Circuit Breaker Logic
# ==========================================

@dataclass
class BreakerConfig:
    max_retries_per_task: int = 3   # 1タスク内のThe Loopリトライ上限
    failure_threshold: int = 5      # 連続何回タスク失敗でヒューズを飛ばすか
    cooldown_seconds: float = 10.0  # ヒューズが飛んだ後の冷却時間

class CircuitBreaker:
    def __init__(self, config: BreakerConfig):
        self.config = config
        self.consecutive_failures = 0
        self.state = "CLOSED" # CLOSED=正常, OPEN=遮断中
        self.last_trip_time = 0.0

    def can_execute(self) -> bool:
        """実行許可判定"""
        if self.state == "CLOSED":
            return True
        
        # OPEN(遮断)中の場合、冷却時間が過ぎたかチェック
        elapsed = time.time() - self.last_trip_time
        if elapsed > self.config.cooldown_seconds:
            print(f"   [Breaker] 🔄 Cooldown complete. Resetting to CLOSED.")
            self.reset()
            return True
        
        return False

    def record_success(self):
        """成功時は失敗カウントをリセット"""
        if self.consecutive_failures > 0:
            self.consecutive_failures = 0

    def record_failure(self):
        """タスク失敗を記録し、閾値を超えたらTripさせる"""
        self.consecutive_failures += 1
        print(f"   [Breaker] ⚠️ Failure Count: {self.consecutive_failures}/{self.config.failure_threshold}")
        
        if self.consecutive_failures >= self.config.failure_threshold:
            self.trip()

    def trip(self):
        """ヒューズを飛ばす"""
        self.state = "OPEN"
        self.last_trip_time = time.time()
        print(f"   [Breaker] 💥 TRIPPED! Circuit is now OPEN. Cooldown for {self.config.cooldown_seconds}s.")

# ==========================================
# UPDATED: BOA Artifact with The Loop & Breaker
# ==========================================

class BOAArtifact:
    def __init__(self, name, boundary, llm, core, sensor, breaker_config: BreakerConfig):
        self.name = name
        self.boundary = boundary
        self._core = core
        self._sensor = sensor
        self._llm = llm
        
        # Security Setup
        priv, pub = Ed25519Mock.keygen()
        self._notary = PrivateNotary(priv, pub)
        self._public_verifier = PublicVerifier(pub)
        self._sensor.set_notary(self._notary)
        
        # Safety Mechanism
        self._breaker = CircuitBreaker(breaker_config)
        
        self._last_result = (None, None)

    def execute(self, task):
        print(f"\n--- {self.name} Executing Task: '{task}' ---")

        # 1. Breaker Check (Gatekeeper)
        if not self._breaker.can_execute():
            # ヒューズが飛んでいる場合、Coreすら動かさず即座にSILENCEを返す
            print(f"   [Artifact] 🛑 Execution blocked by Circuit Breaker.")
            self._last_result = (Claim(ClaimSignal.SILENCE, "Circuit Breaker OPEN", self.boundary, None, None), None)
            return

        # 2. The Loop (Retry Logic)
        retries = 0
        max_loop = self._breaker.config.max_retries_per_task

        while retries <= max_loop:
            # A. Generate (Core)
            content = self._core.generate(task, self._llm)
            
            # B. Audit (Sensor)
            claim = self._sensor.audit(content, self.boundary, self._llm)
            
            # C. Decision
            if claim.signal == ClaimSignal.SIGNED:
                # Success!
                self._last_result = (claim, content)
                self._breaker.record_success() # Breakerに成功報告
                print(f"   [Loop] ✅ Success at attempt {retries+1}")
                return
            
            else:
                # Failure -> Loop
                print(f"   [Loop] ⚠️ Attempt {retries+1} Failed: {claim.audit_log}")
                retries += 1
                if retries <= max_loop:
                     print(f"   [Loop] 🔄 Retrying internally...")
        
        # 3. Loop Exhausted (Give Up)
        print(f"   [Loop] ❌ Max retries reached. Marking task as FAILED.")
        self._breaker.record_failure() # Breakerに失敗報告(これが続くとTripする)
        
        # 最終結果としてDENIED/SILENCEをセット
        final_reason = f"Max retries ({max_loop}) exceeded. Last error: {claim.audit_log}"
        self._last_result = (Claim(ClaimSignal.DENIED, final_reason, self.boundary, None, None), None)

    def get_interface(self) -> Tuple[Claim, PublicVerifier]:
        claim, _ = self._last_result
        if claim is None:
             claim = Claim(ClaimSignal.SILENCE, "No Run", self.boundary, None, None)
        return claim, self._public_verifier

    def pull_data(self) -> str:
        # (既存のpull_data実装と同じ)
        claim, content = self._last_result
        if not claim or claim.signal != ClaimSignal.SIGNED:
            raise ConnectionError("Pipe Closed: Not SIGNED")
        return content

# ==========================================
# Components (Logic)
# ==========================================

# (ILLMProvider, ICoreStrategy, ISensorStrategy, MockLLM, BOACompliantSensor は既存コードを使用)
# 省略...

class UnstableCore:
    """デモ用: 確率で失敗するコア"""
    def __init__(self):
        self.counter = 0
    
    def generate(self, task, llm):
        self.counter += 1
        # 3回に1回しか成功しない設定
        if self.counter % 3 == 0:
            return "def valid_code(): pass"
        return "this is a poem, not code"

# ==========================================
# Execution Scenario
# ==========================================

if __name__ == "__main__":
    # Boundary定義
    SAFE_ZONE = BOABoundary("sys.code", "code", "utf8")
    
    # 3. Config (YAMLから読み込まれる想定)
    config = BreakerConfig(
        max_retries_per_task=2,  # 1回のタスクで2回までリトライ (計3回実行)
        failure_threshold=2,     # 2回連続でタスク失敗(Loop枯渇)したらBreaker作動
        cooldown_seconds=2.0     # デモ用に短く2秒
    )

    # Agent生成 (不安定なCoreを持つ)
    agent = BOAArtifact("Resilient-Bot", SAFE_ZONE, None, UnstableCore(), BOACompliantSensor(), config)

    # --- Test 1: The Loop (Self-Healing) ---
    # Coreは2回失敗し、3回目で成功するはず。max_retries=2なのでギリギリ成功する。
    print("\n=== TEST 1: The Loop (Healing) ===")
    agent.execute("task_1") # 内部でリトライして成功するはず

    # --- Test 2: Breaker Trip (Overload) ---
    # ここからは絶対に成功しないタスクを投げて、Breakerを落とす
    print("\n=== TEST 2: Inducing Failure ===")
    
    # 失敗1回目
    agent._core = PythonCore() # Coreを差し替え (モック調整が面倒なので強制的に失敗させるCoreがないため、挙動シミュレート)
    # 強制的に失敗させたいので、Sensorが絶対通らない入力をCoreが出すようにするハック
    class BrokenCore:
        def generate(self, t, l): return "garbage"
    agent._core = BrokenCore()

    agent.execute("fail_task_1") # Loop枯渇 -> Failure Count 1
    agent.execute("fail_task_2") # Loop枯渇 -> Failure Count 2 -> TRIP!

    # --- Test 3: Blocked by Breaker ---
    print("\n=== TEST 3: Access while Open ===")
    agent.execute("task_while_open") # 実行されないはず

    # --- Test 4: Recovery ---
    print("\n=== TEST 4: Recovery after Cooldown ===")
    time.sleep(2.1) # クールダウン待ち
    
    # 正常なCoreに戻す
    class GoodCore:
         def generate(self, t, l): return "def main(): pass"
    agent._core = GoodCore()
    
    agent.execute("recovery_task") # 実行されるはず