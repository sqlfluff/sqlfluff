"""WSL2/Windows-host noise mitigation.

The CPU governor/turbo controls live on the Windows host, not inside the
WSL2 VM, so the power-plan switch shells out to powercfg.exe (available via
WSL's Win32 interop). Everything here is best-effort: if powershell.exe /
powercfg.exe aren't reachable, we warn and continue rather than fail the
sweep - the measurements are still useful, just less clean.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from dataclasses import asdict, dataclass, field
from typing import Optional

HIGH_PERFORMANCE_GUID = "8c5e7fce-e8bf-4a96-9a85-a6e23a8c635c"


def _run(cmd: list, timeout: float = 10) -> Optional[subprocess.CompletedProcess]:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return None


def _powershell(command: str) -> Optional[subprocess.CompletedProcess]:
    return _run(["powershell.exe", "-NoProfile", "-Command", command])


@dataclass
class EnvReading:
    """One environment snapshot: power source, CPU clock, load average."""

    timestamp: float
    warnings: list = field(default_factory=list)
    on_ac_power: Optional[bool] = None
    cpu_current_mhz: Optional[int] = None
    cpu_max_mhz: Optional[int] = None
    throttle_suspected: Optional[bool] = None
    load_avg: Optional[tuple] = None
    active_power_scheme: Optional[str] = None

    def as_dict(self) -> dict:
        """Return this reading as a plain, JSON-serialisable dict."""
        return asdict(self)


def detect_environment() -> EnvReading:
    """Take one environment snapshot, warning (not failing) on any gap."""
    reading = EnvReading(timestamp=time.time())

    try:
        with open("/proc/loadavg") as f:
            parts = f.read().split()
            reading.load_avg = tuple(float(x) for x in parts[:3])
    except OSError as exc:
        reading.warnings.append(f"could not read /proc/loadavg: {exc}")

    r = _powershell(
        "(Get-CimInstance Win32_Battery | Select-Object -First 1 -ExpandProperty BatteryStatus)"
    )
    if r is not None and r.returncode == 0:
        status = r.stdout.strip()
        # BatteryStatus 1 == "Discharging"; any other present value (charging,
        # fully charged, ...) or no battery device at all implies AC power.
        reading.on_ac_power = status != "1"
    else:
        reading.warnings.append(
            "could not query Windows battery status via powershell.exe"
        )

    r = _powershell(
        "Get-CimInstance Win32_Processor | Select-Object -First 1 "
        "CurrentClockSpeed,MaxClockSpeed | ConvertTo-Json -Compress"
    )
    if r is not None and r.returncode == 0 and r.stdout.strip():
        try:
            data = json.loads(r.stdout)
            reading.cpu_current_mhz = data.get("CurrentClockSpeed")
            reading.cpu_max_mhz = data.get("MaxClockSpeed")
            if reading.cpu_current_mhz and reading.cpu_max_mhz:
                reading.throttle_suspected = (
                    reading.cpu_current_mhz < 0.85 * reading.cpu_max_mhz
                )
        except ValueError:
            reading.warnings.append("could not parse Windows CPU clock speed JSON")
    else:
        reading.warnings.append(
            "could not query Windows CPU clock speed via powershell.exe"
        )

    r = _powershell("(powercfg /getactivescheme)")
    if r is not None and r.returncode == 0:
        reading.active_power_scheme = r.stdout.strip()

    if reading.on_ac_power is False:
        reading.warnings.append("laptop appears to be running on battery power")
    if reading.throttle_suspected:
        reading.warnings.append(
            f"possible CPU throttling: current {reading.cpu_current_mhz}MHz vs "
            f"max {reading.cpu_max_mhz}MHz"
        )
    if reading.load_avg is not None and reading.load_avg[0] > (os.cpu_count() or 1):
        reading.warnings.append(f"high background load average: {reading.load_avg}")

    return reading


class PowerPlanGuard:
    """Best-effort switch to High Performance for the run's duration.

    Restores whatever power plan was active before on exit, whether that
    exit is normal or via an exception.
    """

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self._previous_guid: Optional[str] = None

    def __enter__(self) -> "PowerPlanGuard":
        if not self.enabled:
            return self
        r = _powershell("(powercfg /getactivescheme)")
        if r is not None and r.returncode == 0 and r.stdout.strip():
            for tok in r.stdout.strip().split():
                if len(tok) == 36 and tok.count("-") == 4:
                    self._previous_guid = tok
                    break
        result = _run(["powercfg.exe", "/setactive", HIGH_PERFORMANCE_GUID])
        if result is None or result.returncode != 0:
            print(
                "WARNING: could not switch Windows power plan via powercfg.exe "
                "(continuing without it)"
            )
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        if self.enabled and self._previous_guid:
            _run(["powercfg.exe", "/setactive", self._previous_guid])
        return False


def wrap_affinity(cmd: list, cores: Optional[str], nice_level: Optional[int]) -> list:
    """Wrap a command with taskset/nice where available.

    Silently skips whichever binary isn't on PATH rather than failing the
    measurement.
    """
    wrapped = list(cmd)
    if nice_level is not None and shutil.which("nice"):
        wrapped = ["nice", "-n", str(nice_level), *wrapped]
    if cores and shutil.which("taskset"):
        wrapped = ["taskset", "-c", cores, *wrapped]
    return wrapped
