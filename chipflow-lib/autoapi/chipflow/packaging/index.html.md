# chipflow.packaging

Package definitions and pin allocation.

This module provides everything needed to define IC packages and
allocate pins to component interfaces, including:

- Pin dataclasses (PowerPins, JTAGPins, BringupPins)
- Port description models (PortDesc, PortMap)
- Lock file models (LockFile, Package)
- Base classes (BasePackageDef, LinearAllocPackageDef)
- Concrete package types (QuadPackageDef, BareDiePackageDef, GAPackageDef, OpenframePackageDef)
- Pin allocation algorithms

## Submodules

* [chipflow.packaging.allocation](allocation/index.md)
* [chipflow.packaging.base](base/index.md)
* [chipflow.packaging.commands](commands/index.md)
* [chipflow.packaging.grid_array](grid_array/index.md)
* [chipflow.packaging.lockfile](lockfile/index.md)
* [chipflow.packaging.openframe](openframe/index.md)
* [chipflow.packaging.pins](pins/index.md)
* [chipflow.packaging.port_desc](port_desc/index.md)
* [chipflow.packaging.standard](standard/index.md)
* [chipflow.packaging.utils](utils/index.md)

## Exceptions

| [`UnableToAllocate`](#chipflow.packaging.UnableToAllocate)   | Raised when pin allocation fails   |
|--------------------------------------------------------------|------------------------------------|

## Classes

| [`PowerType`](#chipflow.packaging.PowerType)                         | Type of power pin (power or ground)                                        |
|----------------------------------------------------------------------|----------------------------------------------------------------------------|
| [`JTAGWire`](#chipflow.packaging.JTAGWire)                           | Wire names in a JTAG interface                                             |
| [`PortType`](#chipflow.packaging.PortType)                           | Type of port                                                               |
| [`PowerPins`](#chipflow.packaging.PowerPins)                         | A matched pair of power pins, with optional notation of the voltage range. |
| [`JTAGPins`](#chipflow.packaging.JTAGPins)                           | Pins for a JTAG interface.                                                 |
| [`BringupPins`](#chipflow.packaging.BringupPins)                     | Essential pins for bringing up an IC, always in fixed locations.           |
| [`PortDesc`](#chipflow.packaging.PortDesc)                           | Description of a port and its pin assignment.                              |
| [`PortMap`](#chipflow.packaging.PortMap)                             | Mapping of components to interfaces to ports.                              |
| [`Package`](#chipflow.packaging.Package)                             | Serializable identifier for a defined packaging option.                    |
| [`LockFile`](#chipflow.packaging.LockFile)                           | Representation of a pin lock file.                                         |
| [`BasePackageDef`](#chipflow.packaging.BasePackageDef)               | Abstract base class for the definition of a package.                       |
| [`LinearAllocPackageDef`](#chipflow.packaging.LinearAllocPackageDef) | Base class for package types with linear pin/pad allocation.               |
| [`BareDiePackageDef`](#chipflow.packaging.BareDiePackageDef)         | Definition of a package with pins on four sides.                           |
| [`QuadPackageDef`](#chipflow.packaging.QuadPackageDef)               | Definition of a quad flat package.                                         |
| [`GAPin`](#chipflow.packaging.GAPin)                                 | Pin identifier for grid array packages (row letter, column number)         |
| [`GALayout`](#chipflow.packaging.GALayout)                           | Layout type for grid array packages                                        |
| [`GAPackageDef`](#chipflow.packaging.GAPackageDef)                   | Definition of a grid array package.                                        |
| [`OFPin`](#chipflow.packaging.OFPin)                                 | Pin identifier for Openframe package                                       |
| [`OpenframePackageDef`](#chipflow.packaging.OpenframePackageDef)     | Definition of the ChipFoundry Openframe harness package.                   |
| [`PinCommand`](#chipflow.packaging.PinCommand)                       | CLI command handler for pin-related operations.                            |

## Functions

| [`load_pinlock`](#chipflow.packaging.load_pinlock)()   | Load the pin lock file from the chipflow root.     |
|--------------------------------------------------------|----------------------------------------------------|
| [`lock_pins`](#chipflow.packaging.lock_pins)([config]) | Create or update the pin lock file for the design. |

## Package Contents

### *class* chipflow.packaging.PowerType

Bases: [`enum.StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)

Type of power pin (power or ground)

### *class* chipflow.packaging.JTAGWire

Bases: [`enum.StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)

Wire names in a JTAG interface

### *class* chipflow.packaging.PortType

Bases: [`enum.StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)

Type of port

### *class* chipflow.packaging.PowerPins

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

### *class* chipflow.packaging.JTAGPins

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

### *class* chipflow.packaging.BringupPins

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

### *class* chipflow.packaging.PortDesc

Bases: `pydantic.BaseModel`, `Generic`[`chipflow.packaging.pins.Pin`]

Description of a port and its pin assignment.

Attributes:
: type: Type of port (e.g., ‘io’, ‘clock’, ‘reset’, ‘power’, ‘heartbeat’)
  pins: List of pins assigned to this port, or None if not yet allocated
  port_name: Name of the port
  iomodel: IO model configuration for this port

#### *property* width

Width of the port (number of pins)

#### *property* direction

Direction of the port

#### *property* invert *: [collections.abc.Iterable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[bool](https://docs.python.org/3/library/functions.html#bool)] | [None](https://docs.python.org/3/library/constants.html#None)*

Inversion settings for port wires

* **Return type:**
  [collections.abc.Iterable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[bool](https://docs.python.org/3/library/functions.html#bool)] | None

### *class* chipflow.packaging.PortMap

Bases: `pydantic.BaseModel`

Mapping of components to interfaces to ports.

This represents the complete pin allocation for an IC package,
organized hierarchically by component and interface.

#### get_ports(component, interface)

Get ports for a specific component and interface.

Args:
: component: Component name
  interface: Interface name

Returns:
: Dictionary of port names to PortDesc, or None if not found

* **Parameters:**
  * **component** ([*str*](https://docs.python.org/3/library/stdtypes.html#str))
  * **interface** ([*str*](https://docs.python.org/3/library/stdtypes.html#str))
* **Return type:**
  [Interface](../../../../amaranth-soc/csr/bus.md#amaranth_soc.csr.bus.Interface) | None

#### get_clocks()

Get all clock ports in the port map

* **Return type:**
  List[[PortDesc](#chipflow.packaging.PortDesc)]

#### get_resets()

Get all reset ports in the port map

* **Return type:**
  List[[PortDesc](#chipflow.packaging.PortDesc)]

### *class* chipflow.packaging.Package

Bases: `pydantic.BaseModel`

Serializable identifier for a defined packaging option.

Attributes:
: package_type: Package type (discriminated union of all PackageDef types)

### *class* chipflow.packaging.LockFile

Bases: `pydantic.BaseModel`

Representation of a pin lock file.

The lock file stores the complete pin allocation for a design,
allowing pins to remain consistent across design iterations.

Attributes:
: process: Semiconductor process being used
  package: Information about the physical package
  port_map: Mapping of components to interfaces to ports
  metadata: Amaranth metadata, for reference

### *class* chipflow.packaging.BasePackageDef

Bases: `pydantic.BaseModel`, `Generic`[`PinType`], [`abc.ABC`](https://docs.python.org/3/library/abc.html#abc.ABC)

Abstract base class for the definition of a package.

Serializing this or any derived classes results in the
description of the package (not serializable directly).

All package definitions must inherit from this class and
implement the required abstract methods.

Attributes:
: name: The name of the package

#### model_post_init(\_\_context)

Initialize internal tracking structures

#### register_component(name, component)

Register a component to be allocated to the pad ring and pins.

Args:
: name: Component name
  component: Amaranth wiring.Component to allocate

* **Parameters:**
  * **name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str))
  * **component** ([*amaranth.lib.wiring.Component*](../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Component))
* **Return type:**
  None

#### allocate_pins(config, process, lockfile)

Allocate package pins to the registered components.

Pins should be allocated in the most usable way for users
of the packaged IC.

This default implementation uses \_linear_allocate_components with
self._allocate for the allocation strategy. Subclasses can override
if they need completely different allocation logic.

Args:
: config: ChipFlow configuration
  process: Semiconductor process
  lockfile: Optional existing lockfile to preserve allocations

Returns:
: LockFile representing the pin allocation

Raises:
: UnableToAllocate: If the ports cannot be allocated

* **Parameters:**
  * **config** ([*chipflow.config.Config*](../config/index.md#chipflow.config.Config))
  * **process** ([*chipflow.config.Process*](../config/index.md#chipflow.config.Process))
  * **lockfile** ([*chipflow.packaging.lockfile.LockFile*](lockfile/index.md#chipflow.packaging.lockfile.LockFile) *|* *None*)
* **Return type:**
  [chipflow.packaging.lockfile.LockFile](lockfile/index.md#chipflow.packaging.lockfile.LockFile)

#### *property* bringup_pins *: [chipflow.packaging.pins.BringupPins](pins/index.md#chipflow.packaging.pins.BringupPins)*

* **Abstractmethod:**
* **Return type:**
  [chipflow.packaging.pins.BringupPins](pins/index.md#chipflow.packaging.pins.BringupPins)

Get the bringup pins for this package.

To aid bringup, these are always in the same place for each
package type. Should include core power, clock and reset.

Power, clocks and resets needed for non-core are allocated
with the port.

Returns:
: BringupPins configuration

### *class* chipflow.packaging.LinearAllocPackageDef

Bases: [`BasePackageDef`](#chipflow.packaging.BasePackageDef)[[`int`](https://docs.python.org/3/library/functions.html#int)]

Base class for package types with linear pin/pad allocation.

This is used for packages where pins are allocated from a
simple linear ordering (e.g., numbered pins around a perimeter).

Subclasses should populate self._ordered_pins in model_post_init
before calling super().model_post_init(_\_context).

Not directly serializable - use concrete subclasses.

### *class* chipflow.packaging.BareDiePackageDef

Bases: [`chipflow.packaging.base.LinearAllocPackageDef`](base/index.md#chipflow.packaging.base.LinearAllocPackageDef)

Definition of a package with pins on four sides.

Sides are labeled north, south, east, west with an integer
identifier within each side, indicating pads across or down
from top-left corner.

This is typically used for direct die attach without traditional
packaging.

Attributes:
: width: Number of die pads on top and bottom sides
  height: Number of die pads on left and right sides

#### model_post_init(\_\_context)

Initialize pin ordering

#### *property* bringup_pins *: [chipflow.packaging.pins.BringupPins](pins/index.md#chipflow.packaging.pins.BringupPins)*

Bringup pins for bare die package

* **Return type:**
  [chipflow.packaging.pins.BringupPins](pins/index.md#chipflow.packaging.pins.BringupPins)

### *class* chipflow.packaging.QuadPackageDef

Bases: [`chipflow.packaging.base.LinearAllocPackageDef`](base/index.md#chipflow.packaging.base.LinearAllocPackageDef)

Definition of a quad flat package.

A package with ‘width’ pins on the top and bottom and ‘height’
pins on the left and right. Pins are numbered anti-clockwise
from the top left pin.

This includes many common package types:

- QFN: quad flat no-leads (bottom pad = substrate)
- BQFP: bumpered quad flat package
- BQFPH: bumpered quad flat package with heat spreader
- CQFP: ceramic quad flat package
- EQFP: plastic enhanced quad flat package
- FQFP: fine pitch quad flat package
- LQFP: low profile quad flat package
- MQFP: metric quad flat package
- NQFP: near chip-scale quad flat package
- SQFP: small quad flat package
- TQFP: thin quad flat package
- VQFP: very small quad flat package
- VTQFP: very thin quad flat package
- TDFN: thin dual flat no-lead package
- CERQUAD: low-cost CQFP

Attributes:
: width: The number of pins across on the top and bottom edges
  height: The number of pins high on the left and right edges

#### model_post_init(\_\_context)

Initialize pin ordering

#### *property* bringup_pins *: [chipflow.packaging.pins.BringupPins](pins/index.md#chipflow.packaging.pins.BringupPins)*

Bringup pins for quad package

* **Return type:**
  [chipflow.packaging.pins.BringupPins](pins/index.md#chipflow.packaging.pins.BringupPins)

### *class* chipflow.packaging.GAPin

Bases: `NamedTuple`

Pin identifier for grid array packages (row letter, column number)

### *class* chipflow.packaging.GALayout

Bases: [`enum.StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)

Layout type for grid array packages

### *class* chipflow.packaging.GAPackageDef

Bases: [`chipflow.packaging.base.BasePackageDef`](base/index.md#chipflow.packaging.base.BasePackageDef)[[`GAPin`](#chipflow.packaging.GAPin)]

Definition of a grid array package.

Pins or pads are arranged in a regular array of ‘width’ by ‘height’.
Pins are identified by a 2-tuple of (row, column), counting from
the bottom left when looking at the underside of the package.
Rows are identified by letter (A-Z), columns by number.

The grid may be complete or have missing pins (e.g., center cutout).

This includes many package types:

- CPGA: Ceramic Pin Grid Array
- OPGA: Organic Pin Grid Array
- SPGA: Staggered Pin Grid Array
- CABGA: Chip Array Ball Grid Array
- CBGA/PBGA: Ceramic/Plastic Ball Grid Array
- CTBGA: Thin Chip Array Ball Grid Array
- CVBGA: Very Thin Chip Array Ball Grid Array
- DSBGA: Die-Size Ball Grid Array
- FBGA: Fine Ball Grid Array / Fine Pitch Ball Grid Array
- FCmBGA: Flip Chip Molded Ball Grid Array
- LBGA: Low-Profile Ball Grid Array
- LFBGA: Low-Profile Fine-Pitch Ball Grid Array
- MBGA: Micro Ball Grid Array
- MCM-PBGA: Multi-Chip Module Plastic Ball Grid Array
- nFBGA: New Fine Ball Grid Array
- SuperBGA (SBGA): Super Ball Grid Array
- TABGA: Tape Array BGA
- TBGA: Thin BGA
- TEPBGA: Thermally Enhanced Plastic Ball Grid Array
- TFBGA: Thin and Fine Ball Grid Array
- UFBGA/UBGA: Ultra Fine Ball Grid Array
- VFBGA: Very Fine Pitch Ball Grid Array
- WFBGA: Very Very Thin Profile Fine Pitch Ball Grid Array
- wWLB: Embedded Wafer Level Ball Grid Array

Attributes:
: width: Number of columns
  height: Number of rows
  layout_type: Pin layout configuration
  channel_width: For PERIMETER/CHANNEL/ISLAND layouts
  island_width: For ISLAND layout, size of center island
  missing_pins: Specific pins to exclude (overrides layout)
  additional_pins: Specific pins to add (overrides layout)

#### model_post_init(\_\_context)

Initialize pin ordering

#### *property* bringup_pins *: [chipflow.packaging.pins.BringupPins](pins/index.md#chipflow.packaging.pins.BringupPins)*

Bringup pins for grid array package

* **Return type:**
  [chipflow.packaging.pins.BringupPins](pins/index.md#chipflow.packaging.pins.BringupPins)

#### *property* heartbeat *: Dict[[int](https://docs.python.org/3/library/functions.html#int), [GAPin](#chipflow.packaging.GAPin)]*

Numbered set of heartbeat pins for the package

* **Return type:**
  Dict[[int](https://docs.python.org/3/library/functions.html#int), [GAPin](#chipflow.packaging.GAPin)]

### *class* chipflow.packaging.OFPin

Bases: `NamedTuple`

Pin identifier for Openframe package

### *class* chipflow.packaging.OpenframePackageDef

Bases: [`chipflow.packaging.base.LinearAllocPackageDef`](base/index.md#chipflow.packaging.base.LinearAllocPackageDef)

Definition of the ChipFoundry Openframe harness package.

This is a standardized package/carrier used for open-source
silicon projects, particularly with the ChipFoundry chipIgnite
and OpenMPW programs.

Attributes:
: name: Package name (default “openframe”)

#### model_post_init(\_\_context)

Initialize pin ordering from GPIO list

#### *property* bringup_pins *: [chipflow.packaging.pins.BringupPins](pins/index.md#chipflow.packaging.pins.BringupPins)*

Bringup pins for Openframe package

* **Return type:**
  [chipflow.packaging.pins.BringupPins](pins/index.md#chipflow.packaging.pins.BringupPins)

### *exception* chipflow.packaging.UnableToAllocate

Bases: [`chipflow.ChipFlowError`](../index.md#chipflow.ChipFlowError)

Raised when pin allocation fails

### chipflow.packaging.load_pinlock()

Load the pin lock file from the chipflow root.

Returns:
: LockFile model

Raises:
: ChipFlowError: If lockfile not found or malformed

* **Return type:**
  [chipflow.packaging.lockfile.LockFile](lockfile/index.md#chipflow.packaging.lockfile.LockFile)

### chipflow.packaging.lock_pins(config=None)

Create or update the pin lock file for the design.

This allocates package pins to component interfaces and writes
the allocation to pins.lock. Will attempt to reuse previous
pin positions if pins.lock already exists.

Args:
: config: Optional Config object. If not provided, will be parsed from chipflow.toml

Raises:
: ChipFlowError: If configuration is invalid or pin allocation fails

* **Parameters:**
  **config** (*Optional* *[*[*chipflow.config.Config*](../config/index.md#chipflow.config.Config) *]*)
* **Return type:**
  None

### *class* chipflow.packaging.PinCommand(config)

CLI command handler for pin-related operations.

This class provides the command-line interface for managing
pin allocations and lock files.

#### build_cli_parser(parser)

Build the CLI parser for pin commands.

Args:
: parser: argparse parser to add subcommands to

#### run_cli(args)

Execute the CLI command.

Args:
: args: Parsed command-line arguments

#### lock()

Lock the pin map for the design.

Will attempt to reuse previous pin positions.
