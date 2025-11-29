# PLD Event Report — Demo Dataset

This report summarizes observable behavior patterns found in the demo PLD
event dataset.  
It is intended for learning, debugging, and inspection — not for formal model
evaluation or compliance certification.

---

## 1. Dataset Overview

- **Total sessions:** 3  
- **Event types observed:**
  - `continue_allowed`
  - `drift_detected`
  - `repair_triggered`
  - `latency_spike`
  - `session_closed`
  - `info (derived metric: M1_PRDR)`

This dataset intentionally represents **contrasting runtime outcomes**:

| Session ID | Pattern Type | Outcome |
|-----------|--------------|---------|
| `demo-fail-01` | Persistent drift + repeated repair | Session terminated after failed recovery |
| `demo-ok-01` | Drift → single repair → successful recovery | Completed normally |
| `demo-metrics-01` | Drift → repair → recurrence → metric emission | Completed with derived metric logging |

---

## 2. Session Case Studies

### 2.1 `demo-fail-01` — Persistent Repair Loop

Pattern observed:

```
continue → drift → repair × N → session_closed
```


- The runtime identified a tool-related drift condition.
- Repeated soft repair strategies were applied.
- After multiple attempts, the runtime closed the session.

**Interpretation:**  
This represents a **progressive collapse case** where the model does not
recover despite repair attempts.

This pattern is useful for:

- Fail condition inspection
- Analysis of retry effectiveness
- Measuring repair failure scenarios

---

### 2.2 `demo-ok-01` — Successful Single Repair

Observed flow:

```
continue → drift → repair → continue → (optional observability event) → close
```


Key properties:

- Drift was detected early (`D1_instruction`)
- A single clarification-style repair (`R1_clarify`) resolved ambiguity
- The model resumed normal execution successfully

This demonstrates a **healthy recovery cycle** and is suitable for:

- Recovery latency tracking  
- Repair efficiency scoring  
- Model stability analysis  

---

### 2.3 `demo-metrics-01` — Post-Repair Drift Recurrence (PRDR)

Behavior sequence:

```
continue → drift → repair → drift recurrence → derived metric emitted → close
```


A derived metric event (`M1_PRDR`) was logged to indicate **post-repair drift
recurrence**.

This pattern demonstrates:

- How metrics may be emitted as standalone events
- A case where the repair was partially effective but the system continued
to deviate

---

## 3. Observed Metric Signals (Qualitative)

| Metric Category | Signals Observed |
|----------------|------------------|
| Drift rate | Multiple drift events across sessions |
| Repair depth | 1–5 repair attempts depending on context |
| Recovery behavior | Full recovery (ok), partial recovery (metrics), no recovery (fail) |
| Observability | Latency spike recorded in one session |
| Derived metrics | PRDR captured as standalone event |

These patterns provide meaningful dimensions for future dashboards or
automated analysis.

---

## 4. Notes on Interpretation

This dataset is intentionally small and handcrafted.

When interpreting logs:

- **Do not treat event ordering as strict causal proof** — it mirrors runtime patterns, not enforced logic.
- **Derived metrics (M-prefix events) are not ground truth** — they act as informal annotations.
- **Repair events do not guarantee success** — drift and repair are informational signals, not outcomes.

---

## 5. Suggested Next Steps

To continue exploring metrics:

```bash
python verify_metrics_local.py
```

You can then:

- Compare behaviors across sessions
- Adjust drift conditions or repair strategies
- Inspect how new logging patterns affect model observability

---

✔ Report generation complete.
