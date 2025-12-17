# chipflow.platform.io.signatures

Common interface signatures for ChipFlow platforms.

## Classes

| [`SimInterface`](#chipflow.platform.io.signatures.SimInterface)                       | Simulation interface metadata for ChipFlow components.                                             |
|---------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------|
| [`DataclassProtocol`](#chipflow.platform.io.signatures.DataclassProtocol)             | Base class for protocol classes.                                                                   |
| [`SoftwareBuild`](#chipflow.platform.io.signatures.SoftwareBuild)                     | This holds the information needed for building software and providing the built outcome            |
| [`BinaryData`](#chipflow.platform.io.signatures.BinaryData)                           | This holds the information needed for building software and providing the built outcome            |
| [`Data`](#chipflow.platform.io.signatures.Data)                                       | Container for data associated with a ChipFlow component.                                           |
| [`DriverModel`](#chipflow.platform.io.signatures.DriverModel)                         | Options for [`SoftwareDriverSignature`](#chipflow.platform.io.signatures.SoftwareDriverSignature). |
| [`JTAGSignature`](#chipflow.platform.io.signatures.JTAGSignature)                     | Description of an interface object.                                                                |
| [`SPISignature`](#chipflow.platform.io.signatures.SPISignature)                       | Description of an interface object.                                                                |
| [`QSPIFlashSignature`](#chipflow.platform.io.signatures.QSPIFlashSignature)           | Description of an interface object.                                                                |
| [`UARTSignature`](#chipflow.platform.io.signatures.UARTSignature)                     | Description of an interface object.                                                                |
| [`I2CSignature`](#chipflow.platform.io.signatures.I2CSignature)                       | Description of an interface object.                                                                |
| [`GPIOSignature`](#chipflow.platform.io.signatures.GPIOSignature)                     | Description of an interface object.                                                                |
| [`SoftwareDriverSignature`](#chipflow.platform.io.signatures.SoftwareDriverSignature) | Description of an interface object.                                                                |

## Functions

| [`simulatable_interface`](#chipflow.platform.io.signatures.simulatable_interface)([base])   | Decorator for creating simulatable interface signatures.   |
|---------------------------------------------------------------------------------------------|------------------------------------------------------------|

## Module Contents

### *class* chipflow.platform.io.signatures.SimInterface

Bases: `typing_extensions.TypedDict`

Simulation interface metadata for ChipFlow components.

Attributes:
: uid: Unique identifier for the interface.
  parameters: List of (name, value) tuples for interface parameters.

### *class* chipflow.platform.io.signatures.DataclassProtocol

Bases: `Protocol`

Base class for protocol classes.

Protocol classes are defined as:

```default
class Proto(Protocol):
    def meth(self) -> int:
        ...
```

Such classes are primarily used with static type checkers that recognize
structural subtyping (static duck-typing).

For example:

```default
class C:
    def meth(self) -> int:
        return 0

def func(x: Proto) -> int:
    return x.meth()

func(C())  # Passes static type check
```

See PEP 544 for details. Protocol classes decorated with
@typing.runtime_checkable act as simple-minded runtime protocols that check
only the presence of given attributes, ignoring their type signatures.
Protocol classes can be generic, they are defined as:

```default
class GenProto[T](Protocol):
    def meth(self) -> T:
        ...
```

### *class* chipflow.platform.io.signatures.SoftwareBuild(\*, sources, includes=[], include_dirs=[], offset=0)

This holds the information needed for building software and providing the built outcome

* **Parameters:**
  * **sources** ([*list*](https://docs.python.org/3/library/stdtypes.html#list) *[*[*pathlib.Path*](https://docs.python.org/3/library/pathlib.html#pathlib.Path) *]*)
  * **includes** ([*list*](https://docs.python.org/3/library/stdtypes.html#list) *[*[*pathlib.Path*](https://docs.python.org/3/library/pathlib.html#pathlib.Path) *]*)

### *class* chipflow.platform.io.signatures.BinaryData(\*, filename, offset=0)

This holds the information needed for building software and providing the built outcome

* **Parameters:**
  **filename** ([*pathlib.Path*](https://docs.python.org/3/library/pathlib.html#pathlib.Path))

### *class* chipflow.platform.io.signatures.Data

Bases: `typing_extensions.TypedDict`, `Generic`[`_T_DataClass`]

Container for data associated with a ChipFlow component.

Attributes:
: data: The dataclass instance containing component data.

### *class* chipflow.platform.io.signatures.DriverModel

Bases: `typing_extensions.TypedDict`

Options for [`SoftwareDriverSignature`](#chipflow.platform.io.signatures.SoftwareDriverSignature).

Attributes:
: component: The `wiring.Component` that this is the signature for.
  regs_struct: The name of the C struct that represents the registers of this component.
  h_files: Header files for the driver.
  c_files: C files for the driver.
  regs_bus: The bus of this `Component` which contains its control registers.
  include_dirs: Any extra include directories needed by the driver.

### chipflow.platform.io.signatures.simulatable_interface(base='com.chipflow.chipflow')

Decorator for creating simulatable interface signatures.

The decorated class will have a `__chipflow_parameters__` method that returns
a list of tuples (name, value). It is expected that a model that takes parameters
is implemented as a template, with the parameters in the order given.

Args:
: base: Base UID string for the interface (default: “com.chipflow.chipflow”).

Returns:
: A decorator function that adds chipflow annotation support to a class.

### *class* chipflow.platform.io.signatures.JTAGSignature(\*\*kwargs)

Bases: [`amaranth.lib.wiring.Signature`](../../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature)

Description of an interface object.

An interface object is a Python object that has a `signature` attribute containing
a `Signature` object, as well as an attribute for every member of its signature.
Signatures and interface objects are tightly linked: an interface object can be created out
of a signature, and the signature is used when `connect()`ing two interface objects
together. See the [introduction to interfaces](../../../../../../amaranth/stdlib/wiring.md#wiring-intro1) for a more detailed
explanation of why this is useful.

`Signature` can be used as a base class to define [customized](../../../../../../amaranth/stdlib/wiring.md#wiring-customizing)
signatures and interface objects.

#### WARNING
`Signature` objects are immutable. Classes inheriting from `Signature` must
ensure this remains the case when additional functionality is added.

* **Parameters:**
  **kwargs** (*typing_extensions.Unpack* *[*[*chipflow.platform.io.iosignature.IOModelOptions*](../iosignature/index.md#chipflow.platform.io.iosignature.IOModelOptions) *]*)

### *class* chipflow.platform.io.signatures.SPISignature(\*\*kwargs)

Bases: [`amaranth.lib.wiring.Signature`](../../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature)

Description of an interface object.

An interface object is a Python object that has a `signature` attribute containing
a `Signature` object, as well as an attribute for every member of its signature.
Signatures and interface objects are tightly linked: an interface object can be created out
of a signature, and the signature is used when `connect()`ing two interface objects
together. See the [introduction to interfaces](../../../../../../amaranth/stdlib/wiring.md#wiring-intro1) for a more detailed
explanation of why this is useful.

`Signature` can be used as a base class to define [customized](../../../../../../amaranth/stdlib/wiring.md#wiring-customizing)
signatures and interface objects.

#### WARNING
`Signature` objects are immutable. Classes inheriting from `Signature` must
ensure this remains the case when additional functionality is added.

* **Parameters:**
  **kwargs** (*typing_extensions.Unpack* *[*[*chipflow.platform.io.iosignature.IOModelOptions*](../iosignature/index.md#chipflow.platform.io.iosignature.IOModelOptions) *]*)

### *class* chipflow.platform.io.signatures.QSPIFlashSignature(\*\*kwargs)

Bases: [`amaranth.lib.wiring.Signature`](../../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature)

Description of an interface object.

An interface object is a Python object that has a `signature` attribute containing
a `Signature` object, as well as an attribute for every member of its signature.
Signatures and interface objects are tightly linked: an interface object can be created out
of a signature, and the signature is used when `connect()`ing two interface objects
together. See the [introduction to interfaces](../../../../../../amaranth/stdlib/wiring.md#wiring-intro1) for a more detailed
explanation of why this is useful.

`Signature` can be used as a base class to define [customized](../../../../../../amaranth/stdlib/wiring.md#wiring-customizing)
signatures and interface objects.

#### WARNING
`Signature` objects are immutable. Classes inheriting from `Signature` must
ensure this remains the case when additional functionality is added.

* **Parameters:**
  **kwargs** (*typing_extensions.Unpack* *[*[*chipflow.platform.io.iosignature.IOModelOptions*](../iosignature/index.md#chipflow.platform.io.iosignature.IOModelOptions) *]*)

### *class* chipflow.platform.io.signatures.UARTSignature(\*\*kwargs)

Bases: [`amaranth.lib.wiring.Signature`](../../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature)

Description of an interface object.

An interface object is a Python object that has a `signature` attribute containing
a `Signature` object, as well as an attribute for every member of its signature.
Signatures and interface objects are tightly linked: an interface object can be created out
of a signature, and the signature is used when `connect()`ing two interface objects
together. See the [introduction to interfaces](../../../../../../amaranth/stdlib/wiring.md#wiring-intro1) for a more detailed
explanation of why this is useful.

`Signature` can be used as a base class to define [customized](../../../../../../amaranth/stdlib/wiring.md#wiring-customizing)
signatures and interface objects.

#### WARNING
`Signature` objects are immutable. Classes inheriting from `Signature` must
ensure this remains the case when additional functionality is added.

* **Parameters:**
  **kwargs** (*typing_extensions.Unpack* *[*[*chipflow.platform.io.iosignature.IOModelOptions*](../iosignature/index.md#chipflow.platform.io.iosignature.IOModelOptions) *]*)

### *class* chipflow.platform.io.signatures.I2CSignature(\*\*kwargs)

Bases: [`amaranth.lib.wiring.Signature`](../../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature)

Description of an interface object.

An interface object is a Python object that has a `signature` attribute containing
a `Signature` object, as well as an attribute for every member of its signature.
Signatures and interface objects are tightly linked: an interface object can be created out
of a signature, and the signature is used when `connect()`ing two interface objects
together. See the [introduction to interfaces](../../../../../../amaranth/stdlib/wiring.md#wiring-intro1) for a more detailed
explanation of why this is useful.

`Signature` can be used as a base class to define [customized](../../../../../../amaranth/stdlib/wiring.md#wiring-customizing)
signatures and interface objects.

#### WARNING
`Signature` objects are immutable. Classes inheriting from `Signature` must
ensure this remains the case when additional functionality is added.

* **Parameters:**
  **kwargs** (*typing_extensions.Unpack* *[*[*chipflow.platform.io.iosignature.IOModelOptions*](../iosignature/index.md#chipflow.platform.io.iosignature.IOModelOptions) *]*)

### *class* chipflow.platform.io.signatures.GPIOSignature(pin_count=1, \*\*kwargs)

Bases: [`amaranth.lib.wiring.Signature`](../../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature)

Description of an interface object.

An interface object is a Python object that has a `signature` attribute containing
a `Signature` object, as well as an attribute for every member of its signature.
Signatures and interface objects are tightly linked: an interface object can be created out
of a signature, and the signature is used when `connect()`ing two interface objects
together. See the [introduction to interfaces](../../../../../../amaranth/stdlib/wiring.md#wiring-intro1) for a more detailed
explanation of why this is useful.

`Signature` can be used as a base class to define [customized](../../../../../../amaranth/stdlib/wiring.md#wiring-customizing)
signatures and interface objects.

#### WARNING
`Signature` objects are immutable. Classes inheriting from `Signature` must
ensure this remains the case when additional functionality is added.

* **Parameters:**
  **kwargs** (*typing_extensions.Unpack* *[*[*chipflow.platform.io.iosignature.IOModelOptions*](../iosignature/index.md#chipflow.platform.io.iosignature.IOModelOptions) *]*)

### *class* chipflow.platform.io.signatures.SoftwareDriverSignature(members, \*\*kwargs)

Bases: [`amaranth.lib.wiring.Signature`](../../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature)

Description of an interface object.

An interface object is a Python object that has a `signature` attribute containing
a `Signature` object, as well as an attribute for every member of its signature.
Signatures and interface objects are tightly linked: an interface object can be created out
of a signature, and the signature is used when `connect()`ing two interface objects
together. See the [introduction to interfaces](../../../../../../amaranth/stdlib/wiring.md#wiring-intro1) for a more detailed
explanation of why this is useful.

`Signature` can be used as a base class to define [customized](../../../../../../amaranth/stdlib/wiring.md#wiring-customizing)
signatures and interface objects.

#### WARNING
`Signature` objects are immutable. Classes inheriting from `Signature` must
ensure this remains the case when additional functionality is added.

* **Parameters:**
  **kwargs** (*typing_extensions.Unpack* *[*[*DriverModel*](#chipflow.platform.io.signatures.DriverModel) *]*)
