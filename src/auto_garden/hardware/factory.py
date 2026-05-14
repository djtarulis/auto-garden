"""Picks real or fake hardware based on whether we're running on a Pi
(or in simulate mode). The rest of the app never imports concrete classes
directly — they ask the factory for what they need.
"""

from __future__ import annotations

from auto_garden.hardware.sensor import FakeMoistureSensor, MoistureSensor, SensorCalibration
from auto_garden.hardware.valve import FakeValve, Valve


def build_sensors(
    calibrations: list[SensorCalibration],
    spi_bus: int,
    spi_device: int,
    *,
    simulate: bool,
) -> list[MoistureSensor]:
    # TODO implement hardware mode
    # built from the calibration list. Otherwise return MCP3008 sensors.
    # Think about what id / starting value the fakes should have.
    if not simulate:
        raise NotImplementedError("hardware mode not yet supported")
    return [FakeMoistureSensor(sensor_id=cal.sensor_id) for cal in calibrations]


def build_valve(gpio_pin: int, active_high: bool, *, simulate: bool) -> Valve:
    # TODO implement hardware mode
    if not simulate:
        raise NotImplementedError("hardware mode not yet supported")
    return FakeValve()
