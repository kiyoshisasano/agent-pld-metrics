<!--
component_id: langgraph_assistants_readme
kind: doc
area: integration
status: stable
authority_level: 2
purpose: Documentation for the LangGraph observer-mode integration example.
-->

# LangGraph + OpenAI Assistants API + PLD Runtime v2.0 (Observer Mode)

> Status: **Working Draft / Exploratory Stage**
> Scope: Minimal, non-disruptive PLD observer integration example
>
> This document reflects the **current working understanding** of how to layer
> PLD runtime v2.0 on top of a LangGraph agent. It is not final and is
> **actively seeking implementation feedback**.

---

## 1. What is this example?

This directory contains a **minimal, observer-mode integration** of:

* **LangGraph**
* **OpenAI Assistants-style API**
* **PLD runtime v2.0**

The goal is to show how you can **"put PLD on top" of an existing LangGraph
agent** without changing the agent's control flow or behavior.

High-level data flow:

```text
user → LangGraph graph → Assistant node (OpenAI Assistants API)
     → PLD observer (RuntimeSignalBridge + RuntimeLoggingPipeline)
     → JSONL PLD events (future OTel-compatible)
```

In other words:

* LangGraph still decides **what the agent does next**.
* PLD runtime just **watches what happens** and emits **structured PLD events**.

This example is intended as a **learning / integration guide**, not as a
canonical or production-ready design.

---

## 2. Repository layout

```text
examples/langgraph_assistants/
  README.md                # This file (overview & how to run)
  config.yaml              # Minimal configuration (model, PLD mode, log path)
  run.py                   # Entry point (loads config, builds graph, runs session)
  graph.py                 # LangGraph graph definition (wires in PLD observer)
  agent_node.py            # LangGraph node that wraps the OpenAI Assistants API
  pld_runtime_integration.py
                          # "Observer-only" bridge from LangGraph state to PLD runtime
```

Each file is deliberately small and focused, so you can copy or adapt them into
your own experiments.

---

## 3. PLD runtime role in this example

This example treats PLD runtime v2.0 as a **runtime observability layer**.

### 3.1 What PLD does here

* Looks at the LangGraph state after each assistant turn

* Chooses a `SignalKind` such as:

  * `CONTINUE_NORMAL` for nominal turns
  * `TOOL_ERROR` for simple/tool-related failure
  * `SESSION_CLOSED` for the last turn

* Builds:

  * a `RuntimeSignal`
  * an `EventContext`

* Calls:

  ```python
  event = bridge.build_event(signal=signal, context=context)
  ```

* Forwards the resulting event dict into a `RuntimeLoggingPipeline` with a
  `JsonlExporter`, which writes JSONL lines to disk.

### 3.2 What PLD does **not** do here

* It does **not** decide control flow in LangGraph.
* It does **not** implement repair or failover strategies.
* It does **not** invent new PLD `event_type`, `phase`, or taxonomy codes.
* It does **not** modify the event dict after `build_event(...)`.

The PLD layer is intentionally **observer-only**.

---

## 4. Files in more detail

### 4.1 `agent_node.py` — Application logic (LLM node)

* Wraps the OpenAI Assistants-style API as a single LangGraph node.
* Reads and updates `state["messages"]` (a chat-style list of `{role, content}`).
* **Does not know about PLD** at all.

This separation keeps your application code independent from PLD concerns.

---

### 4.2 `pld_runtime_integration.py` — PLD observer bridge

This module is the core of the example.

Responsibilities:

* Initialize the PLD observer stack via:

  ```python
  init_pld_observer(jsonl_path=..., validation_mode=...)
  ```
And, at the end of the run, you may optionally call:

```python
shutdown_pld_observer()
```

to flush and close the underlying logging pipeline.

* Expose simple, observer-only functions:

  ```python
  emit_continue_event(state)
  emit_tool_error(state, reason)
  emit_session_closed(state)
  ```

* Internally, these functions:

  * Extract `session_id`, `turn`, `model` from the LangGraph state
  * Construct a `RuntimeSignal` with a suitable `SignalKind`
  * Construct an `EventContext`
  * Call `RuntimeSignalBridge.build_event(...)`
  * Pass the resulting event into a `RuntimeLoggingPipeline`

Important constraints:

* PLD events are **never** built by hand as dictionaries here.
* After `build_event(...)`, the event dict is treated as **immutable** and is only
  forwarded to the logging pipeline.
* Only existing PLD taxonomy / event types are used; no new codes are introduced.

---

### 4.3 `graph.py` — LangGraph wiring

* Builds a small `StateGraph` with a single node (`assistant`).
* For each turn:

  * Calls `AssistantNode.run(state)` to produce the assistant reply.
  * Calls `emit_continue_event(state)` as a side-effect observer.
* Does **not** perform any PLD-specific logic besides calling the observer.

This demonstrates how PLD can be attached as a **side-channel** without
changing the graph structure.

---

### 4.4 `run.py` — Example entry point

* Adds the repo root to `sys.path` so `pld_runtime` and this example package can
  be imported in a simple clone.
* Loads `config.yaml`.
* Verifies that `OPENAI_API_KEY` is set in the environment.
* Initializes the PLD observer via `init_pld_observer(...)`.
* Builds the LangGraph app via `build_graph(model=...)`.
* Creates an initial state and runs a short loop of turns.
* Emits a final `SESSION_CLOSED` event and prints:

  * The final state
  * The JSONL log path

This file is intentionally straightforward so that you can easily adapt it to
other environments (e.g., notebooks, services).

---

## 5. Configuration and API keys

### 5.1 `config.yaml`

A minimal example:

```yaml
model: gpt-4.1-mini
pld_validation_mode: strict

logging:
  jsonl_path: "logs/langgraph_pld_demo.jsonl"
```

* `model` — OpenAI model id to use.
* `pld_validation_mode` — used to configure `RuntimeSignalBridge`.

  * Typical values: `strict`, `warn`, `normalize`.
* `logging.jsonl_path` — where PLD JSONL events will be written.

### 5.2 Secrets and environment variables

> **Important:** Do **not** store API keys or secrets in `config.yaml`.

Instead, set:

```bash
export OPENAI_API_KEY="sk-..."   # macOS / Linux
set OPENAI_API_KEY=sk-...        # Windows (Command Prompt)
```

The example reads the key from the `OPENAI_API_KEY` environment variable.

---

## 6. How to run

From the repository root:

```bash
export OPENAI_API_KEY="sk-..."  # or your platform equivalent

python examples/langgraph_assistants/run.py
```

You should see:

* A few turns of conversation printed to stdout.
* A `Final state: {...}` summary.
* A line indicating where the PLD JSONL logs were written.

Example:

```text
Final state: {'session_id': 'demo-session-1', 'turn': 4, 'model': 'gpt-4.1-mini', 'messages': [...]}
PLD JSONL logs → logs/langgraph_pld_demo.jsonl
```

---

## 7. Status and feedback

This example is in an **exploratory / working draft** phase.

It aims to:

* illustrate how PLD runtime v2.0 can be layered on top of LangGraph agents
* provide a small, readable starting point for your own experiments
* remain open to revision as the PLD runtime and LangGraph ecosystems evolve

If you adapt or extend this example:

* consider sharing back what worked and what did not
* feel free to adjust the structure as long as Level 1–3 PLD constraints remain
  intact and Level 5 APIs are consumed rather than redefined

This document is **not yet finalized** and may change based on real-world
feedback and evaluation.
