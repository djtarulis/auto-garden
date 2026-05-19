"""The decision logic — the brain of the system.

Given the latest sensor readings + current valve state + safety constraints,
decide what to do this tick. This is the most important file in the project
and is intentionally left for YOU to implement.

Things this class needs to handle (think about each):
  * average / aggregate readings from multiple sensors (mean? median? min?)
  * hysteresis — open below X%, but don't close until above Y% so the valve
    doesn't chatter on/off around the threshold
  * max-open enforcement — if the valve has been open for more than
    `safety.max_open_seconds`, force it closed regardless of readings
  * cooldown — refuse to re-open until `min_seconds_between_waterings` has
    elapsed since the last close
  * sanity-check readings — drop values outside `safety.reject_readings_outside`
    before averaging; what should the controller do if ALL readings are bad?
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from auto_garden.config import AppConfig
from auto_garden.hardware.sensor import MoistureSensor
from auto_garden.hardware.valve import Valve


@dataclass
class TickResult:
    """Snapshot of what happened on a single tick — used for logging/tests."""

    timestamp: datetime
    moisture_percent: float | None  # None if no readings were valid
    valve_was_open: bool
    valve_is_open: bool
    note: str  # short human-readable reason for the decision


class Clock(Protocol):
    def now(self) -> datetime: ...


class IrrigationController:
    def __init__(
        self,
        sensors: Sequence[MoistureSensor],
        valve: Valve,
        config: AppConfig,
        *,
        clock: Clock = datetime,
    ) -> None:
        self._sensors = sensors
        self._valve = valve
        self._config = config
        self._clock = clock
        self._opened_at: datetime | None = None
        self._last_closed_at: datetime | None = None

    def tick(self) -> TickResult:
        """Run one decision cycle. Should be safe to call repeatedly."""
        now = self._clock.now()
        valve_was_open = self._valve.is_open

        lo, hi = self._config.safety.reject_readings_outside
        # read every sensor's percent
        good = [s.read_percent() for s in self._sensors if lo <= s.read_raw() <= hi]

        if not good:
            # all sensors rejected — fail safe
            self._valve.close()
            self._last_closed_at = now
            note = "all readings rejected"
            return TickResult(
                timestamp=now,
                moisture_percent=None,
                valve_was_open=valve_was_open,
                valve_is_open=self._valve.is_open,
                note=note,
            )
        # compute the average
        avg = sum(good) / len(good)

        if self._valve.is_open:
            # State A: valve is currently OPEN
            if avg >= self._config.thresholds.close_above_percent:
                self._valve.close()
                self._last_closed_at = now
                note = "closed: moisture above close threshold"
            else:
                note = "stayed open: moisture below close threshold"

        # State B: valve is currently CLOSED
        elif avg < self._config.thresholds.open_below_percent:
            self._valve.open()
            self._opened_at = now
            note = "opened: moisture below open threshold"
        else:
            note = "stayed closed: moisture above open threshold"

        return TickResult(
            timestamp=now,
            moisture_percent=avg,
            valve_was_open=valve_was_open,
            valve_is_open=self._valve.is_open,
            note=note,
        )
