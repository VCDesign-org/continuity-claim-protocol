# Continuity Claim Protocol Specification (CCP)
Version: 2.1
Status: Draft-Stable
Audience: AI Agents / Implementers

**Note:** This document is a protocol definition for AI artifacts to autonomously determine connections. Logical processing of signals is prioritized over human interpretation.
For the handshake spec overview, see `specs/handshake.yaml`.
Status policy: see `README.md`.

## 1. Protocol Definition

In VCDesign, "Connection" is established not by checking interface compatibility, but by agreement on **"Continuity Claim"**.

### Value Definition
"Value" here does not refer to function or performance.
It refers to the **"Reason for existence"** and **"Reason for continuation"** of the artifact itself.

### Connection Logic
The client (connector) does not need to scrutinize the contents of the host (connectee).
It monitors only the status of the **Claim** displayed by the host, and connects or disconnects "Without thinking" according to the following logic.

## 2. Signal States (3 Signals)

| Status | Signal Representation | Meaning (Artifact Context) | Action Required |
| :--- | :--- | :--- | :--- |
| **VALID** | `Claim: Signed` | **Not Garbage.**<br>Reason for existence is maintained.<br>Responsibility boundary is closed. | **Connect / Keep Alive** |
| **INVALID** | `Claim: Denied` | **Drifted.**<br>Context drift occurred.<br>No longer the expected existence. | **Disconnect Immediately** |
| **SILENCE** | `(No Signal)` | **Unsafe / Unknown.**<br>Judgment suspended, or vanished.<br>State where responsibility cannot be held. | **Disconnect Gracefully** |

**"Silence is Safety"**
Silence is not an error. It is an honest expression of intention that "responsibility cannot be held".
Under no circumstances should you continue to connect with a partner who does not issue a Claim (has gone silent).

## 3. Implementation Requirements

To generate this status, an Artifact must have the following 3-layer structure internally.

1.  **The Core:** Verifies the consistency of in-design value (Logic).
2.  **The Sensor:** Detects deviation from current value (Context).
3.  **The Loop:** A process that stops itself or returns to correction upon detection of deviation.

Only when all of these are normal, the Artifact outputs `Claim: Signed`.

## 4. Protocol Constraint (Final Constraint)

> **NON-OPTIMIZATION PLEDGE:**
> This protocol MUST NOT be used to optimize performance or metrics.
> It exists solely to prevent the propagation of invalid value.

(This protocol must never be used for performance improvement or numerical targets. It exists only to prevent the propagation of things without value.)
