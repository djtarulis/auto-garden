"""Smoke tests — confirm the package is importable and fakes work.

This file exists so `pytest` has *something* to run from day one and CI
goes green on the first commit. As you implement features, add real tests
in their own files (test_controller.py, test_config.py, etc.) and delete
or expand this one.
"""

from __future__ import annotations

import auto_garden
from auto_garden.hardware.sensor import FakeMoistureSensor
from auto_garden.hardware.valve import FakeValve


def test_package_has_version() -> None:
    assert auto_garden.__version__


def test_fake_sensor_returns_configured_value() -> None:
    sensor = FakeMoistureSensor("test", raw=512, percent=42.0)
    assert sensor.read_raw() == 512
    assert sensor.read_percent() == 42.0
    assert sensor.sensor_id == "test"


def test_fake_valve_tracks_state() -> None:
    valve = FakeValve()
    assert not valve.is_open
    valve.open()
    assert valve.is_open
    valve.close()
    assert not valve.is_open
    assert valve.open_count == 1
    assert valve.close_count == 1
