# PLD Runtime Architecture

> **Scope: Level 4–5 Concerns**
> This directory covers runtime design, controller structure, and integration patterns.

## 🏗️ Overview

While specifications (Level 1–3) define *what* PLD is, the Architecture defines *how* it is implemented in a runtime environment.

* **Principles**: Core design philosophy (Observer pattern, Loop integrity).
* **Layers**: How the runtime connects to agents (Signal Bridge, Enforcers).
* **Modes**: Differences between Observer (Async) and Governor (Sync) modes.