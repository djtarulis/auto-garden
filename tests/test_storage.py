import sqlite3
from datetime import datetime
from pathlib import Path

from auto_garden.controller import TickResult
from auto_garden.storage import EventLog


def test_init_creates_both_tables(tmp_path: Path) -> None:
    """Test if the tick_log and errors tables are created successfully"""
    db_path = tmp_path / "test.db"
    EventLog(db_path)  # Construct EventLog

    conn = sqlite3.connect(db_path)  # Open test.db
    # fetch both tables
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    conn.close()  # Close connection

    table_names = [row[0] for row in rows]  # Extract first element of each tuple

    assert "tick_log" in table_names
    assert "errors" in table_names


def test_construct_tick_log_twice(tmp_path: Path) -> None:
    """Attempt to create the tick_log twice without crash"""
    db_path = tmp_path / "test.db"
    EventLog(db_path)  # Construct EventLog
    EventLog(db_path)  # Construct EventLog a second time

    conn = sqlite3.connect(db_path)  # Open test.db
    # fetch both tables
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    conn.close()  # Close connection

    table_names = [row[0] for row in rows]  # Extract first element of each tuple

    assert "tick_log" in table_names
    assert "errors" in table_names


def test_successful_adding_tick_result(tmp_path: Path) -> None:
    """Test if table populates successfully after one tick()"""
    db_path = tmp_path / "test.db"
    log = EventLog(db_path)
    tick = TickResult(
        timestamp=datetime(2026, 5, 16, 12, 0, 0),
        moisture_percent=20.0,
        valve_was_open=True,
        valve_is_open=True,
        note="This is a test note",
    )
    log.record_tick(tick)
    conn = sqlite3.connect(db_path)

    table = conn.execute("SELECT * FROM tick_log").fetchall()
    assert len(table) == 1  #   Exactly one row was added
    conn.close()

    row = table[0]

    assert row[1] == tick.timestamp.isoformat()  # ISO format
    assert row[2] == 20.0
    assert row[3] == 1
    assert row[4] == "This is a test note"


def test_record_tick_with_null_moisture(tmp_path: Path) -> None:
    """Verify null tick is stored as SQL NULL"""
    db_path = tmp_path / "test.db"
    log = EventLog(db_path)
    tick = TickResult(
        timestamp=datetime(2026, 5, 16, 12, 0, 0),
        moisture_percent=None,
        valve_was_open=True,
        valve_is_open=True,
        note="This is a test note",
    )
    log.record_tick(tick)
    conn = sqlite3.connect(db_path)

    table = conn.execute("SELECT * FROM tick_log").fetchall()
    assert len(table) == 1  #   Exactly one row was added
    conn.close()

    row = table[0]

    assert row[1] == tick.timestamp.isoformat()  # ISO format
    assert row[2] is None  # Null moisture percent
    assert row[3] == 1
    assert row[4] == "This is a test note"


def test_record_error_in_error_log(tmp_path: Path) -> None:
    """Simulate an error in the error log successfully"""
    db_path = tmp_path / "test.db"
    log = EventLog(db_path)
    when = datetime(2026, 5, 16, 12, 0, 0)
    note = "This is a test error message"
    log.record_error(when, note)
    conn = sqlite3.connect(db_path)

    table = conn.execute("SELECT * FROM errors").fetchall()
    assert len(table) == 1  #   Exactly one row was added
    conn.close()

    row = table[0]

    assert row[1] == when.isoformat()  # ISO format
    assert row[2] == note
