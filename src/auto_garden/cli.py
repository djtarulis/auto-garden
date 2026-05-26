"""Command-line interface.

Wires together: load config -> build hardware (real or fake) -> run loop.

"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Annotated

import typer

from auto_garden.config import SensorChannelConfig, load_config
from auto_garden.controller import IrrigationController, TickResult
from auto_garden.hardware.factory import build_sensors, build_valve
from auto_garden.hardware.sensor import SensorCalibration
from auto_garden.scenarios import Scenario, ScenarioMoistureSensor, build_scenario_sensors

app = typer.Typer(help="Automated garden watering system.")

DEFAULT_CONFIG = Path("config/config.yaml")

ConfigOpt = Annotated[Path, typer.Option(help="Path to config YAML.")]
SimulateOpt = Annotated[bool, typer.Option(help="Use fake hardware (no Pi required).")]
MaxIterationsOpt = Annotated[int, typer.Option(help="Stop after this many tick cycles.")]
IntervalOpt = Annotated[
    int | None, typer.Option(help="Override loop_interval_seconds from config.")
]
ScenarioOpt = Annotated[
    Scenario | None, typer.Option(help="Select test scenario drying|flood|bad-sensor")
]


def _channels_to_calibrations(
    channels: list[SensorChannelConfig],
) -> list[SensorCalibration]:
    """Convert config channel models into hardware-layer calibration objects."""
    return [
        SensorCalibration(
            sensor_id=c.id,
            channel=c.channel,
            dry_value=c.dry_value,
            wet_value=c.wet_value,
        )
        for c in channels
    ]


def _format_tick(result: TickResult) -> str:
    """Format a TickResult as a one-line human-readable summary."""
    valve_state = "OPEN" if result.valve_is_open else "closed"
    moisture = (
        f"{result.moisture_percent:.1f}"  # round to 1 decimal
        if result.moisture_percent is not None
        else "-"
    )
    return f"[{result.timestamp:%H:%M:%S}] moisture={moisture}% valve={valve_state} - {result.note}"


@app.command()
def run(
    config: ConfigOpt = DEFAULT_CONFIG,
    simulate: SimulateOpt = False,
    max_iterations: MaxIterationsOpt = 20,
    interval: IntervalOpt = None,
    scenario: ScenarioOpt = None,
) -> None:
    # 1. Load config
    app_config = load_config(config)

    # 2. Check for simulate flag on scenario demo
    if scenario is not None and not simulate:
        raise typer.BadParameter("--scenario requires --simulate")

    # 3. Convert config channels → SensorCalibration objects (helper)
    calibrations = _channels_to_calibrations(app_config.sensors.channels)

    # 4. Build hardware via the factory
    if scenario is not None:
        sensors = build_scenario_sensors(
            scenario,
            calibrations,
        )
    else:
        sensors = build_sensors(
            calibrations,
            spi_bus=app_config.sensors.spi_bus,
            spi_device=app_config.sensors.spi_device,
            simulate=simulate,
        )

    valve = build_valve(
        gpio_pin=app_config.valve.gpio_pin,
        active_high=app_config.valve.active_high,
        simulate=simulate,
    )

    # 4. Build the controller
    controller = IrrigationController(sensors=sensors, valve=valve, config=app_config)

    # 5. Determine sleep interval (flag overrides config)
    sleep_seconds = interval if interval is not None else app_config.loop_interval_seconds

    # 6. Loop with safe shutdown
    try:
        for _ in range(max_iterations):
            result = controller.tick()
            for s in sensors:
                if isinstance(s, ScenarioMoistureSensor):
                    s.advance()
            print(_format_tick(result))
            time.sleep(sleep_seconds)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        valve.close()  # ALWAYS runs
        print("Valve closed. Exiting.")


@app.command()
def read(
    config: ConfigOpt = DEFAULT_CONFIG,
    simulate: SimulateOpt = False,
) -> None:
    """Take a single reading from each sensor and print it."""
    # TODO: load config, build sensors, print one line per sensor with
    # raw + percent. Handy for calibration and field debugging.
    raise NotImplementedError


if __name__ == "__main__":
    app()
