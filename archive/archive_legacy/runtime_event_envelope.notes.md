# PLD Runtime Event Envelope — Operational Notes (Working Draft — v2.0) (v2.0 — Operational Edition)

This document supplements the schema file located at:

* `pld_runtime/01_schemas/runtime_event_envelope.schema.json`
* Referenced PLD schema: `docs/schemas/pld_event.schema.json`

This document is intended as the **operational companion to the schema**, providing:

* Interpretation guidance
* Required implementation behaviors
* Deployment considerations
* Validation and storage strategies
* Correct usage patterns and anti-patterns

This is the canonical reference for engineers implementing runtime ingestion, logging, validation, observability, analytics pipelines, or schema governance around the PLD Runtime Envelope.

---

## 1. Purpose of the Envelope

The Envelope represents the **transport and observability layer** for PLD runtime activity.
It exists to:

* Carry exactly **one PLD event** (the semantic unit)
* Add runtime context required for routing, indexing, observability, and operational debugging
* Provide metadata used by distributed systems (platform, trace, environment, execution mode)

> The Envelope **does not redefine or override the meaning of the PLD event**.
> PLD semantics (phase, code, transition logic, lifecycle meaning) are defined **only** in `pld_event.schema.json`.

---

## 2. Required Validation Responsibilities

The Envelope schema enforces **structural correctness only**.
Runtime validators **must enforce additional rules**.

### 2.1 Mandatory Runtime Rules

| Runtime Rule                                                              | Enforcement                    | Status   |
| ------------------------------------------------------------------------- | ------------------------------ | -------- |
| `session.session_id == event.session_id`                                  | MUST validate during ingestion | Required |
| Nested `event` MUST validate against PLD schema (`pld_event.schema.json`) | MUST enforce                   | Required |
| Unknown fields must **not pollute canonical schema**                      | MUST isolate into metadata     | Required |

### 2.2 About `x-validation`

The schema may include `x-validation`, but JSON Schema engines do **not execute these rules**.

They function as **"runtime enforcement contracts"**, and **MUST be implemented in code**.

Example enforcement points:

* ingestion middleware
* schema validator service
* message bus interceptors
* CI validation test harness

**Wrong assumption:**

> "Since it's declared in the schema, validation will automatically occur."

Correct behavior:

> "Schema expresses the rule. The runtime enforces it."

---

## 3. Timestamp Semantics

Two timestamps exist intentionally and represent different concepts.

| Field                | Meaning                                                | Typical Use                                                                                     |
| -------------------- | ------------------------------------------------------ | ----------------------------------------------------------------------------------------------- |
| `envelope.timestamp` | Time the envelope was generated/emitted by the runtime | Ingestion latency, pipeline monitoring, debugging, ordering of arrival                          |
| `event.timestamp`    | Time the semantic PLD event occurred                   | Conversation timelines, lifecycle metrics, PRDR/VRL, analytics, primary time-based partitioning |

**Indexing guidance (non-normative but recommended):**

* Use `event.timestamp` as the **primary time axis** for analytical queries and partitioning.
* Use `envelope.timestamp` as a **secondary index** for debugging ingestion delays and pipeline health.

Runtime systems MUST NOT assume these values are equal.

-------|---------|-------------|
| `envelope.timestamp` | Time the envelope was generated/emitted | Operational timestamp — may differ from event timestamp |
| `event.timestamp` | Time the semantic PLD event occurred | Used for analytics, lifecycle evaluation, sequencing |

Runtime systems MUST NOT assume these values are equal.

---

## 4. Ordering Rules — Critical Clarification

PLD systems operate with **two optional ordering indicators**:

| Field                 | Role                                         | Allowed Use                                                                |
| --------------------- | -------------------------------------------- | -------------------------------------------------------------------------- |
| `event.turn_sequence` | **Authoritative ordering of runtime events** | ✔ MUST be used for lifecycle analysis, reconstruction, sequence validation |
| `trace.turn_index`    | Debugging convenience index                  | ❌ MUST NOT be used for ordering, inference, or PLD lifecycle computation   |

```
🔴 Wrong: using trace.turn_index for state evaluation
🟢 Correct: use event.turn_sequence
```

This rule prevents misinterpretation during retries, backfills, partial replays, or distributed tracing edge cases.

---

## 5. `$ref` Resolution Strategy — Deployment Guidance

Envelope schemas reference the PLD event schema. Implementations must support **two resolution modes**:

