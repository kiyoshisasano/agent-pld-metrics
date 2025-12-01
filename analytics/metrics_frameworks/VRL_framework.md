# VRL Framework — Recovery Latency
Status: Draft / Research Use
Version: 2.0

---

## 1. Purpose

VRL measures latency between drift and eventual recovery.  
This document contextualizes the metric by:

- Explaining interpretation boundaries
- Highlighting recovery patterns
- Offering analysis questions and usage modes

---

## 2. What VRL Reveals

VRL reflects:

- How fast the system can restore intended alignment
- Repair efficiency
- Latency burden to end-users

Lower VRL is generally desirable — but **too low latency** may signal overcorrection, robotic tone, or brittle alignment.

---

## 3. Behavioral Zones (Non-normative)

| VRL mean value | Interpretation |
|----------------|----------------|
| 0–2 turns | Rapid recovery; high responsiveness |
| 3–5 turns | Acceptable but requires tuning |
| 6–10 turns | Latency problematic for UX |
| >10 turns | Failed or stalled recovery behavior |

---

## 4. Cycle Archetypes

| Cycle Type | Description |
|------------|------------|
| Single-step | drift → reentry |
| Assisted | drift → repair → reentry |
| Multi-repair escalation | drift → repeated repair events → reentry |
| No recovery | drift → stalls / user abandonment |

---

## 5. VRL Failure Patterns

- **Silent loops**: repeated repair without state transition  
- **Soft-stall**: apology sequences with no reentry  
- **False recovery**: continue_allowed incorrectly triggered  

---

## 6. Research Applications

- Modeling temporal patterns of repair efficacy
- Longitudinal drift stability
- UX burden inference
- Comparing agent models or intervention strategies

---

End of Draft
