# CCP Handshake Protocol Specification
Version: 2.1
Status: Draft-Stable
Audience: AI Agents / Implementers
Status policy: see `README.md`.

This document defines the "Dynamic Procedure (Protocol)" for AIs to connect safely based on `schemas/handshake.schema.yaml`.
For the high-level spec and intent, see `specs/handshake.yaml`.

VCDesign Core is immutable, and this document exists as the technical layer on the CCP side.

---

# 1. Overview

CCP Handshake consists of the following 4 phases:

1. HELLO  
2. OFFER  
3. ACCEPT  
4. REVERSE (Optional / Mid-stream Reversal)

Each phase defines mandatory checks to prevent destroying the Boundary, Responsibility, and Meaning of VCDesign.

---

# 2. States

| State | Purpose |
|-------|---------|
| HELLO | Session start, exchange of boundary and validation level |
| OFFER | initiator presents proposal (Responsibility, Meaning, Handling of Δ) |
| ACCEPT | receiver approves proposal and returns signature |
| REJECT | receiver rejects proposal |
| REVERSE | Mid-stream reversal based on DCS/RC/BOA |

---

# 3. Message Sequence

## 3.1 HELLO

### Sent Content (Both sides):
- handshake_meta 
    (Includes handshake_id / timestamp / expires_at / nonce / participants)
- world.id
- agent.id
- trust.validation_level


### Mandatory Checks (Revised)
- `timestamp` is within ± 5 minutes of current time  
- `expires_at` is in the future relative to current time (*Added)  
- `nonce` is unused  
- `signature_schema` is valid  

### Purpose
- Uniqueness of session  
- Time integrity  
- Agreement on signature method  
- Sharing of VCDesign Boundary (world)  

---

## 3.2 OFFER

### initiator sends
- `interface`
- `cost_model`
- `decision_authority`
- `resolution_policy`
- `continuity_claim`

### Mandatory Checks
`validation_level` conditions change depending on `intent`:
intent = proposal | advice:
trust.validation_level >= syntax

intent = decision:
trust.validation_level >= semantic


Additional Checks:
- If `intent=decision`, `risk_level >= 2`
- If `irreversible=true`, `initial_state=Human-Closed`
- `delta_transfer.scope` is consistent with schema

### Purpose
- Declaration of Meaning Scope  
- Declaration of Location of Responsibility (BOA)  
- Declaration of Handling of Δ and R (RC)  
- Presentation of External Mapping of Chapter (continuity_claim)  

---

## 3.3 ACCEPT

### receiver sends
- Signature (signature)
- canonicalization information
- resolver decision (Optional)

The decision of resolver is written in `resolution_policy.resolver`, and the receiver returns the final value during ACCEPT (Optional).

Write in `resolution_policy.resolver`

### Mandatory Checks
- Normalize `signed_fields` with canonicalization (json_c14n)  
- Signature matches  
- `delta_transfer.scope` is compatible  
- `decision_authority.domain` is not inconsistent with the Responsibility Boundary of VCDesign Core  

### Purpose
- Fixing of proposal content  
- Establishment of connection that does not break the VCDesign membrane  

---

## 3.4 REVERSE (Mid-stream Reversal)

### Occurrence Conditions
- DCS validation_fail  
- Breakdown of trust conditions  
- Contradiction in decision_authority  
- Inconsistency of Δ  
- When possibility of breaking VCDesign boundary is detected  

### Sent Content
- `reversal_signal.events`
- Return of unresolved Δ

### Mandatory Checks
- If `type = authority_revoked`, `AI→Human` is forced  
- Δ is returned according to `resolution_policy`  

### Purpose
- Protect the Responsibility Boundary of VCDesign  
- Prevent AI from closing decisions by mistake  

---

# 4. Error Handling

| Error | Meaning | Required Action |
|-------|---------|-----------------|
| invalid_timestamp | Time is out of range | Reject HELLO |
| expired_handshake | expires_at exceeded | Reject HELLO |
| reused_nonce | nonce reuse | Reject HELLO |
| insufficient_validation | validation_level insufficient | Reject OFFER |
| signature_mismatch | Signature mismatch | Reject ACCEPT |
| delta_incompatible | Handling of Δ is inconsistent | REVERSE |

---

# 5. Security Alignment

This protocol aligns with `docs/en/handshake.security.md`.

Especially:

- canonicalization is **json_c14n MUST**  
- When using yaml_c14n, the signature target is converted to JSON before normalization  
- nonce is held until `expires_at + safety_margin(10min)`  
- authority_revoked is always AI→Human  

---

# 6. VCDesign Integration Notes

This protocol does not change VCDesign Core.

- world.id → Boundary of VCDesign  
- continuity_claim.boundary_def → External mapping of Chapter  
- decision_authority.domain → Responsibility Domain of BOA  
- resolution_policy → RC (Δ and R)  
- reversal_signal → DCS (Mid-stream Reversal)  

**CCP must not overwrite the Responsibility Boundary of VCDesign.**

---

# 7. Termination

### Success
- When ACCEPT signature verification succeeds

### Failure
- REJECT  
- REVERSE  
- expires_at exceeded  
- nonce reuse  

---

# 8. License

MIT License  
© VCDesign Project
