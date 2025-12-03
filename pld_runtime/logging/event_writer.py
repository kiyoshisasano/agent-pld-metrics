# component_id: event_writer
# kind: runtime_module
# area: logging
# status: stable
# authority_level: 5
# version: 2.0.0
# license: Apache-2.0
# purpose: Transport-only event writers and runtime stub entry point for PLD-compatible systems.

from typing import Any, Dict, Optional, Protocol
import logging
import json
import sys
from dataclasses import dataclass
from pathlib import Path

LOGGER_NAME = "pld_runtime.event_writer"
logger = logging.getLogger(LOGGER_NAME)


class EventWriter(Protocol):
    """Callable writer protocol (transport-only).

    Implementations accept a single record dict and return None.
    This layer is transport-only and MUST NOT enforce PLD schema or
    semantic rules. Higher layers handle validation and lifecycle logic.
    """

    def __call__(self, record: Dict[str, Any]) -> None:  # pragma: no cover - protocol
        ...


class RuntimeEventWriterStub:
    """
    Standard runtime event writer stub.

    Responsibilities (high-level):
    - Accept runtime event objects
    - Provide a stable entry point for writing/dispatching events
    - Avoid enforcing PLD validation rules at this layer

    Actual behavior MUST be implemented by downstream runtime developers.
    """

    def __init__(self) -> None:
        self.enabled = True
        logger.debug("RuntimeEventWriterStub initialized (stub mode)")

    def write(self, event: Dict[str, Any]) -> None:
        """Placeholder method for writing runtime events.

        This stub implementation does NOT:
        - Guarantee event schema conformance
        - Apply Level 2 semantic validation
        - Persist to a target system (file, log sink, queue, DB, etc.)

        Implementers SHOULD replace this method with production logic.
        """
        if not self.enabled:
            logger.debug("write() skipped: writer disabled")
            return

        logger.info(f"[STUB] event received: {event}")

    def __call__(self, event: Dict[str, Any]) -> None:
        """Allow this stub to be used wherever an EventWriter is expected."""
        self.write(event)

    def enable(self) -> None:
        self.enabled = True
        logger.debug("RuntimeEventWriterStub enabled")

    def disable(self) -> None:
        self.enabled = False
        logger.debug("RuntimeEventWriterStub disabled")


# ---------------------------------------------------------------------------
# In-memory writer (tests / small demos)
# ---------------------------------------------------------------------------


@dataclass
class MemoryWriter:
    """In-memory writer for tests and small demos.

    Stores emitted records in ``records`` for later inspection.
    This class does not enforce any schema or PLD semantics.
    """

    records: list[Dict[str, Any]]

    def __init__(self) -> None:
        self.records = []

    def __call__(self, record: Dict[str, Any]) -> None:
        self.records.append(record)

    def clear(self) -> None:
        self.records.clear()


# ---------------------------------------------------------------------------
# JSONL file writer
# ---------------------------------------------------------------------------


@dataclass
class JsonlFileWriter:
    """Write one JSON object per line to a file.

    This writer is transport-only and intentionally avoids validation
    or PLD-specific semantics.
    """

    path: Path
    append: bool = True
    ensure_ascii: bool = False
    auto_flush: bool = True

    _file: Optional[Any] = None
    _opened_mode: Optional[str] = None

    def __post_init__(self) -> None:
        self.path = Path(self.path)

    def __call__(self, record: Dict[str, Any]) -> None:
        if self._file is None:
            mode = "a" if self.append else "w"
            self._file = self.path.open(mode, encoding="utf-8")
            self._opened_mode = mode
        line = json.dumps(record, ensure_ascii=self.ensure_ascii)
        self._file.write(line + "\n")
        if self.auto_flush:
            self._file.flush()

    def close(self) -> None:
        if self._file is not None:
            self._file.close()
            self._file = None
            self._opened_mode = None


def make_jsonl_file_writer(
    path: str | Path,
    *,
    append: bool = True,
    ensure_ascii: bool = False,
    auto_flush: bool = True,
) -> JsonlFileWriter:
    """Convenience constructor for :class:`JsonlFileWriter`."""

    return JsonlFileWriter(
        path=Path(path),
        append=append,
        ensure_ascii=ensure_ascii,
        auto_flush=auto_flush,
    )


# ---------------------------------------------------------------------------
# Stream / stdout / stderr writer
# ---------------------------------------------------------------------------


@dataclass
class StreamWriter:
    """Write JSON lines to a text stream (e.g., stdout, stderr).

    Common usage patterns include local debugging and container logs.
    This writer does not perform validation or retries.
    """

    stream: Any = sys.stdout
    ensure_ascii: bool = False
    auto_flush: bool = True

    def __call__(self, record: Dict[str, Any]) -> None:
        line = json.dumps(record, ensure_ascii=self.ensure_ascii)
        self.stream.write(line + "\n")
        if self.auto_flush and hasattr(self.stream, "flush"):
            self.stream.flush()


def make_stdout_writer(
    *,
    ensure_ascii: bool = False,
    auto_flush: bool = True,
) -> StreamWriter:
    """Create a :class:`StreamWriter` bound to ``sys.stdout``."""

    return StreamWriter(stream=sys.stdout, ensure_ascii=ensure_ascii, auto_flush=auto_flush)


def make_stderr_writer(
    *,
    ensure_ascii: bool = False,
    auto_flush: bool = True,
) -> StreamWriter:
    """Create a :class:`StreamWriter` bound to ``sys.stderr``."""

    return StreamWriter(stream=sys.stderr, ensure_ascii=ensure_ascii, auto_flush=auto_flush)


__all__ = [
    "EventWriter",
    "RuntimeEventWriterStub",
    "MemoryWriter",
    "JsonlFileWriter",
    "make_jsonl_file_writer",
    "StreamWriter",
    "make_stdout_writer",
    "make_stderr_writer",
]


