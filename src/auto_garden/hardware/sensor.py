"""Moisture sensor interface and implementations.

Design note: the rest of the app only depends on `MoistureSensor` (the
abstract base). Concrete classes are wired in by the factory. This is what
lets the controller logic be unit-tested without real hardware.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class SensorCalibration:
    """Per-sensor calibration values used to convert raw ADC counts to %.

    `dry_value` is the raw reading when the probe is in dry air.
    `wet_value` is the raw reading when the probe is fully submerged.
    Capacitive sensors typically read *higher* when dry — keep that in mind
    when you implement the conversion.
    """

    sensor_id: str
    channel: int
    dry_value: int
    wet_value: int


class MoistureSensor(ABC):
    """Interface every moisture sensor implementation must satisfy."""

    @property
    @abstractmethod
    def sensor_id(self) -> str: ...

    @abstractmethod
    def read_raw(self) -> int:
        """Return the raw 10-bit ADC reading (0 to 1023)."""

    @abstractmethod
    def read_percent(self) -> float:
        """Return the moisture reading converted to a 0.0 to 100.0 percentage."""


# ---------------------------------------------------------------------------
# Real hardware implementation — YOU implement this on the Pi.
# ---------------------------------------------------------------------------
class MCP3008MoistureSensor(MoistureSensor):
    """Reads a capacitive moisture sensor through an MCP3008 ADC over SPI."""

    def __init__(self, calibration: SensorCalibration, spi_bus: int, spi_device: int) -> None:
        self._calibration = calibration
        self._spi_bus = spi_bus
        self._spi_device = spi_device
        # TODO: open the SPI device using adafruit_mcp3xxx (or spidev).
        #       Store the channel object so read_raw() can call it.

    @property
    def sensor_id(self) -> str:
        return self._calibration.sensor_id

    def read_raw(self) -> int:
        # TODO: read the raw value from the MCP3008 channel and return it.
        # Pseudocode:
        #   value = mcp_channel.value          # adafruit returns 0..65535
        #   return value >> 6                  # scale to 0..1023 if needed
        raise NotImplementedError

    def read_percent(self) -> float:
        # TODO: convert the raw reading into a 0..100 percentage using
        #       self._calibration.dry_value and self._calibration.wet_value.
        # Hints:
        #   - capacitive sensors read HIGHER when dry, LOWER when wet
        #   - clamp the result so noisy readings don't return >100 or <0
        #   - think about what "percent" means here: 0 = as dry as dry_value,
        #     100 = as wet as wet_value
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Fake implementation — used for tests and `--simulate` mode.
# Intentionally trivial so it teaches you nothing about the real problem.
# ---------------------------------------------------------------------------
class FakeMoistureSensor(MoistureSensor):
    """Returns whatever value you put in. For tests and off-Pi development."""

    def __init__(self, sensor_id: str, raw: int = 600, percent: float = 50.0) -> None:
        self._id = sensor_id
        self.raw = raw
        self.percent = percent

    @property
    def sensor_id(self) -> str:
        return self._id

    def read_raw(self) -> int:
        return self.raw

    def read_percent(self) -> float:
        return self.percent
