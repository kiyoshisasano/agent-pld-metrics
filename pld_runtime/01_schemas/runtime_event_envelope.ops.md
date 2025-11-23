version: "2.0.0"
status: "Exploratory — Candidate for Stabilization"
authority_level_scope: "Level 5 — runtime implementation (operational layer)"
purpose: "Provide runtime operational guidance for systems emitting, validating, transporting, and observing PLD runtime events."
change_classification: "extracted + normalized guidance from prior operational notes"
feedback_status: "Actively seeking implementation feedback before stabilization"

---

# PLD Runtime Envelope — Operational Guidance  
*(Exploratory Candidate — Not Final)*

This document provides **operational guidance** for teams implementing or integrating the PLD Runtime Event Envelope.  
It is **not a normative specification** and does not override Level 1–3 rules.  
Instead, it reflects current understanding of best practices for validation, ingestion, and observability in runtime systems.

> This document will evolve based on feedback, implementation testing, and real-world telemetry.

---

## 1. Role of the Runtime Envelope

The Runtime Envelope exists to:

- Carry a **single PLD runtime event**
- Preserve runtime execution context (environment, tooling, trace metadata)
- Support routing, debugging, and observability without altering PLD semantics
- Maintain separation between:
  - **semantic PLD event**
  - **operational metadata**

The envelope does **not** redefine the meaning of the PLD event.  
Semantic interpretation remains governed by:

- `pld_event.schema.json` (Level 1)
- Event Matrix + Semantics Spec (Level 2)
- Runtime Standard (Level 3)

---

## 2. Enforcement Responsibilities

The schema ensures structural correctness only.  
Runtime systems MUST perform additional enforcement.

| Category | Mechanism |
|---------|-----------|
| Schema compliance | JSON Schema validation |
| Semantic compliance | PLD event semantics |
| Runtime rule enforcement | Application-layer logic |

### Required Runtime Rules (Soft Governance Format)

- `session_id` consistency MUST be enforced:

```
event.session_id == envelope.session_id (or equivalent runtime correlate)
```


- Unknown or implementation-specific envelope fields SHOULD NOT modify or overwrite canonical PLD fields.
- Envelope validation SHOULD NOT rely solely on JSON Schema engines.

> Rationale: Some required checks (e.g., semantic consistency) cannot be expressed or executed via JSON Schema.

---

## 3. Ordering Guidance

PLD runtime systems may contain multiple ordering signals.  
To avoid misinterpretation:

| Field | Role | Authority |
|-------|------|-----------|
| `turn_sequence` | Canonical ordering for lifecycle computation | MUST use |
| `trace.turn_index` | Debugging and replay support | MUST NOT use for lifecycle meaning |

> If ordering discrepancies appear, **turn_sequence is always the authoritative source**.

---

## 4. Timestamp Interpretation

Two timestamps may exist in practice:

| Timestamp | Meaning | Usage |
|-----------|---------|-------|
| `event.timestamp` | When the semantic state occurred | Primary key for analysis and lifecycle charts |
| Envelope-level timestamp or transport timestamp | When runtime emitted or packaged the event | Operational telemetry / pipeline debugging |

Recommended operational strategy:

- Use `event.timestamp` for all PLD reasoning and metric generation.
- Use envelope timestamp for ingestion latency, retries, or transport analysis.

---

## 5. Runtime Validation Models

Validation strategies vary across environments.  
The following models are common patterns; choice depends on scale and tolerance.

| Model | Description | Suitable For |
|-------|------------|-------------|
| **Strict Mode** | Validate every message fully | High-trust, regulated, or high-risk domains |
| **Sampling Mode** | Validate a percentage of messages | Large throughput or experimentation |
| **Fail-Open + DLQ** | Accept events but route failures for review | Streaming systems requiring resilience |

> Note: Implementations MAY mix models (e.g., strict at batch replay, sampling for live stream).

---

## 6. Failure Handling and Dead Letter Queues (DLQ)

If a DLQ strategy is used, minimal contents SHOULD include:

- `event_id` (if parseable)
- Raw payload (lossless)
- Root cause classification (machine readable)
- Timestamp of failure

This enables reproducibility, auditability, and replay.

---

## 7. Forward Compatibility Behavior

Since envelope and event schemas may evolve at different speeds, systems SHOULD handle unknown or future schema versions gracefully.

Recommended behaviors:

- Warn but do not drop events with **newer schema versions**
- Retain raw message for reprocessing once validators update
- Emit telemetry indicating forward schema encounter frequency

---

## 8. Operational Recommendations Summary

- **Use turn_sequence → not trace index** for lifecycle meaning  
- **Do not overwrite canonical PLD fields with runtime metadata**
- **Store metric staging in `runtime.*` (Level 5 scope) when needed**
- **Validate semantics in runtime logic — not only schema**
- **Plan for version drift and replay requirements**

---

## 9. Future Work (Open / Not Binding)

These areas remain under evaluation:

- Standardizing telemetry formats for runtime observability
- Optional recommended runtime keys (latency patterns, resource hints)
- Version negotiation strategy across distributed systems

Status: *Unresolved / Seeking implementation data*

---

## Feedback Channel

This document is intentionally open-ended.  
Feedback from real implementations is requested.

Suggested forms of feedback:

- Logs or examples where current guidance was unclear
- Operational failure patterns not currently addressed
- Extensions that appear consistently necessary

> The goal is to refine this into a stable operational standard when sufficient evidence accumulates.

---

**End of Document — v2.0.0**

