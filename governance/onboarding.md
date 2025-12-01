# PLD Onboarding & Diagnostics for Collaborators

This document is a **practical onboarding and first-diagnostics guide**  
for teams who want to collaborate on PLD-based systems.

**Note:** PLD terminology refers to observable conversational behavior,  
 not model psychology, intention inference, or emotional state attribution.

It answers:

- How do we get a new team “PLD-literate” quickly?
- What do we look at together in the first week?
- How do we run a simple health check on a PLD integration?

---

## 1. Onboarding Objectives

By the end of onboarding, collaborators should:

1. Understand the PLD loop:
   - Drift → Repair → Reentry → Continue → Outcome
2. Recognize drift and repair in real traces
3. Know where PLD is wired into the system (runtime/integration)
4. Be able to read and interpret basic PLD metrics

They do **not** need to understand:
- All internal implementation details
- All operator codes or schema fields
- Your full infrastructure

---

## 2. 90-Minute Onboarding Session (Template)

You can adapt this agenda for a live call or internal workshop.

### Part 1 — Concepts (20–30 min)

- Walk through the PLD loop diagram:
  - What is drift, with concrete domain examples?
  - Soft vs Hard repair
  - Reentry as a checkpoint, not just a phrase
- Show how this maps to:
  - Your agent’s flow
  - Your tools / memory / RAG components

### Part 2 — Live Trace Tour (30–40 min)

Take 3–5 real or demo transcripts and:

- Ask collaborators to point where drift seems to begin
- Show the actual PLD annotations:
  - `drift.type`, `repair.mode`, `reentry.success`, `outcome.status`
- Compare their intuition with the event log
- Discuss:
  - Which repairs felt appropriate?
  - Where reentry was missing or weak?
  - How the interaction ended (outcome)

### Part 3 — Metrics Overview (15–20 min)

Show a simple dashboard or summary table:

- Drift rate
- Soft vs Hard repair ratio
- Reentry success
- Outcome distribution

Explain how these connect to decisions:

- When drift is high: tune prompts, tools, or memory
- When hard repairs dominate: adjust architecture or UX
- When reentry is weak: add confirmation patterns
- When outcomes are poor: adjust task design or constraints

### Part 4 — Next Steps (10 min)

Agree on:

- What kind of sessions to collect in the next week
- How often to review traces together
- Who will adjust what (prompts, UX, routing, tools, etc.)

---

## 3. Early Diagnostics Checklist

Use this after **1–2 weeks** of running a PLD-equipped system with a partner.

### 3.1 Drift

- [ ] Drift events are logged and visible
- [ ] Drift types (e.g. intent, information, constraint) are distinguishable
- [ ] Drift is not overwhelmingly concentrated in one scenario

### 3.2 Repair

- [ ] Soft repairs are present and understandable to humans
- [ ] Hard repairs are rare and clearly justified
- [ ] Common repair templates are defined (LLM patterns / UX copy)

### 3.3 Reentry

- [ ] Reentry confirmations exist (explicit or implicit)
- [ ] Reentry success is measured
- [ ] Sessions with failed reentry are easy to inspect

### 3.4 Outcome

- [ ] Each session or task has an outcome label
- [ ] “Partial but acceptable” vs “failed” is clearly separated
- [ ] Catastrophic failures are rare and investigated

### 3.5 Latency & Perception

- [ ] Long latency phases are signaled (typing indicator, hold pattern)
- [ ] No user abandons purely due to unexplained silence
- [ ] High-latency events appear in PLD logs

---

## 4. Shared Diagnostics Document

For each collaboration, create a shared document with:

- Link(s) to PLD dashboards
- A small set of **canonical traces**:
  - 2–3 “good” sessions
  - 2–3 “borderline” sessions
  - 1–2 “failure” sessions
- Current baseline metrics (drift, repair, reentry, outcome)
- A short list of open questions:
  - “What counts as acceptable partial completion?”
  - “Which drifts are tolerable vs. critical?”
  - “Which tools are most fragile?”

This becomes the **reference point** for:

- deciding whether a PLD integration is “good enough”
- tracking changes over time
- onboarding new engineers or partners

---

## 5. What Not to Over-Optimize in Early PoC

During early joint experiments, avoid:

- Numerical micro-optimization (±1–2% metric changes)
- Overfitting to a single scenario
- Treating every drift as a bug

Instead, focus on:

- Are we seeing **the right kinds of repair**?
- Is reentry helping, not annoying, users?
- Are we catching catastrophic failures before they reach users?

---

> Onboarding is not about teaching PLD in full.  
> It is about giving collaborators **just enough structure**  
> so their intuition lines up with the PLD runtime loop.

