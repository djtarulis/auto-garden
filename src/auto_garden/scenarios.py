from collections.abc import Callable
from enum import StrEnum

from auto_garden.hardware.sensor import MoistureSensor, SensorCalibration


class Scenario(StrEnum):
    DRYING = "drying"
    FLOOD = "flood"
    BAD_SENSOR = "bad-sensor"


def drying(tick: int, sensor_index: int) -> tuple[int, float]:
    """All sensors dry over time."""
    percent = max(10.0, 80.0 - tick * 5.0)
    return (700, percent)


def flood(tick: int, sensor_index: int) -> tuple[int, float]:
    """All sensors flood over time."""
    percent = min(100.0, 20.0 + tick * 8.0)
    return (700, percent)


def bad_sensor(tick: int, sensor_index: int) -> tuple[int, float]:
    """Only sensor 0 is bad"""
    if sensor_index == 0:  # First sensor reads bad input
        return (2000, 25.0)
    return (700, 20.0)


# It takes a tick number and a sensor index, returns (raw, percent).
ScenarioFn = Callable[[int, int], tuple[int, float]]

# The dispatch table: enum value -> function.
SCENARIOS: dict[Scenario, ScenarioFn] = {
    Scenario.DRYING: drying,
    Scenario.FLOOD: flood,
    Scenario.BAD_SENSOR: bad_sensor,
}


class ScenarioMoistureSensor(MoistureSensor):
    """A moisture sensor whose readings come from a scenario function.

    Use `advance()` to step the simulation forward each loop iteration.
    """

    def __init__(self, sensor_id: str, sensor_index: int, scenario_fn: ScenarioFn) -> None:
        self._id = sensor_id
        self._index = sensor_index
        self._scenario_fn = scenario_fn
        self._tick = 0
        # populate cache from tick 0 so the sensor is readable immediately
        self._raw, self._percent = scenario_fn(self._tick, self._index)

    @property
    def sensor_id(self) -> str:
        return self._id

    def read_raw(self) -> int:
        return self._raw

    def read_percent(self) -> float:
        return self._percent

    def advance(self) -> None:
        # step the simulation forward by one tick, recompute cached readings
        self._tick += 1
        self._raw, self._percent = self._scenario_fn(self._tick, self._index)


def build_scenario_sensors(
    scenario: Scenario,
    calibrations: list[SensorCalibration],
) -> list[MoistureSensor]:
    func = SCENARIOS[scenario]
    return [
        ScenarioMoistureSensor(sensor_id=c.sensor_id, sensor_index=index, scenario_fn=func)
        for index, c in enumerate(calibrations)
    ]
