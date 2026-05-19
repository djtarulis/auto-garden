from datetime import datetime, timedelta

import pytest

from auto_garden.config import AppConfig


@pytest.fixture
def app_config() -> AppConfig:
    """Sensible default config for controller tests. Override fields per-test if needed."""
    return AppConfig.model_validate(
        {
            "loop_interval_seconds": 60,
            "sensors": {
                "spi_bus": 0,
                "spi_device": 0,
                "channels": [
                    {"id": "alpha", "channel": 0, "dry_value": 800, "wet_value": 350},
                    {"id": "bravo", "channel": 1, "dry_value": 800, "wet_value": 350},
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
    )


class FakeClock:
    def __init__(self, start: datetime) -> None:
        # store start
        self._now = start

    def now(self) -> datetime:
        # return stored time
        return self._now

    def advance(self, seconds: int) -> None:
        # add timedelta(seconds=seconds) to stored time
        self._now += timedelta(seconds=seconds)


def test_fake_clock_advances() -> None:
    start = datetime(2026, 5, 16, 12, 0, 0)
    clock = FakeClock(start)
    assert clock.now() == start
    clock.advance(seconds=60)
    assert clock.now() == start + timedelta(seconds=60)
