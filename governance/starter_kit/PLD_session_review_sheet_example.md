# PLD Session Review Sheet — Example (Filled Version)

This example shows how to complete the lightweight PLD Session Review Sheet
using three representative sessions from an early PLD PoC.

Use this file as a guide when filling out your own `PLD_session_review_sheet.md`.

---

## Example Review Table

| Session ID | Drift Occurred? | Repair Type | Reentry Confirmed? | Outcome | Notes                                                                                |
| ---------- | --------------- | ----------- | ------------------ | ------- | ------------------------------------------------------------------------------------ |
| sess_001   | Yes             | Soft        | Yes                | Success | Agent misinterpreted date; user corrected; agent clarified.                          |
|            |                 |             |                    |         |                                                                                      |
| sess_002   | Yes             | Hard        | No                 | Fail    | Tool call failed twice; agent repeated incorrect call; no confirmation before retry. |
|            |                 |             |                    |         |                                                                                      |
| sess_003   | No              | None        | N/A                | Success | Smooth flow; no drift detected; task completed.                                      |

---

## Session Summaries

### **sess_001 — Soft Repair Example**

* **Drift:** Agent assumed the wrong date.
* **Repair:** Agent asked for clarification.
* **Reentry:** Confirmed successfully.
* **Outcome:** Successful booking.
* **Why it matters:** Shows that soft repair works well for mild misunderstandings.

---

### **sess_002 — Hard Repair Needed but Incomplete**

* **Drift:** Repeated tool schema error.
* **Repair:** Agent attempted a hard repair but didn’t confirm alignment.
* **Reentry:** Missing.
* **Outcome:** Failure.
* **Why it matters:** Highlights need for better tool-error handling.

---

### **sess_003 — No Drift Case**

* **Drift:** None.
* **Repair:** None.
* **Reentry:** Not applicable.
* **Outcome:** Smooth, correct flow.
* **Why it matters:** Provides a control case for comparison.

---

## How to Use This Example

* Compare these rows with your own sessions.
* Keep notes brief (1–2 sentences).
* Focus on whether repair and reentry happened.
* Use plain language — PLD specialist knowledge not required.

This example represents a typical early-stage PoC with a mix of stable flows, recoverable drifts, and failure cases.
