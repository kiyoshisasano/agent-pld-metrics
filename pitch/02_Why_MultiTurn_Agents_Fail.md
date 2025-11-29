<!--
path: pitch/02_Why_MultiTurn_Agents_Fail.md
kind: doc
audience: product leaders, engineering leads, applied ML teams
status: exploratory
authority_level: 1
version: 0.1.0
purpose: Describe why multi-turn AI systems become unstable, using relatable examples and narrative framing.
license: CC-BY-4.0
feedback: "If this resonates — or if your experience differs — feedback is welcome."
-->

# Why Multi-Turn Agents Fail  
*A short story most teams eventually recognize.*

---

At first, the assistant works.

The demo looks great.  
The first user tests go smoothly.  
A few dialogs even feel… **smart.**  

Then it scales.

- Different users ask in different ways  
- The agent receives unexpected context  
- A tool call fails  
- The conversation drifts slightly — then again — and again  

Nothing *breaks* outright.  
But the behavior becomes unpredictable.

---

## The Pattern We See Repeated

Across support bots, RAG assistants, planning agents, and internal copilots, the same failure curve appears:

| Phase | What it looks like |
|-------|--------------------|
| **Turn 1–3:** Stable | Answers are consistent and useful |
| **Turn 4–7:** Drift begins | The agent repeats, contradicts itself, or forgets context |
| **Turn 8+:** Collapse | Hallucination, wrong tool usage, or disconnected responses |

This isn’t a model capability issue — it’s a **behavioral stability problem.**

---

## A Real Example (Simplified)

```
User: Summarize the last decisions made in this session.
Agent: What decisions? Please restate them.
User: You said them earlier.
Agent: I don’t have that context.
User: …
```


The assistant didn’t *fail* —  
it simply lost alignment with the interaction.

---

## Expected Behavior (With Stability Principles in Place)

User: Summarize the last decisions made in this session.  
Agent: Here’s what I have so far — tell me if anything is missing:

1. A → Approved  
2. B → Needs revision  
3. C → Pending confirmation  


Not perfect — but predictable, recoverable, and aligned.

---

## The Core Insight

Multi-turn AI doesn’t degrade because it lacks information.  
It degrades because it lacks **mechanisms to recognize and correct behavioral drift.**

Once drift begins, every additional turn **amplifies entropy.**

---

## Why This Matters

When teams test early prototypes, behavior feels fine.  
But when the system meets:

- real users  
- longer conversations  
- tool calls  
- edge cases  
- retries  
- multiple models or routing  

…the cracks show.

Operational cost rises.  
Confidence drops.  
Agents stall in “promising prototype” status.

---

## The Opportunity

Stability isn’t magic — it’s a **runtime discipline.**

Understanding *why* these failures occur is the first step toward designing systems that:

- stay aligned  
- recover gracefully  
- and continue executing the intended task  

not just in one turn —  
but **across the entire interaction.**

---

> *If your team has experienced this pattern, you’re not alone —  
and there are ways to manage it without redesigning everything that already works.*

---

**Before (Typical Behavior Without Governance Layer)**

