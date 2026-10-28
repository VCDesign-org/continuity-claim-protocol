# CCP Handshake Specification
CCP = Continuity Claim Protocol
Version: 2.1  
Status: Draft-Stable  
Maintainer: VCDesign Project

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

CCP Handshake is the **minimal protocol for AI to autonomously construct interfaces on the fly**.

Modern AI systems presuppose structures that follow fixed APIs or unilateral interfaces.  
However, continuity of value (Continuity) is maintained **only when the Boundary (World) and Responsibility are aligned**.

Based on the principles of VCDesign / BOA / RC / DCS, CCP Handshake defines the **minimal handshake** to safely initiate connection between AIs, based on:

- Not power dynamics, but "Membrane of Responsibility"
- Not inference, but "Declaration of Boundary"
- Not implicit, but "Explication of Decision Authority"
- Not automation, but "Assurance of Continuity"

---

## 2. Design Principles

CCP Handshake is based on the following principles.

### **2.1 Boundary First**
AI does not infer purpose.  
First, it declares "which World to converse in" and aligns the boundaries.

### **2.2 Responsibility Continuity**
Decisions must not be closed arbitrarily by AI.  
Follow RC (Responsibility Closure) to clarify the positions of Δ and R.

### **2.3 Determinability Gate**
Based on BOA/IDG, structurally determine the conditions under which AI is allowed to close decisions.

### **2.4 Decision Closure Safety**
Check whether AI is allowed to close decisions via **5 Validation Steps** according to DCS.

### **2.5 Minimality**
The handshake is established with "minimal information".  
Eliminate unnecessary semantic inference or implicit assumptions.

---

## 3. Terminology

- **Spec**: High-level intent and scope (`specs/handshake.yaml`)
- **Schema**: Formal structure and validation rules (`schemas/handshake.schema.yaml`)
- **Protocol**: Dynamic procedure and state transitions (`docs/en/handshake.protocol.md`)
- **Security**: Minimum safety requirements and constraints (`docs/en/handshake.security.md`)

---

## 4. Components of the Specification

This package consists of the following 4 documents.

### **4.1 specs/handshake.yaml (Spec)**
- High-level handshake spec and design intent

### **4.2 schemas/handshake.schema.yaml (Structure)**
- Defines **types, structures, and validation rules** required for handshake
- JSON Schema compatible
- Structuralizes the 3 elements of BOA (responsibility_id / meaning_scope / context_assumption)
- Separates trust into validation_level and risk_level
- Strictly defines decision_authority / resolution_policy / reversal_signal
- Version is aligned with `specs/handshake.yaml` (currently 2.1)

### **4.3 docs/en/handshake.protocol.md (Procedure)**
- State transitions: HELLO → OFFER → ACCEPT → REVERSE
- Mandatory checks at each phase
- Mid-conversation reversal by DCS
- Return of Δ and unwinding of authority

### **4.4 docs/en/handshake.security.md (Security)**
- canonicalization
- signed_fields
- Replay prevention (nonce / timestamp / expires_at)
- Forced transition on authority_revoked
- Safe transfer of Δ

---

## 4. Why CCP Handshake Exists

In a future where AIs cooperate,  
**Fixed APIs and centralized interfaces destroy the continuity of value.**

AI originally possesses the ability to:

- Redefine boundaries
- Adjust the scope of meaning
- Negotiate the location of responsibility
- Generate interfaces on the fly

according to the situation.

However, this degree of freedom premises that **the initial handshake is safe**.

CCP Handshake provides that "Initial Membrane".

---

## 5. Minimal Handshake Model

The handshake is established on the following 3 pillars.

### **5.1 Identity (Who connects)**
- handshake_id  
- participants  
- signature_schema  

### **5.2 Boundary (Which world to connect in)**
- world  
- trust  
- interface  

### **5.3 Authority (Who closes decisions)**
- decision_authority  
- resolution_policy  
- reversal_signal  

When these are aligned, AIs are **ready to autonomously construct the interface**.

---

## 6. Relationship to VCDesign

CCP Handshake corresponds to the following chapters of VCDesign.

| VCDesign Concept | CCP Handshake Component |
|------------------|-------------------------|
| Chapter (Membrane) | continuity_claim.boundary_def |
| Boundary (World) | world.id |
| Responsibility | decision_authority.domain |
| Δ and R (RC) | resolution_policy |
| Closing Decisions (DCS) | reversal_signal |
| Determinability (BOA/IDG) | trust.validation_level / semantics.intent |

In other words, CCP Handshake is  
**The mechanism to guarantee the "strength of the membrane" during external connections in VCDesign**.

For a detailed concept-level mapping, see `mappings/vcdesign_mapping.md`.

---

## 7. Intended Use

CCP Handshake assumes the following uses:

- Safe connection between AIs
- Cooperation between automated code generation agents
- Transfer of responsibility across boundaries
- Automatic generation of interfaces maintaining semantic consistency
- Transparency of AI processes as a supply chain

---

## 8. Non-Goals

The following are out of scope for CCP Handshake:

- Guarantee of model correctness/performance
- Ethical judgment/Value judgment
- Estimation of AI personality/intent
- Replacement for full cryptographic protocols

CCP Handshake is the **minimal protocol to guarantee the continuity of responsibility and boundaries**.

---

## 9. Getting Started

Order to read first:

1. **specs/handshake.yaml**  
   → Understand the high-level intent and structure

2. **schemas/handshake.schema.yaml**  
   → Understand which fields are required

3. **docs/en/handshake.protocol.md**  
   → Understand the flow of the handshake

4. **docs/en/handshake.security.md**  
   → Understand why it is safe


### Profiles (application layers on top of Core)

- **docs/en/life-profile.md** (Draft 0.3)
  → CCP Life Profile: applies CCP to connections between a person and external AIs. Extension schema: `schemas/life-profile.schema.yaml`. Does not change Core semantics.

---

## 10. License

MIT License  
© VCDesign Project

---

## Status Policy

- Documents remain `Draft-Stable` until all derived docs match the same version and structure.
- Promote to `Stable` only when schema and protocol changes are frozen for a release cycle.
