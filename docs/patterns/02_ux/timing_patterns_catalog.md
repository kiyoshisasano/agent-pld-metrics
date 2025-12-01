# Timing Patterns Catalog — Applied UX for LLM Interaction Systems  
*(Timing as a Meaning-Bearing Interaction Layer)*

**Purpose:**  
Provide a practical catalog of timing-aware interaction patterns that reduce perceived drift, increase trust, and stabilize multi-turn AI experiences — especially in latency-sensitive environments (LLMs, tool calls, multi-agent pipelines).

**Audience:**  
UX designers, frontend engineers, and applied AI builders implementing timing-aware human-machine interaction.

---

## 01 — Why Timing Matters

In AI systems, **time itself communicates meaning.**

Users interpret delays as signals:

| Delay Duration | User Interpretation |
|----------------|---------------------|
| **0–300ms** | Machine-like responsiveness |
| **300–900ms** | “Thinking…” |
| **1–2.2s** | Ambiguity forming |
| **2.2–3.5s** | Doubt or distrust |
| **3.5s+** | Something is wrong |

→ The interface must **communicate timing**, not let silence decide meaning.

---

## 02 — Timing as a Repair Mechanism

Timing response patterns map directly to PLD:

| Phase | Timing Cue | Function |
|-------|------------|----------|
| **Drift** | Delay spike | Detect confusion or mismatch |
| **Soft Repair** | Micro delays + clarifying message | Stabilize correctness |
| **Hard Repair** | Intentional pause | Reset expectations |
| **Reentry** | Rhythmic pacing | Return user to task mode |
| **Resonance** | Stable rhythm | Predictability builds trust |

Timing preserves emotional and cognitive stability.

---

## 03 — Core Timing Patterns

### **3.1 — Progressive Disclosure Loading**

Use staged messaging rather than a single spinner.

```
0–500ms → Subtle pulse
500–1800ms → "Checking availability…"
1800–3500ms → "Still working — this step usually takes a moment."
>3500ms → Retry / adjust / continue option
```

✔ Prevents perceived stalling  
✔ Reinforces transparency  
✔ Aligns expectations  

---

### **3.2 — Micro-Acknowledgment Pattern**

Triggered when the system receives input but response generation is not instant.

Examples:

- “Got it.”
- “Okay, processing that.”
- “One moment…”

Reduces abandonment impulses during **600–2400ms** latency windows.

---

### **3.3 — Rhythmic Messaging Pattern**

Ensure timing consistency across responses.

If one turn takes **2.2s** and another **0.6s**, users feel instability.

Solution:

```
min(wait_time, 1.2s) → normalize output cadence
```

Humans prefer **predictable rhythm** over unpredictable speed.

---

### **3.4 — Pre-Commit Loading**

Used before irreversible actions (e.g., booking, payment).

Pattern:

```
1) Micro-confirmation → "Preparing booking…"
2) Visual lock state → optimistic hold
3) Execution → response + reentry
```

Protects trust under high-stakes actions.

---

## 04 — Timing + Tone Matrix

Timing isn't neutral — tone must match user emotional state.

| Situation | Timing Requirement | Tone Mode |
|-----------|--------------------|-----------|
| Neutral task | Stable rhythm | Efficient |
| Ambiguity | Faster acknowledgment | Reassuring |
| Failure recovery | Deliberate pacing | Transparent |
| Reentry after repair | Calm cadence | Confidence-restoring |

Predictability > speed.

---

## 05 — When Timing Becomes Semantics

Timing carries meaning when:

| Signal | User Interpretation |
|--------|---------------------|
| Sudden silence | Confusion or failure |
| Quick correction | Detected repair |
| Long pause after drift | Risk of abandonment |
| Stable rhythm resumes | System has recovered |

Timing is a communicative layer.

---

## 06 — Anti-Patterns

Avoid:

- ❌ Unstructured silence > **2.5s**
- ❌ Spinners with no meaning-based text
- ❌ Rapid message bursts (chaotic pacing)
- ❌ Confident tone after long latency
- ❌ Freezing UI as “thinking state”

These destroy perceived competence even if content is correct.

---

## 07 — Metrics for Production Systems

Recommended telemetry signals:

| Metric | Purpose |
|--------|---------|
| **First Meaningful Response Time (FMRT)** | Predict abandonment |
| **Soft Repair latency variance** | Detect hesitation patterns |
| **Turn-to-turn latency stability** | Detect rhythm collapse |
| **Time-to-task-completion** | Measure UX fluency |

These map to PLD telemetry.

---

## 08 — Implementation Checklist

✔ Acknowledge user input within 600–1200ms  
✔ Normalize response rhythm across turns  
✔ Use staged messaging under latency  
✔ Show fallback when delay exceeds threshold  
✔ Match tone to timing context  
✔ Use timing as a recovery mechanism  

---

## Attribution

Maintainer: **Kiyoshi Sasano**  
File: `patterns/02_ux/timing_patterns_catalog.md`  

License: **CC BY 4.0**