| Mode                     | Typical Environment                                       | Behavior                                   |
| ------------------------ | --------------------------------------------------------- | ------------------------------------------ |
| Local Resolution Mode    | Development / monorepo                                    | Use existing relative `$ref`               |
| Registry Resolution Mode | CI/CD, schema registry, microservices, Docker, serverless | Resolve using `$id` or URI, not filesystem |

Example production pattern:

```
$ref: "https://schemas.pld.dev/schema/pld_event/2.0.json"
```

Runtime validators MUST configure a resolver/resolution strategy and **not assume directory layout**.

---

## 6. Handling Unknown / Extended Fields

Fields under `session`, `runtime`, and `trace` allow extension for forward compatibility.
Unknown fields MUST be treated according to this policy:

| Category                    | Action                                                          |
| --------------------------- | --------------------------------------------------------------- |
| Canonical defined fields    | Extract and store in fixed columns                              |
| Unknown or extension fields | Store in a metadata bucket (e.g., `meta_json`, `envelope_meta`) |

This avoids schema pollution (example failure: storing typos like `seession_id`).

---

## 7. Validation Strategy Models

Different environments require different validation strictness.
Implementations SHOULD choose one of the following models based on **SLOs, risk profile, and traffic volume**.

| Model                  | Behavior                                                                                                   | Typical Use Case                                                                                                  |
| ---------------------- | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Strict Mode**        | Every message fully validated (schema + semantics)                                                         | Regulated, financial, clinical, high-risk or audit-heavy domains                                                  |
| **Sampling Mode**      | Validate a fixed percentage (e.g., 1–10%) of messages                                                      | Large-volume systems where full validation is costly, but drift detection and quality monitoring are still needed |
| **Fail-Open With DLQ** | Main pipeline continues even if validation fails; invalid messages are routed to a Dead Letter Queue (DLQ) | Reliability-first or low-latency streaming systems, experimentation pipelines                                     |

For the purpose of this Working Draft, “large-scale” can be read as:

* sustained throughput above roughly **1k–5k envelopes per second**, or
* workloads where schema validation is demonstrably a non-trivial fraction of processing cost.

**Practical guidance (research-phase deployments):**

* Solo / lab research, early PoC → Sampling Mode or Fail-Open+DLQ is often acceptable.
* Shared or multi-team environment → Prefer Strict Mode on at least one ingestion path (e.g., batch backfill).
* Regulated / user-facing with SLAs → Strongly prefer Strict Mode with DLQ for resilience.

Dead Letter Queue (DLQ) MUST retain enough metadata for replay and root-cause analysis (see Appendix).

-------|----------|----------|
| **Strict Mode** | Every message fully validated | Regulated, financial, clinical, high risk domains |
| **Sampling Mode** | Validate a fixed % (e.g., 1–10%) | Large-scale or high-throughput systems |
| **Fail-Open With DLQ** | Invalid messages do not block processing; they are queued for review | Reliability-first streaming or real-time systems |

Dead Letter Queue (DLQ) MUST retain enough metadata for replay and root-cause analysis.

---

## 8. Examples

### 8.1 Valid Minimal Envelope

```json
{
  "envelope_id": "645d1c3e-4bf4-4d32-92fd-7d3a4a0f1a11",
  "timestamp": "2025-01-01T12:00:00Z",
  "version": "2.0",
  "session": { "session_id": "sess_001" },
  "runtime": { "environment": "production", "mode": "stream" },
  "event": {
    "schema_version": "2.0",
    "event_id": "c1309a4f-1805-4c50-8a14-9a14b8a0b9e9",
    "timestamp": "2025-01-01T11:59:59Z",
    "session_id": "sess_001",
    "turn_sequence": 1,
    "event_type": "continue_allowed",
    "source": "runtime",
    "pld": { "phase": "continue", "code": "C0_normal" }
  }
}
```

### 8.2 Invalid (Session ID mismatch)

Rejected at ingestion.

### 8.3 Invalid (Semantic mismatch: phase vs event_type)

Fails PLD semantic validation.

---

## 9. CI/CD Enforcement Requirements

CI/CD pipelines SHOULD enforce:

* Schema validation for the Envelope and PLD event schemas
* Example-based tests (valid examples must pass / invalid examples must fail)
* Guardrails against schema-breaking changes (or at least manual review and explicit version updates)

To reduce fragmentation between teams, it is RECOMMENDED to share:

* A common ingestion validator implementation (or library), and
* A shared error taxonomy (see Appendix) for logging and DLQ routing.

---

## 10. Glossary (Operational Definitions)

