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

```bash
# Run with the default config
auto-garden run

# Run in simulation mode (no real hardware required)
auto-garden run --simulate

# One-off sensor read
auto-garden read
```

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

- [ ] v0.1 — sensor read → threshold decision → valve open/close, with logging
- [ ] v0.2 — YAML-driven config + safety limits (max open duration, cooldown)
- [ ] v0.3 — SQLite event/reading log
- [ ] v0.4 — Web dashboard (FastAPI + a simple chart)
- [ ] v0.5 — Weather API integration (skip if rain forecast)
- [ ] v0.6 — Notifications (Pushover / Telegram)
- [ ] v0.7 — Sensor calibration CLI command
- [ ] v0.8 — systemd service for auto-start on boot

## License

[MIT](LICENSE)
