# chipflow.packaging.base

Base classes for package definitions.

This module provides the abstract base classes that all package
definitions inherit from, defining the common interface for
pin allocation and package description.

## Classes

| [`BasePackageDef`](#chipflow.packaging.base.BasePackageDef)               | Abstract base class for the definition of a package.         |
|---------------------------------------------------------------------------|--------------------------------------------------------------|
| [`LinearAllocPackageDef`](#chipflow.packaging.base.LinearAllocPackageDef) | Base class for package types with linear pin/pad allocation. |

## Module Contents

### *class* chipflow.packaging.base.BasePackageDef

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
  * **component** ([*amaranth.lib.wiring.Component*](../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Component))
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
  * **config** ([*chipflow.config.Config*](../../config/index.md#chipflow.config.Config))
  * **process** ([*chipflow.config.Process*](../../config/index.md#chipflow.config.Process))
  * **lockfile** ([*chipflow.packaging.lockfile.LockFile*](../lockfile/index.md#chipflow.packaging.lockfile.LockFile) *|* *None*)
* **Return type:**
  [chipflow.packaging.lockfile.LockFile](../lockfile/index.md#chipflow.packaging.lockfile.LockFile)

#### *property* bringup_pins *: [chipflow.packaging.pins.BringupPins](../pins/index.md#chipflow.packaging.pins.BringupPins)*

* **Abstractmethod:**
* **Return type:**
  [chipflow.packaging.pins.BringupPins](../pins/index.md#chipflow.packaging.pins.BringupPins)

Get the bringup pins for this package.

To aid bringup, these are always in the same place for each
package type. Should include core power, clock and reset.

Power, clocks and resets needed for non-core are allocated
with the port.

Returns:
: BringupPins configuration

### *class* chipflow.packaging.base.LinearAllocPackageDef

Bases: [`BasePackageDef`](#chipflow.packaging.base.BasePackageDef)[[`int`](https://docs.python.org/3/library/functions.html#int)]

Base class for package types with linear pin/pad allocation.

This is used for packages where pins are allocated from a
simple linear ordering (e.g., numbered pins around a perimeter).

Subclasses should populate self._ordered_pins in model_post_init
before calling super().model_post_init(_\_context).

Not directly serializable - use concrete subclasses.
