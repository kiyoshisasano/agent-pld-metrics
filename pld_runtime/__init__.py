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
It handles imports from internal numbered directories (e.g., 03_detection)
so that external users see a clean API.
"""

import importlib

# ---------------------------------------------------------------------------
# Helper for importing from numbered directories (e.g., '03_detection')
# Python syntax forbids 'from .03_detection import ...', so we use importlib.
# ---------------------------------------------------------------------------
def _import_internal(submodule: str):
    """Import a submodule relative to pld_runtime."""
    return importlib.import_module(f".{submodule}", package="pld_runtime")

# -------------------------
# Level 5 — Runtime Detection
# -------------------------
# Source: pld_runtime/03_detection/runtime_signal_bridge.py
_bridge_mod = _import_internal("03_detection.runtime_signal_bridge")

RuntimeSignalBridge = _bridge_mod.RuntimeSignalBridge
RuntimeSignal = _bridge_mod.RuntimeSignal
SignalKind = _bridge_mod.SignalKind
EventContext = _bridge_mod.EventContext
ValidationMode = _bridge_mod.ValidationMode

# -------------------------
# Level 5 — Logging Surface
# -------------------------
# Source: pld_runtime/06_logging/runtime_logging_pipeline.py
_pipeline_mod = _import_internal("06_logging.runtime_logging_pipeline")
RuntimeLoggingPipeline = _pipeline_mod.RuntimeLoggingPipeline

# Source: pld_runtime/06_logging/exporters/exporter_jsonl.py
_jsonl_mod = _import_internal("06_logging.exporters.exporter_jsonl")
JsonlExporter = _jsonl_mod.JsonlExporter

# Source: pld_runtime/06_logging/structured_logger.py
_logger_mod = _import_internal("06_logging.structured_logger")
StructuredLogger = _logger_mod.StructuredLogger


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
