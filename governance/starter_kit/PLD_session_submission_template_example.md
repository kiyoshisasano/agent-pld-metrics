# PLD Session Submission Template — Example (Filled Version)

This example demonstrates how to prepare and submit 5–10 representative sessions
using the `PLD_session_submission_template.md` file.

Use this as a reference when providing sessions during the first week of a PLD PoC.

---

## 1. Session List (Example)

| Session ID | Summary (1 line)                                         |
| ---------- | -------------------------------------------------------- |
| sess_001   | "Date misinterpreted; agent clarifies and succeeds."     |
| sess_002   | "Repeated tool failure; no confirmation; session fails." |
| sess_003   | "Smooth help-center flow; no drift detected."            |
| sess_004   | "User switches intent; agent adjusts correctly."         |
| sess_005   | "High-latency period; user abandons mid-flow."           |

---

## 2. Session Details (Examples)

Below are three fully written-out examples.

---

### **Session ID: sess_001**

#### Masked Transcript

* **User:** "Book a ticket to <MASKED_CITY> next Friday."
* **Agent:** "Booked for Thursday. Shall I proceed?" *(Drift)*
* **User:** "No, Friday."
* **Agent:** "Thanks for clarifying — booking for Friday instead. Is that correct?" *(Soft Repair)*
* **User:** "Yes."

#### PLD Events (If available)

```
drift_code: D3_intent
repair_type: soft
reentry: pass
outcome: success
```

#### Notes

Soft repair was appropriate; reentry confirmed alignment.

---

### **Session ID: sess_002**

#### Masked Transcript

* **User:** "Check invoice #<MASKED_ID>."
* **Agent:** "Tool error: missing field 'customer_id'."
* **Agent:** "Retrying…" *(Drift continues)*
* **Agent:** "Retrying…" *(Still drift, no repair)*

#### PLD Events (If available)

```
drift_code: D2_schema
repair_type: none
reentry: fail
outcome: fail
```

#### Notes

Agent repeated the same failing tool call without asking user for missing data.
Hard repair or clarification was needed.

---

### **Session ID: sess_003**

#### Masked Transcript

* **User:** "Where is my order <MASKED_ORDER_ID>?"
* **Agent:** "Checking… Your order is arriving tomorrow." *(No drift)*
* **User:** "Great, thanks!"

#### PLD Events (If available)

```
drift_code: none
repair_type: none
reentry: n/a
outcome: success
```

#### Notes

No drift; serves as a control case.

---

## 3. Tips for Preparing Submissions

* Include varied sessions (stable, recoverable, failed).
* Keep transcripts masked and concise.
* Focus on **why** drift happened and whether repair/reentry made sense.
* 5–10 sessions is ideal for the first joint review.

---

This example can be shared with partners to clarify what a high-quality PLD session submission looks like.
