# chipflow.platform

Platform definitions for ChipFlow.

This module provides platform implementations for silicon, simulation,
and software targets, along with their associated build steps.

## Submodules

* [chipflow.platform.base](base/index.md)
* [chipflow.platform.io](io/index.md)

## Classes

| [`SiliconPlatformPort`](#chipflow.platform.SiliconPlatformPort)         | Represents an abstract library I/O port that can be passed to a buffer.                                                                                                                                                                                                                   |
|-------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [`SiliconStep`](#chipflow.platform.SiliconStep)                         | Step to Prepare and submit the design for an ASIC.                                                                                                                                                                                                                                        |
| [`SimStep`](#chipflow.platform.SimStep)                                 | Base class for ChipFlow build steps.                                                                                                                                                                                                                                                      |
| [`SoftwareStep`](#chipflow.platform.SoftwareStep)                       | Base step to build the software.                                                                                                                                                                                                                                                          |
| [`BoardStep`](#chipflow.platform.BoardStep)                             | Build the design for a board.                                                                                                                                                                                                                                                             |
| [`IOSignature`](#chipflow.platform.IOSignature)                         | An [`Amaranth Signature`](../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature) used to decorate wires that would usually be brought out onto a port on the package.                                                                                                       |
| [`IOModel`](#chipflow.platform.IOModel)                                 | Setting for IO Ports (see also base class [`IOModelOptions`](#chipflow.platform.IOModelOptions)).                                                                                                                                                                                         |
| [`IOTripPoint`](#chipflow.platform.IOTripPoint)                         | Models various options for trip points for inputs.                                                                                                                                                                                                                                        |
| [`IOModelOptions`](#chipflow.platform.IOModelOptions)                   | Options for an IO pad/pin.                                                                                                                                                                                                                                                                |
| [`JTAGSignature`](#chipflow.platform.JTAGSignature)                     | Description of an interface object.                                                                                                                                                                                                                                                       |
| [`SPISignature`](#chipflow.platform.SPISignature)                       | Description of an interface object.                                                                                                                                                                                                                                                       |
| [`I2CSignature`](#chipflow.platform.I2CSignature)                       | Description of an interface object.                                                                                                                                                                                                                                                       |
| [`UARTSignature`](#chipflow.platform.UARTSignature)                     | Description of an interface object.                                                                                                                                                                                                                                                       |
| [`GPIOSignature`](#chipflow.platform.GPIOSignature)                     | Description of an interface object.                                                                                                                                                                                                                                                       |
| [`QSPIFlashSignature`](#chipflow.platform.QSPIFlashSignature)           | Description of an interface object.                                                                                                                                                                                                                                                       |
| [`SoftwareDriverSignature`](#chipflow.platform.SoftwareDriverSignature) | Description of an interface object.                                                                                                                                                                                                                                                       |
| [`SoftwareBuild`](#chipflow.platform.SoftwareBuild)                     | This holds the information needed for building software and providing the built outcome                                                                                                                                                                                                   |
| [`Sky130DriveMode`](#chipflow.platform.Sky130DriveMode)                 | Models the potential drive modes of an SkyWater 130 IO cell [sky130_fd_io_\_gpiov2]([https://skywater-pdk.readthedocs.io/en/main/contents/libraries/sky130_fd_io/docs/user_guide.html](https://skywater-pdk.readthedocs.io/en/main/contents/libraries/sky130_fd_io/docs/user_guide.html)) |
| [`StepBase`](#chipflow.platform.StepBase)                               | Base class for ChipFlow build steps.                                                                                                                                                                                                                                                      |

## Functions

| [`OutputIOSignature`](#chipflow.platform.OutputIOSignature)(width, \*\*kwargs)   | This creates an [`Amaranth Signature`](../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature) which is then used to decorate package output signals         |
|----------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [`InputIOSignature`](#chipflow.platform.InputIOSignature)(width, \*\*kwargs)     | This creates an [`Amaranth Signature`](../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature) which is then used to decorate package input signals          |
| [`BidirIOSignature`](#chipflow.platform.BidirIOSignature)(width, \*\*kwargs)     | This creates an [`Amaranth Signature`](../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature) which is then used to decorate package bi-directional signals |
| [`setup_amaranth_tools`](#chipflow.platform.setup_amaranth_tools)()              | Configure environment for Amaranth/WASM tools.                                                                                                                            |
| [`top_components`](#chipflow.platform.top_components)(config)                    | Return the top level components for the design, as configured in `chipflow.toml`.                                                                                         |
| [`get_software_builds`](#chipflow.platform.get_software_builds)(m, component)    | Extract software build information from a component's interfaces.                                                                                                         |

## Package Contents

### *class* chipflow.platform.SiliconPlatformPort(name, port_desc)

Bases: [`amaranth.lib.io.PortLike`](../../../../amaranth/stdlib/io.md#amaranth.lib.io.PortLike), `Generic`[`Pin`]

Represents an abstract library I/O port that can be passed to a buffer.

The port types supported by most platforms are `SingleEndedPort` and
`DifferentialPort`. Platforms may define additional port types where appropriate.

#### NOTE
`amaranth.hdl.IOPort` is not an instance of [`amaranth.lib.io.PortLike`](../../../../amaranth/stdlib/io.md#amaranth.lib.io.PortLike).

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str))
  * **port_desc** ([*chipflow.packaging.PortDesc*](../packaging/index.md#chipflow.packaging.PortDesc))

#### *property* direction

Direction of the port.

* **Return type:**
  `Direction`

### *class* chipflow.platform.SiliconStep(config)

Step to Prepare and submit the design for an ASIC.

#### prepare()

Elaborate the design and convert it to RTLIL.

Returns the path to the RTLIL file.

#### submit(rtlil_path, args)

Submit the design to the ChipFlow cloud builder.

Options:
: –dry-run: Don’t actually submit
  –wait: Wait until build has completed. Use ‘-v’ to increase level of verbosity
  –log-file <file>: Log full debug output to file

### *class* chipflow.platform.SimStep(config)

Bases: [`chipflow.platform.base.StepBase`](base/index.md#chipflow.platform.base.StepBase)

Base class for ChipFlow build steps.

#### build_cli_parser(parser)

Build the cli parser for this step

#### run_cli(args)

Called when this step’s is used from chipflow command

#### build(\*args)

Builds the simulation model for the design

#### run(\*args)

Run the simulation. Will ensure that the simulation and the software are both built.

#### check(\*args)

Run the simulation and check events against reference (tests/events_reference.json). Will ensure that the simulation and the software are both built.

### *class* chipflow.platform.SoftwareStep(config)

Bases: [`chipflow.platform.base.StepBase`](base/index.md#chipflow.platform.base.StepBase)

Base step to build the software.

#### build_cli_parser(parser)

Build the cli parser for this step

#### run_cli(args)

Called when this step’s is used from chipflow command

#### build(\*args)

Build the software for your design

### *class* chipflow.platform.BoardStep(config, platform)

Bases: [`chipflow.platform.base.StepBase`](base/index.md#chipflow.platform.base.StepBase)

Build the design for a board.

#### build_cli_parser(parser)

Build the cli parser for this step

#### run_cli(args)

Called when this step’s is used from chipflow command

#### build(\*args)

Build for the given platform

### *class* chipflow.platform.IOSignature(\*\*kwargs)

Bases: [`amaranth.lib.wiring.Signature`](../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature)

An [`Amaranth Signature`](../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature) used to decorate wires that would usually be brought out onto a port on the package.
This class is generally not directly used.  Instead, you would typically utilize the more specific
[`InputIOSignature`](#chipflow.platform.InputIOSignature), [`OutputIOSignature`](#chipflow.platform.OutputIOSignature), or [`BidirIOSignature`](#chipflow.platform.BidirIOSignature) for defining pin interfaces.

* **Parameters:**
  **kwargs** (*typing_extensions.Unpack* *[*[*IOModel*](#chipflow.platform.IOModel) *]*)

#### *property* direction *: [amaranth.lib.io.Direction](../../../../amaranth/stdlib/io.md#amaranth.lib.io.Direction)*

The direction of the IO port

* **Return type:**
  [amaranth.lib.io.Direction](../../../../amaranth/stdlib/io.md#amaranth.lib.io.Direction)

#### *property* width *: [int](https://docs.python.org/3/library/functions.html#int)*

The width of the IO port, in wires

* **Return type:**
  [int](https://docs.python.org/3/library/functions.html#int)

#### *property* invert *: [collections.abc.Iterable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[bool](https://docs.python.org/3/library/functions.html#bool)]*

A tuple as wide as the IO port, with a bool for the polarity inversion for each wire

* **Return type:**
  [collections.abc.Iterable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[bool](https://docs.python.org/3/library/functions.html#bool)]

#### *property* options *: [IOModelOptions](#chipflow.platform.IOModelOptions)*

Options set on the io port at construction

* **Return type:**
  [IOModelOptions](#chipflow.platform.IOModelOptions)

### *class* chipflow.platform.IOModel

Bases: [`IOModelOptions`](#chipflow.platform.IOModelOptions)

Setting for IO Ports (see also base class [`IOModelOptions`](#chipflow.platform.IOModelOptions)).

Attributes:
: direction: `io.Direction.Input`, `io.Direction.Output` or `io.Direction.Bidir`.
  width: Width of port, default is 1.

### *class* chipflow.platform.IOTripPoint

Bases: [`enum.StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)

Models various options for trip points for inputs.
Depending on process and cell library, these may be statically or dynamically configurable.

You will get an error if the option is not available with the chosen process and cell library

### *class* chipflow.platform.IOModelOptions

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

### chipflow.platform.OutputIOSignature(width, \*\*kwargs)

This creates an [`Amaranth Signature`](../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature) which is then used to decorate package output signals
intended for connection to the physical pads of the integrated circuit package.

* **Parameters:**
  * **width** ([*int*](https://docs.python.org/3/library/functions.html#int)) – specifies the number of individual output wires within this port, each of which will correspond to a separate physical pad on the integrated circuit package.
  * **kwargs** (*typing_extensions.Unpack* *[*[*IOModelOptions*](#chipflow.platform.IOModelOptions) *]*)

### chipflow.platform.InputIOSignature(width, \*\*kwargs)

This creates an [`Amaranth Signature`](../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature) which is then used to decorate package input signals
intended for connection to the physical pads of the integrated circuit package.

* **Parameters:**
  * **width** ([*int*](https://docs.python.org/3/library/functions.html#int)) – specifies the number of individual input wires within this port, each of which will correspond to a separate physical pad on the integrated circuit package.
  * **kwargs** (*typing_extensions.Unpack* *[*[*IOModelOptions*](#chipflow.platform.IOModelOptions) *]*)

### chipflow.platform.BidirIOSignature(width, \*\*kwargs)

This creates an [`Amaranth Signature`](../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature) which is then used to decorate package bi-directional signals
intended for connection to the physical pads of the integrated circuit package.

* **Parameters:**
  * **width** ([*int*](https://docs.python.org/3/library/functions.html#int)) – specifies the number of individual input/output wires within this port. Each pair of input/output wires will correspond to a separate physical pad on the integrated circuit package.
  * **kwargs** (*typing_extensions.Unpack* *[*[*IOModelOptions*](#chipflow.platform.IOModelOptions) *]*)

### *class* chipflow.platform.JTAGSignature(\*\*kwargs)

Bases: [`amaranth.lib.wiring.Signature`](../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature)

Description of an interface object.

An interface object is a Python object that has a `signature` attribute containing
a `Signature` object, as well as an attribute for every member of its signature.
Signatures and interface objects are tightly linked: an interface object can be created out
of a signature, and the signature is used when `connect()`ing two interface objects
together. See the [introduction to interfaces](../../../../amaranth/stdlib/wiring.md#wiring-intro1) for a more detailed
explanation of why this is useful.

`Signature` can be used as a base class to define [customized](../../../../amaranth/stdlib/wiring.md#wiring-customizing)
signatures and interface objects.

#### WARNING
`Signature` objects are immutable. Classes inheriting from `Signature` must
ensure this remains the case when additional functionality is added.

* **Parameters:**
  **kwargs** (*typing_extensions.Unpack* *[*[*chipflow.platform.io.iosignature.IOModelOptions*](io/iosignature/index.md#chipflow.platform.io.iosignature.IOModelOptions) *]*)

### *class* chipflow.platform.SPISignature(\*\*kwargs)

Bases: [`amaranth.lib.wiring.Signature`](../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature)

Description of an interface object.

An interface object is a Python object that has a `signature` attribute containing
a `Signature` object, as well as an attribute for every member of its signature.
Signatures and interface objects are tightly linked: an interface object can be created out
of a signature, and the signature is used when `connect()`ing two interface objects
together. See the [introduction to interfaces](../../../../amaranth/stdlib/wiring.md#wiring-intro1) for a more detailed
explanation of why this is useful.

`Signature` can be used as a base class to define [customized](../../../../amaranth/stdlib/wiring.md#wiring-customizing)
signatures and interface objects.

#### WARNING
`Signature` objects are immutable. Classes inheriting from `Signature` must
ensure this remains the case when additional functionality is added.

* **Parameters:**
  **kwargs** (*typing_extensions.Unpack* *[*[*chipflow.platform.io.iosignature.IOModelOptions*](io/iosignature/index.md#chipflow.platform.io.iosignature.IOModelOptions) *]*)

### *class* chipflow.platform.I2CSignature(\*\*kwargs)

Bases: [`amaranth.lib.wiring.Signature`](../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature)

Description of an interface object.

An interface object is a Python object that has a `signature` attribute containing
a `Signature` object, as well as an attribute for every member of its signature.
Signatures and interface objects are tightly linked: an interface object can be created out
of a signature, and the signature is used when `connect()`ing two interface objects
together. See the [introduction to interfaces](../../../../amaranth/stdlib/wiring.md#wiring-intro1) for a more detailed
explanation of why this is useful.

`Signature` can be used as a base class to define [customized](../../../../amaranth/stdlib/wiring.md#wiring-customizing)
signatures and interface objects.

#### WARNING
`Signature` objects are immutable. Classes inheriting from `Signature` must
ensure this remains the case when additional functionality is added.

* **Parameters:**
  **kwargs** (*typing_extensions.Unpack* *[*[*chipflow.platform.io.iosignature.IOModelOptions*](io/iosignature/index.md#chipflow.platform.io.iosignature.IOModelOptions) *]*)

### *class* chipflow.platform.UARTSignature(\*\*kwargs)

Bases: [`amaranth.lib.wiring.Signature`](../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature)

Description of an interface object.

An interface object is a Python object that has a `signature` attribute containing
a `Signature` object, as well as an attribute for every member of its signature.
Signatures and interface objects are tightly linked: an interface object can be created out
of a signature, and the signature is used when `connect()`ing two interface objects
together. See the [introduction to interfaces](../../../../amaranth/stdlib/wiring.md#wiring-intro1) for a more detailed
explanation of why this is useful.

`Signature` can be used as a base class to define [customized](../../../../amaranth/stdlib/wiring.md#wiring-customizing)
signatures and interface objects.

#### WARNING
`Signature` objects are immutable. Classes inheriting from `Signature` must
ensure this remains the case when additional functionality is added.

* **Parameters:**
  **kwargs** (*typing_extensions.Unpack* *[*[*chipflow.platform.io.iosignature.IOModelOptions*](io/iosignature/index.md#chipflow.platform.io.iosignature.IOModelOptions) *]*)

### *class* chipflow.platform.GPIOSignature(pin_count=1, \*\*kwargs)

Bases: [`amaranth.lib.wiring.Signature`](../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature)

Description of an interface object.

An interface object is a Python object that has a `signature` attribute containing
a `Signature` object, as well as an attribute for every member of its signature.
Signatures and interface objects are tightly linked: an interface object can be created out
of a signature, and the signature is used when `connect()`ing two interface objects
together. See the [introduction to interfaces](../../../../amaranth/stdlib/wiring.md#wiring-intro1) for a more detailed
explanation of why this is useful.

`Signature` can be used as a base class to define [customized](../../../../amaranth/stdlib/wiring.md#wiring-customizing)
signatures and interface objects.

#### WARNING
`Signature` objects are immutable. Classes inheriting from `Signature` must
ensure this remains the case when additional functionality is added.

* **Parameters:**
  **kwargs** (*typing_extensions.Unpack* *[*[*chipflow.platform.io.iosignature.IOModelOptions*](io/iosignature/index.md#chipflow.platform.io.iosignature.IOModelOptions) *]*)

### *class* chipflow.platform.QSPIFlashSignature(\*\*kwargs)

Bases: [`amaranth.lib.wiring.Signature`](../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature)

Description of an interface object.

An interface object is a Python object that has a `signature` attribute containing
a `Signature` object, as well as an attribute for every member of its signature.
Signatures and interface objects are tightly linked: an interface object can be created out
of a signature, and the signature is used when `connect()`ing two interface objects
together. See the [introduction to interfaces](../../../../amaranth/stdlib/wiring.md#wiring-intro1) for a more detailed
explanation of why this is useful.

`Signature` can be used as a base class to define [customized](../../../../amaranth/stdlib/wiring.md#wiring-customizing)
signatures and interface objects.

#### WARNING
`Signature` objects are immutable. Classes inheriting from `Signature` must
ensure this remains the case when additional functionality is added.

* **Parameters:**
  **kwargs** (*typing_extensions.Unpack* *[*[*chipflow.platform.io.iosignature.IOModelOptions*](io/iosignature/index.md#chipflow.platform.io.iosignature.IOModelOptions) *]*)

### *class* chipflow.platform.SoftwareDriverSignature(members, \*\*kwargs)

Bases: [`amaranth.lib.wiring.Signature`](../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature)

Description of an interface object.

An interface object is a Python object that has a `signature` attribute containing
a `Signature` object, as well as an attribute for every member of its signature.
Signatures and interface objects are tightly linked: an interface object can be created out
of a signature, and the signature is used when `connect()`ing two interface objects
together. See the [introduction to interfaces](../../../../amaranth/stdlib/wiring.md#wiring-intro1) for a more detailed
explanation of why this is useful.

`Signature` can be used as a base class to define [customized](../../../../amaranth/stdlib/wiring.md#wiring-customizing)
signatures and interface objects.

#### WARNING
`Signature` objects are immutable. Classes inheriting from `Signature` must
ensure this remains the case when additional functionality is added.

* **Parameters:**
  **kwargs** (*typing_extensions.Unpack* *[*[*DriverModel*](io/signatures/index.md#chipflow.platform.io.signatures.DriverModel) *]*)

### *class* chipflow.platform.SoftwareBuild(\*, sources, includes=[], include_dirs=[], offset=0)

This holds the information needed for building software and providing the built outcome

* **Parameters:**
  * **sources** ([*list*](https://docs.python.org/3/library/stdtypes.html#list) *[*[*pathlib.Path*](https://docs.python.org/3/library/pathlib.html#pathlib.Path) *]*)
  * **includes** ([*list*](https://docs.python.org/3/library/stdtypes.html#list) *[*[*pathlib.Path*](https://docs.python.org/3/library/pathlib.html#pathlib.Path) *]*)

### *class* chipflow.platform.Sky130DriveMode

Bases: [`enum.StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)

Models the potential drive modes of an SkyWater 130 IO cell [sky130_fd_io_\_gpiov2]([https://skywater-pdk.readthedocs.io/en/main/contents/libraries/sky130_fd_io/docs/user_guide.html](https://skywater-pdk.readthedocs.io/en/main/contents/libraries/sky130_fd_io/docs/user_guide.html))
These are both statically configurable and can be set at runtime on the :py:mod:drive_mode.Sky130Port lines on the port.

### *class* chipflow.platform.StepBase(config={})

Bases: [`abc.ABC`](https://docs.python.org/3/library/abc.html#abc.ABC)

Base class for ChipFlow build steps.

#### build_cli_parser(parser)

Build the cli parser for this step

#### run_cli(args)

Called when this step’s is used from chipflow command

#### build(\*args)

builds the design

### chipflow.platform.setup_amaranth_tools()

Configure environment for Amaranth/WASM tools.

### chipflow.platform.top_components(config)

Return the top level components for the design, as configured in `chipflow.toml`.

Args:
: config: The parsed chipflow configuration

Returns:
: Dictionary mapping component names to instantiated Component objects

Raises:
: ChipFlowError: If component references are invalid or instantiation fails

* **Parameters:**
  **config** (*chipflow.config.models.Config*)
* **Return type:**
  Dict[[str](https://docs.python.org/3/library/stdtypes.html#str), [amaranth.lib.wiring.Component](../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Component)]

### chipflow.platform.get_software_builds(m, component)

Extract software build information from a component’s interfaces.

Args:
: m: Module containing the component
  component: Name of the component

Returns:
: Dictionary of interface names to SoftwareBuild objects

* **Parameters:**
  **component** ([*str*](https://docs.python.org/3/library/stdtypes.html#str))
