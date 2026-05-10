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

from dataclasses import dataclass
from datetime import datetime

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


class IrrigationController:
    def __init__(
        self,
        sensors: list[MoistureSensor],
        valve: Valve,
        config: AppConfig,
        *,
        clock: type[datetime] = datetime,
    ) -> None:
        self._sensors = sensors
        self._valve = valve
        self._config = config
        self._clock = clock
        self._opened_at: datetime | None = None
        self._last_closed_at: datetime | None = None

    def tick(self) -> TickResult:
        """Run one decision cycle. Should be safe to call repeatedly."""
        # TODO: implement the decision logic. Pseudocode to get you started:
        #
        #   now = self._clock.now()
        #   readings = [s.read_percent() for s in self._sensors]
        #   filter out bad readings using config.safety.reject_readings_outside
        #     (note: that range is in RAW values, you'll need raw + percent —
        #      decide if you want to filter at raw or percent level)
        #   if no good readings -> close valve, return TickResult with note
        #
        #   avg = mean of good readings
        #
        #   if valve is currently open:
        #       if open longer than max_open_seconds -> force close
        #       elif avg >= close_above_percent -> close
        #       else -> leave open
        #   else (valve closed):
        #       if cooldown not elapsed -> stay closed
        #       elif avg < open_below_percent -> open
        #       else -> stay closed
        #
        #   build and return a TickResult that captures the decision.
        raise NotImplementedError
