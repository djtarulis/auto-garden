# Architecture

## High-level flow

```
┌─────────────┐    ┌─────────────────┐    ┌──────────┐
│ MoistureSensor │ -> │ IrrigationController │ -> │  Valve   │
└─────────────┘    └─────────────────┘    └──────────┘
                          │
                          ▼
                     ┌──────────┐
                     │ EventLog │
                     └──────────┘
```

The CLI loads config → builds hardware via the factory (real or fake) →
constructs the controller → runs `tick()` on a loop.

## Why a hardware abstraction layer?

`MoistureSensor` and `Valve` are abstract. The controller never imports
`MCP3008MoistureSensor` or `RelayValve` directly. This buys us:

- **Off-Pi development.** You can run the whole thing on Windows/macOS using the fake implementations, no GPIO required.
- **Real unit tests.** The controller can be tested against fakes that return whatever values the test wants — including weird ones (negative readings, wildly bouncing values, "all sensors disconnected").
- **Future flexibility.** Swap MCP3008 for an I²C ADC, or swap the relay for a MOSFET driver, without touching the controller.

## Layering rules

- `hardware/` — talks to physical devices, nothing else. No app logic.
- `config.py` — pydantic models + loader. No I/O beyond reading the YAML.
- `controller.py` — pure decision logic. Depends only on the abstract interfaces and config. **No GPIO imports.**
- `storage.py` — persistence. No decision logic.
- `cli.py` — wiring + entry points. Thin.

If you find yourself importing `gpiozero` outside `hardware/`, stop and reroute through an interface. That's the rule that keeps the project testable and portable.

## Loop pseudocode

```
while not stopped:
    tick = controller.tick()           # reads sensors, decides, acts on valve
    storage.record_tick(tick, ...)     # persist
    sleep(loop_interval_seconds)
on shutdown:
    valve.close()                      # always leave the bed safe
```

Safety invariants the controller must uphold:

1. The valve is never open longer than `safety.max_open_seconds` in one stretch.
2. After the valve closes, it stays closed for at least `safety.min_seconds_between_waterings`.
3. If all sensor readings are bad in a tick, default to closing the valve.
