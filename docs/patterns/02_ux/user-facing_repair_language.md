---
title: "User-Facing Repair Language — Applied UX Patterns"
version: 2025.1
maintainer: "Kiyoshi Sasano"
status: stable
category: "patterns/ux"
tags:
  - PLD
  - UX writing
  - repair language
  - trust patterns
  - conversational recovery
---

# User-Facing Repair Language  
_The UX voice rules for drift-aware interactions_

When drift, confusion, or tool errors occur, users should **never feel blamed**, overwhelmed, or uncertain about next steps.  
This document defines **microcopy rules, tone guidelines, and reusable phrasing patterns** for presenting PLD repairs in a calm, predictable manner.

---

## 🎯 Design Principles

| Principle | Meaning | Example Signal |
|----------|---------|----------------|
| **Transparency, not confession** | State what is happening without over-apologizing | “Let me check that again.” |
| **Ownership, not blame** | The assistant—not the user—takes responsibility | “I'll fix that.” |
| **Single next action** | Always offer a clear next step, not multiple paths | “Which of these best describes what you meant?” |
| **Consistent tone across states** | Repairs should sound like the same assistant, not a new persona | No abrupt tone shifts |

---

## 🧪 Tone Calibration Matrix

| Severity | System Behavior | Tone Style | Avoid |
|---------|----------------|------------|-------|
| Minor drift | Clarification | Light, curious | “I don't understand.” |
| Moderate drift | Soft repair | Neutral, confident | “You said something confusing.” |
| Major failure | Hard repair | Calm, reset-focused | “Everything broke.” |
| Failover | Escalation | Formal, minimal | Over-explaining |

---

## 🧱 Structure of a Repair Message

Every visible repair message must follow this pattern:

```
1) Acknowledge context
2) State adjustment or clarification request
3) Offer structured options or required information
4) Confirm next step
```

Example:

```
Thanks — before I continue, I want to clarify something.

Did you mean:

1) Booking a flight
2) Finding recommendations
3) Something else

Just reply with the number.
```

---

## 🔧 Repair Language Templates

### 🧩 Soft Repair — Clarification

| Situation | Recommended Microcopy |
|----------|------------------------|
| Intent ambiguous | “To make sure I’m following you correctly — which of these do you mean?” |
| Missing constraint | “Before I continue, I need one small detail.” |
| Misinterpretation detected | “Let me check: were you asking about ___ or something else?” |

---

### 🛠 Soft Repair — Constraint Correction

```
Thanks — one note:

That request requires a date range.
Please choose:

📅 1) This week  
📅 2) Next week  
📅 3) Custom dates
```

---

### 🔁 Reentry Confirmation

Once alignment is regained, the assistant should:

✔ Confirm  
✔ Resume task  
✔ Avoid apologies unless user emotion requires it  

Example:

```
Great — now that it's clear, continuing with the search.
```

Alternate variations (rotate to prevent repetition):

- “Perfect — continuing.”
- “Got it — moving ahead.”
- “Thanks — updating the plan now.”

---

### 🧰 Hard Repair (Session Reset Language)

Hard repair should be:

- short  
- neutral  
- never emotional  

```
It looks like things got off track.
I'll restart the task with a clean structure.

First question: what's the goal?
```

---

### 🚨 Failover Language (Critical)

Failover text MUST:

- Avoid promising retry  
- Avoid blaming the user  
- Avoid anthropomorphism  

```
I wasn’t able to complete this safely.
I’m transferring this to a supported fallback path.
```

Optional: ask permission first (user-friendly systems):

```
Would you like me to escalate this to support or restart the task?
```

---

## 🎛 Tone Modifiers (Optional Layering)

| Tag | When to Use | Tone Effect |
|-----|-------------|-------------|
| `[Reassurance]` | Long latency or repeated attempts | Signals stability |
| `[Progress Cue]` | Tool calls or async actions | Reduces uncertainty |
| `[Validation]` | Emotionally sensitive tasks | Retains trust |

Examples:

- `[Reassurance]` → “Still here — working on it.”
- `[Progress Cue]` → “One moment — applying your filters.”

---

## ⏱ Latency + Pacing Phrases

| Delay | Recommended text |
|-------|-----------------|
| 1–2s | (silent, unless tool context requires) |
| 3–5s | “Working on it — just a moment.” |
| 5–12s | “Still processing — almost done.” |
| >12s | Allow cancellation: “This is taking longer than expected — continue or cancel?” |

---

## Final Checklist

```
☑ No user-blaming language
☑ One clear next step
☑ Repair messages never exceed 2 turns
☑ Tone consistent across repair, reentry, and outcome
☑ Confirmation uses clean forward motion (“continuing” not “fixing mistake”)
```

---

### Maintainer  
**Kiyoshi Sasano — Applied AI UX Engineering**

---

> “Repairs should feel like smooth guidance —  
> not admission, apology, or interruption.”

