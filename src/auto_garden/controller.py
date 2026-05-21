"""The decision logic — the brain of the system.

Given the latest sensor readings + current valve state + safety constraints,
decide what to do this tick.

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
    """Controller that decides whether the garden needs water, and act on that decision safely.
    Tick is called once per loop iteration."""

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

    def _close_valve(self, now: datetime) -> None:
        """Close the valve and record the close time. Always use this to close."""
        self._valve.close()
        self._last_closed_at = now

    def _decide_open_state(self, now: datetime, avg: float) -> str:
        """Handle a tick while the valve is open. Returns the TickResult note."""
        assert self._opened_at is not None  # invariant: open -> opened_at is set
        elapsed_seconds = (now - self._opened_at).total_seconds()
        if elapsed_seconds > self._config.safety.max_open_seconds:
            self._close_valve(now)
            return "closed: max open time exceeded"
        elif avg >= self._config.thresholds.close_above_percent:
            self._close_valve(now)
            return "closed: moisture above close threshold"
        else:
            return "stayed open: moisture below close threshold"

    def _decide_closed_state(self, now: datetime, avg: float) -> str:
        """Handle a tick while the valve is closed. Returns the TickResult note."""
        if avg < self._config.thresholds.open_below_percent:
            cooldown_active = (
                self._last_closed_at is not None
                and (now - self._last_closed_at).total_seconds()
                < self._config.safety.min_seconds_between_waterings
            )
            if cooldown_active:
                return "stayed closed: cooldown not elapsed"
            else:
                self._valve.open()
                self._opened_at = now
                return "opened: moisture below open threshold"
        else:
            return "stayed closed: moisture above open threshold"

    def tick(self) -> TickResult:
        """Run one decision cycle. Should be safe to call repeatedly."""
        now = self._clock.now()
        valve_was_open = self._valve.is_open

        lo, hi = self._config.safety.reject_readings_outside
        # read each sensor, keeping only readings inside the safety range
        good_readings = [s.read_percent() for s in self._sensors if lo <= s.read_raw() <= hi]

        if not good_readings:
            # all sensors rejected — fail safe
            self._close_valve(now)
            note = "all readings rejected"
            return TickResult(
                timestamp=now,
                moisture_percent=None,
                valve_was_open=valve_was_open,
                valve_is_open=self._valve.is_open,
                note=note,
            )
        # compute the average
        avg = sum(good_readings) / len(good_readings)

        if self._valve.is_open:
            note = self._decide_open_state(now, avg)
        else:
            note = self._decide_closed_state(now, avg)

        return TickResult(
            timestamp=now,
            moisture_percent=avg,
            valve_was_open=valve_was_open,
            valve_is_open=self._valve.is_open,
            note=note,
        )
