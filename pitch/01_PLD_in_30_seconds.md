---
path: pitch/01_PLD_in_30_seconds.md
kind: doc
audience: product leaders, engineering leads, applied ML teams
status: exploratory
authority_level: 1
version: 0.1.0
purpose: Provide a concise, business-friendly explanation of PLD, suitable for internal onboarding or executive review.
license: CC-BY-4.0
feedback: "Feedback welcome — this document is evolving."
---

# PLD in 30 Seconds  
*A high-level explanation for teams evaluating multi-turn AI systems.*

---

Most multi-turn AI systems fail **not because they lack knowledge**,  
but because their behavior becomes **unstable over time**.

PLD (Phase Loop Dynamics) introduces a lightweight **runtime governance layer** that:

- observes how the system behaves across turns  
- detects when behavior begins to drift  
- guides recovery and continuation without replacing the existing architecture  

PLD is **not a framework, model, or agent library.**  
It works **alongside** tools like LangGraph, Assistants API, Rasa, and custom orchestration —  
helping teams maintain **predictable behavior, recoverability, and observability** as complexity grows.

In short:

> **“PLD keeps multi-turn AI stable — without requiring you to rebuild what already works.”**

---
