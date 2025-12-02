#!/usr/bin/env python
# component_id: pld_runtime_public_api
# kind: runtime_module
# area: api
# status: stable
# authority_level: 5
# license: Apache-2.0
# purpose: Public API surface for PLD Runtime v2.0. Re-exports Level-5 interfaces.

"""
PLD Runtime v2.0 — Public API Surface
=====================================

This module exposes the *safe public entrypoints* for integrations.

Now that internal folders have been renamed from numbered (e.g., `03_detection`)
to stable names (e.g., `detection`), direct imports are used instead of dynamic
resolution.
"""

# -------------------------
# Level 5 — Runtime Detection
# -------------------------
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
from .logging.runtime_logging_pipeline import RuntimeLoggingPipeline
from .logging.exporters.exporter_jsonl import JsonlExporter
from .logging.structured_logger import StructuredLogger


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
    "StructuredLogger",
]

