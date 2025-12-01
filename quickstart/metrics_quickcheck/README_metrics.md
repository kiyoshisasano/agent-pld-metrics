<!--
path: quickstart/metrics_quickcheck/README.md
component_id: quickstart_metrics_quickcheck_readme
kind: doc
area: metrics
status: draft
authority_level: 2
version: 0.2.0
license: Apache-2.0
purpose: Entry-point README for the metrics_quickcheck module, combining dataset, guide, and report into a single quickstart.
-->

# Metrics Quickcheck Pack

This folder provides a **small, self-contained pack** for exploring metrics
derived from PLD event logs.

It does **not** define official evaluation rules, taxonomy, or analysis
standards. Those are governed by the Level 1–3 canonical specifications.

Instead, this pack demonstrates how a developer can:

- Inspect PLD event logs locally  
- Compute lightweight derived metrics  
- Understand drift / repair / recovery patterns in context  
- Use a simple dashboard configuration to visualize behavior  


---

## 📁 Folder Structure

```text
quickstart/metrics_quickcheck/
├── README.md
├── pld_events_demo.jsonl
├── verify_metrics_local.py
└── reentry_success_dashboard.json
```

Each item plays a focused role:

### 1. `pld_events_demo.jsonl`

A handcrafted, educational PLD event dataset.  

It includes:  

- A successful recovery case
- A partial recovery case with recurrence
- A failure case after repeated repairs

The dataset is intentionally small and interpretable.  
It is **not synthetic evaluation data** and MUST NOT be used for benchmarking.

### 2. `verify_metrics_local.py`

A lightweight script that:

- Loads the demo dataset
- Counts drift, repair, and reentry-related patterns
- Prints a small set of summary metrics in the terminal


Run it with:
```sh
python verify_metrics_local.py
```

This provides a **first-pass analytical view** without modifying or validating events.

### 3. `reentry_success_dashboard.json`

A tool-agnostic dashboard configuration that illustrates how one might  
visualize:

- Drift frequency
- Repair depth per session
- Recovery / reentry patterns
- Session timelines (ordered event views)

It is conceptual and designed for experimentation, not as a production
dashboard spec.

---

## Drift, Repair, and Reentry — Concept Overview

This section summarizes how **drift events** appear in PLD logs and how they
relate to repair and continuation.

### What Is a Drift Event?

A **drift event** indicates that the model response or reasoning path is moving  
away from the intended instruction, behavior, or expected context.

Common drift conditions:

| Drift Type        | Example Signal                                 |
| ----------------- | ---------------------------------------------- |
| Instruction drift | The response does not follow the user request. |
| Repetition drift  | The model repeats previous responses.          |
| Tooling drift     | A tool call fails or yields irrelevant output. |

A drift event is logged using:

- `event_type = "drift_detected"`
- `pld.phase = "drift"`
- `pld.code` indicating a subtype (mapped in runtime bridges)

Example (adapted from the demo dataset):

```json
{
  "event_type": "drift_detected",
  "pld": {
    "phase": "drift",
    "code": "D1_instruction",
    "confidence": 0.8
  },
  "payload": {
    "note": "User request underspecified; needs clarification."
  }
}
```

Interpretation:
> The runtime has identified that it cannot confidently execute the current request.

### What Happens After Drift?

A drift event does **not** end the session.  
It typically triggers a **repair sequence**.  

A common lifecycle pattern is:

```text
drift_detected → repair_triggered → (reentry_observed) → continue_allowed
```

- `repair_triggered` captures the corrective action taken
- `reentry_observed` (when present) marks a successful re-entry into the normal flow
- `continue_allowed` indicates that the system resumes regular operation

Example snippet:

```json
{"event_type": "drift_detected", "pld": {"phase": "drift"}}
{"event_type": "repair_triggered", "pld": {"phase": "repair"}}
{"event_type": "continue_allowed", "pld": {"phase": "continue"}}
```

This indicates the runtime took corrective action and returned to normal flow.

### Measuring Drift

When inspecting PLD logs, developers often look at:

| Metric              | Purpose                                                 |
| ------------------- | ------------------------------------------------------- |
| Drift rate          | How often drift is detected across sessions.            |
| Repair depth        | How many repair attempts are required before recovery.  |
| Recovery success    | Whether drift resolves without failover or abandonment. |
| Latency interaction | Whether drift correlates with higher latency or pauses. |

The script `verify_metrics_local.py` computes a minimal set of drift-related
metrics from `pld_events_demo.jsonl` to support this inspection.

