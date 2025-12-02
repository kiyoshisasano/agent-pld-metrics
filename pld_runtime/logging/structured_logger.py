# component_id: structured_logger
# kind: runtime_module
# area: logging
# status: draft
# authority_level: 5
# version: 2.0.0
# license: Apache-2.0
# purpose: Structured logger facade over transport event writers for PLD-compatible runtimes.

from __future__ import annotations

from typing import Any, Dict, Optional
from enum import Enum
import logging

from .event_writer import EventWriter

LOGGER_NAME = "pld_runtime.structured_logger"
logger = logging.getLogger(LOGGER_NAME)


class LoggingMode(str, Enum):
    """Logging verbosity / intent indicator.

    This enum is transport-agnostic; higher layers MAY interpret modes
    to decide which records to emit. The core StructuredLogger in this
    module does not enforce any behavior based on the mode value.
    """

    DEBUG = "debug"
    COMPACT = "compact"
    EVALUATION = "evaluation"
    SILENT = "silent"


class StructuredLogger:
    """Thin structured logging facade over an :class:`EventWriter`.

    This class is responsible for:
    - Accepting structured ``Dict[str, Any]`` records
    - Optionally enriching them with a static "base context"
    - Forwarding the final record to a transport-only :class:`EventWriter`

    This layer MUST NOT:
    - Enforce PLD schema validity
    - Interpret PLD phases or codes
    - Perform retries, buffering, or transport-level concerns

    Higher-level controllers and enforcement layers own PLD semantics.
    """

    def __init__(
        self,
        writer: EventWriter,
        *,
        base_context: Optional[Dict[str, Any]] = None,
        log_errors: bool = True,
        mode: "LoggingMode | str | None" = None,
    ) -> None:
        """Create a new :class:`StructuredLogger`.

        Parameters
        ----------
        writer:
            A callable conforming to the :class:`EventWriter` protocol.
        base_context:
            Optional mapping to be shallow-merged into every record before
            emission. Callers SHOULD ensure that base_context is JSON-serializable
            if the underlying writer expects JSON-compatible structures.
        log_errors:
            When True, exceptions raised by ``writer`` are caught and logged
            using the module logger. When False, exceptions are propagated.
        """
        self._writer = writer
        self._base_context: Dict[str, Any] = dict(base_context or {})
        self._log_errors = log_errors
        self._mode = mode

    @property
    def base_context(self) -> Dict[str, Any]:
        """Return a shallow copy of the current base context."""

        return dict(self._base_context)

    def with_context(self, extra: Dict[str, Any]) -> "StructuredLogger":
        """Return a new :class:`StructuredLogger` with merged base context.

        The original instance remains unchanged; contexts are shallow-merged
        (``extra`` values override existing keys).
        """

        merged = {**self._base_context, **extra}
        return StructuredLogger(self._writer, base_context=merged, log_errors=self._log_errors)

    def log(self, record: Dict[str, Any]) -> None:
        """Emit a structured record via the underlying writer.

        The provided ``record`` is shallow-merged on top of the stored
        ``base_context`` (record keys override base_context keys).
        """

        payload: Dict[str, Any] = {**self._base_context, **record}

        if self._log_errors:
            try:
                self._writer(payload)
            except Exception:  # pragma: no cover - defensive path
                logger.exception("StructuredLogger failed to emit record")
        else:
            self._writer(payload)


def make_console_logger(
    *,
    mode: "LoggingMode | str | None" = None,
    stream: Any = None,
) -> StructuredLogger:
    """Create a StructuredLogger that writes JSON lines to a text stream.

    This helper mirrors the v1.1 console logger shape while delegating
    transport concerns to a simple in-process writer. ``mode`` is
    accepted for compatibility but not interpreted at this layer.
    """

    import json
    import sys

    if stream is None:
        stream = sys.stdout

    def _writer(rec: Dict[str, Any]) -> None:
        stream.write(json.dumps(rec, ensure_ascii=False) + "\n")
        if hasattr(stream, "flush"):
            stream.flush()

    return StructuredLogger(writer=_writer, base_context=None, log_errors=True, mode=mode)


__all__ = ["LoggingMode", "StructuredLogger", "make_console_logger"]

