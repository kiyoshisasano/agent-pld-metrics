# PLD Practitioner Vocabulary Mapping Guide

This document provides a **practitioner-friendly mapping** between everyday operational vocabulary used by engineers and the **formal terminology** defined in the PLD specification (Levels 1–3).

It does **not** redefine PLD rules, introduce new lifecycle phases, or alter taxonomy codes. Its purpose is purely interpretive: to help practitioners understand how their natural language maps to the PLD lifecycle and event semantics.

---

# 0. Core Phase Mapping (Start Here)

The PLD lifecycle consists of five phases:

**Drift → Repair → Reentry → Continue → Outcome**

This section offers a direct mapping between **Practitioner Vocabulary** and **PLD Formal Terms**.

| Practitioner Vocabulary                                | PLD Formal Phase | Canonical Elements (Levels 1–3)                                           |
| ------------------------------------------------------ | ---------------- | ------------------------------------------------------------------------- |
| "wobble", "off-track", "drift", "going sideways"       | **Drift**        | D-family taxonomy (`drift_detected`, D1–D4 classifications)               |
| "self-correction", "retry", "cleanup", "fixing itself" | **Repair**       | R-family taxonomy (`repair_triggered`, R1–R5 patterns)                    |
| "back on track", "looks fine now", "recovered"         | **Reentry**      | *Expressed implicitly via subsequent evaluation/continue rules*           |
| "normal operation", "keep going", "continue"           | **Continue**     | `continue_allowed`, `continue_blocked`                                    |
| "completed", "failed", "gave up", "final state"        | **Outcome**      | O-family taxonomy (`session_closed`, normal completion) |

> **Reentry has no dedicated event type in Levels 1–3.** It is inferred through successful evaluation leading to `continue_allowed`.

---

# 1. Purpose of This Guide

This guide:

* Helps practitioners interpret PLD lifecycle terminology in familiar language.
* Establishes a consistent bridge between real-world debugging terminology and PLD’s structured taxonomy.
* Avoids inventing new PLD terms or pseudo-canonical language.
* Improves communication between platform engineers, observability teams, and PLD authors.

This guide **does not**:

* Modify the PLD specification (Levels 1–3).
* Add new lifecycle phases or taxonomy codes.
* Define any events or semantics not already present in the canonical spec.

---

# 1.1 Applicability Across Execution Scales (Interpretive)

PLD terminology is often associated with **long-running or multi-turn agent systems**.
However, the same lifecycle semantics also apply to **short-lived executions**,
including single-session RAG pipelines and tool-using request flows.

The distinction is **not duration**, but **the presence of multiple execution steps
with state that must remain consistent**.

The table below provides an *interpretive* mapping between common short-lived
agent behaviors and the PLD lifecycle concepts they correspond to.

> This mapping is **interpretive only**.
> It does not introduce new PLD terms, phases, or taxonomy codes.

| Execution Context (Practitioner View) | Interpreted as PLD Concept | Notes |
| ------------------------------------- | -------------------------- | ----- |
| Single user request with retries      | Multi-step interaction    | Multiple execution steps constitute a PLD loop |
| RAG pipeline with re-ranking          | Repair attempt            | Retrieval adjustment is a form of repair |
| Tool failure followed by retry        | Drift → Repair            | Even within one request |
| Output correction before response     | Reentry (inferred)        | Successful repair allows continuation |
| Latency spike or partial degradation  | Drift signal              | Early instability, not necessarily failure |

In other words:

> **“Multi-turn” in PLD refers to execution state transitions,  
> not to long-lived agents or persistent online learning.**

This allows PLD concepts to be applied consistently across both
short-lived and long-running agent architectures.

---

# 2. Practitioner Vocabulary → PLD Formal Terminology

## 2.1 Drift Phase

| Practitioner Says…          | PLD Maps To          | Notes                                 |
| --------------------------- | -------------------- | ------------------------------------- |
| "The agent is wobbling"     | Drift                | Early signs of deviation              |
| "It went off-track"         | `drift_detected`     | Often corresponds to D1–D4 categories |
| "Bad tool call"             | Drift (tool-related) | Often D4_tool_error                   |
| "Lost the plot"             | Drift                | Intent or context drift               |
| "Answer degraded over time" | Drift episode        | Progressive divergence                |

---

## 2.2 Repair Phase

