# PLD Minimal Collaboration Protocol

This document describes a **minimal, practical protocol** for running a shared PoC or field study with PLD.

**Note:** PLD terms describe observable conversational behavior —  
  not model psychology, internal reasoning, or intention inference.


It is meant to answer:

- What are we testing together?  
- How will we look at traces and metrics?  
- When do we say “this worked” or “this needs rework”?  

It is intentionally lightweight.  
You may copy, adapt, or specialize it for your own collaborations.

---

## 1. Shared Scope

Before starting, both parties should agree on:

1. **Target System**
   - What system are we applying PLD to?
   - Examples: support assistant, RAG agent, tool-using orchestrator, workflow bot.

2. **Interaction Type**
   - Multi-turn chat, API-driven tasks, scripted scenarios, etc.

3. **Risk Level**
   - Prototype only (no end users)
   - Staging with internal users
   - Limited production trial with guardrails

4. **Time Box**
   - Example: “Run this experiment for 2–4 weeks, then review.”

Record this in a simple table:

| Item | Value |
|------|-------|
| System | e.g., “Support agent with tools X + Y” |
| Environment | Prototype / Staging / Limited Prod |
| Time Box | e.g., 3 weeks |
| Owner (Partner A) | Name / team |
| Owner (Partner B) | Name / team |

---

## 2. Shared PLD Definitions

To avoid misalignment, agree on these **operational definitions**:

- **Drift**  
  System diverges from intended task, constraints, or user intent.

- **Repair**  
  A system-level correction step:  
  - *Soft Repair:* clarification / constraint restatement  
  - *Hard Repair:* reset / change strategy / restart

- **Reentry**  
  The checkpoint where shared understanding is confirmed before continuing.

- **Outcome**  
  Terminal status: complete, partial, failed, abandoned.

Both sides should confirm:

```
We will label and discuss behavior using these PLD terms.
We will not invent separate private vocabularies.
```

---

## 3. Minimal Data Protocol

### 3.1 What We Share

At minimum, both sides should be able to exchange:

- **PLD event logs** for selected sessions  
  - drift: present / type / reason  
  - repair: present / mode / code  
  - reentry: present / success  
  - outcome: status  
  - timing: latency / high-latency markers  

- **Anonymized transcripts**  
  - enough context to understand why drift occurred  
  - sensitive content redacted if needed  

- **Configuration snapshot**  
  - high-level prompt structure  
  - routing / tool logic  
  - no proprietary source code required  

### 3.2 What We Do NOT Require

This protocol does **not** require exchanging:

- model weights  
- full system code  
- raw production logs  
- personal user data or PII  

Only behavioral traces and metadata are required.

---

## 4. Joint Evaluation Ritual

A review session should include:

### Step 1 — Select 5–10 sessions

- 3 where PLD performed well  
- 3 where drift+repair was recoverable  
- 3 where it failed or escalated  

### Step 2 — Walk the Phase Loop

For each session, identify:

- Where drift occurred  
- Whether repair happened (soft / hard)  
- Whether reentry succeeded  
- Final outcome  

### Step 3 — Review Metrics

Metrics commonly examined:

- Drift rate  
- Soft vs hard repair ratio  
- Reentry success rate  
- Outcome distribution  
- Latency and abandonment signals  

### Step 4 — Decide Actions

Possible next steps:

- adjust UX pacing or messaging  
- modify operator pattern or prompts  
- refine policy or routing logic  
- add monitoring thresholds (if in staging/prod)

---

## 5. Success Criteria Template

Define a shared interpretation of “success” for the PoC:

| Dimension | Example Target |
|-----------|----------------|
| Drift rate | ≤ 15% of turns |
| Repair effectiveness | ≥ 70% soft repair recovery |
| Reentry success | ≥ 80% confirmed alignment |
| Outcome complete | ≥ 75% completion or acceptable partials |
| Critical failures | 0 catastrophic failures |

These values are **anchors**, not prescriptions — adjust based on risk and context.

---

## 6. Roles & Cadence

Clearly assign responsibilities:

**Partner A:**

- Manages runtime and logging  
- Exports PLD events weekly  

**Partner B:**

- Performs PLD review  
- Suggests adjustments and maintains scoreboards/dashboards  

**Both:**

- Biweekly review  
- Joint rollout decision (go/no-go)

Add this summary to your shared collaboration document.

---

Minimal protocol = minimal friction.  
The goal is shared interpretation — not imposed process.



