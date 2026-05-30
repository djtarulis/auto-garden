from pathlib import Path
from typing import Any

import pydantic
import pytest
import yaml

from auto_garden.config import AppConfig, load_config


@pytest.fixture
def valid_config_data() -> dict[str, Any]:
    return {
        "loop_interval_seconds": 60,
        "sensors": {
            "spi_bus": 0,
            "spi_device": 0,
            "channels": [
                {"id": "bed_front", "channel": 0, "dry_value": 800, "wet_value": 350},
            ],
        },
        "thresholds": {"open_below_percent": 30, "close_above_percent": 60},
        "safety": {
            "max_open_seconds": 120,
            "min_seconds_between_waterings": 1800,
            "reject_readings_outside": [50, 1000],
        },
        "valve": {"gpio_pin": 17, "active_high": True},
        "storage": {"database_path": "data/auto-garden.db"},
        "logging": {"level": "INFO"},
    }


def test_load_config_reads_valid_yaml(tmp_path: Path, valid_config_data: dict[str, Any]) -> None:
    config_path = tmp_path / "config.yaml"

    with config_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(valid_config_data, f)

    result = load_config(config_path)

    assert isinstance(result, AppConfig)
    assert result.loop_interval_seconds == 60
    assert result.safety.max_open_seconds == 120
    assert result.valve.gpio_pin == 17
    assert result.thresholds.close_above_percent == 60


def test_load_config_raises_when_file_missing(tmp_path: Path) -> None:
    # tmp_path is empty — point load_config at a file that doesn't exist
    missing = tmp_path / "does_not_exist.yaml"
    substring = "config.example.yaml"
    with pytest.raises(FileNotFoundError) as excinfo:
        load_config(missing)
    assert substring in str(excinfo.value)


def test_load_config_raises_on_malformed_yaml(tmp_path: Path) -> None:
    # write deliberately broken YAML to a file
    bad = tmp_path / "broken.yaml"
    bad.write_text("this is: not\n  - valid: yaml: at all", encoding="utf-8")
    # assert it raises yaml.YAMLError
    # (look up the exact exception class in the pyyaml docs if you need to)
    with pytest.raises(yaml.YAMLError):
        load_config(bad)


def test_load_config_raises_on_schema_violation(
    tmp_path: Path, valid_config_data: dict[str, Any]
) -> None:
    config_path = tmp_path / "data_dump.yaml"
    bad_data = dict(valid_config_data)
    bad_data["thresholds"] = {"open_below_percent": 200, "close_above_percent": -60}
    # write it to tmp_path / "bad_schema.yaml" via yaml.safe_dump
    with config_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(bad_data, f)
    # assert it raises pydantic.ValidationError
    with pytest.raises(pydantic.ValidationError):
        load_config(config_path)
