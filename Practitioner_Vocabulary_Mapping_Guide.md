# Practitioner Vocabulary Mapping Guide

*A conceptual bridge between practitioner language and PLD formal terminology*

This document provides a **practitioner-friendly mapping** for understanding PLD terminology.
It does **not** describe internal implementations; it only offers conceptual alignment between the shapes observed by practitioners in multi-turn agent traces and the corresponding formal terms used in PLD.

---

## 1. High-Level Conceptual Mapping

| Practitioner Vocabulary           | PLD Formal Terminology       | Notes                                                 |
| --------------------------------- | ---------------------------- | ----------------------------------------------------- |
| Agent wobble                      | Early instability episode    | First detectable deviation from expected behavior.    |
| Latency bulge / drift             | Latency deviation sequence   | Temporal signature around instability onset.          |
| Reasoning going off-track         | Divergent reasoning branch   | Practitioner intuition aligned with structural shift. |
| Self-correction / retrying        | Correction sub-loop          | Structured recovery attempt.                          |
| Relapse after correction          | Post-correction instability  | Drift reappears after stabilization.                  |
| Break in consistency across turns | Multi-turn coherence failure | Deviations in expectations across turns.              |
| Bad tool call / tool confusion    | Tool-chain inconsistency     | Mismatch across planned vs executed operations.       |
| Loss of focus                     | Attention drift event        | Informal symptom matched to trace pattern.            |
| Looping                           | Recovery failure loop        | Repeated unsuccessful corrections.                    |
| Session died early                | Premature closure pattern    | Abnormal termination category.                        |
| Slow degradation over time        | Long-horizon drift curve     | Gradual instability progression.                      |

---

## 2. Trace-Level Vocabulary Mapping

### 2.1 Event-Level Concepts

| Practitioner Vocabulary | PLD Formal Concept      | Notes                                   |
| ----------------------- | ----------------------- | --------------------------------------- |
| Event                   | Timestamped node        | Anchored point in the lifecycle.        |
| Span                    | Execution segment       | Parent/child structured unit.           |
| User turn / Agent turn  | Turn-indexed sequence   | Core frame for instability windows.     |
| Tool call result        | External operation node | Leaf nodes feeding back into reasoning. |
| Monitoring alert        | Side-channel signal     | Auxiliary event type.                   |

---

## 3. Instability Pattern Vocabulary Mapping

| Practitioner Description       | PLD Pattern                          | Description                                   |
| ------------------------------ | ------------------------------------ | --------------------------------------------- |
| Output became verbose/rambling | Expansion drift                      | Output length inflation without mandate.      |
| Skipped a required step        | Missing-step divergence              | Omission relative to expected structure.      |
| Confused tool-choice           | Misaligned tool-selection transition | Selection diverges from plan.                 |
| Made up new constraints        | Constraint hallucination             | Added internal rules not grounded in context. |
| Keeps fixing the same issue    | Unsuccessful correction loop         | Repeated correction attempts.                 |
| Quality drops every few turns  | Gradual degradation slope            | Slow weakening of structure/coherence.        |
| Sudden sharp failure           | Sudden-break anomaly                 | Abrupt deviation in timing or logic.          |

---

## 4. Latency & Timing Vocabulary Mapping

| Practitioner Vocabulary | PLD Timing Construct       | Meaning                            |
| ----------------------- | -------------------------- | ---------------------------------- |
| Latency spike           | Local positive deviation   | Early marker of instability onset. |
| Pattern changed shape   | Temporal-mode shift        | Mode transition across segments.   |
| Slower after turn N     | Post-drift latency plateau | Stabilization or degradation zone. |
| Jitter                  | High-variance window       | Noisy instability region.          |

---

## 5. Session Outcome Vocabulary Mapping

| Practitioner Description    | PLD Outcome Category  | Notes                                   |
| --------------------------- | --------------------- | --------------------------------------- |
| Completed fine              | Stable termination    | Expected lifecycle closure.             |
| Ended early / hung          | Premature closure     | Termination outside expected lifecycle. |
| Recovered eventually        | Recovery completion   | Stabilized after instability.           |
| Recovered then failed again | Post-recovery relapse | Strong signal of deeper instability.    |

---

## 6. Higher-Level Behavioral Mapping

| Practitioner Model       | PLD Formal View         | Notes                                 |
| ------------------------ | ----------------------- | ------------------------------------- |
| Agent state drift        | Latent-state divergence | State inferred from structure/timing. |
| Forgot prior steps       | Dependency break        | Broken referential alignment.         |
| Lost the thread          | Context-deficit pattern | Reduced contextual linkage.           |
| Exploring the wrong path | Divergent branch        | Structural fork forming.              |

---

## 7. Purpose of This Mapping Document

This document exists to:

* help practitioners read PLD pattern descriptions,
* align practitioner symptoms with formal lifecycle terminology,
* reduce ambiguity when interpreting instability episodes,
* provide a conceptual bridge layer without implementation details.

---

## 8. Recommended Usage

* Place this file at the **root of the PLD repository**.
* Link it from README or CONTRIBUTING for clarity.
* Use during onboarding, cross-team reviews, debugging sessions, instability walkthroughs.
