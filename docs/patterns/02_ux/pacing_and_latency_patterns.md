---
title: "Pacing & Latency Patterns — UX Timing Guide"
version: 2025.1
status: stable
maintainer: "Kiyoshi Sasano"
category: "patterns/ux"
tags:
  - latency
  - pacing
  - repair UX
  - conversational rhythm
  - PLD-runtime
---

# Pacing & Latency Patterns  
_Design rules for timing, turn pacing, perceived responsiveness, and repair timing._

Humans judge intelligence, confidence, and trustworthiness **not only by correctness — but by timing.**  
Latency and pacing are critical behavioral signals in PLD-based systems.

This guide defines how timing influences:

- Drift interpretation  
- Repair comfort  
- Reentry confidence  
- Failover predictability  

---

## 🧠 Why Timing Matters

Users unconsciously map system timing to **intent**:

| Latency | User Interpretation |
|---------|---------------------|
| Instant (0–900ms) | “It already knew.” |
| Moderate (1–4s) | “It’s thinking.” |
| Long pause (5–9s) | “Something’s wrong.” |
| Over 10s | “System failure.” |

Proper pacing prevents:

- premature responses  
- overcorrection loops  
- perceived confusion  
- trust degradation  

---

## ⚙️ Timing Rules by Phase

| PLD Phase | Ideal Response Window | Behavior |
|-----------|-----------------------|----------|
| **Continue** | 700ms–2.0s | Natural conversational pace |
| **Drift Detected** | 1.2–3.5s | Slight delay → signals *checking* |
| **Soft Repair** | 1.8–4.5s | Intentional pause before intervention |
| **Hard Repair** | 2.5–6.0s | Must include pacing text if >3s |
| **Failover** | 4.0–8.0s | Must include progress update + optional cancel affordance |

---

## ⏱ Microcopy Timing Cues

If a response exceeds thresholds, the system must communicate pacing.

### Threshold 1 — Mild Delay (≥2.5s)

```
One moment — reviewing that.
```

Variants:

- “Still checking.”
- “Let me verify that.”

---

### Threshold 2 — Extended Delay (≥5s)

Must include **progress framing**:

```
Still working — applying your request.
```

Optional user control:

```
Would you like me to continue or cancel?
```

---

### Threshold 3 — Failover Risk (≥10s)

Visible recovery or reset:

```
This is taking longer than expected — I may need to restart this step.
```

If triggered again → failover.

---

## 📏 Turn Rhythm Patterns

### Pattern 1 — Repair Wait-then-Confirm

```
(Short pause)
Soft repair message
User response
(Immediate confirmation + resumed flow)
```

This prevents **rapid-fire correction**, which feels defensive or robotic.

---

### Pattern 2 — Async Tool Completion

Use a *two-stage UX rhythm*:

```
→ Latency cue
→ Final response
```

Example:

```
Looking it up…
(2–4 seconds)
Here are the results — sorted by cost.
```

---

## 🧘 Pacing as Confidence Signal

Too fast → **appears shallow or scripted**  
Too slow → **appears confused or failing**

Use the **Calibration Triangle**:

| Dimension | Too Low | Optimal | Too High |
|----------|---------|---------|----------|
| Tempo | Interruptive | Conversational flow | Slow / frozen |
| Acknowledgment | Silent / abrupt | Brief and contextual | Over-validation |
| Recovery | Instant silent fix | Visible soft repair | Multi-turn apology |

---

## 🔁 Reentry Timing Rules

After a repair, the system must not **rush back into task execution**.

Required pause markers:

```
Got it — continuing.
```

Optional nuance variants:

- “Thanks — applying the fix.”
- “Okay — updating and moving forward.”

Reentry responses should feel **intentional and grounded**, not reflexive.

---

## 🧯 Latency and Emotion Sensitivity

If user shows frustration signals:

| User Signal | Adjustment |
|------------|------------|
| “Hello??” / repeated input | Shorten pacing text, reduce hesitation |
| Negative tone | Add validation layer |
| “Take your time.” | Extend natural latency range |

Example adaptive response:

```
Thanks — still working. I’ll reply with results when ready.
```

---

## ✔ Checklist (Pre-Release Validation)

```
☑ No silent delays >3s
☑ Repair confirmation always has pacing + structure
☑ Failover latency includes choice or status indicator
☑ Async tool calls follow two-stage messaging pattern
☑ Timing varies subtly across turn types (not robotic)
```

---

### Maintainer  
**Kiyoshi Sasano — UX Behavioral Systems Engineering**

---

> _Timing is meaning.  
A system that waits intelligently feels intentional—  
a system that stalls feels lost._

