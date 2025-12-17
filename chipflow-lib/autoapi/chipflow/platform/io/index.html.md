# chipflow.platform.io

IO signatures and utilities for ChipFlow platforms.

This module provides IO signature definitions, annotations, and
platform-specific IO utilities.

## Submodules

* [chipflow.platform.io.annotate](annotate/index.md)
* [chipflow.platform.io.iosignature](iosignature/index.md)
* [chipflow.platform.io.signatures](signatures/index.md)
* [chipflow.platform.io.sky130](sky130/index.md)

## Classes

| [`IOTripPoint`](#chipflow.platform.io.IOTripPoint)                         | Models various options for trip points for inputs.                                                                                                                                                                                                                                        |
|----------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [`IOModelOptions`](#chipflow.platform.io.IOModelOptions)                   | Options for an IO pad/pin.                                                                                                                                                                                                                                                                |
| [`IOModel`](#chipflow.platform.io.IOModel)                                 | Setting for IO Ports (see also base class [`IOModelOptions`](#chipflow.platform.io.IOModelOptions)).                                                                                                                                                                                      |
| [`IOSignature`](#chipflow.platform.io.IOSignature)                         | An [`Amaranth Signature`](../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature) used to decorate wires that would usually be brought out onto a port on the package.                                                                                                    |
| [`JTAGSignature`](#chipflow.platform.io.JTAGSignature)                     | Description of an interface object.                                                                                                                                                                                                                                                       |
| [`SPISignature`](#chipflow.platform.io.SPISignature)                       | Description of an interface object.                                                                                                                                                                                                                                                       |
| [`I2CSignature`](#chipflow.platform.io.I2CSignature)                       | Description of an interface object.                                                                                                                                                                                                                                                       |
| [`UARTSignature`](#chipflow.platform.io.UARTSignature)                     | Description of an interface object.                                                                                                                                                                                                                                                       |
| [`GPIOSignature`](#chipflow.platform.io.GPIOSignature)                     | Description of an interface object.                                                                                                                                                                                                                                                       |
| [`QSPIFlashSignature`](#chipflow.platform.io.QSPIFlashSignature)           | Description of an interface object.                                                                                                                                                                                                                                                       |
| [`SoftwareDriverSignature`](#chipflow.platform.io.SoftwareDriverSignature) | Description of an interface object.                                                                                                                                                                                                                                                       |
| [`SoftwareBuild`](#chipflow.platform.io.SoftwareBuild)                     | This holds the information needed for building software and providing the built outcome                                                                                                                                                                                                   |
| [`Sky130DriveMode`](#chipflow.platform.io.Sky130DriveMode)                 | Models the potential drive modes of an SkyWater 130 IO cell [sky130_fd_io_\_gpiov2]([https://skywater-pdk.readthedocs.io/en/main/contents/libraries/sky130_fd_io/docs/user_guide.html](https://skywater-pdk.readthedocs.io/en/main/contents/libraries/sky130_fd_io/docs/user_guide.html)) |

## Functions

| [`InputIOSignature`](#chipflow.platform.io.InputIOSignature)(width, \*\*kwargs)                         | This creates an [`Amaranth Signature`](../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature) which is then used to decorate package input signals          |
|---------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [`OutputIOSignature`](#chipflow.platform.io.OutputIOSignature)(width, \*\*kwargs)                       | This creates an [`Amaranth Signature`](../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature) which is then used to decorate package output signals         |
| [`BidirIOSignature`](#chipflow.platform.io.BidirIOSignature)(width, \*\*kwargs)                         | This creates an [`Amaranth Signature`](../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature) which is then used to decorate package bi-directional signals |
| [`submodule_metadata`](#chipflow.platform.io.submodule_metadata)(fragment, component_name[, recursive]) | Generator that finds `component_name` in `fragment` and yields metadata.                                                                                                     |

## Package Contents

### *class* chipflow.platform.io.IOTripPoint

Bases: [`enum.StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)

Models various options for trip points for inputs.
Depending on process and cell library, these may be statically or dynamically configurable.

You will get an error if the option is not available with the chosen process and cell library

### *class* chipflow.platform.io.IOModelOptions

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
  buffer_in: Should the IO pad have an input buffer? Defaults to True for
  : ports with input direction.
  <br/>
  buffer_out: Should the IO pad have an output buffer? Defaults to True for
  : ports with output direction.
  <br/>
  sky130_drive_mode: Drive mode for output buffer on sky130. See
  : [`Sky130DriveMode`](#chipflow.platform.io.Sky130DriveMode) for available options.
  <br/>
  trip_point: Trip Point configuration for input buffer. See
  : [`IOTripPoint`](#chipflow.platform.io.IOTripPoint) for available options.
  <br/>
  init: The value for the initial values of the port. Can be an integer or
  : boolean.
  <br/>
  init_oe: The value for the initial values of the output enable(s) of the
  : port. Can be an integer or boolean.

### *class* chipflow.platform.io.IOModel

Bases: [`IOModelOptions`](#chipflow.platform.io.IOModelOptions)

Setting for IO Ports (see also base class [`IOModelOptions`](#chipflow.platform.io.IOModelOptions)).

Attributes:
: direction: `io.Direction.Input`, `io.Direction.Output` or `io.Direction.Bidir`.
  width: Width of port, default is 1.

### *class* chipflow.platform.io.IOSignature(\*\*kwargs)

Bases: [`amaranth.lib.wiring.Signature`](../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature)

An [`Amaranth Signature`](../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature) used to decorate wires that would usually be brought out onto a port on the package.
This class is generally not directly used.  Instead, you would typically utilize the more specific
[`InputIOSignature`](#chipflow.platform.io.InputIOSignature), [`OutputIOSignature`](#chipflow.platform.io.OutputIOSignature), or [`BidirIOSignature`](#chipflow.platform.io.BidirIOSignature) for defining pin interfaces.

* **Parameters:**
  **kwargs** (*typing_extensions.Unpack* *[*[*IOModel*](#chipflow.platform.io.IOModel) *]*)

#### *property* direction *: [amaranth.lib.io.Direction](../../../../../amaranth/stdlib/io.md#amaranth.lib.io.Direction)*

The direction of the IO port

* **Return type:**
  [amaranth.lib.io.Direction](../../../../../amaranth/stdlib/io.md#amaranth.lib.io.Direction)

#### *property* width *: [int](https://docs.python.org/3/library/functions.html#int)*

The width of the IO port, in wires

* **Return type:**
  [int](https://docs.python.org/3/library/functions.html#int)

#### *property* invert *: [collections.abc.Iterable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[bool](https://docs.python.org/3/library/functions.html#bool)]*

A tuple as wide as the IO port, with a bool for the polarity inversion for each wire

* **Return type:**
  [collections.abc.Iterable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[bool](https://docs.python.org/3/library/functions.html#bool)]

#### *property* options *: [IOModelOptions](#chipflow.platform.io.IOModelOptions)*

Options set on the io port at construction

* **Return type:**
  [IOModelOptions](#chipflow.platform.io.IOModelOptions)

### chipflow.platform.io.InputIOSignature(width, \*\*kwargs)

This creates an [`Amaranth Signature`](../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature) which is then used to decorate package input signals
intended for connection to the physical pads of the integrated circuit package.

* **Parameters:**
  * **width** ([*int*](https://docs.python.org/3/library/functions.html#int)) – specifies the number of individual input wires within this port, each of which will correspond to a separate physical pad on the integrated circuit package.
  * **kwargs** (*typing_extensions.Unpack* *[*[*IOModelOptions*](#chipflow.platform.io.IOModelOptions) *]*)

### chipflow.platform.io.OutputIOSignature(width, \*\*kwargs)

This creates an [`Amaranth Signature`](../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature) which is then used to decorate package output signals
intended for connection to the physical pads of the integrated circuit package.

* **Parameters:**
  * **width** ([*int*](https://docs.python.org/3/library/functions.html#int)) – specifies the number of individual output wires within this port, each of which will correspond to a separate physical pad on the integrated circuit package.
  * **kwargs** (*typing_extensions.Unpack* *[*[*IOModelOptions*](#chipflow.platform.io.IOModelOptions) *]*)

### chipflow.platform.io.BidirIOSignature(width, \*\*kwargs)

This creates an [`Amaranth Signature`](../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature) which is then used to decorate package bi-directional signals
intended for connection to the physical pads of the integrated circuit package.

* **Parameters:**
  * **width** ([*int*](https://docs.python.org/3/library/functions.html#int)) – specifies the number of individual input/output wires within this port. Each pair of input/output wires will correspond to a separate physical pad on the integrated circuit package.
  * **kwargs** (*typing_extensions.Unpack* *[*[*IOModelOptions*](#chipflow.platform.io.IOModelOptions) *]*)

### *class* chipflow.platform.io.JTAGSignature(\*\*kwargs)

Bases: [`amaranth.lib.wiring.Signature`](../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature)

Description of an interface object.

An interface object is a Python object that has a `signature` attribute containing
a `Signature` object, as well as an attribute for every member of its signature.
Signatures and interface objects are tightly linked: an interface object can be created out
of a signature, and the signature is used when `connect()`ing two interface objects
together. See the [introduction to interfaces](../../../../../amaranth/stdlib/wiring.md#wiring-intro1) for a more detailed
explanation of why this is useful.

`Signature` can be used as a base class to define [customized](../../../../../amaranth/stdlib/wiring.md#wiring-customizing)
signatures and interface objects.

#### WARNING
`Signature` objects are immutable. Classes inheriting from `Signature` must
ensure this remains the case when additional functionality is added.

* **Parameters:**
  **kwargs** (*typing_extensions.Unpack* *[*[*chipflow.platform.io.iosignature.IOModelOptions*](iosignature/index.md#chipflow.platform.io.iosignature.IOModelOptions) *]*)

### *class* chipflow.platform.io.SPISignature(\*\*kwargs)

Bases: [`amaranth.lib.wiring.Signature`](../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature)

Description of an interface object.

An interface object is a Python object that has a `signature` attribute containing
a `Signature` object, as well as an attribute for every member of its signature.
Signatures and interface objects are tightly linked: an interface object can be created out
of a signature, and the signature is used when `connect()`ing two interface objects
together. See the [introduction to interfaces](../../../../../amaranth/stdlib/wiring.md#wiring-intro1) for a more detailed
explanation of why this is useful.

`Signature` can be used as a base class to define [customized](../../../../../amaranth/stdlib/wiring.md#wiring-customizing)
signatures and interface objects.

#### WARNING
`Signature` objects are immutable. Classes inheriting from `Signature` must
ensure this remains the case when additional functionality is added.

* **Parameters:**
  **kwargs** (*typing_extensions.Unpack* *[*[*chipflow.platform.io.iosignature.IOModelOptions*](iosignature/index.md#chipflow.platform.io.iosignature.IOModelOptions) *]*)

### *class* chipflow.platform.io.I2CSignature(\*\*kwargs)

Bases: [`amaranth.lib.wiring.Signature`](../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature)

Description of an interface object.

An interface object is a Python object that has a `signature` attribute containing
a `Signature` object, as well as an attribute for every member of its signature.
Signatures and interface objects are tightly linked: an interface object can be created out
of a signature, and the signature is used when `connect()`ing two interface objects
together. See the [introduction to interfaces](../../../../../amaranth/stdlib/wiring.md#wiring-intro1) for a more detailed
explanation of why this is useful.

`Signature` can be used as a base class to define [customized](../../../../../amaranth/stdlib/wiring.md#wiring-customizing)
signatures and interface objects.

#### WARNING
`Signature` objects are immutable. Classes inheriting from `Signature` must
ensure this remains the case when additional functionality is added.

* **Parameters:**
  **kwargs** (*typing_extensions.Unpack* *[*[*chipflow.platform.io.iosignature.IOModelOptions*](iosignature/index.md#chipflow.platform.io.iosignature.IOModelOptions) *]*)

### *class* chipflow.platform.io.UARTSignature(\*\*kwargs)

Bases: [`amaranth.lib.wiring.Signature`](../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature)

Description of an interface object.

An interface object is a Python object that has a `signature` attribute containing
a `Signature` object, as well as an attribute for every member of its signature.
Signatures and interface objects are tightly linked: an interface object can be created out
of a signature, and the signature is used when `connect()`ing two interface objects
together. See the [introduction to interfaces](../../../../../amaranth/stdlib/wiring.md#wiring-intro1) for a more detailed
explanation of why this is useful.

`Signature` can be used as a base class to define [customized](../../../../../amaranth/stdlib/wiring.md#wiring-customizing)
signatures and interface objects.

#### WARNING
`Signature` objects are immutable. Classes inheriting from `Signature` must
ensure this remains the case when additional functionality is added.

* **Parameters:**
  **kwargs** (*typing_extensions.Unpack* *[*[*chipflow.platform.io.iosignature.IOModelOptions*](iosignature/index.md#chipflow.platform.io.iosignature.IOModelOptions) *]*)

### *class* chipflow.platform.io.GPIOSignature(pin_count=1, \*\*kwargs)

Bases: [`amaranth.lib.wiring.Signature`](../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature)

Description of an interface object.

An interface object is a Python object that has a `signature` attribute containing
a `Signature` object, as well as an attribute for every member of its signature.
Signatures and interface objects are tightly linked: an interface object can be created out
of a signature, and the signature is used when `connect()`ing two interface objects
together. See the [introduction to interfaces](../../../../../amaranth/stdlib/wiring.md#wiring-intro1) for a more detailed
explanation of why this is useful.

`Signature` can be used as a base class to define [customized](../../../../../amaranth/stdlib/wiring.md#wiring-customizing)
signatures and interface objects.

#### WARNING
`Signature` objects are immutable. Classes inheriting from `Signature` must
ensure this remains the case when additional functionality is added.

* **Parameters:**
  **kwargs** (*typing_extensions.Unpack* *[*[*chipflow.platform.io.iosignature.IOModelOptions*](iosignature/index.md#chipflow.platform.io.iosignature.IOModelOptions) *]*)

### *class* chipflow.platform.io.QSPIFlashSignature(\*\*kwargs)

Bases: [`amaranth.lib.wiring.Signature`](../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature)

Description of an interface object.

An interface object is a Python object that has a `signature` attribute containing
a `Signature` object, as well as an attribute for every member of its signature.
Signatures and interface objects are tightly linked: an interface object can be created out
of a signature, and the signature is used when `connect()`ing two interface objects
together. See the [introduction to interfaces](../../../../../amaranth/stdlib/wiring.md#wiring-intro1) for a more detailed
explanation of why this is useful.

`Signature` can be used as a base class to define [customized](../../../../../amaranth/stdlib/wiring.md#wiring-customizing)
signatures and interface objects.

#### WARNING
`Signature` objects are immutable. Classes inheriting from `Signature` must
ensure this remains the case when additional functionality is added.

* **Parameters:**
  **kwargs** (*typing_extensions.Unpack* *[*[*chipflow.platform.io.iosignature.IOModelOptions*](iosignature/index.md#chipflow.platform.io.iosignature.IOModelOptions) *]*)

### *class* chipflow.platform.io.SoftwareDriverSignature(members, \*\*kwargs)

Bases: [`amaranth.lib.wiring.Signature`](../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature)

Description of an interface object.

An interface object is a Python object that has a `signature` attribute containing
a `Signature` object, as well as an attribute for every member of its signature.
Signatures and interface objects are tightly linked: an interface object can be created out
of a signature, and the signature is used when `connect()`ing two interface objects
together. See the [introduction to interfaces](../../../../../amaranth/stdlib/wiring.md#wiring-intro1) for a more detailed
explanation of why this is useful.

`Signature` can be used as a base class to define [customized](../../../../../amaranth/stdlib/wiring.md#wiring-customizing)
signatures and interface objects.

#### WARNING
`Signature` objects are immutable. Classes inheriting from `Signature` must
ensure this remains the case when additional functionality is added.

* **Parameters:**
  **kwargs** (*typing_extensions.Unpack* *[*[*DriverModel*](signatures/index.md#chipflow.platform.io.signatures.DriverModel) *]*)

### *class* chipflow.platform.io.SoftwareBuild(\*, sources, includes=[], include_dirs=[], offset=0)

This holds the information needed for building software and providing the built outcome

* **Parameters:**
  * **sources** ([*list*](https://docs.python.org/3/library/stdtypes.html#list) *[*[*pathlib.Path*](https://docs.python.org/3/library/pathlib.html#pathlib.Path) *]*)
  * **includes** ([*list*](https://docs.python.org/3/library/stdtypes.html#list) *[*[*pathlib.Path*](https://docs.python.org/3/library/pathlib.html#pathlib.Path) *]*)

### *class* chipflow.platform.io.Sky130DriveMode

Bases: [`enum.StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)

Models the potential drive modes of an SkyWater 130 IO cell [sky130_fd_io_\_gpiov2]([https://skywater-pdk.readthedocs.io/en/main/contents/libraries/sky130_fd_io/docs/user_guide.html](https://skywater-pdk.readthedocs.io/en/main/contents/libraries/sky130_fd_io/docs/user_guide.html))
These are both statically configurable and can be set at runtime on the :py:mod:drive_mode.Sky130Port lines on the port.

### chipflow.platform.io.submodule_metadata(fragment, component_name, recursive=False)

Generator that finds `component_name` in `fragment` and yields metadata.

Yields the `wiring.Component` instances of that component’s submodule, along
with their names and metadata.

Can only be run once for a given component (or its children).

Args:
: fragment: The fragment to search in.
  component_name: The name of the component to find.
  recursive: If True, name is a tuple of the hierarchy of names. Otherwise,
  <br/>
  > name is the string name of the first level component.

Yields:
: Tuple of (component, name, metadata) for each submodule.

* **Parameters:**
  * **fragment** (*amaranth.Fragment*)
  * **component_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str))
* **Return type:**
  [collections.abc.Generator](https://docs.python.org/3/library/collections.abc.html#collections.abc.Generator)[Tuple[[amaranth.lib.wiring.Component](../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Component), [str](https://docs.python.org/3/library/stdtypes.html#str) | [tuple](https://docs.python.org/3/library/stdtypes.html#tuple), [dict](https://docs.python.org/3/library/stdtypes.html#dict)]]
