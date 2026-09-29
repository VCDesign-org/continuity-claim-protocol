# CCP Handshake Security Specification
Version: 3.0
Status: Draft-Stable
Audience: AI Agents / Implementers

This document defines the "Minimum Safety Requirements" applied to `schemas/handshake.schema.yaml` and `docs/en/handshake.protocol.md`.
For the high-level spec and intent, see `specs/handshake.yaml`.
Status policy: see `README.md`.

CCP implements [Value Continuity](https://github.com/value-continuity/value-continuity) on the side of crossings between organizations and agents. The signature, canonicalization and replay protection below are technical means; they do not change the meaning of Value Continuity or VCDesign.

---

# 1. Threat Model

CCP Handshake assumes the following threats:

- Replay Attack (Resending past handshake to spoof agreement)
- Man-in-the-Middle Attack (Tampering with content)
- Signature Mismatch (Hash mismatch due to differences in normalization methods)
- Participant Impersonation
- Unauthorized Transfer of Δ (moving a Δ without a holder, or across a failure domain)
- Unauthorized Authority (an AI presented as final_decider, or execution beyond the authorized scope)
- Unauthorized Expand (widening scope without an observed Positive Δ and confirmed recovery)
- Leakage through basis_flow (basis that itself carries a loss: confidential data, excess authority)
- Transitive trust (inheriting the other party's conclusion without revalidation)

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

## 3.1 MUST / MAY

```
MUST: json_c14n
MAY:  yaml_c14n (the signature target must be converted to JSON before canonicalizing)
```

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

```
signed_fields:
  - handshake_meta
  - world
  - agent
  - trust
  - interface
  - decision_authority
  - boundary_policy
  - continuity_claim.boundary
  - continuity_claim.declaration
```

`signature_schema` itself (algorithm, key reference, normalization method) is technical metadata and does not need to be signed.

`decision_authority`, `boundary_policy` and the claim parts of `continuity_claim` are recommended because they are the content of the agreement. Signing them makes it possible to verify:

- Who closed the decision, and within what scope the connection runs
- What is stopped and what is passed on at this boundary
- Which boundary, precondition and value intent were agreed upon, and whether they were rewritten later

---

# 5. Replay Protection

Combine the following 3 elements to prevent replay attacks.

## 5.1 Retention Period of nonce
nonce must be retained until `expires_at + safety_margin`.
safety_margin is recommended to be 10 minutes (SHOULD).

## 5.2 Allowable Range of timestamp
- Within ±5 minutes

## 5.3 Enforcement of expires_at
- Expired handshakes are invalid

---

# 6. Authority Safety (Safety of Decision Authority)

AI supports decisions but does not hold final responsibility (VCDesign axioms A3). The following are mandatory.

## 6.1 Human final decider
- `decision_authority.final_decider.kind = human`
- `authorization.decided_by` matches the final_decider, or its delegation is shown in `trust.evidence`

## 6.2 Case of intent=decision
- `trust.risk_level >= 2`
- `trust.validation_level >= semantic`
- `authorization.decision_ref` is present (the decision was closed by a human before the crossing)
- If `irreversible=true`, `blast_radius.max_loss` is declared

## 6.3 Expand
- `authorization.expand_basis.positive_delta_ref` is present (average outcome alone is never a basis)
- `authorization.expand_basis.recovery_confirmed = true` (recovery is possible in the widened scope)

## 6.4 AI in slow loops
- If `agent.kind = ai` and `decision_authority.loop` is `physical`, `value` or `responsibility`, the crossing must carry `authorization.decision_ref`. LLM output requires an explicit gate before real-world effect.

## 6.5 Return of control
Execution stops and control returns to the human final_decider under the following conditions:

- `reversal_signal.type = authority_revoked`
- `guard_unknown` that cannot be resolved inside the connection
- `blast_radius_exceeded` with `on_exceed = halt` or `escalate`
- Inconsistency of Δ

---

# 7. Boundary Safety

## 7.1 containment (do not let downside propagate)
- `propagation` is `deny` by default. `attested_only` and `allow` must be explicit.
- `on_breach` (quarantine / halt / deny) is declared.
- `shared_dependencies` are declared; they are holes in the bulkhead.

## 7.2 basis_flow (make upside propagable)
- `default` is `allow` by default. Basis, evidence, residual assets and Positive Δ pass; conclusions do not.
- Only basis that itself carries a loss is `restricted`, and each item has a reason.
- If `redaction = required`, delete personal and confidential information before passing.
- The reason for a `deny` is passed as basis.
- Passing does not mean widening. Widening the connection requires Expand.

## 7.3 revalidation
- `upstream_trust` is `none` by default. The other party's conclusion is not inherited.
- precondition, evidence freshness and authority are re-checked at the receiving boundary.
- A mismatch is `unknown`.

## 7.4 Δ
- `delta.transfer.scope`: `prompt` / `artifact` / `state` / `tool_call`
- When transferring a Δ, the sender adds a hash of the Δ and names its holder.
- A Δ without recorded polarity is treated as negative.

---

# 8. Reversal Safety (Safety of Mid-stream Reversal)

## 8.1 Occurrence Conditions
- `guard_deny` / `guard_unknown`
- `precondition_broken`
- `blast_radius_exceeded`
- `authority_revoked`
- `validation_fail`

## 8.2 Notification Content
- `reversal_signal.events`
- `phase` (HELLO / OFFER / ACCEPT / REVERSE / CLOSE)
- `reason`
- `delta_ref` and `holder` of the returned Δ

## 8.3 Authority Rewind
- If `authority_revoked`, execution stops and control returns to the human final_decider.
- State may be reverted; the responsibility record (verdicts, reversals, Δ holders) is append-only.

---

# 9. Value Continuity and VCDesign Integration Safety

- CCP does not redefine Value Continuity, the Value Asymmetry Principle, the five principles or Decision.
- CCP does not redefine VCDesign terms; `decision_authority.loop`, `boundary_policy` and `boundary_policy.delta` refer to them as they are.
- Technical fields (signature, canonicalization, nonce, cost_model) do not carry value meaning.

---

# 10. Termination Safety

## 10.1 Success
- When ACCEPT signature verification succeeds
- CLOSE with residual assets handed over to named holders

## 10.2 Failure
- REJECT
- REVERSE
- expires_at exceeded
- nonce reuse

---

# 11. License

MIT License
© VCDesign Project
