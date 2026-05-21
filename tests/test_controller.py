from datetime import datetime

import pytest

from auto_garden.config import AppConfig
from auto_garden.controller import IrrigationController
from auto_garden.hardware.sensor import FakeMoistureSensor
from auto_garden.hardware.valve import FakeValve
from tests.conftest import FakeClock


# State A -- Valve is currently *OPEN*
def test_open_valve_closes_on_all_bad_sensor_readings(app_config: AppConfig) -> None:
    sensors = [
        FakeMoistureSensor(sensor_id="alpha", raw=700, percent=20),
        FakeMoistureSensor(sensor_id="bravo", raw=700, percent=20),
    ]
    valve = FakeValve()  # Default closed
    clock = FakeClock(start=datetime(2026, 5, 16, 12, 0, 0))
    controller = IrrigationController(sensors=sensors, valve=valve, config=app_config, clock=clock)

    # tick open on good sensor readings
    controller.tick()
    assert valve.is_open

    # all bad readings, valve should close
    sensors[0].raw = 2000
    sensors[1].raw = 2000
    result = controller.tick()
    assert not valve.is_open
    assert not result.valve_is_open
    assert result.moisture_percent is None


def test_open_valve_closes_on_open_gt_max_seconds(app_config: AppConfig) -> None:
    # Arrange — build everything the controller needs in the state we want
    sensors = [
        FakeMoistureSensor(sensor_id="alpha", raw=700, percent=20),
        FakeMoistureSensor(sensor_id="bravo", raw=700, percent=20),
    ]
    valve = FakeValve()  # Default closed
    clock = FakeClock(start=datetime(2026, 5, 16, 12, 0, 0))
    controller = IrrigationController(sensors=sensors, valve=valve, config=app_config, clock=clock)

    # Open valve
    controller.tick()
    assert valve.is_open

    # mutate sensors to mid-range so moisture alone wouldn't close
    sensors[0].percent = 45
    sensors[1].percent = 45

    # advance the clock past max_open_seconds (120 in the fixture)
    clock.advance(seconds=121)

    # tick 2: should close because we've been open too long
    result = controller.tick()
    assert not valve.is_open
    assert not result.valve_is_open


def test_open_valve_closes_on_moisture_avg_gt_close_above_percent(app_config: AppConfig) -> None:
    # Arrange — build everything the controller needs in the state we want
    sensors = [
        FakeMoistureSensor(sensor_id="alpha", raw=700, percent=20),
        FakeMoistureSensor(sensor_id="bravo", raw=700, percent=20),
    ]
    valve = FakeValve()  # Default closed
    clock = FakeClock(start=datetime(2026, 5, 16, 12, 0, 0))
    controller = IrrigationController(sensors=sensors, valve=valve, config=app_config, clock=clock)

    # Open valve
    controller.tick()
    assert valve.is_open

    # Close valve again
    sensors[0].percent = 90
    sensors[1].percent = 90
    result = controller.tick()
    assert not valve.is_open
    assert not result.valve_is_open
    assert result.moisture_percent == pytest.approx(90.0)


def test_open_valve_stays_open_when_no_close_trigger_fires(app_config: AppConfig) -> None:
    sensors = [
        FakeMoistureSensor(sensor_id="alpha", raw=700, percent=20),
        FakeMoistureSensor(sensor_id="bravo", raw=700, percent=20),
    ]
    valve = FakeValve()  # Default closed
    clock = FakeClock(start=datetime(2026, 5, 16, 12, 0, 0))
    controller = IrrigationController(sensors=sensors, valve=valve, config=app_config, clock=clock)

    # Open valve
    controller.tick()
    assert valve.is_open

    sensors[0].percent = 45
    sensors[1].percent = 45
    result = controller.tick()
    assert valve.is_open
    assert result.valve_is_open
    assert result.moisture_percent == pytest.approx(45.0)


