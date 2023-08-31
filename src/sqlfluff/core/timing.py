"""Timing summary class."""

from collections import defaultdict
from typing import Dict, List, Optional, Set, Tuple, Union


class TimingSummary:
    """An object for tracking the timing of similar steps across many files."""

    def __init__(self, steps: Optional[List[str]] = None):
        self.steps = steps
        self._timings: List[Dict[str, float]] = []

    def add(self, timing_dict: Dict[str, float]) -> None:
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


class RuleTimingSummary:
    """An object for tracking the timing of rules across many files."""

    def __init__(self) -> None:
        self._timings: List[Tuple[str, str, float]] = []

    def add(self, rule_timings: List[Tuple[str, str, float]]) -> None:
        """Add a set of rule timings."""
        # Add records to the main list.
        self._timings.extend(rule_timings)

    def summary(
        self, threshold: float = 0.5
    ) -> Dict[str, Dict[str, Union[float, str]]]:
        """Generate a summary for display."""
        keys: Set[Tuple[str, str]] = set()
        vals: Dict[Tuple[str, str], List[float]] = defaultdict(list)

        for code, name, time in self._timings:
            vals[(code, name)].append(time)
            keys.add((code, name))

        summary: Dict[str, Dict[str, Union[float, str]]] = {}
        for code, name in sorted(keys):
            timings = vals[(code, name)]
            # For brevity, if the total time taken is less than
            # `threshold`, then don't display.
            if sum(timings) < threshold:
                continue
            # NOTE: This summary isn't covered in tests, it's tricky
            # to force it to exist in a test environment without
            # making things complicated.
            summary[f"{code}: {name}"] = {  # pragma: no cover
                "sum (n)": f"{sum(timings):.2f} ({len(timings)})",
                "min": min(timings),
                "max": max(timings),
            }
        return summary
