# PLD PoC Kickoff Guide — 1‑Page Business Overview

This one‑page guide helps teams begin a PLD (Phase Loop Dynamics) Proof‑of‑Concept quickly, with a shared understanding of goals, expectations, and success criteria. It is designed for **business stakeholders, PMs, CX leads, partner teams, and non‑technical collaborators**.

PLD provides a **common language** for evaluating the stability of AI assistants and tool‑enabled agents. It helps different organizations align on what “went wrong,” what “worked,” and how to improve systems over time.

---

## 🌐 What Is PLD? (Business Definition)

PLD is a **behavioral evaluation framework** that makes AI system behavior easier to understand, measure, and improve.

It focuses on four observable stages:

```
Drift → Repair → Reentry → Outcome
```

* **Drift** — the system goes off‑track
* **Repair** — the system attempts to fix the issue
* **Reentry** — both sides confirm alignment before continuing
* **Outcome** — the final result (success, partial, failure)

These concepts let two organizations discuss system behavior **clearly and consistently**, without requiring access to proprietary code or model internals.

---

## 💼 Why PLD Matters for Business

PLD helps teams:

* Reduce unpredictable or unstable AI responses
* Detect harmful or confusing patterns early in testing
* Make PoC evaluations **repeatable and objective**
* Align partner teams on what counts as a “failure” or “success”
* Communicate issues clearly without sharing sensitive data
* Improve customer experience through stability insights

PLD lowers the barrier for collaboration by ensuring everyone is “speaking the same language” about AI behavior.

---

## 📊 What PLD Enables (Outputs)

During a PoC, PLD produces actionable insights such as:

* **Drift Rate** (How often the system goes off track)
* **Repair Effectiveness** (How often the system recovers)
* **Reentry Confirmation Rate** (How reliably alignment is restored)
* **Outcome Distribution** (Success / Partial / Failure)
* **Session‑level notes** highlighting critical issues

These outputs feed into roadmap planning, product decisions, and partner alignment.

---

## 🚀 What You Need to Start

A PLD PoC requires only lightweight preparation:

* **1–3 scenarios** you want to evaluate
* **5–10 example sessions** (internal or user‑generated)
* Basic understanding of Drift / Repair / Reentry
* Agreement on masking or sanitization rules
* High‑level description of tools or workflows involved

Teams do *not* need schema knowledge, model internals, or detailed runtime understanding.

---

## 📅 The PoC Flow (Fast Overview)

A typical PLD PoC follows a simple 3‑step loop:

### **1. Define Scope (Day 1)**

* Target system
* Scenario(s) under evaluation
* Timebox (usually 2–4 weeks)
* Expected business outcomes

### **2. Collect Sessions (Days 2–5)**

* Capture 5–10 real interactions
* Mask sensitive content
* Annotate using the Starter Kit submission template

### **3. Joint Review (Days 6–7)**

* Identify where drift occurred
* Evaluate whether repairs were appropriate
* Verify reentry and outcomes
* Decide next steps (improve, iterate, expand)

This process provides a shared, evidence‑based view of system stability.

---

## 👥 Who This Guide Is For

* Partner organizations evaluating your AI system
* Product and business teams running a trial
* PMs, analysts, QA, CX, and operations teams
* Anyone needing a clear, non‑technical explanation of PLD

---

A PLD PoC is designed to be fast, lightweight, and collaborative.
This guide is the first step toward a shared understanding of how your system behaves — and how it can improve.
