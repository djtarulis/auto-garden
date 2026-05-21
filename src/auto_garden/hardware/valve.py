"""Solenoid valve interface and implementations.

Safety reminder: a valve that fails open will drain the entire barrel onto
the bed. The controller is responsible for max-open-duration enforcement;
this module is only responsible for "open" / "close" / "what state am I in".
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class Valve(ABC):
    """Interface every valve implementation must satisfy."""

    @abstractmethod
    def open(self) -> None:
        """Energise the relay so the solenoid opens."""

    @abstractmethod
    def close(self) -> None:
        """De-energise the relay so the solenoid closes (it is normally closed)."""

    @property
    @abstractmethod
    def is_open(self) -> bool: ...


# ---------------------------------------------------------------------------
# Real hardware implementation
# ---------------------------------------------------------------------------
class RelayValve(Valve):
    """Drives a 5 V relay module from a single GPIO pin."""

    def __init__(self, gpio_pin: int, active_high: bool = True) -> None:
        self._pin = gpio_pin
        self._active_high = active_high
        self._is_open = False
        # TODO: set up the GPIO pin as an output using gpiozero.OutputDevice
        #       (or RPi.GPIO if you prefer). Make sure it starts CLOSED.

    def open(self) -> None:
        # TODO: drive the GPIO pin to the level that energises the relay.
        # Hint: `active_high` means HIGH = on. For active-low boards it's
        # inverted — that's why the config exposes the choice.
        raise NotImplementedError

    def close(self) -> None:
        # TODO: drive the GPIO pin to the opposite level so the relay opens
        # and the solenoid de-energises (and snaps shut, since it's NC).
        raise NotImplementedError

    @property
    def is_open(self) -> bool:
        return self._is_open


# ---------------------------------------------------------------------------
# Fake implementation — used for tests and `--simulate` mode.
# ---------------------------------------------------------------------------
class FakeValve(Valve):
    """In-memory valve. Records open/close calls for assertions in tests."""

    def __init__(self) -> None:
        self._is_open = False
        self.open_count = 0
        self.close_count = 0

    def open(self) -> None:
        self._is_open = True
        self.open_count += 1

    def close(self) -> None:
        self._is_open = False
        self.close_count += 1

    @property
    def is_open(self) -> bool:
        return self._is_open
