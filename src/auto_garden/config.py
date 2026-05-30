"""Configuration loading + validation.

Uses pydantic so a malformed YAML file fails loudly at startup — not at
3 a.m. when a sensor pin is wrong and the bed is overflowing.

Review every field against `config/config.example.yaml`. If you add a new
config key, add it in BOTH places or pydantic will reject the YAML.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class SensorChannelConfig(BaseModel):
    id: str
    channel: int = Field(ge=0, le=7)
    dry_value: int
    wet_value: int


class SensorsConfig(BaseModel):
    spi_bus: int
    spi_device: int
    channels: list[SensorChannelConfig]


class ThresholdsConfig(BaseModel):
    open_below_percent: float = Field(ge=0, le=100)
    close_above_percent: float = Field(ge=0, le=100)


class SafetyConfig(BaseModel):
    max_open_seconds: int = Field(gt=0)
    min_seconds_between_waterings: int = Field(ge=0)
    reject_readings_outside: tuple[int, int]


class ValveConfig(BaseModel):
    gpio_pin: int
    active_high: bool = True


class StorageConfig(BaseModel):
    database_path: str


class LoggingConfig(BaseModel):
    level: str = "INFO"


class AppConfig(BaseModel):
    loop_interval_seconds: int = Field(gt=0)
    sensors: SensorsConfig
    thresholds: ThresholdsConfig
    safety: SafetyConfig
    valve: ValveConfig
    storage: StorageConfig
    logging: LoggingConfig


def load_config(path: Path) -> AppConfig:
    try:
        with path.open("r", encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"File Not Found -> {path}: copy config/config.example.yaml to config/config.yaml"
        ) from None
    return AppConfig.model_validate(yaml_data)
