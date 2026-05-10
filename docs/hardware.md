# Hardware

## Bill of materials

| # | Part | Notes |
| - | --- | --- |
| 1 | Raspberry Pi 5 | Any 40-pin Pi works; Pi 5 is what this project is built on. |
| N | Capacitive Soil Moisture Sensor v1.2 (3.3–5.5 V) | One per zone you want to monitor. |
| 1 | MCP3008 ADC | 8-channel 10-bit SPI ADC. Required because the Pi has no analog input. |
| 1 | 5 V relay module (opto-isolated, 1-channel) | Verify it has a flyback diode across the relay coil. |
| 1 | U.S. Solid 12 V DC NPT Brass Solenoid Valve, 3/4", normally closed | Inductive load — never drive directly from GPIO. |
| 1 | 12 V DC PSU, ≥1 A | Powers the solenoid. Separate from the Pi's 5 V supply. |
| 1 | Water barrel + plumbing | Gravity-fed. Mount higher than the bed for usable pressure. |

## Wiring

> TODO: drop a Fritzing diagram or hand-drawn schematic here once the
> hardware is assembled. A picture is worth a thousand words for portfolio
> reviewers.

Key wiring rules:

- **Common ground.** The 12 V supply ground and the Pi ground must be tied together if you're switching the relay from a Pi GPIO pin.
- **Relay vs MOSFET.** A relay module is the simplest path. The relay's input pin goes to a Pi GPIO; the relay's switched contacts go between 12 V+ and the solenoid.
- **Flyback diode.** A solenoid is an inductor; when it switches off it produces a voltage spike that will eat unprotected switches. Most relay modules already include a flyback diode across the coil — confirm on the datasheet, and add one externally across the solenoid leads if not.
- **MCP3008 → Pi (SPI).** VDD and VREF to 3.3 V, AGND/DGND to ground, CLK → SCLK (BCM 11), DOUT → MISO (BCM 9), DIN → MOSI (BCM 10), CS → CE0 (BCM 8). Sensor analog outputs go to CH0…CH7.

## Calibration

Capacitive sensors don't ship with a meaningful calibration. For each sensor:

1. Hold it in dry air. Run `auto-garden read --simulate=false` and record the raw value as `dry_value`.
2. Submerge the probe (NOT the electronics) in water. Record the raw value as `wet_value`.
3. Put both numbers in `config/config.yaml` under that sensor's entry.

These values drift over time and from sensor to sensor — recalibrate every season.
