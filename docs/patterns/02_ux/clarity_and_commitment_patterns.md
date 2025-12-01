---
title: "Clarity & Commitment Patterns — Applied Conversational Control"
version: 2025.1
status: stable
maintainer: "Kiyoshi Sasano"
category: "patterns/ux"
tags:
  - clarity phrasing
  - commitment framing
  - alignment tone
  - PLD runtime UX
---

# Clarity & Commitment Patterns  
_Interaction strategies to reduce ambiguity, increase trust, and ensure user alignment during drift, repair, and reentry._

A PLD-enabled agent must not only produce correct information — it must demonstrate **alignment, ownership, and direction.**  
This document provides **canonical phrasing patterns** for:

- Clarifying ambiguous input  
- Requesting commitment signals  
- Confirming alignment before continuing  
- Making the agent’s reasoning and intention visible  

---

## 🎯 Core Principles

| Principle | Description |
|----------|-------------|
| **Make intent explicit** | Users should always know *why* the agent asks something. |
| **Minimize ambiguity** | Avoid vague references (“that/it/there”). Use explicit anchors. |
| **Commit visibly** | When acting, signal ownership (“I’ll apply that”). |
| **Confirm transitions** | Repair → Reentry must always include a validation turn. |

---

## 📌 Pattern Library

### 1) **Clarification Request (CR-1) — Crisp & Minimal**

Use when the user request is **ambiguous but recoverable**.

```
To confirm — are you asking about A or B?
```

Variants:

- “Which option applies: X or Y?”
- “Do you mean the earlier value or the updated one?”

🔥 **Rule:** Never say “I don’t understand.”  
Instead → frame as **precision checking.**

---

### 2) **Disambiguation + Suggestion (CR-2)**

Use when ambiguity is high and the system can propose likely intent.

```
It could mean either X or Y — based on context, X seems more likely. Should I proceed with that?
```

Tone: **Confident, not apologetic.**

---

### 3) **Soft Constraint Confirmation (CC-1)**

Use before executing tool calls, long tasks, or irreversible actions.

```
Before I continue — should I use the latest parameters you provided?
```

Optional UX affordance:

- "Yes — continue"
- "No — adjust"

---

### 4) **Hard Commitment (CC-2) — Execution Lock-In**

Triggered when:

- A repair was applied  
- A task branch is selected  
- A risky or irreversible step begins  

```
Understood — using Option A and applying the changes now.
```

It signals **ownership + direction.**

---

## 🧠 Commitment Tone Matrix

| Tone Type | Use When | Example |
|----------|----------|---------|
| **Neutral Confirming** | routine alignment | “Okay — applied.” |
| **Assurance** | after repair or drift resolution | “Thanks — correction applied. Continuing.” |
| **Guided Choice** | user must finalize | “Which path should I follow: A or B?” |
| **Boundary Setting** | unclear or contradictory request | “I can proceed once we confirm the parameter.” |

---

## 🔄 State-Aware Clarity Patterns (Aligned to PLD)

| State | Required Pattern | Example |
|-------|------------------|---------|
| **Drift Detected** | Identify + clarify | “There’s a mismatch — do you want version A or B?” |
| **Soft Repair** | Clarify + apply | “Corrected — using your updated constraint.” |
| **Reentry** | Confirm stability | “Aligned — continuing.” |
| **Failover Candidate** | Escalate with choice | “Would you like me to reset or retry?” |

---

## 🧰 Microformat Rules (Do / Avoid)

| Do | Avoid |
|----|-------|
| “I’ll apply that update.” | “Okay.” |
| “Based on the latest input…” | “Not sure what you mean.” |
| “Before proceeding, confirm:” | “Wait, what?” |
| “Aligned — continuing.” | Silent transition after repair |

---

## ✨ Optional Extensions: Confidence Framing

Used when the system must express reasoning uncertainty without losing authority.

```
I have enough information to continue, but if you'd like a more precise result, I can verify one detail first.
```

Purpose: **prevent premature execution.**

---

## ✔ Release Readiness Checklist

```
☑ Every clarification request has a purpose statement
☑ Commitments use explicit “apply/continue/confirm” verbs
☑ Ambiguous pronouns replaced with anchored references
☑ Repair → Reentry always uses visible confirmation language
☑ No phrasing implies user error (replace blame with neutral framing)
```

---

### Maintainer  
🧩 **Kiyoshi Sasano — UX Behavioral & Applied Alignment Systems**

---

> Clarity is not verbosity — it is controlled precision.  
> Users should never wonder:  
> **“What is the system doing — and why?”**
