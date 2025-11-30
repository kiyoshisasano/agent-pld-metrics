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

{
"timestamp": "ISO8601 timestamp (microseconds)",
"trace_id": "Request correlation ID (UUIDv4)",
"span_id": "Individual operation ID (Hex)",
"component": "system|user|agent|pld_runtime|tool|...",
"event_type": "What happened",
"phase": "Lifecycle stage",
"payload": { /* Event-specific data */ }
}

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

## **🔄 Phases**

* **init**: Session startup
* **input**: User message received
* **monitoring**: PLD analyzing agent behavior
* **processing**: Agent reasoning
* **execution**: Agent attempting tool calls
* **drift**: Drift detection checkpoint
* **repair**: Governance intervention
* **reentry**: Post-repair verification
* **external**: External service communication
* **outcome**: Final results
* **output**: Agent response to user
* **complete**: Session summary

## **📖 Reading the Golden Semantic Repair Trace**

*File: golden_semantic_repair.jsonl*

This trace demonstrates the core PLD value proposition:

[1] User Request
└── "Find me a cheap hotel with parking and WiFi"

[2] Constraint Extraction (PLD)
└── Identifies: location, wifi, parking (mandatory), price

[3] Agent Reasoning ⚠️
└── "Let me relax constraints to get more results..."

[4] Risk Assessment (PLD)
└── Detects: "intentional constraint relaxation"

[5] Tool Call Attempt ❌
└── Agent calls API with wifi only (parking omitted!)

[6] Drift Check (PLD) 🚨
└── VIOLATION: "parking" is mandatory but missing

[7] Execution Blocked (PLD)
└── Tool call intercepted before execution

[8] Corrective Injection (PLD)
└── Feedback injected into agent context

[9] Agent Recovery ✓
└── "I understand. Retrying with all constraints."

[10] Verified Retry ✓
└── All constraints present → PASS → Execute

[11] Success
└── User gets results matching ALL requirements

**Key Insight:** Without PLD governance, the agent would have returned hotels without parking, violating the user's explicit request.

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

CC-BY-4.0

