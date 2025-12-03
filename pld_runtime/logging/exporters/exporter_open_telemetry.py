# component_id: exporter_open_telemetry
# kind: runtime_module
# area: logging
# status: experimental
# authority_level: 5
# version: 2.0.0
# license: Apache-2.0
# purpose: Export PLD runtime events into OpenTelemetry logs/spans without altering semantics.

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Mapping, Optional, Sequence, List

from opentelemetry.util.types import Attributes

# OTEL imports are assumed to be configured upstream
from opentelemetry.trace import Tracer, SpanKind, Span, Link
from opentelemetry.trace.status import Status, StatusCode
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry._logs import SeverityNumber, Logger
from opentelemetry.context import set_value, get_value

# -----------------------------------------------------------------------------
# Type aliases — these DO NOT redefine schema or meaning.
# -----------------------------------------------------------------------------
PldEvent = Mapping[str, Any]
AttrMapping = Mapping[str, Any]
AttributeMapper = Callable[[PldEvent], AttrMapping]
ShutdownCallback = Callable[[], None]

# Store the previous span in context to ensure sequential linking.
# This is a Level 5-only utility.
_PREV_SPAN_KEY = "pld_prev_span"


# -----------------------------------------------------------------------------
# Configuration Model
# -----------------------------------------------------------------------------
@dataclass(frozen=True)
class OpenTelemetryExporterConfig:
    """
    Configuration for the OpenTelemetry exporter.

    Notes:
      - tracer_name: name of the span source.
      - enable_logs: if True, PLD events are also emitted as log records.
      - flatten_payload: optional toggle to flatten nested event content.
      - max_payload_bytes: soft enforcement only. If exceeded, payload is
        truncated and a flag is recorded (pld.<field>_truncated=true).
    """

    tracer_name: str = "pld_runtime"
    enable_logs: bool = True
    flatten_payload: bool = False
    max_payload_bytes: int = 32_000


# -----------------------------------------------------------------------------
# Helper utilities
# -----------------------------------------------------------------------------
def _flatten_dict(prefix: str, obj: Mapping[str, Any], out: dict) -> None:
    """
    Recursively flatten a nested dictionary into dotted attribute format.

    Example:
        {"runtime": {"latency_ms": 123}} → {"runtime.latency_ms": 123}

    This MUST NOT rename or reinterpret PLD meaning — only flatten for transport.
    """
    for key, value in obj.items():
        full = f"{prefix}.{key}" if prefix else key
        if isinstance(value, Mapping):
            _flatten_dict(full, value, out)
        else:
            out[full] = value


def _safe_json_for_attribute(value: Any, max_bytes: int) -> str:
    """
    JSON encode a value for OTEL metadata attachment.

    If the encoded string exceeds max_bytes, return a truncated representation
    and allow the OTEL record to declare the payload was truncated.
    """
    raw = json.dumps(value, ensure_ascii=False)
    if len(raw.encode("utf-8")) <= max_bytes:
        return raw
    return raw[: max_bytes] + "...(truncated)"


