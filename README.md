# auto-garden

> Automated garden watering system for Raspberry Pi — capacitive moisture sensors decide when a gravity-fed solenoid valve opens.

[![CI](https://github.com/djtarulis/auto-garden/actions/workflows/ci.yml/badge.svg)](https://github.com/djtarulis/auto-garden/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)

## Overview

`auto-garden` keeps a home garden bed watered automatically. Capacitive soil moisture sensors are read through an MCP3008 ADC; when the average reading falls below a configurable threshold, the controller opens a 12 V DC solenoid valve at the base of a gravity-fed water barrel. Every reading and watering event is logged for later inspection.

The project is designed to be:

- **Testable off-Pi** — a hardware abstraction layer with fake implementations means logic can be developed and tested on any machine.
- **Configuration-driven** — pin assignments, thresholds, schedules, and safety limits live in YAML, not source.
- **Safe by default** — max-open duration, cooldown periods, and sensor-sanity checks prevent flooding the bed if anything goes wrong.

## Hardware

| Component | Purpose |
| --- | --- |
| Raspberry Pi 5 | Controller |
| Capacitive Soil Moisture Sensor (3.3–5.5 V, corrosion-resistant) | Reads moisture in the bed |
| MCP3008 ADC | Converts analog sensor output to digital over SPI (Pi has no analog input) |
| 5 V relay module (opto-isolated) | Switches the solenoid safely from a GPIO pin |
| U.S. Solid 12 V DC NPT Brass Solenoid Valve, 3/4", normally closed | Controls water flow from barrel |
| 12 V DC, ≥1 A power supply | Powers the solenoid |
| Water barrel | Gravity-fed reservoir |

See [docs/hardware.md](docs/hardware.md) for a wiring diagram and detailed pinout.

## Architecture

See [docs/architecture.md](docs/architecture.md). High-level: a periodic loop reads sensors → controller decides → valve actor applies → storage logs everything.

## Setup

```bash
# Clone
git clone https://github.com/djtarulis/auto-garden.git
cd auto-garden

# Create venv and install (dev tools)
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# On the Pi only — install hardware extras
pip install -e ".[dev,pi]"

# Wire up pre-commit hooks
pre-commit install
```

Copy the example config and edit it:

```bash
cp config/config.example.yaml config/config.yaml
```

## Usage

The CLI exposes two commands: `run` (the control loop) and `read` (a one-off sensor dump for calibration).

### Running the control loop

```bash
# Run with the default config (config/config.yaml)
auto-garden run

# Point at a specific config file
auto-garden run --config config/bed_back.yaml
```

### Try it without hardware

The whole system runs on any machine in **simulation mode** — no Pi, sensors, or valve required. Scripted scenarios drive the controller through its decision branches so you can watch it behave:

```bash
# Soil dries out over time -> controller opens the valve, then closes once watered
auto-garden run --simulate --scenario drying --max-iterations 10 --interval 1

# Bed is already wet -> valve stays closed
auto-garden run --simulate --scenario flood --max-iterations 10 --interval 1

# A sensor returns garbage -> bad readings are rejected; if all are bad the
# valve fails safe (closed)
auto-garden run --simulate --scenario bad-sensor --max-iterations 10 --interval 1
```

Useful flags:

| Flag | Default | Purpose |
| --- | --- | --- |
| `--simulate` | off | Use fake hardware instead of real GPIO/SPI |
| `--scenario` | none | Scripted demo: `drying`, `flood`, or `bad-sensor` (requires `--simulate`) |
| `--max-iterations` | 20 | Stop after N tick cycles |
| `--interval` | from config | Seconds between ticks (overrides `loop_interval_seconds`) |

Every tick prints a one-line summary and is persisted to SQLite. Scenario runs write to a separate `data/demo.db` so they never pollute real history.

### Reading sensors (calibration)

```bash
auto-garden read --simulate
```

Prints the raw ADC value and converted percentage for each configured sensor. Record the raw values with the probe in dry air and fully submerged, then plug those into `dry_value` / `wet_value` in your config.

## Development

```bash
# Lint + format
ruff check .
ruff format .

# Type check
mypy

# Test
pytest
```

All three are wired into pre-commit and CI.

## Roadmap

- [x] v0.1 — sensor read → threshold decision → valve open/close, with logging
- [x] v0.2 — YAML-driven config + safety limits (max open duration, cooldown)
- [x] v0.3 — SQLite event log
- [x] v0.7 — Sensor calibration CLI command (`auto-garden read`)
- [ ] Pi hardware drivers (MCP3008 ADC + relay) — wiring up real GPIO/SPI
- [ ] v0.4 — Web dashboard (FastAPI + a simple chart)
- [ ] v0.5 — Weather API integration (skip if rain forecast)
- [ ] v0.6 — Notifications (Pushover / Telegram)
- [ ] v0.8 — systemd service for auto-start on boot

## License

[MIT](LICENSE)
