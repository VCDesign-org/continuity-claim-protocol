# CCP Handshake Specification
CCP = Continuity Claim Protocol
Version: 3.0
Status: Draft-Stable
Maintainer: VCDesign Project

CCP implements [Value Continuity](https://github.com/value-continuity/value-continuity) on the side of
**crossings between organizations and agents**.

Value Continuity is *keeping the ability to create the next value, even through change and failure*.
Its central principle, the **Value Asymmetry Principle**, is: *make upside propagable; do not let downside propagate.*
Those definitions live in the canonical repository and are not redefined here.
CCP specifies what two parties declare before a crossing, how the crossing is checked,
what is stopped and what is passed on, and how a connection is reversed and closed.

---

> **Protocol Manifesto**
>
> Every crossing is checked, and the check closes as pass, deny, or unknown.
> Unknown is never treated as pass: it stops, is exposed, and is raised to a human.
>
> Decisions are closed by humans, with the six words of Value Continuity.
> A closed decision authorizes a scope; within it, agents may act on their own.
> A change that would exceed that scope is a Δ, and it is decided again.
>
> At the boundary, losses are stopped and basis passes on.
> The other party's conclusion is not inherited; it is revalidated.
>
> If, during connection,
> the declared precondition or ceiling is broken,
> a mid-course reversal is performed, and every Δ is returned with a holder.
>
> And when the connection no longer leads to the next value,
> it is retired, and what remains is handed over to someone who will hold it.

---

## 0. Value Continuity Family

```
Value Continuity  — the principle (canonical definitions)
├── VCDesign      — judgment and responsibility
├── BEAM          — (defined in its own repository)
└── CCP           — crossings between organizations and agents
```

| | Role | Repository |
|---|---|---|
| Value Continuity | Definition, Value Asymmetry Principle, five principles, Decision | [value-continuity/value-continuity](https://github.com/value-continuity/value-continuity) |
| VCDesign | Implements Value Continuity on the side of judgment and responsibility | [VCDesign-org/vcdesign](https://github.com/VCDesign-org/vcdesign) |
| BEAM | A sibling implementation of Value Continuity | — |
| CCP | Implements Value Continuity on the side of crossings between organizations and agents | this repository |

CCP does not redefine Value Continuity, and it does not redefine the terms of its siblings.
Where VCDesign already names a mechanism (guard, containment, basis_flow, revalidation, the six decisions),
CCP uses the same word and the same meaning. VCDesign's boundary pattern refers to CCP for
`external_crossing`.

---

## 1. Overview

CCP Handshake is the **minimal protocol for AI to autonomously construct interfaces on the fly** across organizations and agents.

Modern AI systems presuppose structures that follow fixed APIs or unilateral interfaces.
However, value continues across a crossing **only when the boundary, the responsibility and the authorized scope are declared before crossing**.

CCP Handshake defines the **minimal handshake** to safely initiate connection between AIs, based on:

- Not power dynamics, but a **declared boundary with an owner**
- Not inference, but a **declared precondition and value intent**
- Not implicit authority, but a **human-closed decision and its scope**
- Not symmetric trust, but **losses stopped and basis passed on**

---

## 2. Design Principles

### **2.1 Boundary First**
AI does not infer purpose.
First, it declares which World to cross into, who owns the boundary, and on what precondition.

### **2.2 Humans Close Decisions**
AI supports decisions but does not hold final responsibility.
The final decider is always human, and the decision is one of the six words: Proceed, Expand, Limit, Reframe, Defer, Retire.

### **2.3 Scope Authorized by a Decision**
A crossing runs within the scope declared by a human decision (proceed / expand / limit: blast radius, reversibility).
Exceeding it is a Δ and is re-decided.

### **2.4 Asymmetry at the Boundary**
Negative Δ is contained. Basis, evidence, residual assets and Positive Δ are made propagable.
Propagating further — widening the connection — requires Expand, with an observed Positive Δ and confirmed recovery.

### **2.5 Unknown Fails Safe**
If the input is not sufficient for a verdict, the verdict is unknown: stop, expose, escalate. Never guess.

### **2.6 Minimality**
The handshake is established with minimal information.
Eliminate unnecessary semantic inference or implicit assumptions.

---

## 3. Terminology

- **Spec**: High-level intent and scope (`specs/handshake.yaml`)
- **Schema**: Formal structure and validation rules (`schemas/handshake.schema.yaml`)
- **Protocol**: Dynamic procedure and state transitions (`docs/en/handshake.protocol.md`)
- **Security**: Minimum safety requirements and constraints (`docs/en/handshake.security.md`)
- **Guard verdict**: `pass` / `deny` / `unknown` on a single crossing. Not a decision.
- **Decision**: One of the six words of Value Continuity, closed by a human.

---

## 4. Components of the Specification

### **4.1 specs/handshake.yaml (Spec)**
- High-level handshake spec, design intent, and alignment with Value Continuity and VCDesign

### **4.2 schemas/handshake.schema.yaml (Structure)**
- Defines **types, structures, and validation rules** required for the handshake
- JSON Schema compatible
- `decision_authority`: human final decider, owner, loop, authorization (decision, blast radius, reversibility), escalation
- `boundary_policy`: containment, basis_flow, revalidation, and the holder of Δ
- `continuity_claim`: boundary (owner, precondition, meaning scope), declaration (value intent, residual assets, spread signals), signature
- Version is aligned with `specs/handshake.yaml` (currently 3.0)

### **4.3 docs/en/handshake.protocol.md (Procedure)**
- State transitions: HELLO → OFFER → ACCEPT / REJECT → REVERSE → CLOSE
- Mandatory checks at each phase
- Guard verdicts and how the six decisions appear in the protocol
- Return of Δ with a holder, and return of control to a human

### **4.4 docs/en/handshake.security.md (Security)**
- canonicalization
- signed_fields
- Replay prevention (nonce / timestamp / expires_at)
- Authority safety (human final decider, Expand conditions, AI in slow loops)
- Boundary safety (containment, basis_flow, revalidation, Δ)

### **4.5 docs/en/continuity-claim.md (Claim signals)**
- `Signed` / `Denied` / `Silence` as guard verdicts `pass` / `deny` / `unknown`

---

## 5. Why CCP Handshake Exists

In a future where AIs cooperate,
**fixed APIs and centralized interfaces let a single failure spread, and let no learning pass.**

AI originally possesses the ability to:

- Redefine boundaries
- Adjust the scope of meaning
- Negotiate the location of responsibility
- Generate interfaces on the fly

according to the situation.

However, this degree of freedom presupposes that **the initial crossing is declared and checked**.

CCP Handshake provides that first boundary: where losses stop, basis passes on, and a human-closed decision sets the scope.

---

## 6. Minimal Handshake Model

The handshake satisfies VCDesign's `external_crossing` requirement: **identity, declared boundary, authority, signature**.

### **6.1 Identity (Who connects)**
- handshake_meta (handshake_id, participants)
- agent (id, provider, kind)

### **6.2 Declared Boundary (Which world, on what precondition)**
- world
- continuity_claim.boundary (owner, precondition, meaning_scope)
- continuity_claim.declaration (value_intent, residual_assets)
- boundary_policy (containment, basis_flow, revalidation, delta)

### **6.3 Authority (Who closed the decision, within what scope)**
- decision_authority (final_decider, owner, loop, authorization, escalation)
- reversal_signal

### **6.4 Signature**
- continuity_claim.signature_schema

When these are aligned, AIs are **ready to autonomously construct the interface** within the authorized scope.

---

## 7. Relationship to Value Continuity and VCDesign

| Value Continuity / VCDesign | CCP Handshake Component |
|-----------------------------|-------------------------|
| Value Asymmetry Principle (downside) / containment | `boundary_policy.containment` |
| Value Asymmetry Principle (upside) / basis_flow | `boundary_policy.basis_flow` |
| revalidation | `boundary_policy.revalidation` |
| guard verdict (pass / deny / unknown) | ACCEPT / REJECT, claim signals |
| Decision (six words) | `decision_authority.authorization.decision` and protocol outcomes |
| Δ (baseline: precondition + value intent) | `continuity_claim.boundary.precondition`, `continuity_claim.declaration.value_intent` |
| closure_loop (Δ never ownerless) | `boundary_policy.delta.holder` |
| tenure (who keeps holding the boundary) | `continuity_claim.boundary.owner` |
| AI extension (A3, loops, haltability) | `agent.kind`, `decision_authority.loop`, `escalation.halt_owner` |
| boundary pattern `external_crossing` | the whole handshake |

For the full concept-level mapping, see `mappings/vcdesign_mapping.md`.

---

## 8. Migration from 2.1

3.0 is not compatible with 2.1, following VCDesign v2. Read the 2.1 vocabulary as follows.

| 2.1 | 3.0 |
|-----|-----|
| Positioning: technical membrane outside the immutable VCDesign Core | Implementation of Value Continuity on the side of crossings; sibling of VCDesign and BEAM |
| BOA / RC / DCS / IDG / RCA | guard (with determinability), containment, basis_flow, revalidation, six decisions |
| `decision_authority.initial_state: Human-Closed / AI-Closed` | `decision_authority.final_decider` (always `human`). AI-Closed is removed (AI does not hold final responsibility) |
| `decision_authority.allowed_transitions`, `escalation_rules` (AI→Human) | `decision_authority.escalation` (`on_unknown`, `halt_owner`); control always returns to the human final decider |
| `decision_authority.domain: meaning / responsibility / execution` | `decision_authority.loop: physical / semantic / value / responsibility` |
| — | `decision_authority.owner`, `decision_authority.authorization` (decision, decision_ref, decided_by, blast_radius, reversibility, expand_basis) |
| `resolution_policy` (Δ and R) | `boundary_policy` |
| `resolution_policy.delta_transfer.{allowed, scope}` | `boundary_policy.delta.transfer.{allowed, scope}` |
| `resolution_policy.delta_transfer.redaction` | `boundary_policy.basis_flow.redaction` |
| `resolution_policy.resolver` | `boundary_policy.delta.holder` (Δ is held until a decision closes it) |
| — | `boundary_policy.containment`, `boundary_policy.basis_flow`, `boundary_policy.revalidation` |
| `reversal_signal.events.type: validation_fail / authority_revoked` | adds `guard_deny`, `guard_unknown`, `precondition_broken`, `blast_radius_exceeded`; payload adds `delta_ref`, `holder` |
| `continuity_claim.boundary_def` (BOA three elements) | `continuity_claim.boundary` + `continuity_claim.declaration` |
| `boundary_def.responsibility_id` | `boundary.owner` (+ optional `boundary.responsibility_boundary`, B1–B17) |
| `boundary_def.context_assumption` | `boundary.precondition` |
| `boundary_def.meaning_scope` | `boundary.meaning_scope` |
| — | `declaration.value_intent`, `residual_assets`, `spread_signals`, `review_triggers`, `depends_on` |
| — | `agent.kind: ai / human / system` |
| States HELLO / OFFER / ACCEPT / REJECT / REVERSE | adds CLOSE; ACCEPT = `pass`, REJECT = `deny` or `unknown` |
| "Mid-stream reversal based on DCS" | REVERSE on guard verdict, broken precondition, exceeded blast radius, or revoked authority |
| Claim signals Signed / Denied / Silence | unchanged, read as guard verdicts pass / deny / unknown |
| `specs/handshake.yaml schema_definition` (inline copy) | `specs/handshake.yaml schema.ref` → `schemas/handshake.schema.yaml` |

The two PDFs under `docs/` describe 2.1 and are kept as a historical record.

---

## 9. Intended Use

CCP Handshake assumes the following uses:

- Safe connection between AIs across organizations
- Cooperation between automated code generation agents
- Handover of responsibility and of Δ across boundaries
- Automatic generation of interfaces maintaining semantic consistency
- Transparency of AI processes as a supply chain

---

## 10. Non-Goals

The following are out of scope for CCP Handshake:

- Redefining Value Continuity or VCDesign
- Guarantee of model correctness/performance
- Ethical judgment/Value judgment
- Estimation of AI personality/intent
- Replacement for full cryptographic protocols

CCP Handshake is the **minimal protocol that keeps losses from crossing and lets basis cross**.

---

## 11. Getting Started

Order to read first:

1. **[Value Continuity](https://github.com/value-continuity/value-continuity)**
   → The principle CCP implements

2. **specs/handshake.yaml**
   → Understand the high-level intent and structure

3. **schemas/handshake.schema.yaml**
   → Understand which fields are required

4. **docs/en/handshake.protocol.md**
   → Understand the flow of the handshake

5. **docs/en/handshake.security.md**
   → Understand why it is safe

---

## 12. License

MIT License
© VCDesign Project

---

## Status Policy

- Documents remain `Draft-Stable` until all derived docs match the same version and structure.
- Promote to `Stable` only when schema and protocol changes are frozen for a release cycle.
