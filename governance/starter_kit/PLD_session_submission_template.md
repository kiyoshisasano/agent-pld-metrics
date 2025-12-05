# File: PLD_session_submission_template.md

## PLD Session Submission Template (For First Week)

**How to use:**

1. Provide 5–10 representative sessions.
2. Mask any sensitive text.
3. Include PLD logs if available.

---

### 1. Session List

Provide a short description for each.

| Session ID | Summary (1 line)                              |
| ---------- | --------------------------------------------- |
| sess_001   | "User attempts booking; agent confuses date." |
| sess_002   | "Tool call fails twice; agent recovers."      |

---

### 2. Session Details (repeat per session)

```
Session ID: sess_001
Masked Transcript:
- User: "Book a flight to <MASKED_CITY>"
- Agent: "Hotels in <MASKED_CITY>?"  (Drift)

PLD Events (if available):
- drift_code: <e.g., D3_intent>
- repair_type: <e.g., soft>
- reentry: <pass/fail>
- outcome: <success/partial/fail>
```

---

### 3. Notes for Review

* What seemed to cause drift?
* Was the repair appropriate?
* Did reentry confirm alignment?

---

This completes the lightweight starter kit drafts. Add each section as a separate file under `governance/starter_kit/`.