| Term                | Definition                                                   |
| ------------------- | ------------------------------------------------------------ |
| Envelope            | Transport/observability wrapper carrying one PLD event       |
| PLD Event           | Semantically meaningful lifecycle event governed by PLD spec |
| Transport Timestamp | Envelope creation time                                       |
| Event Timestamp     | Time the semantic event occurred                             |
| Trace Metadata      | Debugging and observability context only — not semantic      |
| Extension Fields    | Unknown or future fields preserved for forward compatibility |

---

## Appendix — Runtime Behavior & Common Questions

This appendix captures typical questions from runtime engineers and provides recommended behavior.
It is descriptive rather than exhaustive, and future revisions may refine these patterns.

### A. Deduplication & Idempotency

It is common to see **the same PLD event** transported in **multiple envelopes**, for example when retries or replays occur.

Two identifiers exist:

* `envelope_id` — identifies the envelope (transport instance)
* `event.event_id` — identifies the semantic PLD event

Recommended usage:

| Layer                                          | Key to use       | Behavior                                                                                |
| ---------------------------------------------- | ---------------- | --------------------------------------------------------------------------------------- |
| Transport / streaming (Kafka, Pub/Sub, queues) | `envelope_id`    | Detect and manage duplicate envelopes at transport level                                |
| Analytics / application logic / storage        | `event.event_id` | Treat as the semantic idempotency key. Use to deduplicate events with the same meaning. |

Consumers SHOULD:

* Use `event_id` as the primary deduplication key for semantic processing.
* Avoid using `envelope_id` for semantic uniqueness checks.

### B. Version Mismatch Handling (Forward Compatibility)

Envelope and PLD event schemas may evolve at different speeds.
Implementations need a clear policy when encountering **newer PLD event versions**.

Let `supported_event_versions` be the set of PLD event schema versions known to the validator.

| Case                           | Example                                                  | Recommended Behavior                                                                                            |
| ------------------------------ | -------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Known version                  | `event.schema_version` in `supported_event_versions`     | Perform full schema + semantic validation                                                                       |
| Older version                  | `event.schema_version` < min(`supported_event_versions`) | MAY validate if backwards-compatibility is maintained, or quarantine if not supported                           |
| Newer version (forward-compat) | `event.schema_version` > max(`supported_event_versions`) | Do **not** fail ingestion by default. Store raw event, emit warning/metric, optionally route to a review queue. |

In the forward-compatibility case, systems SHOULD:

* Preserve the raw event for later reprocessing once validators are updated.
* Emit structured logs or metrics indicating “unknown schema_version encountered”.

### C. Dead Letter Queue (DLQ) Minimum Contents

When using a DLQ, each DLQ message SHOULD include at least:

* `envelope_id`
* `event.event_id` (if present and parseable)
* Original raw payload (or a lossless representation)
* A machine-readable error code (see Error Taxonomy below)
* A human-readable error message (optional but helpful)
* Timestamp when the failure was observed

This enables later replay, inspection, and remediation.

### D. Error Taxonomy (Suggested)

To reduce fragmentation across teams, a shared error classification is helpful.
A simple, extensible starting point:

* `INVALID_ENVELOPE_SCHEMA` — Envelope failed structural validation.
* `INVALID_EVENT_SCHEMA` — PLD event failed schema or semantic validation.
* `FORWARD_INCOMPATIBLE_EVENT_VERSION` — Event uses a newer `schema_version` than the validator supports.
* `VALIDATION_TIMEOUT` — Validation did not complete in allotted time.
* `INTERNAL_VALIDATOR_ERROR` — Unexpected failure within the validation service.

Teams MAY extend this taxonomy, but reusing these codes improves searchability and dashboards.

---

## Feedback and Contribution

This specification is part of an exploratory research effort and may evolve based on real-world testing and feedback.
If you are implementing the PLD Runtime Envelope or adapting it for production, your feedback is especially valuable.

Feedback is welcome via:

* **GitHub Issues**
* **GitHub Discussions**

Future revisions will incorporate lessons learned from early adopters.

---

## Summary

* The Envelope defines transportation and runtime context — not the semantics of the PLD event.
* The PLD event provides the lifecycle meaning and MUST be interpreted using the PLD event schema.
* Validation behavior depends on deployment requirements and may use strict, sampling, or fail-open validation.
* Forward compatibility and schema evolution are expected and supported.

> Goal: Incrementally move toward interoperability while remaining flexible during experimentation.

---

**End of Working Draft — v2.0**