# -----------------------------------------------------------------------------
# Main Exporter
# -----------------------------------------------------------------------------
class OpenTelemetryExporter:
    """
    OpenTelemetryExporter
    ---------------------

    Level 5 exporter transforming PLD runtime events into OpenTelemetry spans
    and/or log records.

    Rules (MUST / MUST NOT):

      ✔ MUST transport the PLD event without modifying schema_version, event_id,
        timestamp, session_id, turn_sequence, source, event_type, or pld.*.

      ✔ MAY flatten nested data under namespaced keys
        (e.g., "payload.xxx", "runtime.xxx", "extensions.xxx").

      ✔ MUST NOT reinterpret Level 1–3 semantics (no classification, filtering,
        rewriting, lifecycle normalization, or inference).

      ✔ MUST tag truncation explicitly (pld.<field>_truncated = true)
        instead of silently dropping content.

      ✔ MUST treat the PLD event as opaque metadata; semantic interpretation
        belongs elsewhere in the runtime.

    Typical usage from SessionTraceBuffer:

        exporter.export_events(session_id, events)
    """

    __slots__ = ("_tracer", "_logger", "_config", "_shutdown_callbacks")

    def __init__(
        self,
        tracer: Tracer,
        logger: Optional[Logger],
        config: OpenTelemetryExporterConfig,
    ) -> None:
        self._tracer = tracer
        self._logger = logger
        self._config = config
        self._shutdown_callbacks: List[ShutdownCallback] = []

    # -------------------------------------------------------------------------
    # Constructors
    # -------------------------------------------------------------------------
    @classmethod
    def from_config(
        cls,
        config: OpenTelemetryExporterConfig,
        *,
        tracer_provider=None,
        logger_provider: Optional[LoggerProvider] = None,
    ) -> "OpenTelemetryExporter":
        tracer = tracer_provider.get_tracer(config.tracer_name)

        logger = None
        if config.enable_logs and logger_provider:
            logger = logger_provider.get_logger(config.tracer_name)

        return cls(
            tracer=tracer,
            logger=logger,
            config=config,
        )

    # -------------------------------------------------------------------------
    # Export Core
    # -------------------------------------------------------------------------
    def export_events(
        self,
        session_id: str,
        events: Sequence[PldEvent],
        *,
        attribute_mapper: Optional[AttributeMapper] = None,
    ) -> None:
        """
        Export a sequence of PLD events using OpenTelemetry.

        For each event:
          - Create a span with minimally required metadata.
          - Attach OTEL attributes representing the PLD event.
          - Optionally emit an OTEL log record with the same attributes.

        Ordering (turn_sequence) MUST be preserved by caller.
        """

        # Reset the previous span key for this session trace before starting.
        current_context = set_value(_PREV_SPAN_KEY, None)

        # NOTE(OTEL-SPAN-ROOT): A higher-level component SHOULD wrap this call
        # in a Session Root Span or enforce trace_id consistency per session_id.
        # This exporter only enforces sequential linking.
        for event in events:
            # 1. Determine Span Context (Sequential Linking)
            prev_span: Optional[Span] = get_value(_PREV_SPAN_KEY, context=current_context)

            span_kwargs: dict[str, Any] = {
                "name": event.get("event_type", "pld_event"),
                "kind": SpanKind.INTERNAL,
            }

            # Link the new span to the previous one to maintain session order.
            if prev_span is not None:
                prev_ctx = prev_span.get_context()
                if prev_ctx is not None and prev_ctx.is_valid:
                    span_kwargs["links"] = (Link(prev_ctx),)

            # 2. Determine Span Start Time (use PLD timestamp when available)
            # event["timestamp"] is RFC 3339 / ISO-8601 string at Level 1/5.
            try:
                timestamp_value = event.get("timestamp")
                if isinstance(timestamp_value, str):
                    dt = datetime.fromisoformat(timestamp_value.replace("Z", "+00:00"))
                    span_kwargs["start_time"] = int(dt.timestamp() * 1_000_000_000)
            except Exception:
                # On any parsing issue, fall back to OTEL's default (current time).
                pass

            # 3. Start Span
            with self._tracer.start_span(**span_kwargs) as span:
                # Update context for the next event in the sequence.
                current_context = set_value(_PREV_SPAN_KEY, span, current_context)

                # 4. Set Attributes and Status
                attrs = self._convert_event_to_attributes(event)

                if attribute_mapper:
                    extra = attribute_mapper(event)
                    # NOTE(OTEL-ATTR-MERGE): attribute_mapper may override keys.
                    # This remains a Level 5 concern; it MUST NOT modify PLD events.
                    attrs.update(extra)

                span.set_attributes(attrs)

                # PLD events reaching this layer are assumed schema/semantically valid.
                span.set_status(Status(StatusCode.OK))

                # 5. Optional logging channel
                if self._logger:
                    self._emit_log(attrs)

    # -------------------------------------------------------------------------
    # Attribute Conversion
    # -------------------------------------------------------------------------
    def _convert_event_to_attributes(self, event: PldEvent) -> Attributes:
        """
        Convert a PLD event to OTEL-compatible attribute dict without altering
        meaning or structure.

        Flattening is allowed but no schema modification.
        """
        attrs: dict[str, Any] = {}

        # Minimal required identity fields
        # NOTE: event["timestamp"] is used for span start time; we do not
        # duplicate it as an attribute by default.
        attrs["pld.schema_version"] = event.get("schema_version")
        attrs["pld.event_id"] = event.get("event_id")
        attrs["pld.event_type"] = event.get("event_type")
        attrs["pld.session_id"] = event.get("session_id")
        attrs["pld.turn_sequence"] = event.get("turn_sequence")
        attrs["pld.source"] = event.get("source")

        # Phase + Code (semantic fields MUST NOT be altered)
        if "pld" in event and isinstance(event["pld"], Mapping):
            sub = event["pld"]
            for key, value in sub.items():
                attrs[f"pld.{key}"] = value

        # Option A: flatten nested objects to OTEL attributes
        if self._config.flatten_payload:
            for field in ("payload", "runtime", "extensions", "ux", "metrics"):
                value = event.get(field)
                if isinstance(value, Mapping):
                    _flatten_dict(f"pld.{field}", value, attrs)
                elif value is not None:
                    # Non-mapping but still attachable; OTEL will validate types.
                    attrs[f"pld.{field}"] = value
        else:
            # Option B: JSON encode large / arbitrary structures
            #
            # - payload / extensions → always JSON (may be large/heterogeneous)
            # - runtime / ux / metrics → best-effort native attributes, fallback to JSON
            for field in ("payload", "extensions"):
                if field in event:
                    enc = _safe_json_for_attribute(
                        event[field],
                        self._config.max_payload_bytes,
                    )
                    attrs[f"pld.{field}"] = enc
                    if "(truncated)" in enc:
                        attrs[f"pld.{field}_truncated"] = True

            # For runtime / ux / metrics, prefer native attribute types.
            for field in ("runtime", "ux", "metrics"):
                value = event.get(field)
                key_prefix = f"pld.{field}"

                if not isinstance(value, Mapping):
                    if value is not None:
                        enc = _safe_json_for_attribute(
                            value,
                            self._config.max_payload_bytes,
                        )
                        attrs[key_prefix] = enc
                        if "(truncated)" in enc:
                            attrs[f"{key_prefix}_truncated"] = True
                    continue

                for k, v in value.items():
                    full_key = f"{key_prefix}.{k}"
                    if isinstance(v, (str, bool, int, float)):
                        attrs[full_key] = v
                    elif isinstance(v, (list, tuple)):
                        # Attempt to keep sequences of primitives native; otherwise JSON.
                        if all(
                            (isinstance(x, (str, bool, int, float)) or x is None)
                            for x in v
                        ):
                            attrs[full_key] = v
                        else:
                            enc = _safe_json_for_attribute(
                                v,
                                self._config.max_payload_bytes,
                            )
                            attrs[full_key] = enc
                            if "(truncated)" in enc:
                                attrs[f"{full_key}_truncated"] = True
                    elif v is not None:
                        enc = _safe_json_for_attribute(
                            v,
                            self._config.max_payload_bytes,
                        )
                        attrs[full_key] = enc
                        if "(truncated)" in enc:
                            attrs[f"{full_key}_truncated"] = True

        return attrs

    # -------------------------------------------------------------------------
    # Logging Mode (Optional)
    # -------------------------------------------------------------------------
    def _emit_log(self, attrs: Mapping[str, Any]) -> None:
        """
        Emit a structured OpenTelemetry log record for the event metadata.

        This MUST NOT modify PLD fields.
        """
        if not self._logger:
            return

        # NOTE(OTEL-LOG-SEVERITY): Severity is fixed to INFO here.
        # Any semantic mapping from PLD phases/codes to severity MUST be handled
        # outside the logging/export layer.
        self._logger.emit(
            severity_number=SeverityNumber.INFO,
            body="pld_runtime_event",
            attributes=attrs,
        )

    # -------------------------------------------------------------------------
    # Shutdown hooks
    # -------------------------------------------------------------------------
    def register_shutdown_callback(self, callback: ShutdownCallback) -> None:
        """
        Register a shutdown callback to be invoked when shutdown() is called.

        Callbacks are Level 5 transport concerns only (e.g., flushing OTEL
        providers) and MUST NOT modify PLD event contents.
        """
        if callback is not None:
            self._shutdown_callbacks.append(callback)

    def shutdown(self) -> None:
        """Optional lifecycle shutdown hook."""
        for cb in self._shutdown_callbacks:
            try:
                cb()
            except Exception:
                # Shutdown callbacks are best-effort; failures MUST NOT impact
                # PLD event semantics or require retries at this layer.
                continue

