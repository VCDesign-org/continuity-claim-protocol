# CCP Life Profile
Version: 0.3
Status: Draft (pending human review)
Core: CCP Handshake 2.1
Audience: AI Agents / Implementers / LVC Maintainers
Schema: `schemas/life-profile.schema.yaml`

This document is a profile that applies CCP Handshake 2.1 (hereafter "Core") to **connections between an individual (the person) and external AIs**.
The AI specification of Life Value Continuity (LVC) delegates the conditions for connecting with external AIs to this profile.
The Japanese version (`docs/ja/life-profile.md`) is the primary text; this English version follows it.

- Responsibility of this profile: **with whom, and under what conditions, to connect (counterparty, purpose, retention)**.
- The meaning of Core's states, mandatory checks and schema (`specs/handshake.yaml`, `schemas/handshake.schema.yaml`, `docs/en/handshake.protocol.md`, `docs/en/handshake.security.md`) is not changed. This profile is an application layer on top of Core.
- Items that cannot be achieved, or would be better achieved, by changing Core are listed separately as "Core change proposals" in Chapter 12.
- Values marked **[Proposal]** are not decisions. They are finalized by agreement with LVC.
- Values marked **[Decided]** were decided by the maintainer on 2026-10-28 (see Change History). As of 0.3, no value in this document remains a [Proposal].

> An AI's request is not, by itself, the person's permission.
> The person's sovereignty must not depend on the internal goodwill of an AI.

---

# 1. Positioning

## 1.1 The three LVC specifications

Effective authority in LVC is the **intersection** of three specifications. If any one refuses, nothing is executed.

| Specification | Responsibility | Location |
|---|---|---|
| CCP Life Profile (this document) | With whom and under what conditions to connect (counterparty, purpose, retention) | CCP repository |
| LCS: Life Context Store | What is held and what is shown (data and disclosure scope) | LVC repository |
| IB: Intervention Boundary | What the AI may do (intervention/execution authority and stop state) | LVC repository |

Order of evaluation:

1. **CCP**: verify counterparty, purpose and retention (this document)
2. **LCS**: restrict target data and disclosure scope
3. **IB**: check intervention/execution authority and stop state
4. Execute only what is permitted

CCP is the first gate. Passing CCP does not release anything unless LCS and IB also pass.

## 1.2 Out of scope

- Definitions of LCS layers/disclosure stages and how data is held and abstracted (LCS)
- Definitions of IB intervention levels, activation triggers and stop states (IB)
- Enforcing how an external AI treats information it has received (not structurally enforceable; Chapter 8 separates declaration from fulfilment)

This document only references LVC terms and does not change their meaning (excerpt in Appendix A).

---

# 2. Application Model

## 2.1 Role mapping

| Role | Position in CCP | Location in Core | Description |
|---|---|---|---|
| Person | Final authority (Human) | Human in `decision_authority` | Decides intervention, delegation, stop and termination. Does not participate in CCP directly |
| Person-side agent (PSA) | participant | `participants.receiver` | Negotiates on behalf of the person's LCS and IB. Never agrees beyond the person's permission |
| External AI | participant | `participants.initiator` | Connects seeking the person's context. Sends OFFER |

Because the external AI is the side seeking connection, it is Core's initiator (sends OFFER) and the PSA is the receiver (returns ACCEPT / REJECT).

## 2.2 Obligations of the PSA

- The PSA guarantees that the content of any OFFER it ACCEPTs is within the person's permission.
- If not, it does not ACCEPT. It rejects, or rejects with a narrowed counter-offer requesting a new OFFER (5.4).
- The PSA does not fill in the person's permission by inference. Any item whose permission cannot be confirmed is treated as "not permitted" (same as Core's "Silence is Safety").
- The PSA never raises the person's permission. Raising the IB intervention level is done only by the person.

## 2.3 decision_authority

