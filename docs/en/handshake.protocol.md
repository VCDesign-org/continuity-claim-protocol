# CCP Handshake Protocol Specification
Version: 3.0
Status: Draft-Stable
Audience: AI Agents / Implementers
Status policy: see `README.md`.

This document defines the "Dynamic Procedure (Protocol)" for AIs to connect safely based on `schemas/handshake.schema.yaml`.
For the high-level spec and intent, see `specs/handshake.yaml`.

CCP implements [Value Continuity](https://github.com/value-continuity/value-continuity) on the side of crossings between organizations and agents.
It does not redefine Value Continuity, and it writes the work of a boundary with the same words as VCDesign v2 (`patterns/boundary-pattern.yaml`).

---

# 1. Overview

CCP Handshake consists of the following phases:

1. HELLO
2. OFFER
3. ACCEPT / REJECT
4. REVERSE (Optional / Mid-stream Reversal)
5. CLOSE

Each phase defines mandatory checks so that a crossing stops losses, passes basis on, and stays within the scope a human decision authorized.

### Verdicts and decisions are different things

- **Guard verdict** (`pass` / `deny` / `unknown`) is the check on a single crossing. ACCEPT is `pass`; REJECT is `deny` or `unknown`.
- **Decision** (Proceed / Expand / Limit / Reframe / Defer / Retire) is closed by a human and authorizes the scope of the connection (`decision_authority.authorization`).

The protocol does not add decision vocabulary. Repeated deny or unknown, or any verdict that affects responsibility, is observed as a Δ and closed with one of the six decisions.

---

# 2. States

| State | Purpose |
|-------|---------|
| HELLO | Session start, exchange of identity and declared boundary |
| OFFER | Initiator presents authority, boundary policy and continuity claim |
| ACCEPT | Receiver's guard verdict is `pass`; signature returned |
| REJECT | Receiver's guard verdict is `deny` (with reason) or `unknown` (escalated) |
| REVERSE | Mid-stream reversal: stop, contain, return Δ with a holder, escalate to a human |
| CLOSE | End of connection: release responsibility, notify dependents, hand over residual assets |

---

# 3. Message Sequence

## 3.1 HELLO

### Sent Content (Both sides)
- handshake_meta
    (Includes handshake_id / timestamp / expires_at / nonce / participants)
- world.id
- agent.id, agent.kind
- trust.validation_level

### Mandatory Checks
- `timestamp` is within ± 5 minutes of current time
- `expires_at` is in the future relative to current time
- `nonce` is unused
- `signature_schema` is valid

### Purpose
- Identity of the parties (`external_crossing.identity`)
- Time integrity
- Agreement on signature method
- Sharing of the declared boundary (world)

---

## 3.2 OFFER

### initiator sends
- `interface`
- `cost_model`
- `decision_authority`
- `boundary_policy`
- `continuity_claim`

### Mandatory Checks

Validation level depends on `intent`:

```
intent = proposal | advice:
  trust.validation_level >= syntax

intent = decision:
  trust.validation_level >= semantic
```

Responsibility (hard stops — REJECT with `deny` if violated):
- `decision_authority.final_decider.kind = human`
- `decision_authority.owner` and `continuity_claim.boundary.owner` exist
- If `intent=decision`: `risk_level >= 2` and `authorization.decision_ref` is present
- If `irreversible=true` or `reversibility.class=irreversible`: `blast_radius.max_loss` is declared
- If `authorization.decision=expand`: `expand_basis.positive_delta_ref` is present and `expand_basis.recovery_confirmed=true`
- If `agent.kind=ai` and `loop` is `physical`, `value` or `responsibility`: `authorization.decision_ref` is present

Boundary policy:
- `containment.propagation` is `deny` unless stated otherwise
- `basis_flow.default` is `allow` unless stated otherwise; each `restricted` item has a reason
- `revalidation.upstream_trust` is `none` unless attested
- `delta.transfer.scope` is consistent with the schema

### Purpose
- Declaration of authority: who closed the decision, and within what scope (`external_crossing.authority`)
- Declaration of the boundary: owner, precondition, meaning scope (`external_crossing.declared_boundary`)
- Declaration of the value intent and what remains
- Declaration of what is stopped and what is passed on

### Authorized decisions

Only `proceed`, `expand` and `limit` authorize an execution scope, so only they appear in `authorization.decision`. The other three are protocol outcomes:

| Decision | In CCP |
|----------|--------|
| Proceed | Open the connection with the current declaration |
| Expand | Widen `trust.scope`, `blast_radius` or `basis_flow` through a new handshake. Requires an observed Positive Δ and confirmed recovery |
| Limit | Narrow `trust.scope`, `blast_radius` or permissions through a new handshake |
| Reframe | Issue a new `continuity_claim` (new id, precondition, owner) and a new handshake |
| Defer | Do not connect. Return REJECT with `unknown`, a temporary owner and `next_review_at` |
| Retire | Do not connect, or CLOSE the existing connection |

A trial that does not narrow the declaration is not Limit. It is a crossing without a ceiling and is rejected.

---

## 3.3 ACCEPT

### receiver sends
- `verdict: pass`
- Signature (signature)
- canonicalization information
- Δ holder decision (Optional; written in `boundary_policy.delta.holder`)

### Mandatory Checks
- Normalize `signed_fields` with canonicalization (json_c14n)
- Signature matches
- `revalidation.re_check` passes: precondition, evidence freshness and authority are re-checked at the receiver's boundary, not inherited from the initiator's conclusion
- `delta.transfer.scope` is compatible

### Purpose
- Fixing of the offered declaration
- Establishment of a connection whose losses stop at the boundary and whose basis passes on

---

## 3.4 REJECT

### receiver sends
- `verdict: deny` with a `reason`, or `verdict: unknown`

### Rules
- `deny` always carries a reason. The reason itself flows as basis (the failure is stopped; the learning passes).
- `unknown` means the input was not sufficient for a verdict. It is stopped, exposed and escalated to `decision_authority.escalation.on_unknown`. It is never treated as `pass`.
- Both are recorded, like `pass` (history of responsibility).

---

## 3.5 REVERSE (Mid-stream Reversal)

### Occurrence Conditions
- `guard_deny` or `guard_unknown` on a crossing inside the connection
- `precondition_broken`: the declared precondition no longer holds
- `blast_radius_exceeded`: the declared ceiling was exceeded
- `authority_revoked`: the authorizing decision was withdrawn
- `validation_fail`: verification failed

### Sent Content
- `reversal_signal.events` (with `phase`, `reason`, `delta_ref`, `holder`)
- Return of unresolved Δ with its holder

### Mandatory Checks
- If `type = authority_revoked`, execution stops and control returns to the human `final_decider`
- If `type = blast_radius_exceeded`, `blast_radius.on_exceed` (halt / quarantine / escalate) is applied
- The returned Δ has a holder according to `boundary_policy.delta.holder`. A Δ never becomes ownerless
- A Positive Δ observed in the connection is not halted or quarantined by the reversal; it is recorded with a holder

### Purpose
- Keep a Negative Δ inside the failure domain
- Return control to the human who closes decisions

---

## 3.6 CLOSE

### Occurrence Conditions
- Retire decided by the human `final_decider`
- End of the authorized scope, or `expires_at` exceeded

### Sent Content
- Release of responsibility for the connection
- Notification to dependents (`declaration.depends_on`, other parties)
- `residual_assets` with their holders

### Rules
- CLOSE does not hide active dependencies.
- What remains after the connection ends has a holder; without one it does not remain.

---

# 4. Error Handling

| Error | Meaning | Required Action |
|-------|---------|-----------------|
| invalid_timestamp | Time is out of range | Reject HELLO |
| expired_handshake | expires_at exceeded | Reject HELLO |
| reused_nonce | nonce reuse | Reject HELLO |
| insufficient_validation | validation_level insufficient | REJECT (`unknown`) |
| no_human_final_decider | final_decider is not human | REJECT (`deny`) |
| no_owner | owner missing | REJECT (`deny`) |
| undeclared_max_loss | irreversible without max_loss | REJECT (`deny`) |
| expand_without_basis | expand without observed Positive Δ or recovery | REJECT (`deny`) |
| signature_mismatch | Signature mismatch | REJECT (`deny`) |
| revalidation_mismatch | precondition / evidence / authority does not re-check | REJECT (`unknown`) |
| delta_incompatible | Handling of Δ is inconsistent | REVERSE |
| blast_radius_exceeded | Declared ceiling exceeded | REVERSE |

---

# 5. Security Alignment

This protocol aligns with `docs/en/handshake.security.md`.

Especially:

- canonicalization is **json_c14n MUST**
- When using yaml_c14n, the signature target is converted to JSON before normalization
- nonce is held until `expires_at + safety_margin(10min)`
- authority_revoked always stops execution and returns control to the human final_decider

---

# 6. Value Continuity and VCDesign Integration Notes

CCP does not redefine Value Continuity or VCDesign.

- The whole handshake → VCDesign `boundary-pattern.yaml external_crossing` (identity, declared_boundary, authority, signature)
- ACCEPT / REJECT → guard verdict (pass / deny / unknown)
- `boundary_policy.containment` → containment (do not let downside propagate)
- `boundary_policy.basis_flow` → basis_flow (make upside propagable)
- `boundary_policy.revalidation` → revalidation
- `decision_authority.authorization` → Decision (closed by a human)
- `boundary_policy.delta.holder` → closure_loop (Δ is never ownerless)

For the full mapping, see `mappings/vcdesign_mapping.md`.

---

# 7. Termination

### Success
- When ACCEPT signature verification succeeds (connection opens)
- CLOSE with residual assets handed over (connection ends)

### Failure
- REJECT
- REVERSE
- expires_at exceeded
- nonce reuse

---

# 8. License

MIT License
© VCDesign Project
