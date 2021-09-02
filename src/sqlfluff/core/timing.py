"""Timing summary class."""

from typing import Optional, List, Dict
from collections import defaultdict


class TimingSummary:
    """An object for tracking the timing of similar steps across many files."""

    def __init__(self, steps: Optional[List[str]] = None):
        self.steps = steps
        self._timings: List[Dict[str, float]] = []

    def add(self, timing_dict: Dict[str, float]):
        """Add a timing dictionary to the summary."""
        self._timings.append(timing_dict)
        if not self.steps:
            self.steps = list(timing_dict.keys())

    def summary(self) -> Dict[str, Dict[str, float]]:
        """Generate a summary for display."""
        vals: Dict[str, List[float]] = defaultdict(list)
        if not self.steps:  # pragma: no cover
            return {}

        for timing_dict in self._timings:
            for step in self.steps:
                if step in timing_dict:
                    vals[step].append(timing_dict[step])
        summary = {}
        for step in self.steps:
            if vals[step]:
                summary[step] = {
                    "cnt": len(vals[step]),
                    "sum": sum(vals[step]),
                    "min": min(vals[step]),
                    "max": max(vals[step]),
                    "avg": sum(vals[step]) / len(vals[step]),
                }
        return summary
