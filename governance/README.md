# PLD Field Collaboration & PoC Guide

This folder exists for **collaborating with other teams or organizations** using PLD.

While the rest of the repository focuses on:

- understanding the PLD runtime loop  
- implementing operators and patterns  
- logging and evaluating behavior  

`field/` focuses on:

- how to **run a shared PoC**
- how to **align interpretation of drift / repair / reentry**
- how to **exchange traces and metrics safely**
- how to **decide whether a PLD integration “works” in a real environment**

It is not a legal agreement.  
It is a **lightweight operational playbook** for applied collaboration.

---

## When to Use This Folder

Use `field/` when:

- you are involving **another team or organization** in a PLD experiment  
- you want to share **traces, metrics, and configurations**  
- you need a **repeatable framework** for alignment during a PoC  

Typically, this becomes relevant **after**:

1. You have a local PLD prototype (`quickstart/`)
2. You are logging PLD events (`quickstart/metrics/`)
3. (Optional) You’ve explored reference examples  
   → `quickstart/patterns/04_integration_recipes/`
4. You have several real interaction traces (`analytics/`-style logs)

Then:

```
local prototype → shared PoC → field deployment
                  ↑
                this folder
```

---

## Files in This Folder

| File | Purpose |
|------|---------|
| `pld_minimal_collaboration_protocol.md` | Lightweight shared PoC protocol |
| `pld_onboarding_and_diagnostics.md` | First-week diagnostics and alignment |
| `pld_trace_examples.md` | Annotated examples to align interpretation |

---

## Who This Is For

- External collaborators evaluating PLD with you  
- Product + applied AI teams piloting PLD  
- Internal org teams scaling PLD across surfaces  
- Anyone who needs shared operational language for drift/repair/reentry  

> PLD describes **observable system behavior**, not psychology or intent inference.

---

## `field/pld_minimal_collaboration_protocol.md`

```markdown
# PLD Minimal Collaboration Protocol
A practical, lightweight protocol for joint evaluation and PoC testing.

It answers:

- What are we testing together?
- How will we interpret traces and metrics?
- How do we define “works” vs “needs refinement”?

It is intentionally short and customizable.
```

---

## 1 — Shared Scope

Before starting, clarify:

| Dimension | Notes |
|-----------|-------|
| Target System | e.g., tool-based assistant, RAG agent, workflow bot |
| Interaction Type | chat, task API, scripted scenario |
| Risk Level | prototype → staging → guarded production |
| Time Box | e.g., 2–4 weeks before review |

---

## 2 — Shared PLD Definitions

To avoid mismatched assumptions, a shared vocabulary helps:

- **Drift** = misalignment from task intent or context  
- **Repair** = soft clarification or hard recovery/reset  
- **Reentry** = checkpoint confirming alignment before continuation  
- **Outcome** = complete, partial, failed, or abandoned

Both sides may find it helpful to confirm:

```
We will use shared PLD terms.
We will avoid creating private or alternate taxonomies.
```

---

## 3 — Minimal Data Protocol

### 3.1 What We Share

- PLD event logs
- anonymized transcripts
- high-level configuration snapshot

### 3.2 What We Do **Not** Require

- raw production logs  
- model weights  
- private prompts or code  
- PII  

Only **behavioral traces and metrics**.

---

## 4 — Joint Evaluation Ritual

### Step 1 — Review 5–10 sessions

- 3 stable  
- 3 recovered  
- 3 failed or escalated  

### Step 2 — Walk the Loop

- Where did drift start?  
- Was repair attempted? soft/hard?  
- Did reentry succeed?  
- What was the final outcome?  

### Step 3 — Look at Metrics

- Drift frequency  
- Soft vs hard repair ratio  
- Reentry confirmation rate  
- Outcome distribution  
- Latency / abandonment signals  

For detailed definitions of these metrics,  
see: `/docs/07_pld_operational_metrics_cookbook.md`  
(PRDR, REI, VRL reference definitions)

### Step 4 — Decide Next Action

UX → operator → routing → monitoring refinement.

---

## 5 — Shared Success Criteria Template

| Dimension | Example Target |
|----------|----------------|
| Drift rate | ≤ 15% on target flows |
| Soft repair recovery | ≥ 70% |
| Reentry confirmation | ≥ 80% |
| Outcome success | ≥ 75% |
| Critical failures | 0 in N sessions |

Targets adjust by domain and risk.

---

## 6 — Roles & Cadence

| Role | Responsibility |
|------|---------------|
| Partner A | Implementation + log export |
| Partner B | Review + metrics + recommendations |
| Both | Bi-weekly check-in + go/no-go decision |

Minimal protocol → minimal friction → high alignment.

---

Maintainer: **Kiyoshi Sasano**  

