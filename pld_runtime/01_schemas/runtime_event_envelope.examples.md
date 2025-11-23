version: "2.0.0"
status: "Working Draft — Examples Library"
authority_level_scope: "Level 5 — runtime implementation"
purpose: "Provide example payloads demonstrating valid and invalid PLD runtime events using the runtime_event_envelope.json schema."
change_classification: "partial extension"
tone: "neutral documentation"

---

# Runtime Event Envelope — Examples Catalog

This file provides example payloads intended to support:

- Runtime implementation
- Validator testing
- Debugging and ingestion pipeline evaluation
- Schema drift monitoring

These examples are **illustrative only** and do not introduce new normative rules.

Additional cases may be added as implementation feedback is received.

---

## 1. Valid Example — Minimal Runtime Envelope

This example represents the smallest event satisfying validation expectations.

```json
{
  "schema_version": "2.0",
  "event_id": "00000000-0000-4000-8000-000000000000",
  "timestamp": "2025-02-01T00:00:00Z",
  "session_id": "session-123",
  "turn_sequence": 1,
  "source": "runtime",
  "event_type": "continue_allowed",
  "pld": {
    "phase": "continue",
    "code": "C0_normal"
  },
  "payload": {},
  "runtime": {},
  "ux": {
    "user_visible_state_change": false
  }
}
```

---

## 2. Valid Example — Runtime Observability Fields Present

This example demonstrates optional but commonly observed runtime metadata.

```json
{
  "schema_version": "2.0",
  "event_id": "6ec2e96b-c503-4e24-bd45-2e6d97e0fc11",
  "timestamp": "2025-02-01T00:15:48Z",
  "session_id": "sess-0021",
  "turn_sequence": 5,
  "source": "assistant",
  "event_type": "evaluation_pass",
  "pld": {
    "phase": "outcome",
    "code": "O2_resolved",
    "confidence": 0.92,
    "metadata": {
      "taxonomy_status": "canonical"
    }
  },
  "payload": {
    "response_length_tokens": 181
  },
  "runtime": {
    "latency_ms": 182,
    "model": "model-alpha-3",
    "tool": null,
    "agent_state": "stable"
  },
  "ux": {
    "user_visible_state_change": true
  },
  "extensions": {
    "environment": "dev",
    "trace_state": "sampling"
  }
}
```

---

## 3. Valid Example — M-Prefix Staging (Experimental Pattern)

This example demonstrates optional staging information for derived metrics such as PRDR or VRL.
This pattern is still considered experimental and subject to revision.

```json
{
  "schema_version": "2.0",
  "event_id": "f1b213b2-6908-4fcd-b884-3a17cb2dbe91",
  "timestamp": "2025-02-01T00:22:10Z",
  "session_id": "sess-445",
  "turn_sequence": 3,
  "source": "runtime",
  "event_type": "info",
  "pld": {
    "phase": "none",
    "code": "M0_observation",
    "metadata": {
      "taxonomy_status": "provisional"
    }
  },
  "runtime": {
    "latency_ms": 98,
    "model": "model-beta-2",
    "staging": {
      "raw_latency_delta": 42,
      "token_growth_signal": 1.2
    }
  },
  "ux": {
    "user_visible_state_change": false
  }
}
```

---

## 4. Invalid Example — Ordering Rule Violation

This example is intentionally invalid to support validator testing.

- `turn_sequence` decreases across events (non-monotonic)
- `phase` and event_type mapping do not align (`repair_triggered` but phase=`continue`)

  ```json
  {
  "schema_version": "2.0",
  "event_id": "ff4dd0ed-508c-4e79-a671-09c67c825051",
  "timestamp": "2025-02-01T00:23:55Z",
  "session_id": "sess-445",
  "turn_sequence": 2,
  "source": "runtime",
  "event_type": "repair_triggered",
  "pld": {
    "phase": "continue",
    "code": "C1_warning"
  },
  "ux": {
    "user_visible_state_change": false
  }
}
```

Expected behavior:
Validators should reject this payload or route it to a review path or DLQ, depending on selected operational model.

---

## 5. Notes for Implementers

- Example payloads may evolve as real-world telemetry patterns emerge.
- Alignment with Level 1–3 semantics always takes precedence.
- Feedback, additional examples, or edge-case findings are welcome.

---

End of examples file — v2.0.0 (partial draft)
