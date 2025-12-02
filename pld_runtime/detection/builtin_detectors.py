# component_id: builtin_detectors
# kind: runtime_module
# area: detection
# status: experimental
# authority_level: 5
# version: 2.0.0
# license: Apache-2.0
# purpose: Built-in drift detectors that extend the DriftDetector template and emit PLD v2-compliant drift events.

from __future__ import annotations

import typing as _t

from .drift_detector import DriftDetector, DriftDetectorContext, DriftSignal


class SimpleKeywordDetector(DriftDetector):
    """
    Simple keyword-based drift detector.

    Responsibilities:
    - Check a user/system text for the presence of any "NG" keywords.
    - When a keyword is found, emit a D* drift event via the DriftDetector template.

    Notes:
    - This class operates purely at Level 5 and MUST NOT redefine Level 1–3 rules.
    - Default taxonomy code is D1_instruction, suitable for instruction-level drift.
    """

    def __init__(
        self,
        ctx: DriftDetectorContext,
        *,
        keywords: _t.Sequence[str],
        code: str = "D1_instruction",
        case_insensitive: bool = True,
    ) -> None:
        if not keywords:
            raise ValueError("keywords must not be empty for SimpleKeywordDetector")

        super().__init__(ctx)
        self._keywords: tuple[str, ...] = tuple(k for k in keywords if k)
        if not self._keywords:
            raise ValueError("keywords must contain at least one non-empty string")

        self._code = code
        self._case_insensitive = case_insensitive

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect_and_build_event(
        self,
        *,
        text: str,
        turn_sequence: int,
        user_visible_state_change: bool = False,
        payload: dict[str, _t.Any] | None = None,
    ) -> dict[str, _t.Any] | None:
        """
        Run keyword-based detection on the given text and, if drift is found,
        build a PLD-compliant drift event.

        Parameters
        ----------
        text:
            Text to inspect for drift-related keywords.
        turn_sequence:
            Monotonic 1-based turn index within the session.
        user_visible_state_change:
            Whether the resulting event corresponds to a user-visible change.
        payload:
            Optional payload dict to include in the event. If omitted, a
            minimal payload containing the inspected text is attached.

        Returns
        -------
        dict | None
            A PLD event dict when drift is detected, or None when no drift
            is found.
        """
        drift_signal = self._run_keyword_detection(text=text)
        if drift_signal is None:
            return None

        if payload is None:
            payload = {"text": text}
        elif "text" not in payload:
            # Avoid overwriting an existing "text" key from the caller.
            payload = {**payload, "text": text}

        return self._build_drift_event(
            turn_sequence=turn_sequence,
            drift_signal=drift_signal,
            user_visible_state_change=user_visible_state_change,
            payload=payload,
        )

    # ------------------------------------------------------------------
    # Template overrides
    # ------------------------------------------------------------------

    def _run_detection(self, *, turn_sequence: int) -> DriftSignal | None:  # type: ignore[override]
        """
        This detector is typically driven via `detect_and_build_event(text=..., ...)`
        rather than the base `detect_and_build_event` signature.

        To keep the template contract satisfied, this override is provided but
        intentionally returns None. Callers SHOULD use the text-aware API above.
        """
        return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run_keyword_detection(self, *, text: str) -> DriftSignal | None:
        if self._case_insensitive:
            haystack = text.lower()
        else:
            haystack = text

        for kw in self._keywords:
            needle = kw.lower() if self._case_insensitive else kw
            if needle and needle in haystack:
                metadata: dict[str, _t.Any] = {
                    "matched_keyword": kw,
                    "detector": "SimpleKeywordDetector",
                }
                return DriftSignal(code=self._code, confidence=1.0, metadata=metadata)

        return None


class SchemaComplianceDetector(DriftDetector):
    """
    Simple schema-compliance drift detector.

    Responsibilities:
    - Check whether a dict-like payload contains a set of required keys.
    - When required keys are missing, emit a D* drift event via the template.

    Typical usage:
    - Context / form / tool output is expected to contain specific fields.
    - Missing fields are treated as context-level drift (default D2_context).

    Notes:
    - This detector operates at Level 5 and uses DriftDetector to construct
      PLD-compliant events. It does NOT modify Level 1–3 specifications.
    """

    def __init__(
        self,
        ctx: DriftDetectorContext,
        *,
        required_keys: _t.Iterable[str],
        code: str = "D2_context",
    ) -> None:
        keys = [k for k in required_keys if k]
        if not keys:
            raise ValueError("required_keys must contain at least one non-empty key")

        super().__init__(ctx)
        self._required_keys = frozenset(keys)
        self._code = code

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect_dict(
        self,
        data: dict[str, _t.Any],
        *,
        turn_sequence: int,
        user_visible_state_change: bool = False,
        payload: dict[str, _t.Any] | None = None,
    ) -> dict[str, _t.Any] | None:
        """
        Validate that `data` contains all required keys and, if not, emit a
        PLD-compliant drift event.

        Parameters
        ----------
        data:
            Dictionary to validate for required keys.
        turn_sequence:
            Monotonic 1-based turn index within the session.
        user_visible_state_change:
            Whether the resulting event corresponds to a user-visible change.
        payload:
            Optional payload dict to attach to the event. When omitted, the
            inspected `data` is included under the "input" key.

        Returns
        -------
        dict | None
            A PLD event dict when drift is detected, or None when all required
            keys are present.
        """
        missing = sorted(k for k in self._required_keys if k not in data)
        if not missing:
            return None

        metadata: dict[str, _t.Any] = {
            "missing_keys": missing,
            "detector": "SchemaComplianceDetector",
        }

        drift_signal = DriftSignal(
            code=self._code,
            confidence=1.0,
            metadata=metadata,
        )

        if payload is None:
            payload = {"input": data}
        elif "input" not in payload:
            payload = {**payload, "input": data}

        return self._build_drift_event(
            turn_sequence=turn_sequence,
            drift_signal=drift_signal,
            user_visible_state_change=user_visible_state_change,
            payload=payload,
        )

    # ------------------------------------------------------------------
    # Template overrides
    # ------------------------------------------------------------------

    def _run_detection(self, *, turn_sequence: int) -> DriftSignal | None:  # type: ignore[override]
        """
        This detector is intended to be used via `detect_dict(...)`, which
        accepts the dict under inspection.

        To satisfy the DriftDetector template, this override is provided but
        returns None. Callers SHOULD use `detect_dict` instead.
        """
        return None
