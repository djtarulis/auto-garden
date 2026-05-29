"""Persistent log of sensor readings and watering events.

Why: lets you build the dashboard later without re-instrumenting; lets you
debug "why did it water at 3 a.m. last night"; lets you tune thresholds
based on real history.

Recommended: SQLite (stdlib, zero ops). Two tables to start:
  readings(id, ts, sensor_id, raw, percent)
  events(id, ts, kind, note)        -- kind in ('open', 'close', 'error')
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from auto_garden.controller import TickResult


class EventLog:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        conn = sqlite3.connect(db_path)
        conn.execute(  # create tick log table
            """CREATE TABLE IF NOT EXISTS tick_log (
                id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                moisture_percent REAL,
                valve_is_open INTEGER NOT NULL,
                note TEXT NOT NULL
            )"""
        )
        conn.execute(  # create errors table
            """CREATE TABLE IF NOT EXISTS errors (
                id INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                note TEXT NOT NULL
            )"""
        )
        conn.commit()  # save changes
        conn.close()  # close connection

    def record_tick(self, tick: TickResult) -> None:
        conn = sqlite3.connect(self._db_path)
        conn.execute(
            """
                INSERT INTO tick_log (timestamp, moisture_percent, valve_is_open, note)
                VALUES(?, ?, ?, ?)
            """,
            (tick.timestamp.isoformat(), tick.moisture_percent, int(tick.valve_is_open), tick.note),
        )
        conn.commit()
        conn.close()  # Close connection

    def record_error(self, when: datetime, note: str) -> None:
        conn = sqlite3.connect(self._db_path)
        conn.execute(
            """
                INSERT INTO errors (timestamp, note)
                VALUES(?, ?)
            """,
            (when.isoformat(), note),
        )
        conn.commit()
        conn.close()  # Close connection
