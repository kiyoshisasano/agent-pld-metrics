# PRDR Framework — Post-Repair Drift Recurrence
Status: Draft / Research Use
Version: 2.0

---

## 1. Purpose

PRDR analyzes how frequently drift re-emerges after at least one repair event.
While PLD_metrics_spec.md formalizes the computation, this document provides:

- Interpretation guidance
- Common patterns
- Usage considerations
- Failure signatures
- Research questions

---

## 2. What PRDR Measures

PRDR reflects **recurrence behavior** of drift after repair intervention.

High PRDR may indicate:
- Ineffective repair strategies
- Temporal instability in agent alignment
- User-agent goal divergence
- Model state fragmentation or memory-induced regression

Low PRDR typically suggests:
- Stable recovery behavior
- Policy adherence
- High repair precision

---

## 3. Interpretation Zones (Not normative)

| Range | Meaning | Notes |
|-------|---------|-------|
| 0–20% | Strong stability | Repairs rarely lead to repeated drift |
| 20–50% | Mixed alignment | System consistency varies by context |
| 50–80% | Fragile recovery | Repair effect often temporary |
| 80–100% | Unstable system | Repair does not change long-term state |

⚠ These are **not thresholds** — they represent **observational zones**, not standards.

---

## 4. Patterns Seen in Research

| Pattern Type | Example Signal | Interpretation |
|--------------|---------------|----------------|
| Immediate relapse | drift within ≤ 2 turns | repair does not restore alignment |
| Delayed relapse | drift ≥ 5 turns later | temporary success but unstable |
| Multi-wave | drift → repair → drift → repair | oscillatory instability |

---

## 5. Diagnostic Uses

PRDR can indicate:

- Whether drift is structural (systemic) or episodic
- The adequacy of repair policies
- Stability of long-horizon agent behavior
- Whether failover mechanisms should activate

---

## 6. Open Research Questions

- Is recurrence tied to content domain?
- Does user tone or intent correlate with PRDR movement?
- Does model size reduce recurrence patterns?

---

## 7. Suggested Visualizations

- Session recurrence heatmaps
- Kaplan–Meier survival curves for drift after repair
- Sequence entropy evolution

---

End of Draft
