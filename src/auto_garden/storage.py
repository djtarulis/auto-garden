"""Persistent log of sensor readings and watering events.

Why: lets you build the dashboard later without re-instrumenting; lets you
debug "why did it water at 3 a.m. last night"; lets you tune thresholds
based on real history.

Recommended: SQLite (stdlib, zero ops). Two tables to start:
  readings(id, ts, sensor_id, raw, percent)
  events(id, ts, kind, note)        -- kind in ('open', 'close', 'error')
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from auto_garden.controller import TickResult


class EventLog:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        # TODO: open a sqlite3 connection. Run CREATE TABLE IF NOT EXISTS for
        # both tables. Decide: keep the connection open for the life of the
        # process, or open per-call? (Hint: per-call is simpler, fine for
        # this volume.)

    def record_tick(self, tick: TickResult, sensor_readings: dict[str, float]) -> None:
        # TODO: write one row per sensor into `readings`, and if the valve
        # transitioned (open->close or close->open) write a row into `events`.
        raise NotImplementedError

    def record_error(self, when: datetime, note: str) -> None:
        # TODO: insert a row in `events` with kind='error'.
        raise NotImplementedError