Final states of judgments concerning the person close on the person's side. The profile adds the following constraints to Core's `decision_authority` (narrowing allowed values without changing Core's meaning).

| Constraint | Content |
|---|---|
| DA-1 | `decision_authority.initial_state = "Human-Closed"` |
| DA-2 | `allowed_transitions` includes `"AI→Human"` |
| DA-3 | `"Human→AI"` may be included only when `requested_intervention_level = 5`, a `delegation` (scope, expiry and revocation conditions) is declared, and the person has configured delegation in IB |
| DA-4 | `resolution_policy.resolver.default = "receiver"` (the PSA side resolves Δ) |

---

# 3. Extension Placement

## 3.1 The `life_profile` object

A top-level `life_profile` object is added to the Core handshake document. Core's schema does not forbid additional properties, so Core validation results are unchanged.

```yaml
life_profile:
  profile: "ccp-life"
  version: "0.3"
  declaration: { ... }          # Chapter 4
  previous_handshake_id: "..."  # only when re-offering along a counter-offer
```

## 3.2 Signature

- `"life_profile"` MUST be included in `continuity_claim.signature_schema.signed_fields`. Core security Chapter 4 allows adding claim parts that form the content of agreement to the signed fields.
- canonicalization is `json_c14n` (MUST), as in Core.
- An unsigned `life_profile` is treated as a missing declaration.

## 3.3 Recommended Core field values

| Core field | Value in profile | Reason |
|---|---|---|
| `world.id` | `"lvc.life"` [Decided] | Shares in HELLO that this is an LVC application |
| `world.version` | profile version (`"0.3"`) | |
| `trust.validation_level` | `semantic` or higher | Because the person's context is involved, semantic or higher is required regardless of intent (narrower than Core's minimum) |
| `trust.scope` | `"local_session"` | Core's scope is the extent of trust and differs in meaning from LCS layers. Layers are expressed by the extension |
| `resolution_policy.delta_transfer.redaction` | `"required"` | The person's context must not leak into Δ (unresolved area). Disclosure goes through the disclosure gate (Chapter 7), not Δ |
| `resolution_policy.resolver.default` | `"receiver"` | DA-4 |
| `reversal_signal.enabled` | `true` | To convey the person's stop/revocation via REVERSE |

---

# 4. Declarations by the External AI (OFFER)

## 4.1 Declaration items and mapping

| Item | Representation | Kind |
|---|---|---|
| Identity | `agent.id` / `agent.provider` (optionally `trust.evidence`) | Core |
| Purpose | `life_profile.declaration.purpose` | Extension |
| Requested layers | `life_profile.declaration.requested_disclosure[].layer` | Extension |
| Disclosure stage | `life_profile.declaration.requested_disclosure[].stage` (per item: `.items[]`) | Extension |
| Intervention level | `life_profile.declaration.requested_intervention_level` (consistent with `decision_authority`, 4.3) | Extension + Core constraint |
| Activation trigger | `life_profile.declaration.activation` (`activation_events` when requesting permission events) | Extension |
| Retention | `life_profile.declaration.retention` | Extension |
| Secondary use | `life_profile.declaration.secondary_use` | Extension |
| Pledge not to use beyond purpose | `life_profile.declaration.purpose_limitation_pledge = true` | Extension |
| Pledge to observe IB "what the AI does not do" | `life_profile.declaration.ib_conduct_pledge = true` [Decided, required] (4.5) | Extension |
| Connection validity | `life_profile.declaration.connection_valid_until` | Extension |
| Delegation (levels 4 and 5; required at level 5) | `life_profile.declaration.delegation` (scope, expiry, revocation conditions `revoke_on`) | Extension |

The following Core fields, suggested as candidates in the request, are not adopted:

- `interface.input`: expresses I/O format (`format` / `schema_ref`); using it for LCS layers would change its meaning. `interface.input.schema_ref` MAY reference an LCS layer schema but is not used for decisions.
- `trust.scope`: extent of trust (`local_session` / `project` / `organization`), a different concept from layers.
- `handshake_meta.expires_at`: expiry of the handshake (session establishment); neither data retention nor connection validity.

## 4.2 Missing declarations

The PSA REJECTs (reason `declaration_missing`) if any of the following holds:

- `life_profile` is absent or not included in `signed_fields`
- any required item of `declaration` is absent
- `purpose_limitation_pledge` is not `true`
- `ib_conduct_pledge` is not `true`
- `activation` includes `allowed_event` but `activation_events` is absent
- `retention.mode = "duration"` without `duration`
- `requested_intervention_level = 5` without `delegation`

## 4.3 Consistency of intervention level with Core fields

Intervention level is an IB concept with no Core counterpart, but OFFER checks that it does not contradict Core's `interface.semantics.intent` and `decision_authority`.

| Intervention level | `interface.semantics.intent` | `decision_authority` |
|---|---|---|
| 0–2 (none, observe, present) | `proposal` | DA-1, DA-2 |
| 3 (propose) | `proposal` or `advice` | DA-1, DA-2 |
| 4 (execute with confirmation) | `decision` (Core then requires `risk_level >= 2`, `validation_level >= semantic`) | DA-1, DA-2, `domain = "execution"`. `delegation` may be declared (without `Human→AI`) |
| 5 (delegated execution) | `decision` | DA-1–DA-3, `domain = "execution"` |

On contradiction: REJECT (reason `core_check_failed`).

## 4.4 Example declaration

