"""Timing summary class."""

from collections import defaultdict
from typing import Optional, Union


class TimingSummary:
    """An object for tracking the timing of similar steps across many files."""

    def __init__(self, steps: Optional[list[str]] = None):
        self.steps = steps
        self._timings: list[dict[str, float]] = []

    def add(self, timing_dict: dict[str, float]) -> None:
        """Add a timing dictionary to the summary."""
        self._timings.append(timing_dict)
        if not self.steps:
            self.steps = list(timing_dict.keys())

    def summary(self) -> dict[str, dict[str, float]]:
        """Generate a summary for display."""
        vals: dict[str, list[float]] = defaultdict(list)
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
        self._timings: list[tuple[str, str, float]] = []

    def add(self, rule_timings: list[tuple[str, str, float]]) -> None:
        """Add a set of rule timings."""
        # Add records to the main list.
        self._timings.extend(rule_timings)

    def summary(
        self, threshold: float = 0.5
    ) -> dict[str, dict[str, Union[float, str]]]:
        """Generate a summary for display."""
        keys: set[tuple[str, str]] = set()
        vals: dict[tuple[str, str], list[float]] = defaultdict(list)

        for code, name, time in self._timings:
            vals[(code, name)].append(time)
            keys.add((code, name))

        summary: dict[str, dict[str, Union[float, str]]] = {}
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
