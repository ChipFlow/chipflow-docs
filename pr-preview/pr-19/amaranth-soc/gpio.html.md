# GPIO

The [`amaranth_soc.gpio`](#module-amaranth_soc.gpio) module provides a basic GPIO peripheral.

<!-- from amaranth import *
from amaranth.lib import io, wiring
from amaranth.lib.wiring import In, Out, flipped, connect

from amaranth_soc import csr, gpio -->

## Introduction

[GPIO](https://en.wikipedia.org/wiki/General-purpose_input/output) peripherals are commonly used
to interface a SoC (usually a microcontroller) with a variety of external circuitry. This module contains a GPIO peripheral which can be connected to a [CSR bus](csr/bus.md#csr-bus-introduction).

### Example

This example shows a GPIO peripheral being used to drive four LEDs:

```python
class MySoC(wiring.Component):
    def elaborate(self, platform):
        m = Module()

        m.submodules.led_gpio = led_gpio = gpio.Peripheral(pin_count=4, addr_width=8,
                                                           data_width=8)

        for n in range(4):
            led = io.Buffer("o", platform.request("led", n, dir="-"))
            connect(m, led_gpio.pins[n], led)

        m.submodules.csr_decoder = csr_decoder = csr.Decoder(addr_width=31, data_width=8)
        csr_decoder.add(led_gpio.bus, addr=0x1000, name="led_gpio")

        # ...

        return m
```

## Pin modes

### *class* amaranth_soc.gpio.PinMode

GPIO pin mode.

The 2-bit values of this enumeration can be written to a [`Peripheral.Mode`](#amaranth_soc.gpio.Peripheral.Mode) field to
configure the pins of a [`Peripheral`](#amaranth_soc.gpio.Peripheral).

#### INPUT_ONLY *= 0*

Input-only mode.

The pin output is disabled but remains connected to its [`Peripheral.Output`](#amaranth_soc.gpio.Peripheral.Output) field.
Its `alt_mode` bit is wired to 0.

#### PUSH_PULL *= 1*

Push-pull mode.

The pin output is enabled and connected to its [`Peripheral.Output`](#amaranth_soc.gpio.Peripheral.Output) field. Its
`alt_mode` bit is wired to 0.

#### OPEN_DRAIN *= 2*

Open-drain mode.

The pin output is enabled when the value of its [`Peripheral.Output`](#amaranth_soc.gpio.Peripheral.Output) field is 0, and
is itself wired to 0. Its `alt_mode` bit is wired to 0.

#### ALTERNATE *= 3*

Alternate mode.

The pin output is disabled but remains connected to its [`Peripheral.Output`](#amaranth_soc.gpio.Peripheral.Output) field.
Its `alt_mode` bit is wired to 1.

## Pin interface

### *class* amaranth_soc.gpio.PinSignature

GPIO pin signature.

* **Members:**
  * **i** (`In(1)`) – Input.
  * **o** (`Out(1)`) – Output.
  * **oe** (`Out(1)`) – Output enable.

## Peripheral

#### *class* Peripheral.Mode

Mode register.

This [`Register`](csr/reg.md#amaranth_soc.csr.reg.Register) contains an array of `pin_count` read/write fields.
Each field is 2-bit wide and its possible values are defined by the [`PinMode`](#amaranth_soc.gpio.PinMode)
enumeration.

---

If `pin_count` is 8, then the [`Register`](csr/reg.md#amaranth_soc.csr.reg.Register) has the following fields:

---
* **Parameters:**
  **pin_count** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Number of GPIO pins.

#### *class* Peripheral.Input

Input register.

This [`Register`](csr/reg.md#amaranth_soc.csr.reg.Register) contains an array of `pin_count` read-only fields. Each
field is 1-bit wide and is driven by the input of its associated pin in the `pins` array
of the peripheral.

Values sampled from pin inputs go through `Peripheral.input_stages` synchronization
stages (on a rising edge of `ClockSignal("sync")`) before reaching the register.

---

If `pin_count` is 8, then the [`Register`](csr/reg.md#amaranth_soc.csr.reg.Register) has the following fields:

---
* **Parameters:**
  **pin_count** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Number of GPIO pins.

#### *class* Peripheral.Output

Output register.

This [`Register`](csr/reg.md#amaranth_soc.csr.reg.Register) contains an array of `pin_count` read/write fields. Each
field is 1-bit wide and drives the output of its associated pin in the `pins` array of the
peripheral, depending on its associated [`Mode`](#amaranth_soc.gpio.Peripheral.Mode) field.

---

If `pin_count` is 8, then the [`Register`](csr/reg.md#amaranth_soc.csr.reg.Register) has the following fields:

---
* **Parameters:**
  **pin_count** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Number of GPIO pins.

#### *class* Peripheral.SetClr

Output set/clear register.

This [`Register`](csr/reg.md#amaranth_soc.csr.reg.Register) contains an array of `pin_count` write-only fields. Each
field is 2-bit wide; writing it can modify its associated [`Output`](#amaranth_soc.gpio.Peripheral.Output) field
as a side-effect.

---

If `pin_count` is 8, then the [`Register`](csr/reg.md#amaranth_soc.csr.reg.Register) has the following fields:

- Writing 0b01 to a field sets its associated [`Output`](#amaranth_soc.gpio.Peripheral.Output) field.
- Writing 0b10 to a field clears its associated [`Output`](#amaranth_soc.gpio.Peripheral.Output) field.
- Writing 0b00 or 0b11 to a field has no side-effect.

---
* **Parameters:**
  **pin_count** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Number of GPIO pins.

### *class* amaranth_soc.gpio.Peripheral

GPIO peripheral.

* **Parameters:**
  * **pin_count** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Number of GPIO pins.
  * **addr_width** ([`int`](https://docs.python.org/3/library/functions.html#int)) – CSR bus address width.
  * **data_width** ([`int`](https://docs.python.org/3/library/functions.html#int)) – CSR bus data width.
  * **input_stages** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Number of synchronization stages between pin inputs and the [`Input`](#amaranth_soc.gpio.Peripheral.Input)
    register. Optional. Defaults to `2`.
* **Members:**
  * **bus** (`In(csr.Signature(addr_width, data_width))`) – CSR bus interface providing access to registers.
  * **pins** (`Out(PinSignature()).array(pin_count)`) – GPIO pin interfaces.
  * **alt_mode** (`Out(pin_count)`) – Indicates which members of the `pins` array are in alternate mode.
