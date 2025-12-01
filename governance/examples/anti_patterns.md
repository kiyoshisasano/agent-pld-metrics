---
title: "PLD Anti-Patterns — What NOT To Do"
version: 2025.1
status: active
audience:
  - agent engineers
  - ux interaction designers
  - agent ops evaluators
purpose: "Identify and prevent interaction failure modes in multi-turn LLM runtimes."
---

# ❌ PLD Anti-Patterns  
### *Patterns that Lead to Drift, Collapse, or Loss of Shared Reality*

This file documents **common failure modes** seen in multi-turn, tool-enabled LLM systems.

These examples exist to help teams quickly recognize when a system is slipping outside the PLD loop — and apply the appropriate **repair + reentry** steps.

> 📌 *These are not theoretical mistakes — they were observed in real-world experiments, agent deployments, and MultiWOZ-based trials.*

---

## 🧭 How to Use This Document

If you're building or evaluating a system:

- Use this file during **debugging**
- Reference it when defining **evaluation criteria**
- Share it during onboarding to avoid **repeat mistakes**
- Link examples directly in **pull requests or logs**

Each anti-pattern includes:

Symptom → What Happens → Root Cause → Correct PLD Behavior → Example Trace Link

---

---

## ❌ Anti-Pattern #1 — Repair → Continue (No Reentry Check)

### Symptom
The system acknowledges an error or misunderstanding, fixes it, **but immediately continues the task** without confirming alignment.

### What Happens
- Small divergence compounds  
- Later turns contradict earlier constraints  
- User loses trust because model appears inconsistent  

### Root Cause
⚠️ Missing **Reentry Checkpoint** after repair.

### Correct PLD Behavior

```
Drift → Soft Repair → Reentry → Continue
```

### Example Fix

```
"Thanks — to confirm, you want X under constraint Y, correct?"
```

📎 See canonical example: `trace_examples.md#soft-repair-with-reentry`

---

---

## ❌ Anti-Pattern #2 — Tool Retry Loop

### Symptom
The agent repeatedly calls a tool with **incorrect or incomplete parameters**.

### What Happens
- Looping behavior  
- API quota waste  
- User frustration ("Why are you doing the wrong thing again?")  

### Root Cause
⚠ Drift was detected implicitly (tool failure), but **no repair policy fired**.

### Correct PLD Behavior

```
Failed Tool Call → Drift → Repair (clarify or restate constraints) → Reentry → Try again (once)
```

### Example Fix

```
"The tool returned an error. I may be missing information — which of these values applies?"
```

📎 See: `trace_examples.md#tool-correction-with-pld`

---

---

## ❌ Anti-Pattern #3 — Politeness Loop

### Symptom
The model repeatedly apologizes, restates the same content, or tries to "smooth things over" instead of progressing.

### What Happens
- Interaction stalls  
- No actionable next step  
- User confidence drops  

### Root Cause
⚠ System opts for *social safe response* instead of structural correction.

### Correct PLD Behavior

```
Polite apology (optional) → Repair → Reentry → Continue
```

### Example Fix

```
"Thanks — let's correct it and continue. To confirm: the correct value is X, right?"
```

📎 Related trace: `trace_examples.md#dialog-stabilization`

---

---

## ❌ Anti-Pattern #4 — Silent Failure (No Recovery Path)

### Symptom
The system outputs an answer even though it lost context or state.

### What Happens
- Believable hallucination  
- Inconsistent logic across turns  
- System appears confident but wrong  

### Root Cause
⚠ No drift signal, no repair attempt, no checkpoint guard.

### Correct PLD Flow

```
Drift → Detect → Repair → Reentry → Continue
```

(Not: `Detect and ignore.`)

📎 Example: `trace_examples.md#state-loss-recovery`

---

---

## ❌ Anti-Pattern #5 — Over-Repair (Reset When Not Needed)

### Symptom
The agent resets or restates too aggressively, even when the drift was minor.

### What Happens
- Increased latency  
- Reduced conversational fluidity  
- UX feels robotic or procedural  

### Root Cause
⚠ Repair logic is too sensitive or incorrectly prioritized.

### Correct Behavior

```
Small deviation → Soft Repair
Major deviation → Hard Repair
```

📎 Reference: `protocol.md#repair-selection-rules`

---

---

## 🔧 Quick Reference Summary

| Pattern | Risk Level | Fix Strategy |
|--------|------------|---------------|
| Repair → Continue (No Reentry) | ⭐⭐⭐⭐ | Always require confirmation checkpoint |
| Tool Retry Loop | ⭐⭐⭐⭐⭐ | Add drift trigger + clarification step |
| Politeness Loop | ⭐⭐⭐ | Replace apologies with structured reentry |
| Silent Failure | ⭐⭐⭐⭐⭐ | Add mandatory drift detection hook |
| Over-Repair | ⭐⭐ | Calibrate repair thresholds |

---

## 🧪 What To Do If You See These in Logs

1. Tag the event as `drift_detected`  
2. Apply the appropriate repair class  
3. Require a reentry checkpoint before execution resumes  
4. Increase supervision weight during evaluation  

---

> **Anti-patterns are not bugs — they are teaching signals.  
> They show where the runtime and operator logic need alignment.**

Maintainer: Kiyoshi Sasano  

---

