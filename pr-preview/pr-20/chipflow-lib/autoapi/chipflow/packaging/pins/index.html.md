# chipflow.packaging.pins

Pin dataclasses and types for package definitions.

This module contains the fundamental building blocks for defining
physical pin assignments and power/signal groupings in IC packages.

## Classes

| [`PowerType`](#chipflow.packaging.pins.PowerType)     | Type of power pin (power or ground)                                        |
|-------------------------------------------------------|----------------------------------------------------------------------------|
| [`JTAGWire`](#chipflow.packaging.pins.JTAGWire)       | Wire names in a JTAG interface                                             |
| [`PortType`](#chipflow.packaging.pins.PortType)       | Type of port                                                               |
| [`PowerPins`](#chipflow.packaging.pins.PowerPins)     | A matched pair of power pins, with optional notation of the voltage range. |
| [`JTAGPins`](#chipflow.packaging.pins.JTAGPins)       | Pins for a JTAG interface.                                                 |
| [`BringupPins`](#chipflow.packaging.pins.BringupPins) | Essential pins for bringing up an IC, always in fixed locations.           |

## Module Contents

### *class* chipflow.packaging.pins.PowerType

Bases: [`enum.StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)

Type of power pin (power or ground)

### *class* chipflow.packaging.pins.JTAGWire

Bases: [`enum.StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)

Wire names in a JTAG interface

### *class* chipflow.packaging.pins.PortType

Bases: [`enum.StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)

Type of port

### *class* chipflow.packaging.pins.PowerPins

Bases: `Generic`[`Pin`]

A matched pair of power pins, with optional notation of the voltage range.

Attributes:
: power: The power (VDD) pin
  ground: The ground (VSS) pin
  voltage: Optional voltage range or specific voltage
  name: Optional name for this power domain

#### to_set()

Convert power pins to a set

* **Return type:**
  Set[Pin]

### *class* chipflow.packaging.pins.JTAGPins

Bases: `Generic`[`Pin`]

Pins for a JTAG interface.

Attributes:
: trst: Test Reset pin
  tck: Test Clock pin
  tms: Test Mode Select pin
  tdi: Test Data In pin
  tdo: Test Data Out pin

#### to_set()

Convert JTAG pins to a set

* **Return type:**
  Set[Pin]

### *class* chipflow.packaging.pins.BringupPins

Bases: `Generic`[`Pin`]

Essential pins for bringing up an IC, always in fixed locations.

These pins are used for initial testing and debug of the IC.

Attributes:
: core_power: List of core power pin pairs
  core_clock: Core clock input pin
  core_reset: Core reset input pin
  core_heartbeat: Heartbeat output pin (for liveness testing)
  core_jtag: Optional JTAG interface pins

#### to_set()

Convert all bringup pins to a set

* **Return type:**
  Set[Pin]