### When Drift Persists

If repeated drift and repair attempts fail to restore stability, the runtime
may escalate to failover or simply close the session.

Example pattern (captured in the dataset):

```text
drift_detected → repair ×N → session_closed
```

Persistent drift is useful for:

- Model tuning and quality evaluation
- Prompt / tool configuration analysis
- Failure mode exploration

---

### Session Patterns in the Demo Dataset

This section summarizes behavior patterns captured in the demo dataset.  
It compresses the original narrative report into a quick reference.

#### `demo-fail-01` — Persistent Repair Loop

Pattern:

```text
continue → drift → repair × N → session_closed
```

Key observations:

- A tool-related drift is detected early.
- The runtime performs multiple soft repairs.
- Despite these attempts, it ultimately closes the session.

Interpretation:

- This is **a progressive collapse** case: repairs do not converge.
- Useful for:
  - examining fail conditions
  - analyzing retry effectiveness
  - reasoning about when to escalate or abandon

---

#### demo-ok-01 — Single Repair and Successful Recovery

Pattern:

```text
continue → drift → repair → continue → (observability event) → session_closed
```

Key observations:

- Instruction-level drift (`D1_instruction`) is detected.
- A single clarification-style repair (`R1_clarify`) is applied.
- The model returns to normal flow and completes successfully.
- A latency-related observability event appears but does not indicate failure.

Interpretation:

- This represents **a healthy recovery cycle**.
- Suitable for:
  - recovery latency tracking
  - repair efficiency scoring
  - stability assessment after repair

---

#### demo-metrics-01 — Post-Repair Drift Recurrence (PRDR)

Pattern:

```text
continue → drift → repair → drift recurrence → derived metric emitted → session_closed
```

Key observations:

- Drift recurs after an attempted repair.
- A derived metric event (`M1_prdr`) is emitted to record **post-repair drift recurrence**.
- The session ultimately closes after metrics logging.

Interpretation:

- Demonstrates how **M-prefix metrics** may be emitted as standalone events.
- Useful as a blueprint for:
  - measuring repair effectiveness over time
  - detecting patterns where repairs only partially succeed

---

### What to Look At Across Sessions

Across all three sessions, it is helpful to inspect:

- **Drift rate** — how often drift events fire across sessions
- **Repair depth** — how many repairs are attempted before exit or recovery
- **Recovery behavior** — full recovery vs. partial vs. no recovery
- **Observability signals** — latency spikes and pauses that correlate with drift
- **Derived metrics — especially** PRDR-like signals that summarize behavior

When interpreting the logs:

- Event ordering reflects runtime behavior but is **not a formal proof of causality**.
- Derived metrics (M-prefix events) act as **annotations**, not ground truth.
- Drift and repair are **informational signals**, not outcomes by themselves.

---

### How to Use This Folder

A recommended usage flow:

1. Scan the dataset

- Open `pld_events_demo.jsonl` in a viewer.
- Note the three session IDs and the general event patterns.

2. Run the local metrics script

```sh
python verify_metrics_local.py
```

- Review the aggregated counts (drift events, repair events, basic ratios).
- Compare these numbers with your reading of the raw events.

3. Revisit the session patterns in this README

- Align the numeric view (from the script) with the narrative patterns above.
- Use this to build intuition for how drift, repair, and recovery appear.

4. (Optional) Load the dashboard configuration

- Import `reentry_success_dashboard.json` into a compatible tool.
- Explore funnel-style views and per-session timelines for drift/repair flows.

This sequence keeps the experience **simple and loop-oriented**:  
inspect → measure → interpret → visualize (optional).

---

### Design Philosophy

This quickcheck module follows three principles:

| Principle               | Meaning                                                  |
| ----------------------- | -------------------------------------------------------- |
| **Minimal**             | Focus on one pathway: inspect → measure → interpret      |
| **Non-authoritative**   | Does not redefine taxonomy, schema, or runtime contracts |
| **Human-interpretable** | Optimized for clarity and teaching, not completeness     |

The pack is deliberately small. It is a **staging area for experimentation**,  
not an evaluation benchmark.

---

### Next Steps

If you extend this module, consider:

- Adding more session types (longer conversations, tool-heavy flows, ambiguity)
- Introducing additional metric dimensions (latency, plan validation, reasoning traces)
- Integrating with BI tools, Jupyter notebooks, or runtime dashboards
- Refining drift / repair definitions based on real-world logs and feedback

---

✔ Metrics quickcheck pack ready for exploration.