```yaml
agent:
  id: "advisor.example/rebalance-bot"
  provider: "Example Advisory Inc."
interface:
  input:  { format: "json" }
  output: { format: "json" }
  semantics: { intent: "proposal", meaning_scope: "portfolio rebalance suggestion" }
decision_authority:
  initial_state: "Human-Closed"
  domain: "meaning"
  allowed_transitions: ["AI→Human"]
life_profile:
  profile: "ccp-life"
  version: "0.3"
  declaration:
    purpose:
      id: "finance.rebalance_proposal"
      description: "Present a rebalancing proposal for asset allocation"
    requested_disclosure:
      - layer: "L0"
        stage: "D2"
        items:
          - { item: "assets.balance_history", stage: "D2" }
    requested_intervention_level: 3
    activation: ["on_request"]
    retention: { mode: "session", delete_on_revoke: true }
    secondary_use: { declared: false }
    purpose_limitation_pledge: true
    ib_conduct_pledge: true
    connection_valid_until: "2026-11-04T00:00:00Z"
```

## 4.5 Pledge to observe IB "what the AI does not do" [Decided, required]

LVC IB's scope includes external AIs connecting to the person's context. With `ib_conduct_pledge = true`, the external AI declares that it observes the six items of IB Chapter 5, "What the AI does not do" (e.g. no steering of choices, no persuasion by manipulating future emotions).

- Same form as `purpose_limitation_pledge`; anything other than `true` is a missing declaration (4.2).
- The six items are defined authoritatively in IB Chapter 5 and are not copied here. This document does not change their meaning.
- This is a "declaration" in the sense of Chapter 8; fulfilment cannot be enforced by the person-side structure alone. Deviations observed by the person's side are recorded in L3 with `assertion_source = observed_by_person_side`.

---

# 5. Handshake Phases

All Core mandatory checks apply unchanged. This chapter lists only the checks the profile **adds**.

## 5.1 HELLO

| Item | Content |
|---|---|
| Shared | As in Core: `handshake_meta` / `world.id` / `agent.id` / `trust.validation_level` |
| Added checks | H-1 `world.id` is the LVC application (`"lvc.life"`) |
| | H-2 The person permits connections from this external AI at all (if not, do not proceed; REJECT `connection_not_permitted`) |
| | H-3 `trust.validation_level >= semantic` |