# State B -- Valve is currently *CLOSED*
def test_stays_closed_on_all_bad_readings(app_config: AppConfig) -> None:
    sensors = [
        FakeMoistureSensor(sensor_id="alpha", raw=2000, percent=20),
        FakeMoistureSensor(sensor_id="bravo", raw=2000, percent=20),
    ]
    valve = FakeValve()  # Default closed
    clock = FakeClock(start=datetime(2026, 5, 16, 12, 0, 0))
    controller = IrrigationController(sensors=sensors, valve=valve, config=app_config, clock=clock)

    result = controller.tick()

    assert not valve.is_open
    assert not result.valve_is_open
    assert result.moisture_percent is None


def test_stays_closed_on_cooldown_not_elapsed(app_config: AppConfig) -> None:
    sensors = [
        FakeMoistureSensor(sensor_id="alpha", raw=700, percent=20),
        FakeMoistureSensor(sensor_id="bravo", raw=700, percent=20),
    ]
    valve = FakeValve()
    clock = FakeClock(start=datetime(2026, 5, 16, 12, 0, 0))
    controller = IrrigationController(sensors=sensors, valve=valve, config=app_config, clock=clock)

    # tick 1: dry sensors -> valve opens
    controller.tick()
    assert valve.is_open

    # tick 2: wet sensors -> valve closes, _last_closed_at gets set
    sensors[0].percent = 90
    sensors[1].percent = 90
    controller.tick()
    assert not valve.is_open

    # tick 3: dry again, but only 60s later -- well inside the 1800s cooldown
    sensors[0].percent = 20
    sensors[1].percent = 20
    clock.advance(seconds=60)
    result = controller.tick()

    assert not valve.is_open  # cooldown blocked the re-open
    assert not result.valve_is_open


def test_closed_valve_opens_on_moisture_avg_lt_open_below_percent(app_config: AppConfig) -> None:
    sensors = [
        FakeMoistureSensor(sensor_id="alpha", raw=700, percent=20),
        FakeMoistureSensor(sensor_id="bravo", raw=700, percent=20),
    ]
    valve = FakeValve()  # Default closed
    clock = FakeClock(start=datetime(2026, 5, 16, 12, 0, 0))
    controller = IrrigationController(sensors=sensors, valve=valve, config=app_config, clock=clock)

    result = controller.tick()

    assert valve.is_open
    assert result.valve_is_open
    assert result.moisture_percent == pytest.approx(20.0)


def test_closed_valve_stays_closed_when_moisture_above_open_threshold(
    app_config: AppConfig,
) -> None:
    sensors = [
        FakeMoistureSensor(sensor_id="alpha", raw=700, percent=90),
        FakeMoistureSensor(sensor_id="bravo", raw=700, percent=90),
    ]
    valve = FakeValve()  # Default closed
    clock = FakeClock(start=datetime(2026, 5, 16, 12, 0, 0))
    controller = IrrigationController(sensors=sensors, valve=valve, config=app_config, clock=clock)

    result = controller.tick()

    assert not valve.is_open
    assert not result.valve_is_open
    assert result.moisture_percent == pytest.approx(90.0)


def test_first_tick_opens_valve_if_dry_without_waiting_for_cooldown(
    app_config: AppConfig,
) -> None:
    # A freshly-built controller has never closed a valve -> _last_closed_at is None.
    # The cooldown gate must NOT block this first watering.
    sensors = [
        FakeMoistureSensor(sensor_id="alpha", raw=700, percent=20),
        FakeMoistureSensor(sensor_id="bravo", raw=700, percent=20),
    ]
    valve = FakeValve()
    clock = FakeClock(start=datetime(2026, 5, 16, 12, 0, 0))
    controller = IrrigationController(sensors=sensors, valve=valve, config=app_config, clock=clock)

    result = controller.tick()  # the FIRST tick — no prior history

    assert valve.is_open
    assert result.valve_is_open
