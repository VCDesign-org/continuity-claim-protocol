# CCP Handshake Specification
CCP = Continuity Claim Protocol
Version: 2.1  
Status: Draft-Stable  
Maintainer: VCDesign Project

**Positioning (revised 2026-09):** CCP is not a derivative or related project of VCDesign.
It is the implementation form of VCDesign's
[Adjacent Boundary Observation mutuality condition](https://github.com/VCDesign-org/vcdesign/blob/main/specs/policies/adjacent-boundary-observation.yaml)
(the paired requirement that "the neighbor is confirmed to follow the same rule"), and is
positioned as a foundational layer. See §7, "Relationship to VCDesign," for detail.

---

> **Protocol Manifesto**
>
> Judgments are always closed as either affirmative, negative, or unknown,
> and the decision rule does not change while executing that judgment.
>
> To sustain value, the Continuer observes changes in decision rules
> and the environment, and changes the decision rules.
>
> When chaining or composing judgments is required,
> each judgment makes responsibility boundaries explicit,
> and they connect only on the premise that each is "closed."
>
> If, during connection,
> it is judged that those boundaries or premises have broken,
> a mid-course reversal is performed and the judgment must not be closed.
>
> And when value can no longer be maintained,
> it must be acknowledged that the premise for continuing that judgment is lost,
> and the judgment must be abandoned.

---

## 1. Overview

CCP Handshake is the **minimal protocol for safely establishing, on the spot, any connection
across which responsibility is handed off**.

The case that exists as prior art and is already validated is the connection between human
processes. Handover documents, FMEA, and change-approval workflows already implement part of
this handshake — mostly implicitly. CCP extracts that as an explicit structure, making clear
what is already in place and what is missing.

Connection between AIs is a **special case** of this same minimal form. AI was chosen as the
first application not because anthropomorphizing the connection succeeded, but because the
handoff of responsibility is more exposed between AIs than anywhere else — so gaps in the
handshake show up there fastest and are easiest to find.

Modern AI systems presuppose structures that follow fixed APIs or unilateral interfaces.  
However, continuity of value (Continuity) is maintained **only when the Boundary (World) and
Responsibility are aligned**.

Based on the principles of VCDesign / BOA / RC / DCS, CCP Handshake defines the **minimal
handshake** to safely initiate any connection that hands off responsibility, based on:

- Not power dynamics, but "Membrane of Responsibility"
- Not inference, but "Declaration of Boundary"
- Not implicit, but "Explication of Decision Authority"
- Not automation, but "Assurance of Continuity"

---

## 2. Why the same form works across layers and scale

CCP's three pillars (Identity / Boundary / Authority) declare **only the form of the
connection** — they contain nothing about the nature of the parties being connected (human,
AI, department).

- Identity declares who is connecting, regardless of whether that is a person or an AI.
- Boundary declares which world (scope of responsibility) the connection happens in.
- Authority declares who closes the decision.

It is precisely because the form contains nothing about the parties' nature that the same
form carries over across layers and scale. AI was where this minimal form could first be
validated most easily — not because CCP's core is AI-specific.

---

## 3. Notes on applying this to human processes

Do not port the HELLO → OFFER → ACCEPT → REVERSE state machine into a human-process handover
as-is. The procedure designed for AI-to-AI connection is overkill for human process, and its
shape does not fit directly.

Between human processes, part of this handshake — the equivalent of Identity (declaring who is
responsible) and Boundary (declaring the scope of work) — already exists in the form of
handover documents and FMEA.

What is usually missing is **REVERSE**: the declaration of a reversal condition. It is rare
for a handover document to state in advance what should trigger sending this handover or
approval back.

The **minimal application** to human process — manufacturing floors included — is therefore
not introducing a new document format. It is overlaying one question onto the existing
handover/approval flow: *is a reversal condition declared?* This is the intended entry point
into human process and manufacturing floors. The full AI-to-AI protocol (all four pillars) is
introduced only later, when a scenario actually needs it, after this minimal application.

---

## 4. Design Principles

CCP Handshake is based on the following principles.

### **4.1 Boundary First**
The connecting parties do not infer purpose.  
First, each declares "which World to converse in" and aligns the boundaries.

### **4.2 Responsibility Continuity**
A decision must not be closed unilaterally by either party.  
Follow RC (Responsibility Closure) to clarify the positions of Δ and R.

### **4.3 Determinability Gate**
Based on BOA/IDG, structurally determine the conditions under which a decision is allowed to
be closed.

### **4.4 Decision Closure Safety**
Check whether a decision is allowed to be closed via **5 Validation Steps** according to DCS.

### **4.5 Minimality**
The handshake is established with "minimal information".  
Eliminate unnecessary semantic inference or implicit assumptions.

---

## 5. Terminology

- **Spec**: High-level intent and scope (`specs/handshake.yaml`)
- **Schema**: Formal structure and validation rules (`schemas/handshake.schema.yaml`)
- **Protocol**: Dynamic procedure and state transitions (`docs/en/handshake.protocol.md`)
- **Security**: Minimum safety requirements and constraints (`docs/en/handshake.security.md`)

---

## 6. Components of the Specification

This package consists of the following 4 documents.

### **6.1 specs/handshake.yaml (Spec)**
- High-level handshake spec and design intent

### **6.2 schemas/handshake.schema.yaml (Structure)**
- Defines **types, structures, and validation rules** required for handshake
- JSON Schema compatible
- Structuralizes the 3 elements of BOA (responsibility_id / meaning_scope / context_assumption)
- Separates trust into validation_level and risk_level
- Strictly defines decision_authority / resolution_policy / reversal_signal
- Version is aligned with `specs/handshake.yaml` (currently 2.1)

### **6.3 docs/en/handshake.protocol.md (Procedure)**
- State transitions: HELLO → OFFER → ACCEPT → REVERSE (the full form, AI-to-AI included)
- Mandatory checks at each phase
- Mid-conversation reversal by DCS
- Return of Δ and unwinding of authority

### **6.4 docs/en/handshake.security.md (Security)**
- canonicalization
- signed_fields
- Replay prevention (nonce / timestamp / expires_at)
- Forced transition on authority_revoked
- Safe transfer of Δ

---

## 7. Relationship to VCDesign

CCP Handshake is neither an appendage bolted onto the outside of VCDesign nor a derivative
project of it.

VCDesign's operational policy set defines an Adjacent Boundary Observation rule for how far
verification of a boundary must reach. That rule only holds under a mutuality condition: **the
neighboring node is confirmed to be following the same rule.** The rule is incomplete on its
own and must always be operated as a pair (see
[`adjacent-boundary-observation.yaml` / `article_1.mutuality_condition`](https://github.com/VCDesign-org/vcdesign/blob/main/specs/policies/adjacent-boundary-observation.yaml)).

CCP Handshake's HELLO → OFFER → ACCEPT is that mutuality condition — "declare your own
boundary, and confirm the other side has declared theirs, before connecting" — written down as
an executable procedure. REVERSE is the exit procedure for when that mutuality turns out to
have broken after the fact.

In other words, CCP Handshake is not an external-connection option for VCDesign. It is
**the implementation of the mutuality that VCDesign's boundary rule itself requires.**
Connection between AIs is simply the case within that where a missing mutuality surfaces
fastest and is easiest to verify.

For a detailed concept-level mapping, see `mappings/vcdesign_mapping.md`.

| VCDesign Concept | CCP Handshake Component |
|------------------|-------------------------|
| Chapter (Membrane) | continuity_claim.boundary_def |
| Boundary (World) | world.id |
| Responsibility | decision_authority.domain |
| Δ and R (RC) | resolution_policy |
| Closing Decisions (DCS) | reversal_signal |
| Determinability (BOA/IDG) | trust.validation_level / semantics.intent |
| Adjacent Boundary Observation mutuality condition | HELLO → OFFER → ACCEPT (mutual declaration check) |

---

## 8. Intended Use

CCP Handshake assumes the following uses:

- Making the reversal condition explicit in human-process handovers and approvals
- Safe connection between AIs
- Cooperation between automated code generation agents
- Transfer of responsibility across boundaries
- Automatic generation of interfaces maintaining semantic consistency
- Transparency of AI processes as a supply chain

---

## 9. Non-Goals

The following are out of scope for CCP Handshake:

- Guarantee of model correctness/performance
- Ethical judgment/Value judgment
- Estimation of AI personality/intent
- Replacement for full cryptographic protocols

CCP Handshake is the **minimal protocol to guarantee the continuity of responsibility and
boundaries**.

---

## 10. Getting Started

Order to read first:

1. **specs/handshake.yaml**  
   → Understand the high-level intent and structure

2. **schemas/handshake.schema.yaml**  
   → Understand which fields are required

3. **docs/en/handshake.protocol.md**  
   → Understand the flow of the handshake

4. **docs/en/handshake.security.md**  
   → Understand why it is safe



---

## 11. License

MIT License  
© VCDesign Project

---

## Status Policy

- Documents remain `Draft-Stable` until all derived docs match the same version and structure.
- Promote to `Stable` only when schema and protocol changes are frozen for a release cycle.