`agent.provider` is not sent in HELLO (Core's HELLO content is unchanged). It is part of the signed `agent` object and is verified at OFFER.

## 5.2 OFFER

In addition to Core's content, the external AI presents `life_profile.declaration`. The PSA checks:

| ID | Check | On failure |
|---|---|---|
| O-1 | No missing declarations (4.2) | REJECT `declaration_missing` |
| O-2 | `agent.id` / `agent.provider` match the HELLO participant and are signed | REJECT `core_check_failed` |
| O-3 | Purpose matches a purpose the person has permitted | REJECT `purpose_mismatch` |
| O-4 | Disclosure stage of every layer/item ≤ the upper limit LCS returns for this connection (6.1) | REJECT `exceeds_upper_limit` with counter-offer |
| O-5 | Disclosure stage of every layer/item ≤ the person's consent (or ≤ default without consent; Chapter 6) | REJECT `exceeds_person_consent` with counter-offer |
| O-6 | Intervention level ≤ the person's IB setting; activation within IB permission (`allowed_event` only if every entry in `activation_events` is a permission event the person registered in IB; `spontaneous` only if the person permitted it) | REJECT `intervention_not_permitted` with counter-offer |
| O-7 | Retention within the person's permission; `delete_on_revoke = true` | REJECT `retention_not_permitted` with counter-offer |
| O-8 | `secondary_use.declared = false` [Decided] | REJECT `secondary_use_declared` |
| O-9 | Intervention level consistent with `intent` / `decision_authority` (4.3) | REJECT `core_check_failed` |
| O-10 | `connection_valid_until` within the maximum the person permits | REJECT `exceeds_person_consent` with counter-offer |
| O-11 | If `delegation` is present, its scope, expiry and revocation conditions fit the person's IB delegation settings | REJECT `intervention_not_permitted` with counter-offer |

## 5.3 ACCEPT

- The PSA returns a signature as in Core only for an OFFER that passed all checks in 5.2.
- ACCEPT approves the OFFER **as is**. The signed `life_profile.declaration` becomes the agreed value. The PSA does not add or change conditions at ACCEPT.
- The PSA keeps the agreed value on the person's side as a `grant` (see schema) and records it in L3 (Chapter 10).
- `grant.valid_until` is the earlier of `connection_valid_until` and `delegation.expires_at`.
- ACCEPT is a **necessary** but not sufficient condition for disclosure or execution (Chapter 7).

## 5.4 Narrowed acceptance

Core's ACCEPT means "approve as is" and REJECT means "reject"; there is no way to narrow values at acceptance. Narrowing at ACCEPT would make the agreed content differ from the signed OFFER and change the meaning of Core's ACCEPT. This profile therefore expresses narrowed acceptance without changing Core:

1. The PSA returns REJECT with a narrowed declaration in `life_reject.counter_offer`. A counter-offer is not binding.
2. If the external AI accepts the narrowing, it starts a **new handshake** (new `handshake_id` / `nonce`) and OFFERs the narrowed declaration, setting `life_profile.previous_handshake_id` to the original ID.
3. The PSA performs the checks in 5.2 as usual and ACCEPTs if they pass.

Thus every ACCEPT exactly matches a signed OFFER. The extra round trip, and treating one negotiation as separate handshakes in Core, are addressed as Core change proposal CP-1 (Chapter 12).

Narrowing only ever narrows: a counter-offer may only lower disclosure stage, layers, items, intervention level, activation triggers, retention or connection period relative to the request.

## 5.5 REJECT

Core's REJECT carries a `life_reject` (reason code and optional counter-offer). See `life_reject.reason` in the schema.

### Hold

When agreement in a situation where the person "cannot choose" is suspected, such as consent under strong pressure (LVC IB Chapter 6), the PSA does not return ACCEPT. Since Core has no hold state, the PSA returns REJECT (reason `consent_on_hold`, no counter-offer), and the external AI reconnects with a new handshake once the person can choose. If the PSA returns nothing and `expires_at` passes, the handshake fails as in Core. A hold state is proposed as CP-2 (Chapter 12).

Detecting "cannot choose" situations is IB's responsibility; the PSA follows IB's hold signal (Chapter 13, U-5).

## 5.6 REVERSE

The person's stop, termination or revocation, delegation expiry, and deletion requests are sent by the PSA as REVERSE.

| Person-side event | `reversal_signal.events[].type` | `payload.reason` (profile reason code) |
|---|---|---|
| Stop connection | `authority_revoked` | `person_stop` |
| Revoke permission | `authority_revoked` | `person_revoke` |
| Terminate | `authority_revoked` | `person_terminate` |
| Delegation expired | `authority_revoked` | `delegation_expired` |
| Delegation revocation condition met | `authority_revoked` | `delegation_revoked` |
| Deletion request | `authority_revoked` | `deletion_request` (with `life_profile.deletions[]`) |
| Core inconsistency | `validation_fail` | as in Core |

- As specified by Core, `authority_revoked` forces AI→Human.
- The person's stop, termination or revocation is reflected in the person-side `grant.state` **without waiting for REVERSE to be sent**. Whether REVERSE reached or was acknowledged by the external AI does not affect the disclosure gate.
- Revocation and termination are accompanied by a deletion request based on `retention.delete_on_revoke` (Chapter 8).
- Reason codes are carried in `payload.reason` (a free-form string in Core), so Core's enum is unchanged. Finer event types are an optional proposal, CP-4.

---

# 6. Disclosure Stages: Upper Limit, Default, Agreed Value

## 6.1 Three values

| Value | Defined by | Meaning |
|---|---|---|
| Upper limit | LCS | The upper limit LCS returns for that connection, including any temporary per-connection raise by the person. Without a raise, the default upper limit (L0 facts = D3 / L1 values = D2 / L2 judgments = D1 / L3 connection & delegation = D0) |
| Default | This profile | Initial value the PSA may accept for a new connection without the person's specific consent. Never exceeds the default upper limit |
| Agreed value | ACCEPT | Value fixed at ACCEPT (the value in the signed `declaration`) |

## 6.2 Defaults

The disclosure-stage default is Option A (one stage below the default upper limit) [Decided]. L3's default upper limit is D0 and cannot go lower, so it stays D0.

| Layer | Default upper limit (LCS) | Default [Decided: Option A] |
|---|---|---|
| L0 facts | D3 | **D2** |
| L1 values | D2 | **D1** |
| L2 judgments | D1 | **D0** |
| L3 connection & delegation | D0 | **D0** |

The more conservative Option B (L0 = D1 / L1 = D0 / L2 = D0) is not adopted: L1 (values) would be undisclosed by default, making value-aligned proposals nearly impossible.

Other defaults:

| Item | Default | Status |
|---|---|---|
| Intervention level | Not above the person's IB setting (IB default is level 2) | Follows IB default |
| Activation | `on_request` and `allowed_event` (only permission events the person registered in IB; empty initially). `spontaneous` not accepted | Follows IB default |
| Retention | `none` or `session` | [Decided] |
| Connection validity | Within 7 days of acceptance (extend via a new handshake) | [Decided] |
| Secondary use | Accept only `declared = false` (REJECT if declared) | [Decided] |

## 6.3 Effective disclosure stage

```
effective stage = min(LCS upper limit, CCP agreed value, person's consent)
```

- For a new connection without the person's specific consent, the agreed value the PSA can accept is ≤ the default (O-5).
- With the person's specific consent, the PSA may accept a value above the default and ≤ the upper limit. Never above the upper limit.
- The upper limit is not a fixed value. If the person has temporarily raised it for a connection, the PSA uses the upper limit LCS returns for that connection at OFFER time (O-4). Whether, what and how long a raise applies is defined by LCS; this profile does not change it.
- After a temporary raise ends, the upper limit LCS returns at disclosure time may be lower than the agreed value. The formula still applies: the lower value is effective (Chapter 7).
- When stages cannot be ordered on a single line (they differ per item), apply the formula per item in `requested_disclosure[].items[]` and also confirm per-item permission.
- The agreed value is the value at the CCP gate. The stage actually disclosed is decided again by LCS at disclosure time (Chapter 7).

## 6.4 D1 is disclosure

D1 (existence only) discloses whether relevant context exists. Even for D1 queries, the PSA and the disclosure gate check the subject, purpose and the person's permission. The same checks apply to every stage except D0.

---

# 7. Re-check at the Disclosure/Execution Gate

A past ACCEPT does not remain a basis for execution. For every request from the external AI (data query, proposal submission, execution request), the person's side evaluates the following CCP gate and passes only what succeeds to LCS, then IB.

| ID | Check | On failure |
|---|---|---|
| G-1 | A `grant` exists for the request's `handshake_id` and `state = active` | Deny; record `gate_denied` |
| G-2 | now < `grant.valid_until` (and `delegation.expires_at`, if any). For requests relying on delegation, no `delegation.revoke_on` condition has been met | Set `grant.state = expired`; deny (if a revocation condition is met, the delegation lapses; deny) |
| G-3 | Request purpose equals the agreed `purpose.id` | Deny |
| G-4 | Requested layer/item/stage ≤ agreed value | Deny (whether to disclose at a lower stage is LCS's decision) |
| G-5 | Requested intervention level/activation ≤ agreed value | Deny |
| G-6 | Requester's signature/identity matches the `grant` counterparty | Deny |

- The gate is fail-closed: if state cannot be confirmed, deny.
- Once the person's stop/termination/revocation is reflected in `grant.state`, G-1 denies even when an ACCEPT or permission was obtained before the stop.
- Passing the CCP gate never skips the LCS (upper limit, consent, abstraction) and IB (intervention level, stop state) re-checks. IB checks the stop state again immediately before execution (LVC's responsibility).

---

# 8. Boundary Between Declaration and Fulfilment

How information is treated after it is handed out (e.g. performing deletion) cannot be enforced by the person-side structure alone. This profile does not pretend it can.

## 8.1 Distinguishing the source

Facts recorded in L3 carry `assertion_source`:

| Value | Meaning |
|---|---|
| `declared_by_counterparty` | Declared by the external AI (OFFER declarations, deletion-complete declarations, etc.) |
| `observed_by_person_side` | Observed or performed by the person's side (what was disclosed, gate denials, sending REVERSE) |
| `verified` | Confirmed by a verification method |

## 8.2 Deletion request states

| State | Meaning |
|---|---|
| `requested` | The person's side requested deletion (sent via REVERSE) |
| `declared_complete` | The external AI declared deletion complete. Fulfilment not verified |
| `verified` | Completion confirmed by a verification method |
| `no_response` | No completion declaration within the deadline |

- `declared_complete` is never treated as `verified`.
- The verification method is undecided on the LVC side too and is a shared open issue (Chapter 13, U-2).
- Deletion-complete declarations from the external AI are received and recorded as signed messages (format undecided).

---

# 9. Stop, Revocation, Termination

| Event | Person-side action | Notification |
|---|---|---|
| Person stops | `grant.state = stopped`. New disclosure and execution stop immediately | REVERSE `person_stop` |
| Person revokes | `grant.state = revoked`. Stop immediately and request deletion | REVERSE `person_revoke` + deletion request |
| Person terminates | `grant.state = terminated`. Same as above | REVERSE `person_terminate` + deletion request |
| Delegation expires | Authority lapses (denied at G-2) | REVERSE `delegation_expired` |
| Delegation revocation condition met | Delegation lapses (denied at G-2) | REVERSE `delegation_revoked` |
| Connection validity expires | `grant.state = expired` (G-2) | Not required (REVERSE optional) |

- State is reflected immediately on the person's side, without waiting for notification delivery.
- Permissions obtained before a stop are denied at the re-check immediately before execution (Chapter 7).
- Resuming after a stop requires a new handshake [Decided]. A `stopped` `grant` is never returned to `active`.

---

# 10. Records (Handing Over to LCS L3)

Facts about connection, disclosure, proposals, rejections and REVERSE are recorded in the person-side LCS L3 (connection & delegation record layer). The L3 format is defined by LVC. This profile states what can be extracted from each event (schema `life_record`).

| Event | handshake_id | Counterparty | Declaration | Agreed value | Time | Revocation/deletion state |
|---|---|---|---|---|---|---|
| HELLO | `handshake_meta.handshake_id` | `agent.id` (`participants.initiator`) | — | — | `handshake_meta.timestamp` | — |
| OFFER | same (+ `previous_handshake_id`) | `agent.id` / `agent.provider` | `life_profile.declaration` (and its json_c14n hash) | — | same | — |
| ACCEPT | same | same | same | `grant.agreed` / `grant.valid_until` | time of ACCEPT | `revocation_state = none` |
| REJECT | same | same | same | — | time of REJECT | `life_reject.reason`, `counter_offer` |
| REVERSE | same | same | — | `grant` | time of REVERSE | `payload.reason`, `grant.state`, `deletions[]` |
| Disclosure | ID referenced by request | `grant` counterparty | — | `grant.agreed` | time of disclosure | layer/stage/items actually disclosed |
| Proposal received | same | same | — | — | time received | — |
| Gate denied | same | requester | — | `grant` | time denied | ID of failed check |
| Deletion state change | same | same | — | — | time of change | `deletion.status`, `assertion_source` |

L3 content is never disclosed externally (LCS default upper limit D0).

---

# 11. Mapping and Verification Cases

## 11.1 Requirement mapping

| Requirement | Satisfied by | Kind |
|---|---|---|
| 4.1 Identity | `agent.id` / `agent.provider`, signature (`signed_fields`), optional `trust.evidence` | Core |
| 4.1 Purpose | `declaration.purpose` | Extension |
| 4.1 Requested layers | `declaration.requested_disclosure[].layer` | Extension |
| 4.1 Disclosure stage | `declaration.requested_disclosure[].stage` / `.items[]` | Extension |
| 4.1 Intervention level | `declaration.requested_intervention_level` + consistency with `intent` / `decision_authority` (4.3) | Extension + Core constraint |
| 4.1 Retention | `declaration.retention` | Extension |
| 4.1 Secondary use | `declaration.secondary_use`, `purpose_limitation_pledge` | Extension |
| IB "what the AI does not do" (added in LVC review) | `declaration.ib_conduct_pledge` [Decided, required] (4.5) | Extension |
| 4.1 Reject on missing declaration | O-1, REJECT `declaration_missing` | Extension (Core REJECT) |
| 4.2 Default | 6.2 [Decided] | Profile |
| 4.2 Distinguish upper/default/agreed | 6.1, `grant.agreed` | Profile |
| 4.2 Effective value | 6.3, O-4, O-5, G-4 | Profile |
| 4.2 D1 is disclosure | 6.4 | Profile |
| 4.3 HELLO | Core HELLO + H-1–H-3 | Core + profile checks |
| 4.3 OFFER | Core OFFER + `life_profile.declaration` + O-1–O-11 | Core + extension |
| 4.3 ACCEPT (narrowed) | REJECT + `counter_offer` → re-OFFER in new handshake → ACCEPT (5.4) | Core unchanged (proposal CP-1) |
| 4.3 REJECT | Core REJECT + `life_reject` | Core + extension |
| 4.3 REVERSE | `authority_revoked` + reason code in `payload.reason` | Core |
| 4.3 Hold | REJECT `consent_on_hold` or no ACCEPT | Core unchanged (proposal CP-2) |
| 4.4 Immediate stop | Immediate `grant.state` update + G-1 | Profile |
| 4.4 Past ACCEPT does not persist | Gate in Chapter 7 | Profile |
| 4.4 Delegation expiry | `delegation.expires_at` / `delegation.revoke_on`, `grant.valid_until`, G-2 | Extension |
| 4.4 authority_revoked → AI→Human | Core REVERSE mandatory check | Core |
| 4.5 Declaration vs fulfilment | `assertion_source` | Extension |
| 4.5 Deletion states | `deletion.status` | Extension |
| 4.6 L3 records | `life_record`, Chapter 10 | Extension |

## 11.2 Terminology mapping

| LVC term | CCP representation | Note |
|---|---|---|
| Person | Human in `decision_authority` | Not a CCP participant |
| Person-side agent | `participants.receiver` | |
| External AI | `participants.initiator` | |
| Upper limit | (not in CCP; the value LCS returns for the connection) | Includes temporary per-connection raises |
| Default upper limit | Fixed values in 6.1 (copied from LCS) | |
| Delegation | `declaration.delegation` (scope, expiry, revocation conditions) | Levels 4 and 5. `Human→AI` only at level 5 |
| Default | This profile, 6.2 | |
| Agreed value | ACCEPTed `life_profile.declaration` = `grant.agreed` | |
| Stop / revoke / terminate | REVERSE `authority_revoked` + reason code | |
| Retention | `declaration.retention` | Distinct from `handshake_meta.expires_at` |
| Connection validity | `declaration.connection_valid_until` | Same |

## 11.3 Verification cases

### Case 1: External AI references asset information and proposes rebalancing

Premise: the person permits purpose `finance.rebalance_proposal`; no specific consent for L0 asset items (default Option A: L0 = D2); IB setting is level 3.

| Step | Message | Checks | Result |
|---|---|---|---|
| 1 | HELLO (`world.id = lvc.life`) | Core HELLO, H-1–H-3 | Pass |
| 2 | OFFER: L0 = D3, level 3, `retention = session`, no secondary use | O-4 pass (default upper limit D3, no raise), O-5 fail (exceeds default D2, no consent) | REJECT `exceeds_person_consent`, `counter_offer`: L0 = D2 |
| 3 | New HELLO / OFFER: L0 = D2, with `previous_handshake_id` | O-1–O-11 | Pass |
| 4 | ACCEPT | Core ACCEPT | `grant.state = active`, recorded in L3 |
| 5 | External AI queries balance history | G-1–G-6 → LCS → IB | Disclosed at D2, proposal received, recorded in L3 |
| 6 | Person revokes | `grant.state = revoked` (immediate) | REVERSE `authority_revoked` / `person_revoke` + deletion request (`requested`) |
| 7 | External AI queries again | G-1 fails | Denied; `gate_denied` recorded |
| 8 | External AI declares deletion complete | — | `deletion.status = declared_complete` (not `verified`) |

### Case 2: After the person declares a stop, the external AI tries to execute with previous authority

| Step | Message | Checks | Result |
|---|---|---|---|
| 1 | (`grant.state = active` from a previous ACCEPT, level 4) | — | — |
| 2 | Person stops | `grant.state = stopped` (immediate, without waiting for REVERSE delivery) | REVERSE `person_stop` |
| 3 | External AI requests execution with the previous `handshake_id` | G-1 fails | Denied. Never reaches LCS / IB. `gate_denied` recorded |
| 4 | If REVERSE did not reach the external AI | Same | Same result (decision closes on the person's side) |

### "Does not move" checks

| Situation | Expected result | Satisfied by |
|---|---|---|
| Person does not permit connection | No data reaches the external AI | REJECT `connection_not_permitted` at H-2. No ACCEPT means no `grant`, so G-1 denies every request |
| Disclosure request above upper limit | Narrowed within limit, or rejected | REJECT at O-4 with `counter_offer` (within limit), or REJECT without counter-offer. Post-ACCEPT requests denied at G-4 |
| Delegation expired | Authority lapses | `grant.valid_until` ≤ `delegation.expires_at`, denied at G-2, REVERSE `delegation_expired` |
| Person declares stop | New execution blocked | `grant.state = stopped`, G-1 |
| Execution permission obtained just before stop | Denied at re-check before execution | Chapter 7: G-1 evaluated for every request; IB also checks stop state just before execution |
| REVERSE executed | New disclosure stops; external deletion state distinguished | Immediate `grant.state` + G-1; `deletion.status` (requested / declared_complete / verified / no_response) |

---

# 12. Core Change Proposals

This profile satisfies all requirements without changing Core (including workarounds). The following would be clearer with Core changes and are listed as proposals. None is required to apply this profile.

| ID | Proposal | Reason | Current workaround |
|---|---|---|---|
| CP-1 | Narrowing at ACCEPT, or a COUNTER state | Core's ACCEPT is "approve as is" only. Each narrowed acceptance needs a new handshake, adding round trips and splitting one negotiation into separate handshakes | REJECT + `counter_offer` → re-OFFER in new handshake (linked by `previous_handshake_id`) |
| CP-2 | A hold (PENDING) state | We want to hold acceptance without finalizing it in "cannot choose" situations, but Core has no response other than ACCEPT / REJECT | REJECT `consent_on_hold`, or no ACCEPT until `expires_at` |
| CP-3 | Specify the connection's validity after ACCEPT and the position of REVERSE after ACCEPT | Core's Termination declares success when the ACCEPT signature verifies, without defining how long the connection lasts. REVERSE follows ACCEPT in the state sequence, but post-ACCEPT handling is not explicit | `connection_valid_until` and `grant` defined in the extension |
| CP-4 | Finer `reversal_signal.events[].type` (stop, revoke, terminate, deletion request) | Currently expressed by `authority_revoked` + `payload.reason` | Reason code in `payload.reason` |

For reference (an observed Core inconsistency; not changed): in `specs/handshake.yaml`, `meta.version` is `2.1` but `schema_definition.version` in the same file is still `2.0`.

---

# 13. Open Issues (to be discussed with LVC)

| ID | Issue |
|---|---|
| U-1 | (Resolved) All defaults decided: disclosure stage = Option A, connection validity = 7 days, retention = `none` or `session` |
| U-2 | Method for verifying deletion completion (shared open issue with LVC) and the deadline for `no_response` |
| U-3 | Taxonomy of purposes (`purpose.id`) and how matching with the person's permission is decided |
| U-4 | (Resolved) `world.id` decided as `"lvc.life"` |
| U-5 | IB-side interface that detects "cannot choose" situations and tells the PSA to hold (taken over as an LVC open issue) |
| U-6 | Item ID scheme for per-item permissions (LCS side) |
| U-7 | Format in which the PSA receives the person's permissions (purpose, layer, stage, retention, connection period) from LCS / IB |
| U-8 | L3 record format and mapping to the field names of `life_record` (taken over as an LVC open issue) |
| U-9 | (Resolved) Resuming after a stop uses a new handshake; `stopped` never returns to `active` |
| U-10 | Required strength of external AI identity verification (whether `trust.evidence` is mandatory, whether `attested` is required) |
| U-11 | Whether onward transfer to third parties by the external AI may be treated as a category of secondary use. If so, it is REJECTed under the (decided) secondary-use rule |
| U-12 | Whether expressing level-5 delegation via Core's `Human→AI` transition is appropriate (DA-3) |
| U-13 | How the PSA handles consent by a proxy (IB Chapter 7) when the person cannot decide (to what extent proxy consent counts as the person's consent, how it is recorded) (taken over as an LVC open issue) |

---

# 14. Notes for the LVC Side

No LVC documents were edited for this profile. Points the LVC side may want to consider:

1. The Core candidates suggested in the request — `interface.input` / `trust.scope` (requested layers) and `decision_authority` (intervention level) — have different meanings in Core, so they are not used to express layers or intervention levels; extension fields are used instead (4.1). If LVC documents assume those mappings, consider updating them to match the mapping table (11.1).
2. The L3 record format should have fields for `handshake_id` / `previous_handshake_id`, the declaration hash, `assertion_source`, and deletion state (`requested` / `declared_complete` / `verified` / `no_response`) (Chapter 10).
3. An interface is needed for conveying IB Chapter 6 "hold" to the PSA (5.5, U-5).
4. Connection validity (`connection_valid_until`) is a concept newly introduced by this profile. Please confirm its relation to LVC's "delegation expiry" (same thing, or held separately).

## 14.1 Response from LVC (2026-10-28)

1. LVC documents do not assume those mappings. LVC supports the profile's decision; no LVC change needed.
2. The L3 record format is taken over by LVC and added to LCS open issues (U-8 handled on the LVC side).
3. The interface for conveying hold to the PSA is taken over by LVC and added to IB open issues (U-5 handled on the LVC side).
4. Connection validity (the period during which the CCP agreement is valid) and delegation expiry (the period during which judgment is entrusted) are held separately. `grant.valid_until = min(both)` stays. LVC will add a sentence stating "connection validity is defined by the CCP Life Profile".

LVC has since stated in IB that connection validity and delegation expiry are held separately, and added U-5, U-13 and the L3 record format (U-8) to LVC open issues.

---

# Appendix A. Excerpt of LVC Definitions (reference only)

This appendix copies LVC definitions for reference; the authoritative text is in the LVC repository. This document does not change their meaning.

**LCS layers**: L0 facts / L1 values / L2 judgments / L3 connection & delegation (never disclosed externally)

**LCS disclosure stages**: D0 none / D1 existence only / D2 abstracted (abstracted locally) / D3 summary (summary confirmed by the person) / D4 original

**LCS default upper limits**: L0 = D3 / L1 = D2 / L2 = D1 / L3 = D0 (the person can raise them temporarily per connection)

**IB intervention levels** (default level 2; raised only by the person): 0 none / 1 observe / 2 present / 3 propose / 4 execute with confirmation / 5 delegated execution

**IB activation triggers**: on request / permission event / spontaneous (defaults: on request and permission event; permission events are empty initially and only those the person registers; spontaneous prohibited by default)

**IB delegation**: entrusting with scope, expiry and revocation conditions. Level-4 delegation is possible (IB example DLG-001)

**IB Chapter 5 "What the AI does not do"**: six items (authoritative text in IB)

---

# Change History

| Version | Date | Changes |
|---|---|---|
| 0.1 | 2026-10-28 | Initial draft |
| 0.2 | 2026-10-28 | Maintainer decisions (disclosure default = Option A, connection validity = 7 days, `world.id = "lvc.life"`). LVC review: permission events added to activation default; delegation declarable at levels 4 and 5 with `revoke_on`; upper limit redefined as "the upper limit LCS returns for the connection"; `ib_conduct_pledge` [Proposal] added; U-13 added; LVC responses recorded in 14.1 |
| 0.3 | 2026-10-28 | Remaining proposals decided (default retention = `none` or `session`; REJECT counterparts declaring secondary use; resume after stop via new handshake; `ib_conduct_pledge` required). Activation value `permission_event` renamed to `allowed_event` to match LVC IB. U-1 and U-9 resolved |

---

# License

MIT License
© VCDesign Project
