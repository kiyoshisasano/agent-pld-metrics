#!/usr/bin/env python
# component_id: pld_runtime_public_api
# kind: module
# area: api
# status: stable
# authority_level: 1
# purpose: Public API surface for PLD Runtime v2.0. Re-exports Level-5 interfaces only.

"""
PLD Runtime v2.0 — Public API Surface
=====================================

This module exposes the *safe public entrypoints* for integrations.

Consumers SHOULD import from here rather than internal folders:

    from pld_runtime import RuntimeSignalBridge, RuntimeLoggingPipeline

This maintains a stable integration boundary even if internals evolve.

Note:
    The internal package layout is intentionally hidden behind this module.
    If you change file locations inside `pld_runtime/`, update only the
    imports below — external integrations should remain stable.
"""

# -------------------------
# Level 5 — Runtime Detection (Signals)
# -------------------------
# Internal layout example (adjust if your package names differ):
#
# pld_runtime/
#   detection/
#     runtime_signal_bridge.py
#
from .detection.runtime_signal_bridge import (
    RuntimeSignalBridge,
    RuntimeSignal,
    SignalKind,
    EventContext,
    ValidationMode,
)

# -------------------------
# Level 5 — Logging Surface
# -------------------------
# Internal layout example:
#
# pld_runtime/
#   logging/
#     runtime_logging_pipeline.py
#     exporters/
#       exporter_jsonl.py
#
from .logging.runtime_logging_pipeline import RuntimeLoggingPipeline
from .logging.exporters.exporter_jsonl import JsonlExporter


__all__ = [
    # Detection
    "RuntimeSignalBridge",
    "RuntimeSignal",
    "SignalKind",
    "EventContext",
    "ValidationMode",

    # Logging
    "RuntimeLoggingPipeline",
    "JsonlExporter",
]
