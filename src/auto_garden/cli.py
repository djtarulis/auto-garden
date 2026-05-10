"""Command-line interface.

Wires together: load config -> build hardware (real or fake) -> run loop.
Keep this file thin — all real work lives in controller / hardware / storage.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

app = typer.Typer(help="Automated garden watering system.")

DEFAULT_CONFIG = Path("config/config.yaml")

ConfigOpt = Annotated[Path, typer.Option(help="Path to config YAML.")]
SimulateOpt = Annotated[bool, typer.Option(help="Use fake hardware (no Pi required).")]


@app.command()
def run(
    config: ConfigOpt = DEFAULT_CONFIG,
    simulate: SimulateOpt = False,
) -> None:
    """Run the irrigation loop until interrupted."""
    # TODO:
    #   1. load config
    #   2. build sensors + valve via the factory (passing `simulate`)
    #   3. build the controller and the event log
    #   4. loop: tick(), log result, sleep config.loop_interval_seconds
    #   5. handle KeyboardInterrupt -> close valve cleanly before exiting
    raise NotImplementedError


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
