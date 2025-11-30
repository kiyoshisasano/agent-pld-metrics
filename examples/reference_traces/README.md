<!--
path: examples/reference_traces/README.md
component_id: reference_traces_readme
kind: doc
area: examples
status: candidate
authority_level: 3
license: CC-BY-4.0
purpose: Documentation for simulated log traces and generation tools.
-->

# **Reference Traces**

This directory contains simulated log traces that demonstrate how the **Phase Loop Dynamics (PLD)** runtime monitors and governs agent behavior.

**⚠️ Important:** These logs are synthetic examples created for educational and demonstration purposes via simulation scripts. They do not represent actual production data, although they are designed to reflect production schema and entropy.

## **📂 Files Overview**

| File                             | Purpose                                          | Characteristics                                                                            |
| :------------------------------- | :----------------------------------------------- | :----------------------------------------------------------------------------------------- |
| **golden_semantic_repair.jsonl** | Story-focused demo of drift detection and repair | Clean, readable, perfect narrative flow. Demonstrates the "Happy Path" of PLD governance.  |
| **forensic_infra_noise.jsonl**   | Realism-focused trace with infrastructure noise  | Contains timeouts, warnings, partial failures, and realistic cryptographically random IDs. |
| **generators/**                  | Script directory                                 | Contains Python scripts to reproduce these traces with high entropy.                       |

## **📊 Log Schema**

Each line is a JSON object with the following structure:

```json
{
  "timestamp": "ISO8601 timestamp (microseconds)",
  "trace_id": "Opaque session correlation ID (16-char hex)",
  "span_id": "Operation-level ID within the same trace (16-char hex)",
  "component": "system|user|agent|pld_runtime|tool|...",
  "event_type": "What happened",
  "phase": "PLD lifecycle phase",
  "execution_stage": "Operational execution stage",
  "payload": { /* Event-specific data */ }
}
```
## Identifier Rules

| Field      | Purpose                                                                   | Format           | Notes                                               |
| ---------- | ------------------------------------------------------------------------- | ---------------- | --------------------------------------------------- |
| `trace_id` | Groups all events belonging to a single interaction/session               | `^[0-9a-f]{16}$` | Compact, opaque, unique per session (not UUIDv4)    |
| `span_id`  | Represents an individual sub-operation (agent reasoning, tool call, etc.) | `^[0-9a-f]{16}$` | Hierarchical or parallel spans under the same trace |

> These identifiers are intentionally short for readability and scanning,
> while remaining compatible with distributed tracing systems (e.g., OTel, LangGraph spans, AgentOps).

## **🧩 Components**

| Component            | Description                                                       |
| :------------------- | :---------------------------------------------------------------- |
| system               | Session initialization and configuration                          |
| user                 | User input events                                                 |
| agent                | LLM reasoning and actions                                         |
| pld_runtime          | Governance layer (constraint extraction, drift detection, repair) |
| tool / tool_executor | External API calls and results                                    |
| monitor              | System health warnings (e.g., connection pool)                    |
| debug                | Internal checkpoints                                              |

## 🔄 PLD Runtime Phases vs Execution Stages

PLD logs include two parallel classification layers:

---

## 📖 Reading the Golden Semantic Repair Trace

*File: `golden_semantic_repair.jsonl`*

This trace demonstrates the canonical PLD loop:

```
Drift → Repair → Reentry → Continue → Outcome
```

Example repair sequence (simplified):

```jsonc
// 1) Agent attempts tool call — parking missing
{"event_type": "tool_call_attempt", "args": {"amenities": ["wifi"]}}

// 2) PLD flags misalignment
{"event_type": "drift_detected", "missing": ["parking"]}

// 3) PLD intervenes and blocks action
{"event_type": "continue_blocked"}

// 4) Corrective repair injected
{"event_type": "repair_triggered"}

// 5) Agent retries with corrected parameters
{"event_type": "tool_call_attempt", "args": {"amenities": ["wifi", "parking"]}}

// 6) PLD verifies recovery and allows continuation
{"event_type": "evaluation_pass"}
```

This file is recommended as the **first reference** before exploring the higher-entropy forensic trace.

---

### **PLD Lifecycle Phases (High-Level Behavioral State)**  
These indicate **where the agent is in the governance loop**:

| Phase | Meaning |
|-------|---------|
| **drift** | A misalignment is detected or evaluated |
| **repair** | A corrective intervention is initiated |
| **reentry** | The system verifies alignment after repair |
| **continue** | Normal execution (no intervention required or intervention completed) |
| **outcome** | Final evaluation at the end of a turn or session |

These phases represent the **PLD reasoning contract**, not the agent workflow.

---

### **Execution Stages (Fine-Grained Runtime Context)**  
These describe **what the system is doing operationally**:

| Stage | Description |
|--------|------------|
| `init` | Session or runtime initialization |
| `input` | User message received or processed |
| `monitoring` | PLD observing agent reasoning or tool attempts |
| `processing` | LLM reasoning / chain-of-thought / planning |
| `execution` | A tool call or equivalent external action is attempted |
| `recovery` | Agent or runtime attempting correction after intervention |
| `external` | HTTP/API/tool execution outside the model |
| `output` | Model response being generated or finalized |
| `complete` | Session ended, final summary emitted |

---

> **Lifecycle Phases = WHY behavior is happening**  
> **Execution Stages = WHAT the system is currently doing**

Both appear in the JSON traces and are designed to be complementary—not redundant.

---

## **🔍 Reading the Forensic Infra Noise Trace**

*File: forensic_infra_noise.jsonl*

This trace demonstrates realistic production conditions:

* **Debug logs:** Memory usage, goroutine counts
* **Warning logs:** Connection pool pressure, memory limits
* **Timeouts:** 5-second gateway timeout with automatic retry
* **Partial failures:** Some data providers unavailable
* **Realistic IDs:** Cryptographically random UUIDs and hashes

**Use this trace for:**

* Testing log parsers and visualization tools
* Demonstrating infrastructure observability
* Security/forensic analysis exercises

## **🛠 Generating New Traces**

The generators/ directory contains Python scripts for creating new synthetic traces.

To generate a new forensic-quality trace:

# Run from repository root

python examples/reference_traces/generators/generate_forensic_trace.py > my_forensic_trace.jsonl

Each run produces different:

* Session/trace/span IDs (cryptographically random)
* Timestamps (with microsecond jitter)
* Numeric values (latencies, token counts, scores)
* Scenario paths (e.g., success vs. timeout)

## **✅ Verification**

These traces have been validated for:

* [x] **Temporal consistency:** All timestamps are monotonically increasing within causal chains
* [x] **ID uniqueness:** No duplicate trace_id/span_id pairs
* [x] **Schema compliance:** All required fields present
* [x] **Cryptographic plausibility:** Hashes and UUIDs follow standard formats
* [x] **Latency realism:** All durations within expected ranges for their operation types

## **📜 License**

These example traces are provided under the same license as the parent repository.
