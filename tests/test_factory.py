import pytest

from auto_garden.hardware.factory import build_sensors, build_valve
from auto_garden.hardware.sensor import FakeMoistureSensor, SensorCalibration
from auto_garden.hardware.valve import FakeValve

# @pytest.fixture
# def simulated_sensor_data() -> list[SensorCalibration]:
#     return [
#         SensorCalibration(sensor_id="alpha", channel=0, dry_value=100, wet_value=800),
#         SensorCalibration(sensor_id="bravo", channel=1, dry_value=100, wet_value=800),
#         SensorCalibration(sensor_id="charlie", channel=2, dry_value=200, wet_value=600),
#         SensorCalibration(sensor_id="delta", channel=3, dry_value=50, wet_value=700),
#         SensorCalibration(sensor_id="echo", channel=4, dry_value=75, wet_value=600),
#         SensorCalibration(sensor_id="fox", channel=5, dry_value=100, wet_value=1000),
#     ]


def test_build_sensors_in_simulate_mode_returns_fake_sensors() -> None:
    # Two test calibration objects...
    calibrations = [
        SensorCalibration(sensor_id="alpha", channel=0, dry_value=100, wet_value=800),
        SensorCalibration(sensor_id="bravo", channel=1, dry_value=100, wet_value=800),
    ]
    # build_sensors requires a list of calibrations, fakes only read sensor_id
    result = build_sensors(calibrations, spi_bus=0, spi_device=0, simulate=True)

    assert len(result) == len(calibrations)
    assert all(isinstance(sensor, FakeMoistureSensor) for sensor in result)
    assert result[0].sensor_id == "alpha"
    assert result[1].sensor_id == "bravo"


def test_build_valve_in_simulate_mode_returns_fake_valve() -> None:
    result = build_valve(gpio_pin=17, active_high=True, simulate=True)
    assert isinstance(result, FakeValve)


def test_build_sensors_raises_when_simulate_false() -> None:
    calibrations: list[SensorCalibration] = []
    with pytest.raises(NotImplementedError):
        build_sensors(calibrations, spi_bus=0, spi_device=0, simulate=False)


def test_build_valve_raises_when_simulate_false() -> None:
    with pytest.raises(NotImplementedError):
        build_valve(gpio_pin=17, active_high=True, simulate=False)
