"""Hardware abstraction layer.

The application talks to `MoistureSensor` and `Valve` *interfaces* — not
concrete hardware. This means:

- On a Pi, real implementations (MCP3008, GPIO relay) are wired in.
- Off a Pi (your laptop, CI), fake implementations are wired in instead.
- Tests can swap in fakes without ever touching real GPIO.
"""
