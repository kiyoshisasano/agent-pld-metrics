# PLD Scope Template — Example (Filled Version)

This document shows a **completed example** of the PLD Scope Template.
It demonstrates how a team might fill out the scope before starting a Proof-of-Concept (PoC).

Use this example as guidance when completing your own `PLD_scope_template.md`.

---

## 1. Project Overview

**Purpose of the PoC:**
Evaluate whether PLD improves stability and task completion in a customer-support assistant that uses RAG and 2 tools.

**Target System:**
Customer Support Agent (RAG + Internal Tools)

**Environment:**
Staging (Internal users only)

**Time Box:**
3 weeks (2 weeks data collection + 1 week joint review)

---

## 2. Scenarios Under Evaluation

1. **Password Reset Assistance**
   Agent retrieves account info and guides users through steps.
2. **Billing Dispute Flow**
   User explains an unexpected charge; agent uses billing API to cross-check.
3. **Order Tracking + Escalation**
   Agent tracks shipment status and escalates unresolved cases.

---

## 3. Tools and Capabilities Involved

* **Tooling / APIs:**

  * Billing API
  * Account Management API
* **RAG Components:**

  * Knowledge base search
  * Policy retrieval
* **Workflow Logic:**

  * Action router
  * Error-handling layer

---

## 4. Success Criteria (Biz-Level)

These values are examples and should be adjusted based on domain and risk.

* **Drift rate target:** ≤ 15% of turns
* **Soft repair recovery:** ≥ 70%
* **Reentry consistency:** ≥ 80%
* **Outcome success rate:** ≥ 75%
* **Critical failures:** 0 catastrophic workflow breaks

---

## 5. Collaboration Roles

**Partner A (Implementation):**

* "Acme AI Solutions" — Runtime + Logs
* Owner: Jane Doe (AI Engineer)

**Partner B (Review):**

* "Contoso Research" — PLD Review & Metrics
* Owner: Alex Kim (Applied Research)

**Communication Cadence:**

* Weekly async updates
* Bi-weekly synchronous review

---

## 6. Notes / Known Constraints

* Some production prompts cannot be shared; masked transcripts will be used.
* RAG retrieval sometimes fails for rare queries; expected drift source.
* Tool latency may create false user abandonment—will be monitored.

---

This example can be shared with partners to illustrate the level of detail expected before a PLD PoC kickoff.
