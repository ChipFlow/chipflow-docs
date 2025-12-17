# chipflow.platform.io.iosignature

IO signature definitions for ChipFlow platforms.

## Classes

| [`IOTripPoint`](#chipflow.platform.io.iosignature.IOTripPoint)       | Models various options for trip points for inputs.                                                                                                                                        |
|----------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [`IOModelOptions`](#chipflow.platform.io.iosignature.IOModelOptions) | Options for an IO pad/pin.                                                                                                                                                                |
| [`IOModel`](#chipflow.platform.io.iosignature.IOModel)               | Setting for IO Ports (see also base class [`IOModelOptions`](#chipflow.platform.io.iosignature.IOModelOptions)).                                                                          |
| [`IOSignature`](#chipflow.platform.io.iosignature.IOSignature)       | An [`Amaranth Signature`](../../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature) used to decorate wires that would usually be brought out onto a port on the package. |

## Functions

| [`OutputIOSignature`](#chipflow.platform.io.iosignature.OutputIOSignature)(width, \*\*kwargs)   | This creates an [`Amaranth Signature`](../../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature) which is then used to decorate package output signals         |
|-------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [`InputIOSignature`](#chipflow.platform.io.iosignature.InputIOSignature)(width, \*\*kwargs)     | This creates an [`Amaranth Signature`](../../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature) which is then used to decorate package input signals          |
| [`BidirIOSignature`](#chipflow.platform.io.iosignature.BidirIOSignature)(width, \*\*kwargs)     | This creates an [`Amaranth Signature`](../../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature) which is then used to decorate package bi-directional signals |

## Module Contents

### *class* chipflow.platform.io.iosignature.IOTripPoint

Bases: [`enum.StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)

Models various options for trip points for inputs.
Depending on process and cell library, these may be statically or dynamically configurable.

You will get an error if the option is not available with the chosen process and cell library

### *class* chipflow.platform.io.iosignature.IOModelOptions

Bases: `typing_extensions.TypedDict`

Options for an IO pad/pin.

Attributes:
: invert: Polarity inversion. If the value is a simple `bool`, it specifies
  : inversion for the entire port. If the value is an iterable of `bool`,
    the iterable must have the same length as the width of `io`, and the
    inversion is specified for individual wires.
  <br/>
  individual_oe: Controls whether each output wire is associated with an
  : individual Output Enable bit or if a single OE bit will be used for
    entire port. The default value is False (indicating that a single OE
    bit controls the entire port).
  <br/>
  power_domain: The name of the I/O power domain. NB there is only one of
  : these, so IO with multiple power domains must be split up.
  <br/>
  clock_domain: The name of the I/O’s clock domain (see
  : `amaranth.hdl.ClockDomain`). NB there is only one of these, so IO
    with multiple clocks must be split up.
  <br/>
  buffer_in: Should the IO pad have an input buffer?
  buffer_out: Should the IO pad have an output buffer?
  sky130_drive_mode: Drive mode for output buffer on sky130.
  trip_point: Trip Point configuration for input buffer.
  init: The value for the initial values of the port.
  init_oe: The value for the initial values of the output enable(s) of the port.

### *class* chipflow.platform.io.iosignature.IOModel

Bases: [`IOModelOptions`](#chipflow.platform.io.iosignature.IOModelOptions)

Setting for IO Ports (see also base class [`IOModelOptions`](#chipflow.platform.io.iosignature.IOModelOptions)).

Attributes:
: direction: `io.Direction.Input`, `io.Direction.Output` or `io.Direction.Bidir`.
  width: Width of port, default is 1.

### *class* chipflow.platform.io.iosignature.IOSignature(\*\*kwargs)

Bases: [`amaranth.lib.wiring.Signature`](../../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature)

An [`Amaranth Signature`](../../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature) used to decorate wires that would usually be brought out onto a port on the package.
This class is generally not directly used.  Instead, you would typically utilize the more specific
[`InputIOSignature`](#chipflow.platform.io.iosignature.InputIOSignature), [`OutputIOSignature`](#chipflow.platform.io.iosignature.OutputIOSignature), or [`BidirIOSignature`](#chipflow.platform.io.iosignature.BidirIOSignature) for defining pin interfaces.

* **Parameters:**
  **kwargs** (*typing_extensions.Unpack* *[*[*IOModel*](#chipflow.platform.io.iosignature.IOModel) *]*)

#### *property* direction *: [amaranth.lib.io.Direction](../../../../../../amaranth/stdlib/io.md#amaranth.lib.io.Direction)*

The direction of the IO port

* **Return type:**
  [amaranth.lib.io.Direction](../../../../../../amaranth/stdlib/io.md#amaranth.lib.io.Direction)

#### *property* width *: [int](https://docs.python.org/3/library/functions.html#int)*

The width of the IO port, in wires

* **Return type:**
  [int](https://docs.python.org/3/library/functions.html#int)

#### *property* invert *: [collections.abc.Iterable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[bool](https://docs.python.org/3/library/functions.html#bool)]*

A tuple as wide as the IO port, with a bool for the polarity inversion for each wire

* **Return type:**
  [collections.abc.Iterable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[bool](https://docs.python.org/3/library/functions.html#bool)]

#### *property* options *: [IOModelOptions](#chipflow.platform.io.iosignature.IOModelOptions)*

Options set on the io port at construction

* **Return type:**
  [IOModelOptions](#chipflow.platform.io.iosignature.IOModelOptions)

### chipflow.platform.io.iosignature.OutputIOSignature(width, \*\*kwargs)

This creates an [`Amaranth Signature`](../../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature) which is then used to decorate package output signals
intended for connection to the physical pads of the integrated circuit package.

* **Parameters:**
  * **width** ([*int*](https://docs.python.org/3/library/functions.html#int)) – specifies the number of individual output wires within this port, each of which will correspond to a separate physical pad on the integrated circuit package.
  * **kwargs** (*typing_extensions.Unpack* *[*[*IOModelOptions*](#chipflow.platform.io.iosignature.IOModelOptions) *]*)

### chipflow.platform.io.iosignature.InputIOSignature(width, \*\*kwargs)

This creates an [`Amaranth Signature`](../../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature) which is then used to decorate package input signals
intended for connection to the physical pads of the integrated circuit package.

* **Parameters:**
  * **width** ([*int*](https://docs.python.org/3/library/functions.html#int)) – specifies the number of individual input wires within this port, each of which will correspond to a separate physical pad on the integrated circuit package.
  * **kwargs** (*typing_extensions.Unpack* *[*[*IOModelOptions*](#chipflow.platform.io.iosignature.IOModelOptions) *]*)

### chipflow.platform.io.iosignature.BidirIOSignature(width, \*\*kwargs)

This creates an [`Amaranth Signature`](../../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature) which is then used to decorate package bi-directional signals
intended for connection to the physical pads of the integrated circuit package.

* **Parameters:**
  * **width** ([*int*](https://docs.python.org/3/library/functions.html#int)) – specifies the number of individual input/output wires within this port. Each pair of input/output wires will correspond to a separate physical pad on the integrated circuit package.
  * **kwargs** (*typing_extensions.Unpack* *[*[*IOModelOptions*](#chipflow.platform.io.iosignature.IOModelOptions) *]*)
