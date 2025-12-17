# CSR registers

The [`amaranth_soc.csr.reg`](#module-amaranth_soc.csr.reg) module provides a way to define and create CSR registers and register fields.

<!-- from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out, flipped, connect

from amaranth_soc import csr
from amaranth_soc.memory import * -->

## Introduction

Control and Status registers are commonly used as an interface between SoC peripherals and the firmware that operates them.

This module provides the following functionality:

1. Register field description and implementation via the [`Field`](#amaranth_soc.csr.reg.Field) and [`FieldAction`](#amaranth_soc.csr.reg.FieldAction) classes. The [`amaranth_soc.csr.action`](action.md#module-amaranth_soc.csr.action) module provides a built-in [`FieldAction`](#amaranth_soc.csr.reg.FieldAction) subclasses for common use cases. If needed, users can implement their own subclasses.
2. Composable layouts of register fields via [`FieldActionMap`](#amaranth_soc.csr.reg.FieldActionMap) and [`FieldActionArray`](#amaranth_soc.csr.reg.FieldActionArray). These classes are not meant to be instantiated directly, but are useful when introspecting the layout of a register.
3. Register definitions via the [`Register`](#amaranth_soc.csr.reg.Register) class. The fields of a register can be provided as [variable annotations](https://docs.python.org/3/glossary.html#term-variable-annotation) or as instance parameters.
4. A [`Builder`](#amaranth_soc.csr.reg.Builder) class to organize registers of a peripheral into a hierarchy of clusters and arrays, to be converted into a [`MemoryMap`](../memory.md#amaranth_soc.memory.MemoryMap).
5. A bridge between a CSR bus interface and the registers of a peripheral, via the [`Bridge`](#amaranth_soc.csr.reg.Bridge) class.

## Examples

### Defining a register declaratively

If its layout and access mode are known in advance, a register can be concisely defined using [variable annotations](https://docs.python.org/3/glossary.html#term-variable-annotation):

```python
class Status(csr.Register, access="rw"):
    rdy:    csr.Field(csr.action.R,       1)
    err:    csr.Field(csr.action.RW1C,    1)
    _unimp: csr.Field(csr.action.ResR0W0, 6)
```

#### NOTE
By convention, names of [reserved fields](action.md#csr-action-reserved) (such as `_unimp` in the above example) should begin with an underscore.

### Defining a register with instance parameters

If the layout or access mode of a register aren’t known until instantiation, a [`Register`](#amaranth_soc.csr.reg.Register) subclass can override them in `__init__`:

```python
class Data(csr.Register):
    def __init__(self, width=8, access="w"):
        super().__init__(fields={"data": csr.Field(csr.action.W, width)},
                         access=access)
```

### Defining a single-field register

In the previous example, the `Data` register has a single field named `"Data.data"`, which is redundant.

If no other fields are expected to be added in future revisions of the peripheral (or forward compatibility is not a concern), the field name can be omitted like so:

```python
class Data(csr.Register, access="w"):
    def __init__(self):
        super().__init__(csr.Field(csr.action.W, 8))
```

### Defining a register with nested fields

Hierarchical layouts of register fields can be expressed using lists and dicts:

```python
class SetClr(csr.Register, access="r"):
    pin: [{"set": csr.Field(csr.action.W, 1),
           "clr": csr.Field(csr.action.W, 1)} for _ in range(8)]
```

### Connecting registers to a CSR bus

In this example, the registers of `FooPeripheral` are added to a [`Builder`](#amaranth_soc.csr.reg.Builder) to produce a memory map, and then bridged to a bus interface:

```python
class FooPeripheral(wiring.Component):
    class Ctrl(csr.Register, access="rw"):
        enable: csr.Field(csr.action.RW, 1)
        _unimp: csr.Field(csr.action.ResR0W0, 7)

    class Data(csr.Register, access="r"):
        def __init__(self, width):
            super().__init__(csr.Field(csr.action.R, width))

    def __init__(self):
        regs = csr.Builder(addr_width=4, data_width=8)

        reg_ctrl = regs.add("Ctrl", Ctrl())
        reg_data = regs.add("Data", Data(width=32), offset=4)

        self._bridge = csr.Bridge(regs.as_memory_map())

        super().__init__({"csr_bus": In(csr.Signature(addr_width=4, data_width=8))})
        self.csr_bus.memory_map = self._bridge.bus.memory_map

    def elaborate(self, platform):
        return Module() # ...
```

### Defining a custom field action

If [`amaranth_soc.csr.action`](action.md#module-amaranth_soc.csr.action) built-ins do not cover a desired use case, a custom [`FieldAction`](#amaranth_soc.csr.reg.FieldAction) may provide an alternative.

This example shows a “read/write-0-to-set” field action:

```python
class RW0S(csr.FieldAction):
    def __init__(self, shape, init=0):
        super().__init__(shape, access="rw", members={
            "data":  Out(shape),
            "clear": In(shape),
        })
        self._storage = Signal(shape, init=init)
        self._init    = init

    @property
    def init(self):
        return self._init

    def elaborate(self, platform):
        m = Module()

        for i, storage_bit in enumerate(self._storage):
            with m.If(self.clear[i]):
                m.d.sync += storage_bit.eq(0)
            with m.If(self.port.w_stb & ~self.port.w_data[i]):
                m.d.sync += storage_bit.eq(1)

        m.d.comb += [
            self.port.r_data.eq(self._storage),
            self.data.eq(self._storage),
        ]

        return m
```

`RW0S` can then be passed to [`Field`](#amaranth_soc.csr.reg.Field):

```python
class Foo(csr.Register, access="rw"):
    mask: csr.Field(RW0S, 8)
    data: csr.Field(csr.action.RW, 8)
```

## Fields

#### *class* FieldPort.Access

Field access mode.

#### R *= 'r'*

Read-only mode.

#### W *= 'w'*

Write-only mode.

#### RW *= 'rw'*

Read/write mode.

#### NC *= 'nc'*

Not connected.

#### readable()

Readable access mode.

* **Returns:**
  `True` if equal to [`R`](#amaranth_soc.csr.reg.FieldPort.Access.R) or [`RW`](#amaranth_soc.csr.reg.FieldPort.Access.RW).
* **Return type:**
  [`bool`](https://docs.python.org/3/library/functions.html#bool)

#### writable()

Writable access mode.

* **Returns:**
  `True` if equal to [`W`](#amaranth_soc.csr.reg.FieldPort.Access.W) or [`RW`](#amaranth_soc.csr.reg.FieldPort.Access.RW).
* **Return type:**
  [`bool`](https://docs.python.org/3/library/functions.html#bool)

#### *class* FieldPort.Signature

CSR register field port signature.

* **Parameters:**
  * **shape** ([shape-like object](../../amaranth/guide.md#lang-shapelike)) – Shape of the field.
  * **access** ([`FieldPort.Access`](#amaranth_soc.csr.reg.FieldPort.Access)) – Field access mode.
* **Members:**
  * **r_data** (`In(shape)`) – Read data. Must always be valid, and is sampled when `r_stb` is asserted.
  * **r_stb** (`Out(1)`) – Read strobe. Fields with read side effects should perform them when this strobe is
    asserted.
  * **w_data** (`Out(shape)`) – Write data. Valid only when `w_stb` is asserted.
  * **w_stb** (`Out(1)`) – Write strobe. Fields should update their value or perform the write side effect when
    this strobe is asserted.

#### create(\*, path=None, src_loc_at=0)

Create a compatible interface.

See [`amaranth.lib.wiring.Signature.create()`](../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature.create) for details.

* **Return type:**
  [`FieldPort`](#amaranth_soc.csr.reg.FieldPort)

#### \_\_eq_\_(other)

Compare signatures.

Two signatures are equal if they have the same shape and field access mode.

### *class* amaranth_soc.csr.reg.FieldPort

CSR register field port.

An interface between a [`Register`](#amaranth_soc.csr.reg.Register) and one of its fields.

* **Parameters:**
  * **signature** ([`FieldPort.Signature`](#amaranth_soc.csr.reg.FieldPort.Signature)) – Field port signature.
  * **path** (iterable of [`str`](https://docs.python.org/3/library/stdtypes.html#str)) – Path to the field port. Optional. See [`amaranth.lib.wiring.PureInterface`](../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.PureInterface).

### *class* amaranth_soc.csr.reg.Field

Description of a CSR register field.

* **Parameters:**
  * **action_cls** (subclass of [`FieldAction`](#amaranth_soc.csr.reg.FieldAction)) – The type of field action to be instantiated by [`Field.create()`](#amaranth_soc.csr.reg.Field.create).
  * **\*args** ([`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple)) – Positional arguments passed to `action_cls.__init__`.
  * **\*\*kwargs** ([`dict`](https://docs.python.org/3/library/stdtypes.html#dict)) – Keyword arguments passed to `action_cls.__init__`.

#### create()

Instantiate a field action.

* **Returns:**
  The object returned by `action_cls(*args, **kwargs)`.
* **Return type:**
  [`FieldAction`](#amaranth_soc.csr.reg.FieldAction)

## Field actions

### *class* amaranth_soc.csr.reg.FieldAction

CSR register field action.

A component mediating access between a CSR bus and a range of bits within a [`Register`](#amaranth_soc.csr.reg.Register).

* **Parameters:**
  * **shape** ([shape-like object](../../amaranth/guide.md#lang-shapelike)) – Shape of the field.
  * **access** ([`FieldPort.Access`](#amaranth_soc.csr.reg.FieldPort.Access)) – Field access mode.
  * **members** (iterable of ([`str`](https://docs.python.org/3/library/stdtypes.html#str), [`amaranth.lib.wiring.Member`](../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Member)) pairs, optional) – Additional signature members.
* **Members:**
  **port** (`In(csr.reg.FieldPort.Signature(shape, access))`) – Field port.

### *class* amaranth_soc.csr.reg.FieldActionMap

A mapping of field actions.

* **Parameters:**
  **fields** ([`dict`](https://docs.python.org/3/library/stdtypes.html#dict) of [`str`](https://docs.python.org/3/library/stdtypes.html#str) to ([`Field`](#amaranth_soc.csr.reg.Field) or [`dict`](https://docs.python.org/3/library/stdtypes.html#dict) or [`list`](https://docs.python.org/3/library/stdtypes.html#list))) – 

  Register fields. Fields are instantiated according to their type:
  > - a [`Field`](#amaranth_soc.csr.reg.Field) is instantiated as a [`FieldAction`](#amaranth_soc.csr.reg.FieldAction);
  > - a [`dict`](https://docs.python.org/3/library/stdtypes.html#dict) is instantiated as a [`FieldActionMap`](#amaranth_soc.csr.reg.FieldActionMap);
  > - a [`list`](https://docs.python.org/3/library/stdtypes.html#list) is instantiated as a [`FieldActionArray`](#amaranth_soc.csr.reg.FieldActionArray).

#### \_\_getitem_\_(key)

Access a field by name or index.

* **Returns:**
  The field instance associated with `key`.
* **Return type:**
  [`FieldAction`](#amaranth_soc.csr.reg.FieldAction) or [`FieldActionMap`](#amaranth_soc.csr.reg.FieldActionMap) or [`FieldActionArray`](#amaranth_soc.csr.reg.FieldActionArray)
* **Raises:**
  [**KeyError**](https://docs.python.org/3/library/exceptions.html#KeyError) – If there is no field instance associated with `key`.

#### \_\_getattr_\_(name)

Access a field by name.

* **Returns:**
  The field instance associated with `name`.
* **Return type:**
  [`FieldAction`](#amaranth_soc.csr.reg.FieldAction) or [`FieldActionMap`](#amaranth_soc.csr.reg.FieldActionMap) or [`FieldActionArray`](#amaranth_soc.csr.reg.FieldActionArray)
* **Raises:**
  * [**AttributeError**](https://docs.python.org/3/library/exceptions.html#AttributeError) – If the field map does not have a field instance associated with `name`.
  * [**AttributeError**](https://docs.python.org/3/library/exceptions.html#AttributeError) – If `name` is reserved (i.e. starts with an underscore).

#### \_\_iter_\_()

Iterate over the field map.

* **Yields:**
  [`str`](https://docs.python.org/3/library/stdtypes.html#str) – Key (name) for accessing the field.

#### \_\_len_\_()

Field map size.

* **Returns:**
  The number of items in the map.
* **Return type:**
  [`int`](https://docs.python.org/3/library/functions.html#int)

#### flatten()

Recursively iterate over the field map.

* **Yields:**
  * iterable of [`str`](https://docs.python.org/3/library/stdtypes.html#str) – Path of the field. It is prefixed by the name of every nested [`FieldActionMap`](#amaranth_soc.csr.reg.FieldActionMap)
    or [`FieldActionArray`](#amaranth_soc.csr.reg.FieldActionArray).
  * [`FieldAction`](#amaranth_soc.csr.reg.FieldAction) – Field instance.

### *class* amaranth_soc.csr.reg.FieldActionArray

An array of CSR register fields.

* **Parameters:**
  **fields** ([`list`](https://docs.python.org/3/library/stdtypes.html#list) of ([`Field`](#amaranth_soc.csr.reg.Field) or [`dict`](https://docs.python.org/3/library/stdtypes.html#dict) or [`list`](https://docs.python.org/3/library/stdtypes.html#list))) – 

  Register fields. Fields are instantiated according to their type:
  > - a [`Field`](#amaranth_soc.csr.reg.Field) is instantiated as a [`FieldAction`](#amaranth_soc.csr.reg.FieldAction);
  > - a [`dict`](https://docs.python.org/3/library/stdtypes.html#dict) is instantiated as a [`FieldActionMap`](#amaranth_soc.csr.reg.FieldActionMap);
  > - a [`list`](https://docs.python.org/3/library/stdtypes.html#list) is instantiated as a [`FieldActionArray`](#amaranth_soc.csr.reg.FieldActionArray).

#### \_\_getitem_\_(key)

Access a field by index.

* **Returns:**
  The field instance associated with `key`.
* **Return type:**
  [`FieldAction`](#amaranth_soc.csr.reg.FieldAction) or [`FieldActionMap`](#amaranth_soc.csr.reg.FieldActionMap) or [`FieldActionArray`](#amaranth_soc.csr.reg.FieldActionArray)

#### \_\_len_\_()

Field array size.

* **Returns:**
  The number of items in the array.
* **Return type:**
  [`int`](https://docs.python.org/3/library/functions.html#int)

#### flatten()

Recursively iterate over the field array.

* **Yields:**
  * iterable of [`str`](https://docs.python.org/3/library/stdtypes.html#str) – Path of the field. It is prefixed by the name of every nested [`FieldActionMap`](#amaranth_soc.csr.reg.FieldActionMap)
    or [`FieldActionArray`](#amaranth_soc.csr.reg.FieldActionArray).
  * [`FieldAction`](#amaranth_soc.csr.reg.FieldAction) – Field instance.

## Registers

### *class* amaranth_soc.csr.reg.Register

A CSR register.

* **Parameters:**
  * **fields** ([`dict`](https://docs.python.org/3/library/stdtypes.html#dict) or [`list`](https://docs.python.org/3/library/stdtypes.html#list) or [`Field`](#amaranth_soc.csr.reg.Field), optional) – Collection of register fields. If omitted, a dict is populated from Python [variable
    annotations](https://docs.python.org/3/glossary.html#term-variable-annotation). `fields` is used to create
    a [`FieldActionMap`](#amaranth_soc.csr.reg.FieldActionMap), [`FieldActionArray`](#amaranth_soc.csr.reg.FieldActionArray), or [`FieldAction`](#amaranth_soc.csr.reg.FieldAction),
    depending on its type ([`dict`](https://docs.python.org/3/library/stdtypes.html#dict), [`list`](https://docs.python.org/3/library/stdtypes.html#list), or [`Field`](#amaranth_soc.csr.reg.Field)).
  * **access** ([`Access`](bus.md#amaranth_soc.csr.bus.Element.Access)) – Element access mode.
* **Members:**
  **element** (`In(csr.Element.Signature(shape, access))`) – Interface between this [`Register`](#amaranth_soc.csr.reg.Register) and a CSR bus primitive.
* **Raises:**
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If `fields` is not `None` and at least one [variable annotation](https://docs.python.org/3/glossary.html#term-variable-annotation) is a [`Field`](#amaranth_soc.csr.reg.Field).
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If `element.access` is not readable and at least one field is readable.
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If `element.access` is not writable and at least one field is writable.

#### field

Collection of field instances.

* **Return type:**
  [`FieldActionMap`](#amaranth_soc.csr.reg.FieldActionMap) or [`FieldActionArray`](#amaranth_soc.csr.reg.FieldActionArray) or [`FieldAction`](#amaranth_soc.csr.reg.FieldAction)

#### f

Shorthand for [`Register.field`](#amaranth_soc.csr.reg.Register.field).

* **Return type:**
  [`FieldActionMap`](#amaranth_soc.csr.reg.FieldActionMap) or [`FieldActionArray`](#amaranth_soc.csr.reg.FieldActionArray) or [`FieldAction`](#amaranth_soc.csr.reg.FieldAction)

#### \_\_iter_\_()

Recursively iterate over the field collection.

* **Yields:**
  * iterable of [`str`](https://docs.python.org/3/library/stdtypes.html#str) – Path of the field. It is prefixed by the name of every nested [`FieldActionMap`](#amaranth_soc.csr.reg.FieldActionMap)
    or [`FieldActionArray`](#amaranth_soc.csr.reg.FieldActionArray).
  * [`FieldAction`](#amaranth_soc.csr.reg.FieldAction) – Field instance.

### *class* amaranth_soc.csr.reg.Builder

CSR builder.

A CSR builder collects a group of [`Register`](#amaranth_soc.csr.reg.Register)s within an address range with the goal
of producing a [`MemoryMap`](../memory.md#amaranth_soc.memory.MemoryMap) of the resulting layout.

* **Parameters:**
  * **addr_width** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Address width.
  * **data_width** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Data width.
  * **granularity** ([`int`](https://docs.python.org/3/library/functions.html#int), optional) – Granularity. Defaults to 8 bits.
* **Raises:**
  [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If `data_width` is not a multiple of `granularity`.

#### freeze()

Freeze the builder.

Once the builder is frozen, [`Register`](#amaranth_soc.csr.reg.Register)s cannot be added anymore.

#### add(name, reg, \*, offset=None)

Add a register.

* **Parameters:**
  * **name** ([`str`](https://docs.python.org/3/library/stdtypes.html#str)) – Register name.
  * **reg** ([`Register`](#amaranth_soc.csr.reg.Register)) – Register.
  * **offset** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Register offset. Optional.
* **Returns:**
  `reg`, which is added to the builder. Its name is `name`, prefixed by the names and
  indices of any parent [`Cluster()`](#amaranth_soc.csr.reg.Builder.Cluster) and [`Index()`](#amaranth_soc.csr.reg.Builder.Index).
* **Return type:**
  [`Register`](#amaranth_soc.csr.reg.Register)
* **Raises:**
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If the builder is frozen.
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If `reg` is already added to the builder.
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If `offset` is not a multiple of `self.data_width // self.granularity`.

#### Cluster(name)

Define a cluster.

* **Parameters:**
  **name** ([`str`](https://docs.python.org/3/library/stdtypes.html#str)) – Cluster name.

#### Index(index)

Define an array index.

* **Parameters:**
  **index** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Array index.

#### as_memory_map()

Build a memory map.

If a register was added without an explicit `offset`, the [implicit next address](../memory.md#memory-implicit-next-address) of the memory map is used. Otherwise, the register address
is `offset * granularity // data_width`.

Registers are added to the memory map in the same order as they were added to the builder.

* **Return type:**
  [`MemoryMap`](../memory.md#amaranth_soc.memory.MemoryMap).

### *class* amaranth_soc.csr.reg.Bridge

CSR bridge.

* **Parameters:**
  **memory_map** ([`MemoryMap`](../memory.md#amaranth_soc.memory.MemoryMap)) – Memory map of [`Register`](#amaranth_soc.csr.reg.Register)s.
* **Members:**
  **bus** (`In(csr.Signature(memory_map.addr_width, memory_map.data_width))`) – CSR bus providing access to the contents of `memory_map`.
* **Raises:**
  [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If `memory_map` has windows.
