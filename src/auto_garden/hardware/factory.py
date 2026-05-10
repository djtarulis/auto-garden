"""Picks real or fake hardware based on whether we're running on a Pi
(or in simulate mode). The rest of the app never imports concrete classes
directly — they ask the factory for what they need.
"""

from __future__ import annotations

from auto_garden.hardware.sensor import MoistureSensor, SensorCalibration
from auto_garden.hardware.valve import Valve


def build_sensors(
    calibrations: list[SensorCalibration],
    spi_bus: int,
    spi_device: int,
    *,
    simulate: bool,
) -> list[MoistureSensor]:
    # TODO: if `simulate` is True, return a list of FakeMoistureSensor objects
    # built from the calibration list. Otherwise return MCP3008 sensors.
    # Think about what id / starting value the fakes should have.
    raise NotImplementedError


def build_valve(gpio_pin: int, active_high: bool, *, simulate: bool) -> Valve:
    # TODO: same pattern — FakeValve in simulation, RelayValve on the Pi.
    raise NotImplementedError
