# component_id: backoff_policies
# kind: runtime_module
# area: failover
# status: draft
# authority_level: 5
# version: 2.0.0
# license: Apache-2.0
# purpose: Pluggable backoff policies for runtime failover strategies without interpreting PLD semantics.

from __future__ import annotations

import abc
import random
import time
from dataclasses import dataclass
from typing import Optional, Protocol


# ---------------------------------------------------------------------------
# Runtime Backoff Policy Protocol
# ---------------------------------------------------------------------------

class BackoffPolicy(Protocol):
    """
    Contract for backoff strategies used by failover orchestration.

    Notes:
      - This interface MAY be extended with observability hooks but MUST NOT
        emit or mutate PLD events.
      - Any backoff implementation MUST remain deterministic and pure with
        respect to PLD event semantics.
      - Implementations MAY use time.sleep(...) but SHOULD support dry-run or
        async execution patterns when integrated with runtime orchestration.
    """

    def next_delay(self, attempt: int) -> float:
        """
        Compute the next backoff delay in seconds.

        Constraints:
          - attempt is 1-based.
          - MUST NOT mutate attempt or maintain implicit state.
        """
        ...


# ---------------------------------------------------------------------------
# Constant Backoff Strategy
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ConstantBackoff:
    """A fixed-delay backoff policy.

    Useful for deterministic retry flows where jitter or exponential growth
    are undesirable.

    Parameters:
      - delay_seconds: float — MUST be >= 0.
    """

    delay_seconds: float = 1.0

    def next_delay(self, attempt: int) -> float:
        if attempt < 1:
            raise ValueError("attempt MUST be >= 1")
        return self.delay_seconds


# ---------------------------------------------------------------------------
# Exponential Backoff Strategy
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ExponentialBackoff:
    """An exponential growth policy with optional maximum bound.

    Parameters:
      - base_seconds: float — MUST be > 0
      - factor: float — MUST be > 1
      - max_seconds: Optional[float] — upper bound on computed delay.
    """

    base_seconds: float = 1.0
    factor: float = 2.0
    max_seconds: Optional[float] = None

    def __post_init__(self) -> None:
        if self.base_seconds <= 0:
            raise ValueError("base_seconds MUST be > 0")
        if self.factor <= 1:
            raise ValueError("factor MUST be > 1")

    def next_delay(self, attempt: int) -> float:
        if attempt < 1:
            raise ValueError("attempt MUST be >= 1")

        delay = self.base_seconds * (self.factor ** (attempt - 1))
        if self.max_seconds is not None:
            delay = min(delay, self.max_seconds)
        return delay


# ---------------------------------------------------------------------------
# Exponential Jitter Backoff Strategy
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ExponentialJitterBackoff:
    """Exponential backoff with bounded random jitter.

    Behaves like exponential backoff, then applies jitter within ± jitter_ratio.

    Parameters:
      - base_seconds: float — MUST be > 0
      - factor: float — MUST be > 1
      - jitter_ratio: float — MUST be in [0, 1]
      - max_seconds: Optional[float] — upper bound on post-jitter result.

    Notes:
      - The lifetime semantics of randomness are runtime-specific. This file
        does NOT set seeds or reuse random streams.
    """

    base_seconds: float = 1.0
    factor: float = 2.0
    jitter_ratio: float = 0.2
    max_seconds: Optional[float] = None

    def __post_init__(self) -> None:
        if self.base_seconds <= 0:
            raise ValueError("base_seconds MUST be > 0")
        if self.factor <= 1:
            raise ValueError("factor MUST be > 1")
        if not (0.0 <= self.jitter_ratio <= 1.0):
            raise ValueError("jitter_ratio MUST be in [0, 1]")
        # TODO(JITTER-RANGE-POLICY): Confirm whether jitter is allowed to reduce
        # the delay below the base exponential value or if a minimum percentage
        # bound relative to the base delay is required.

    def next_delay(self, attempt: int) -> float:
        if attempt < 1:
            raise ValueError("attempt MUST be >= 1")

        delay = self.base_seconds * (self.factor ** (attempt - 1))
        jitter_bound = delay * self.jitter_ratio

        jitter = random.uniform(-jitter_bound, jitter_bound)
        delay = delay + jitter

        if self.max_seconds is not None:
            delay = min(delay, self.max_seconds)
        return max(0.0, delay)


# ---------------------------------------------------------------------------
# Sleep Utility (Optional execution helper)
# ---------------------------------------------------------------------------

def apply_backoff(policy: BackoffPolicy, attempt: int) -> float:
    """
    Utility to apply a backoff policy.

    Behavior:
      - Computes delay using policy.next_delay(attempt).
      - Sleeps for the computed duration.
      - Returns the computed delay without mutating PLD events.

    TODO(BACKOFF-OWNERSHIP): Confirm whether apply_backoff should remain in
    this module or be delegated to the failover orchestrator component to keep
    policy definition and execution ownership clearly separated.
    """
    delay = policy.next_delay(attempt)
    time.sleep(delay)
    return delay