| Practitioner Says…       | PLD Maps To | Notes                              |
| ------------------------ | ----------- | ---------------------------------- |
| "It corrected itself"    | Repair      | `repair_triggered` (R-family)      |
| "It’s retrying"          | Repair      | Often soft repair or guided retry  |
| "It adjusted output"     | Repair      | Applies to static or guided repair |
| "It patched the mistake" | Repair      | General correction behavior        |

---

## 2.3 Reentry Phase

| Practitioner Says…       | PLD Maps To | Notes                                              |
| ------------------------ | ----------- | -------------------------------------------------- |
| "It seems back on track" | Reentry     | Inferred from successful evaluation + continuation |
| "Ready to continue"      | Reentry     | Occurs prior to an allowed continuation transition |

> **No formal Level 1–3 event corresponds to "reentry".** It is a lifecycle concept inferred when repair has succeeded and evaluation no longer blocks continuation.

---

## 2.4 Continue Phase

| Practitioner Says…     | PLD Maps To        | Notes                     |
| ---------------------- | ------------------ | ------------------------- |
| "Continue execution"   | `continue_allowed` | Safe to proceed           |
| "Wait, it paused"      | `continue_blocked` | Often HITL or policy gate |
| "It kept going anyway" | Continue           | Normal loop iteration     |

---

## 2.5 Outcome Phase

| Practitioner Says…  | PLD Maps To                             |
| ------------------- | --------------------------------------- |
| "It finished"       | Outcome (`outcome_generated`)           |
| "It failed out"     | Outcome (`session_closed`, fail reason) |
| "It gave up"        | Outcome (premature termination)         |
| "Done successfully" | Outcome (normal completion)             |

---

# 3. Practitioner Vocabulary (Not part of the PLD spec)

These terms are **not** part of any PLD specification.
They are included only to help interpret informal engineering conversations.

They must **never** be used as PLD event names or taxonomy codes.

| Practitioner Term | Meaning (Interpretive Only)                   |
| ----------------- | --------------------------------------------- |
| wobble            | Minor, early drift-like behavior              |
| relapse           | Drift after apparent recovery                 |
| looping           | Repeated corrective cycles (repair churn)     |
| late wobble       | Drift occurring after long stable period      |
| misalignment      | General divergence from intent or constraints |
| bad tool call     | Tool error producing drift                    |

> These are **not** PLD terms. They describe symptoms, not lifecycle states.

---

# 4. Interpretive Pattern Layer (Optional)

This section clarifies conceptual patterns **seen in traces**, not formal PLD terminology.
These are **pattern descriptors**, not lifecycle events.

| Interpretive Term  | Meaning                                    | Not PLD Because…                   |
| ------------------ | ------------------------------------------ | ---------------------------------- |
| early instability  | Initial drift symptoms                     | Drift already covers this formally |
| divergence pattern | Output diverges from constraints           | No standalone lifecycle meaning    |
| mode shift         | Behavior changes abruptly (timing/quality) | Not a lifecycle phase              |
| recovery window    | Turns between repair and reentry           | Derived, not canonical             |

These descriptors provide intuition only, and should **not** be used in code or telemetry fields.

---

# 5. How to Use This Mapping

Recommended usage:

* **Debugging:** Translate practitioner remarks ("it’s drifting") into PLD phases.
* **Trace review:** Identify lifecycle transitions using formal events.
* **Metrics interpretation:** Understand PRDR / VRL / FR behavior in practitioner language.
* **Cross-team communication:** Offer a shared vocabulary between operators and PLD designers.

Not recommended usage:

* Defining new event types
* Naming new lifecycle phases
* Extending taxonomy codes

---

# 6. Boundaries of This Guide

This guide **does not**:

* Add new formal terms to PLD
* Introduce new phases
* Modify lifecycle semantics
* Replace Level 1–3 specifications

This guide **does**:

* Help practitioners interpret PLD output
* Provide shared language for operational diagnosis
* Improve clarity during debugging and design review

---

# 7. References (Non-normative)

* PLD Concepts → `docs/concepts/01_introduction.md`
* Drift–Repair Model → `docs/concepts/02_drift_repair_model.md`
* Repair Strategies → `docs/concepts/03_repair_strategies.md`
* Runtime Standards (implementation-specific)
* PLD formal taxonomy (Level 2 / Level 3 definitions)

---

End of document. This guide is non-normative and intended solely to improve practitioner understanding of formal PLD semantics.
