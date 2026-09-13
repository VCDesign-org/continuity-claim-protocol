# CCP ↔ VCDesign Integration Mapping
Version: 1.1
Status: Stable
Audience: This document — AI Agents / Implementers (a field-level mapping reference; CCP itself
is not AI-specific, see README.md §1–§2)
Human‑facing: No, for this mapping reference specifically (VCDesign Core remains unchanged)

---

# 1. Purpose

This document defines the **conceptual mapping** between **CCP Handshake** and **VCDesign
Core**. CCP Handshake is the implementation form of VCDesign's Adjacent Boundary Observation
mutuality condition (see README.md §7) — its scope is any connection that hands off
responsibility, not only connections between AIs. This document itself is a field-level
reference for implementers wiring CCP fields to VCDesign concepts.

VCDesign Core is immutable, and this document is an implementer-facing technical mapping
placed on the CCP side; it does not redefine VCDesign Core.

---

# Contents

1. Purpose
2. Design Principles
3. Non-Goals
4. High-Level Mapping Table
5. Detailed Mapping

---

# 2. Design Principles

1. VCDesign Core is unchanged.
2. CCP is the technical implementation of a mutuality condition VCDesign Core requires — not
   an appendage outside it (see README.md §7).
3. CCP only "references" the concepts of the Core.
4. CCP must not redefine the meaning of the Core.
5. This document is a translation layer for implementers wiring CCP fields to VCDesign
   concepts.
6. This specific field-mapping reference is written for implementers, not general readers —
   that is a statement about this document's audience, not about who CCP is for.

---

# 3. Non-Goals

- Replacing or modifying VCDesign Core
- Formalizing cryptographic or legal guarantees
- Defining governance, ethics, or value judgments
- Providing an exhaustive ontology of VCDesign

---

# 4. High‑Level Mapping Table

| CCP Component | VCDesign Concept | Meaning |
|---------------|------------------|---------|
| `world.id` | Boundary | Declaration of the "World" where conversation takes place |
| `continuity_claim.boundary_def` | Chapter (Membrane) | External mapping of the Membrane of Responsibility |
| `decision_authority.domain` | BOA (Meaning / Responsibility / Execution) | Location of Decision Authority |
| `resolution_policy` | RC (Δ and R) | Handling of Unresolved Areas and Resolutions |
| `reversal_signal` | DCS (Mid-stream Reversal) | Unwinding of Decision Authority |
| `trust.validation_level` | IDG (Determinability) | Promotion Conditions for Decisions |
| `interface.semantics.intent` | Meaning Scope | Scope of Meaning of Output |
| `signature_schema` | Outside VCDesign (Technical Layer) | Cryptographic Membrane not present in Core |

---

# 5. Detailed Mapping

## 5.1 Boundary
**VCDesign:**  
Boundary defines the "Physical Laws of the World".

**CCP:**  
`world.id` references the boundary of VCDesign.

**Rule:**  
CCP must not redefine the meaning of the boundary.

---

## 5.2 Membrane (Chapter)
**VCDesign:**  
Chapter is a "Membrane of Responsibility" and a unit that maintains the continuity of value.

**CCP:**  
`continuity_claim.boundary_def` is the "External Mapping of the Chapter" that structures the 3 elements of BOA.

**Rule:**  
CCP does not generate Chapters.  
The definition of Chapters is done only by VCDesign Core.

---

## 5.3 Responsibility
**VCDesign:**  
Responsibility decides "Where to close the decision".

**CCP:**  
`decision_authority.domain` refers to the tripartite division of BOA.

**Rule:**  
CCP must not change the meaning of responsibility.

---

## 4.4 Δ and R (RC)
**VCDesign:**  
Δ is the unresolved area, R is the solution.

**CCP:**  
`resolution_policy` defines the transfer, resolver, and redaction scope of Δ.

**Rule:**  
CCP must not change the philosophical meaning of Δ.

---

## 4.5 Decision Closure (DCS)
**VCDesign:**  
Determines whether AI is allowed to close decisions via 5 Validation Steps.

**CCP:**  
`reversal_signal` technically notifies the mid-stream reversal of DCS.

**Rule:**  
CCP must not change the judgment logic of DCS.

---

## 4.6 Determinability Gate (BOA/IDG)
**VCDesign:**  
Structurally determines whether it is allowed to decide or not.

**CCP:**  
`trust.validation_level` is the "Technical Mapping" of IDG.

**Rule:**  
validation_level is not a substitute for IDG.

---

## 4.7 Meaning Scope
**VCDesign:**  
The scope of meaning is defined inside the Chapter.

**CCP:**  
`interface.semantics.intent` declares on communication the scope of meaning.

**Rule:**  
intent does not overwrite the Meaning Scope of VCDesign.

---

# 5. Non‑Mapping (Areas not mapped)

The following must **not correspond** between VCDesign Core and CCP.

- signature_schema (Cryptographic Layer)  
- canonicalization (Normalization)  
- nonce / timestamp (Time)  
- cost_model (Computational Resources)  
- participants (AI Identifiers)  

These are irrelevant to the Philosophical Membrane of VCDesign and are **concepts that exist only in the Technical Layer of CCP**.

---

# 6. Integration Rules

The following are **mandatory rules to protect VCDesign Core**.

1. VCDesign Core is immutable, and CCP must not change the Core.  
2. CCP only "references" the concepts of the Core and must not redefine the meaning.  
3. The Technical Layer of CCP (Signature, Normalization, Nonce, etc.) does not affect the Core.  
4. Implementers read this mapping to avoid misapplying the concepts of the Core when wiring
   CCP fields.
5. This mapping reference is written for implementers; VCDesign Core's own documents remain
   the human-facing entry point.
6. CCP must not overwrite the Responsibility Boundary (Meaning / Responsibility / Execution) of VCDesign Core through decision_authority or resolution_policy.


This is the **most important rule to protect the Membrane of VCDesign**.

---

# 7. Intended Audience

- AI Agents  
- CCP Implementers  
- Multi‑Agent System Designers  
- Boundary‑aware AI Frameworks  
- Human process owners applying the reversal-condition minimal pattern (see README.md §3) may
  skip this document — it is a field-level mapping table for implementers, not required
  reading to apply CCP to a handover or approval flow.

---

# 8. Versioning

- VCDesign Core is versioned independently  
- CCP Handshake implements a rule VCDesign Core requires, but does not change Core  
- This Mapping follows the version of CCP  

---

# 9. License

MIT License  
© VCDesign Project
