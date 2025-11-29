# Quickstart Metrics Module

This folder contains a minimal, example-driven workflow for exploring metrics derived
from PLD event logs.

It does **not** define official evaluation rules, taxonomy, or analysis standards.
Those are governed by Level 1–3 canonical specifications.

Instead, this folder demonstrates how a developer can:

* Inspect PLD event logs locally
* Compute lightweight derived metrics
* View early patterns such as drift, repair, and recovery sequences
* Use dashboards and reports to reason about behavior

---

## 📁 Folder Structure

```
metrics/
├── dashboards/
│   └── reentry_success_dashboard.json
├── datasets/
│   └── pld_events_demo.jsonl
├── guides/
│   └── drift_event_logging.md
├── reports/
│   └── pld_events_demo_report.md
└── verify_metrics_local.py
```

Each component plays a specific role in the Quickstart workflow.

---

## 1. `datasets/pld_events_demo.jsonl`

A handcrafted, educational PLD event dataset.

It includes:

* A successful recovery case
* A partial recovery case with recurrence
* A failure case after repeated repairs

This dataset is intentionally small and interpretable.
It is **not synthetic evaluation data** and should not be used for benchmarking.

---

## 2. `verify_metrics_local.py`

A lightweight script that:

* Loads the dataset
* Counts drift, repair, and reentry patterns
* Outputs summary metrics in the terminal

Run it with:

```sh
python verify_metrics_local.py
```

This provides a **first-pass analytical view** without modifying or validating events.

---

## 3. `guides/drift_event_logging.md`

A short reference explaining:

* What drift means in the PLD lifecycle
* How drift, repair, and continuation events relate
* How drift appears in exported logs

This guide complements the dataset and is intended for readers new to PLD event flow.

---

## 4. `reports/pld_events_demo_report.md`

A narrative case study that walks through the demo dataset from a metrics lens.

It explains:

* What patterns appear
* How they relate to expected runtime behavior
* How developers might interpret model performance or interaction structure

This is meant to be read after running the dataset and reviewing raw logs.

---

## 5. `dashboards/reentry_success_dashboard.json`

A placeholder dashboard configuration showing how an analyst or tooling system
might visualize:

* Drift frequency
* Repair depth
* Successful recovery
* Session timelines

The structure is tool-agnostic and conceptual.

---

## How to Use This Folder

1. **Read the dataset**

   * Open the JSONL file or scan with a log viewer.

2. **Run the metric script**

   * Inspect summary metrics and repair patterns.

3. **Compare behavior using the report**

   * Use the walkthrough to connect metrics to event semantics.

4. **Explore drift handling using the guide**

   * Understand how drift and repair relate in the runtime lifecycle.

5. **Visualize with the dashboard**

   * Optional: load the config into a compatible viewer.

---

## Design Philosophy

This Quickstart module follows three rules:

| Principle               | Meaning                                                  |
| ----------------------- | -------------------------------------------------------- |
| **Minimal**             | Focus on one pathway: inspect → measure → interpret      |
| **Non-authoritative**   | Does not redefine taxonomy, schema, or runtime contracts |
| **Human-interpretable** | Designed for clarity over completeness                   |

---

## Next Steps

If extending this module, consider:

* Additional session types (longer conversations, tools, ambiguity)
* Expanded metric dimensions (latency, plan validation, reasoning traces)
* Workflows integrating BI, Jupyter, or runtime dashboards

---

✔ Metrics Quickstart module complete.



