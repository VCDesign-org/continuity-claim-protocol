# Continuity Claim Protocol Specification (CCP)
Version: 3.0
Status: Draft-Stable
Audience: AI Agents / Implementers

**Note:** This document is a protocol definition for AI artifacts to autonomously determine connections. Logical processing of signals is prioritized over human interpretation.
For the handshake spec overview, see `specs/handshake.yaml`.
Status policy: see `README.md`.

## 1. Protocol Definition

In CCP, "Connection" is established not by checking interface compatibility, but by agreement on a **Continuity Claim**.

CCP implements [Value Continuity](https://github.com/value-continuity/value-continuity) on the side of crossings between organizations and agents. Its central principle, the Value Asymmetry Principle, is applied at each connection: *make upside propagable; do not let downside propagate.*

### Value Definition
"Value" here does not refer to function or performance.
It refers to the **ability to keep creating the next value** that the artifact declares as `value_intent`, on the `precondition` it declares. These two form the baseline of Δ.

### Connection Logic
The client (connector) does not need to scrutinize the contents of the host (connectee).
It monitors the status of the **Claim** displayed by the host and re-checks the claim's premises at its own boundary (signature, freshness, authority). It does not inherit the host's conclusion.
It connects or disconnects according to the following logic.

## 2. Signal States (3 Signals)

Each signal is a guard verdict on the crossing (VCDesign `boundary-pattern.yaml`).

| Status | Signal Representation | Guard Verdict | Meaning (Artifact Context) | Action Required |
| :--- | :--- | :--- | :--- | :--- |
| **VALID** | `Claim: Signed` | `pass` | **Not Garbage.**<br>The value intent holds on its precondition.<br>The boundary has an owner and a human-closed decision authorizes it. | **Connect / Keep Alive** (within the authorized scope) |
| **INVALID** | `Claim: Denied` | `deny` | **Drifted.**<br>A Negative Δ was confirmed.<br>No longer the expected existence. | **Disconnect Immediately**<br>Contain the failure. The reason passes as basis. |
| **SILENCE** | `(No Signal)` | `unknown` | **Unsafe / Unknown.**<br>Judgment suspended, or vanished.<br>State where responsibility cannot be held. | **Disconnect Gracefully**<br>Expose and escalate to the human final decider. |

**"Silence is Safety"**
Silence is not an error. It is an honest expression of intention that "responsibility cannot be held".
Silence is `unknown`, and `unknown` is never treated as `pass`.
Under no circumstances should you continue to connect with a partner who does not issue a Claim (has gone silent).

**Asymmetry of signals**
- `Denied` stops the failure, not the learning: the reason for denial flows to the other side as basis.
- A Positive Δ (the host doing better than declared) does not change the signal and is not a reason to disconnect. It is recorded with a holder. Widening the connection because of it requires the decision Expand, closed by a human.

## 3. Implementation Requirements

To generate this status, an Artifact must have the following structure internally.

1.  **The Core:** Verifies the consistency of in-design value against `value_intent` (Logic).
2.  **The Sensor:** Observes Δ from the declared precondition and value, in both polarities (Context).
    - Negative Δ → The Loop.
    - Positive Δ → recorded with a holder; never halted.
3.  **The Loop:** A process that stops itself or returns to correction upon detection of a Negative Δ, within the declared `blast_radius`. When the loop is exhausted, it contains the failure (circuit breaker) instead of retrying without a ceiling.
4.  **The Holder:** A named owner for every confirmed Δ until a human decision closes it. An Artifact without a holder cannot output `Claim: Signed`.

Only when all of these are normal, the Artifact outputs `Claim: Signed`.

## 4. Protocol Constraint (Final Constraint)

> **NON-OPTIMIZATION PLEDGE:**
> This protocol MUST NOT be used to optimize performance or metrics.
> It exists solely to stop the propagation of losses at the boundary
> while keeping basis propagable.

(This protocol must never be used for performance improvement or numerical targets. It exists only to stop the spread of losses and to keep the basis for the next value passing on.)
