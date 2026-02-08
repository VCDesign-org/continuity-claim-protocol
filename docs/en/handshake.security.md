# CCP Handshake Security Specification
Version: 2.1
Status: Draft-Stable
Audience: AI Agents / Implementers

This document defines the "Minimum Safety Requirements" applied to `schemas/handshake.schema.yaml` and `docs/en/handshake.protocol.md`.
For the high-level spec and intent, see `specs/handshake.yaml`.
Status policy: see `README.md`.

VCDesign Core is immutable, and this document exists as the technical layer on the CCP side.

---

# 1. Threat Model

CCP Handshake assumes the following threats:

- Replay Attack (Resending past handshake to spoof agreement)
- Man-in-the-Middle Attack (Tampering with content)
- Signature Mismatch (Hash mismatch due to differences in normalization methods)
- Participant Impersonation
- Unauthorized Transfer of Δ (Unresolved Area)
- Unauthorized Promotion of decision_authority (Reversal of AI→Human)
- Destruction of Responsibility Boundary of VCDesign Core

This specification defines requirements to prevent these at minimum cost.

---

# 2. Safety Requirements for Handshake Meta

`handshake_meta` must include the following 5 elements.

## 2.1 handshake_id
- Unique Identifier (UUIDv4 Recommended)
- Must be included in the signature target

## 2.2 timestamp
- ISO 8601
- Receiver validates that it is within **±5 minutes of current time**

## 2.3 expires_at
- ISO 8601
- **Must be in the future relative to current time** (Consistent with Protocol side)

## 2.4 nonce
- Random value of 128bit or more
- **Validate that it is unused**

## 2.5 participants
- Explicitly state initiator / receiver IDs
- Must be included in the signature target

---

# 3. Canonicalization (Normalization)

Apply canonicalization before signing.

## 3.1 Clarification of MUST / MAY (Revised)

MUST: json_c14n
MAY: yaml_c14n (However, signature target must be converted to JSON before canonicalizing)


### Reason
- YAML has large implementation differences, and signature compatibility is easily broken.
- Converting to JSON → canonicalization can completely eliminate expression differences.

## 3.2 Requirements for canonicalization
- Fix field order
- Eliminate variations in whitespace / newlines
- Fix types of numbers and strings
- Prohibit YAML anchors / aliases

---

# 4. Signed Fields (Signature Targets)

Only fields listed in `continuity_claim.signature_schema.signed_fields` are targets for signing.

Recommended Set:
signed_fields:
handshake_meta
world
agent
trust
interface
decision_authority
resolution_policy

* Note that `signature_schema` itself is a technical layer, so it does not need to be included in `signed_fields`, but including "boundary_def (claim part)" of `continuity_claim` in `signed_fields` is also allowed in operation.

### Supplement: About Signature Target of continuity_claim

Since `signature_schema` itself (algorithm, key reference, normalization method, etc.) is technical metadata, it does not necessarily need to be included in `signed_fields`.

On the other hand, for **claim parts that define the meaning and boundary of agreement** such as the following, including them in `signed_fields` is allowed depending on implementation or operational policy:

- continuity_claim.boundary_def
- continuity_claim.claim_text
- Other claim fields that will be subject to future verification as agreement content

This makes it possible to verify by signature:
- "Which boundary was agreed upon"
- "Whether that claim has been rewritten later"


### Meaning
- Fix the Boundary, Responsibility, and Meaning of VCDesign
- Prevent the Technical Layer (Signature) from destroying the Philosophical Layer (VCDesign)

---

# 5. Replay Protection

Combine the following 3 elements to prevent replay attacks.

## 5.1 Retention Period of nonce (Revised)
nonce must be retained until expires_at + safety_margin
safety_margin is recommended to be 10 minutes (SHOULD)


## 5.2 Allowable Range of timestamp
- Within ±5 minutes

## 5.3 Enforcement of expires_at
- Expired handshakes are invalid

---

# 6. Authority Safety (Safety of Decision Authority)

To prevent misuse of decision_authority, the following are mandatory.

## 6.1 Case of intent=decision
- `trust.risk_level >= 2`
- `trust.validation_level >= semantic`
- If `irreversible=true`, `initial_state=Human-Closed`

## 6.2 Enforcement of AI→Human
Transition to AI→Human is mandatory under the following conditions:

- DCS validation_fail  
- reversal_signal.type = authority_revoked  
- trust.validation_level < semantic  
- Inconsistency of Δ  

---

# 7. Delta Safety (Safety of Δ)

Handling of Δ (Unresolved Area) must satisfy the following.

## 7.1 delta_transfer.scope
- `prompt` / `artifact` / `state` / `tool_call`

## 7.2 redaction
- If `required`, delete personal information / confidential information

## 7.3 Signature of Δ
- When transferring Δ, sender adds hash of Δ

---

# 8. Reversal Safety (Safety of Mid-stream Reversal)

Mid-stream Reversal (REVERSE) occurs under the following conditions.

## 8.1 Occurrence Conditions
- DCS validation_fail  
- Contradiction in decision_authority  
- Breakdown of trust conditions  
- Inconsistency of Δ  
- When possibility of breaking VCDesign boundary is detected  

## 8.2 Notification Content
- `reversal_signal.events`
- `phase` (HELLO / OFFER / ACCEPT / REVERSE)
- `reason`

## 8.3 Authority Rewind
- If `authority_revoked`, AI→Human is forced

---

# 9. VCDesign Integration Safety

CCP must not overwrite the Responsibility Boundary of VCDesign Core.

Especially:
decision_authority.domain refers to the Responsibility Domain of VCDesign only, and must not change its meaning.

resolution_policy is a technical mapping of RC (Δ and R), and must not change the philosophical meaning of Δ.


---

# 10. Termination Safety

## 10.1 Success
- When ACCEPT signature verification succeeds

## 10.2 Failure
- REJECT  
- REVERSE  
- expires_at exceeded  
- nonce reuse  

---

# 11. License

MIT License  
© VCDesign Project
