# CCP ↔ Value Continuity / VCDesign Integration Mapping
Version: 2.0
Status: Stable
Audience: AI Agents / Implementers
Human‑facing: No (Value Continuity and VCDesign are not redefined here)

---

# 1. Purpose

This document defines the **conceptual mapping** between **CCP Handshake** and the two documents it depends on:

- **[Value Continuity](https://github.com/value-continuity/value-continuity)** — the principle (canonical definitions)
- **[VCDesign v2](https://github.com/VCDesign-org/vcdesign)** — its sibling implementation on the side of judgment and responsibility

CCP, VCDesign and BEAM stand side by side under Value Continuity. CCP implements Value Continuity on the side of crossings between organizations and agents. This document is placed only on the CCP side; it is a translation layer so that AI does not misread either document.

---

# Contents

1. Purpose
2. Design Principles
3. Non-Goals
4. Value Continuity Mapping
5. VCDesign v2 Mapping
6. Non-Mapping
7. Integration Rules
8. Legacy (2.1) Terms
9. Versioning

---

# 2. Design Principles

1. Value Continuity is the canonical source of definitions. CCP does not redefine it.
2. VCDesign and CCP are siblings. CCP does not redefine VCDesign terms, and VCDesign does not redefine CCP fields.
3. Where VCDesign already names a mechanism, CCP uses the same word with the same meaning.
4. CCP adds only what is specific to a crossing between parties: identity, signature, replay protection, the handshake states.
5. This document is a translation layer for AI.
6. Humans do not need to read this document (For AI).

---

# 3. Non-Goals

- Replacing or modifying Value Continuity or VCDesign
- Formalizing cryptographic or legal guarantees
- Defining governance, ethics, or value judgments
- Providing an exhaustive ontology of Value Continuity or VCDesign

---

# 4. Value Continuity Mapping

## 4.1 Central principle

| Value Continuity | CCP | Rule |
|------------------|-----|------|
| Value Asymmetry Principle — do not let downside propagate | `boundary_policy.containment` (propagation: deny by default) | Losses do not cross the boundary |
| Value Asymmetry Principle — make upside propagable | `boundary_policy.basis_flow` (default: allow) | Basis, evidence, residual assets and Positive Δ cross; conclusions do not |
| "Propagable" does not mean "propagates automatically" | `authorization.decision = expand` with `expand_basis` | Widening a connection is a human decision |
| Δ (gap from the declared expectation) | `boundary_policy.delta`; baseline = `continuity_claim.boundary.precondition` + `continuity_claim.declaration.value_intent` | CCP does not change the meaning of Δ |
| Negative Δ / Positive Δ | containment / basis_flow; `delta.unrecorded_polarity: negative` | Positive Δ is never halted or quarantined by a reversal |

## 4.2 Five principles

| Principle | CCP |
|-----------|-----|
| Keep（残す） | `continuity_claim.declaration.residual_assets` (with holders), `decision_authority.owner`, `continuity_claim.boundary.owner`, CLOSE |
| Find（見つける） | `continuity_claim.declaration.spread_signals`, `basis_flow.passes: positive_delta` |
| Close（閉じる） | `boundary_policy.containment`, `authorization.blast_radius`, REJECT, REVERSE |
| Try（試す） | `authorization.reversibility`, `escalation.halt_owner`, Expand only within recovery |
| Pass on（伝える） | `boundary_policy.basis_flow`, `boundary_policy.revalidation`, the reason of a deny |

## 4.3 Decision

| Decision | CCP |
|----------|-----|
| Proceed | `authorization.decision = proceed` — open the connection with the current declaration |
| Expand | `authorization.decision = expand` — new handshake with a wider declaration; requires `expand_basis` |
| Limit | `authorization.decision = limit` — new handshake with a narrower declaration |
| Reframe | New `continuity_claim` (new id, precondition, owner) and new handshake |
| Defer | No connection; REJECT with `unknown`, a temporary owner and `next_review_at` |
| Retire | No connection, or CLOSE with residual assets handed over |

**Rule:** CCP does not add decision vocabulary. Handshake states (HELLO, OFFER, ACCEPT, REJECT, REVERSE, CLOSE) are protocol states, not decisions.

---

# 5. VCDesign v2 Mapping

## 5.1 High-level table

| CCP Component | VCDesign v2 | Meaning |
|---------------|-------------|---------|
| The whole handshake | `boundary-pattern.yaml external_crossing` | identity, declared_boundary, authority, signature |
| `handshake_meta`, `agent` | `external_crossing.identity` | Who crosses |
| `world`, `continuity_claim.boundary`, `continuity_claim.declaration` | `external_crossing.declared_boundary` | Where, on what precondition, for what value |
| `decision_authority` | `external_crossing.authority`, `core.yaml decision` | Who closed the decision, within what scope |
| `continuity_claim.signature_schema` | `external_crossing.signature` | Technical layer |
| ACCEPT / REJECT, claim signals | `boundary.guard.verdicts` (pass / deny / unknown) | Check on a crossing, not a decision |
| `trust.validation_level` | `boundary.guard.determinability` (input) | Whether the input is sufficient; not a substitute for the guard |
| `boundary_policy.containment` | `boundary.containment` | Stop failures and commands |
| `boundary_policy.basis_flow` | `boundary.basis_flow` | Pass basis and what remains |
| `boundary_policy.revalidation` | `boundary.revalidation` | Re-check upstream conclusions |
| `continuity_claim.boundary.owner` | `boundary.tenure.owner` | Who keeps holding the boundary |
| `boundary_policy.delta.holder` | `core.yaml closure_loop` | Δ is never ownerless |
| `authorization.blast_radius`, `authorization.reversibility` | `schema_case.yaml blast_radius`, `reversibility` | Pre-declared ceiling and reversal path |
| `decision_authority.final_decider` | `schema_case.yaml final_decider`, axioms A3 | Always human |
| `decision_authority.loop` | `policies.yaml ai_extension.loops` | Which loop the crossing acts on |
| `decision_authority.escalation.halt_owner` | `policies.yaml haltability` | Who can halt |
| `continuity_claim.boundary.responsibility_boundary` | `catalog/boundaries` (B1–B17) | Type of responsibility boundary, if any |

## 5.2 Detailed rules

### Guard verdict
**VCDesign:** A verdict is not a decision. Unknown stops, is exposed, and is escalated; it is never pass.
**CCP:** ACCEPT is `pass`. REJECT is `deny` (with reason) or `unknown` (escalated to `escalation.on_unknown`). `Claim: Silence` is `unknown`.
**Rule:** CCP must not treat silence or unknown as pass.

### Containment and basis_flow
**VCDesign:** Failures are stopped by default; basis and residual assets pass by default. This is the asymmetry of the boundary.
**CCP:** `containment.propagation` defaults to `deny`; `basis_flow.default` defaults to `allow`. The reason of a deny flows as basis.
**Rule:** CCP must not reverse these defaults without stating so in the signed `boundary_policy`.

### Revalidation
**VCDesign:** Upstream conclusions are revalidated, not inherited.
**CCP:** `revalidation.upstream_trust` defaults to `none`; precondition, evidence freshness and authority are re-checked at ACCEPT.
**Rule:** A signature proves who said it, not that it still holds.

### Decision authority
**VCDesign:** Decisions are closed by a human final decider; a closed decision authorizes a scope through its declaration (axioms A2, A3).
**CCP:** `decision_authority.authorization` carries the decision, its reference, the human who closed it, and its declaration.
**Rule:** CCP must not present an AI as final decider, and must not let a crossing exceed the authorized scope.

### Δ
**VCDesign:** A confirmed Δ remains under responsibility until closed by a decision. Positive Δ is observed and held, never halted.
**CCP:** Every Δ returned in REVERSE or transferred in the connection names its holder.
**Rule:** CCP must not change the meaning of Δ, and must not make a Δ ownerless.

---

# 6. Non-Mapping (Areas not mapped)

The following have **no counterpart** in Value Continuity or VCDesign. They exist only in the technical layer of CCP.

- signature_schema (Cryptographic Layer)
- canonicalization (Normalization)
- nonce / timestamp / expires_at (Time)
- cost_model (Computational Resources)
- participants (AI Identifiers)

---

# 7. Integration Rules

The following are **mandatory rules**.

1. CCP must not redefine Value Continuity, the Value Asymmetry Principle, the five principles or Decision.
2. CCP must not redefine VCDesign terms; it uses them with the same meaning.
3. CCP must not add decision vocabulary.
4. The technical layer of CCP (signature, normalization, nonce, cost) carries no value meaning.
5. The final decider of every authorization is human.
6. Unknown is never pass.

The most important rule is: **losses do not cross, basis crosses, and a human decides how far.**

---

# 8. Legacy (2.1) Terms

CCP 2.1 mapped to VCDesign v1 concepts that VCDesign v2 has retired. Read them as follows.

| 2.1 mapping | 3.0 |
|-------------|-----|
| Chapter (Membrane) → `continuity_claim.boundary_def` | `continuity_claim.boundary` + `declaration` |
| Boundary → `world.id` | `world` (declared boundary) |
| BOA (Meaning / Responsibility / Execution) → `decision_authority.domain` | `decision_authority.loop` |
| RC (Δ and R) → `resolution_policy` | `boundary_policy` (delta.holder, containment, basis_flow) |
| DCS (Mid-stream Reversal) → `reversal_signal` | `reversal_signal` on guard verdicts, broken precondition, exceeded blast radius, revoked authority |
| IDG (Determinability) → `trust.validation_level` | guard determinability; `trust.validation_level` as its input |

See the migration table in `README.md` for field-level changes.

---

# 9. Versioning

- Value Continuity is versioned independently
- VCDesign is versioned independently (this mapping targets VCDesign v2.0)
- CCP depends on Value Continuity and refers to VCDesign, but changes neither
- This Mapping follows the version of CCP (CCP 3.0)

---

# 10. License

MIT License
© VCDesign Project
