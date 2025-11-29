"""
verify_metrics_local.py
-----------------------

This utility script loads the demo PLD event dataset and derives a small
set of metrics aligned with the Level 3 PLD Metrics Specification.

📌 Purpose
- Demonstrate how a developer or researcher can locally inspect PLD events.
- Compute simple derived metrics (NOT modify the dataset).
- Provide a lightweight metrics view without introducing runtime controllers.

⚠ IMPORTANT
This script is NOT:
- a validator of PLD compliance
- a canonical metrics computation service
- a replacement for runtime logging

It is a *Quickstart inspection aid* for the demo JSONL dataset.

"""

from pathlib import Path
import json
from collections import defaultdict


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
DATASET_PATH = Path(__file__).parent / "datasets" / "pld_events_demo.jsonl"


# ------------------------------------------------------------
# Metrics Model
# ------------------------------------------------------------

class LocalMetrics:
    """
    Container for derived metrics computed from a PLD event stream.

    These metrics are intentionally simple and human-auditable.
    """
    def __init__(self):
        self.total_events = 0
        self.sessions = set()

        self.drift_events = 0
        self.repair_events = 0
        self.reentry_events = 0
        self.latency_spikes = 0

        # Track repair depth per session for simple statistical output.
        self.repair_attempts_per_session = defaultdict(int)

    def update(self, event: dict):
        self.total_events += 1
        session = event.get("session_id")
        if session:
            self.sessions.add(session)

        event_type = event.get("event_type", "").lower()
        phase = event.get("pld", {}).get("phase", "")
        code = event.get("pld", {}).get("code", "")

        # Basic counters
        if phase == "drift":
            self.drift_events += 1

        if phase == "repair":
            self.repair_events += 1
            self.repair_attempts_per_session[session] += 1

        if phase == "reentry":
            self.reentry_events += 1

        # Observability-only (INFO events)
        if "latency" in code.lower():
            self.latency_spikes += 1

    def as_dict(self):
        """
        Export metrics as a JSON-serializable structure.
        """
        return {
            "total_events": self.total_events,
            "total_sessions": len(self.sessions),
            "drift_events": self.drift_events,
            "repair_events": self.repair_events,
            "reentry_events": self.reentry_events,
            "latency_spikes": self.latency_spikes,
            "avg_repairs_per_session": (
                sum(self.repair_attempts_per_session.values()) / len(self.repair_attempts_per_session)
                if self.repair_attempts_per_session else 0
            ),
            "repair_attempt_histogram": dict(self.repair_attempts_per_session),
        }


# ------------------------------------------------------------
# Execution Logic
# ------------------------------------------------------------

def load_events(path: Path):
    """
    Load events from a JSONL file.
    Each line is expected to contain one valid PLD event object.
    """
    events = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"[WARN] Skipped invalid line: {e}")
    return events


def compute_metrics():
    """
    High-level flow:
      1. Load dataset
      2. Sweep through events
      3. Print derived metrics summary
    """
    if not DATASET_PATH.exists():
        print(f"[ERROR] Dataset not found: {DATASET_PATH}")
        return

    events = load_events(DATASET_PATH)
    metrics = LocalMetrics()

    for event in events:
        metrics.update(event)

    # Results
    print("\n=== Local Metrics Summary ===")
    for key, value in metrics.as_dict().items():
        print(f"{key:30} : {value}")

    print("\n✔ Metrics extraction complete.\n")


# ------------------------------------------------------------
# Script Entry Point
# ------------------------------------------------------------

if __name__ == "__main__":
    compute_metrics()
