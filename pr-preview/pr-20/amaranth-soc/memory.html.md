# Memory maps

The [`amaranth_soc.memory`](#module-amaranth_soc.memory) module provides primitives for organizing the address space of a bus interface.

<!-- from amaranth import *

from amaranth_soc import csr
from amaranth_soc.memory import * -->

<a id="memory-introduction"></a>

## Introduction

The purpose of [`MemoryMap`](#amaranth_soc.memory.MemoryMap) is to provide a hierarchical description of the address space of a System-on-Chip, from its bus interconnect to the registers of its peripherals. It is composed of [resources](#memory-resources) (representing registers, memories, etc) and [windows](#memory-windows) (representing bus bridges), and may be [queried](#memory-accessing-windows) afterwards in order to enumerate its contents, or determine the address of a resource.

<a id="memory-resources"></a>

## Resources

A *resource* is a [`Component`](../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Component) previously added to a [`MemoryMap`](#amaranth_soc.memory.MemoryMap). Each resource occupies an unique range of addresses within the memory map, and represents a device that is a target for bus transactions.

### Adding resources

Resources are added with [`MemoryMap.add_resource()`](#amaranth_soc.memory.MemoryMap.add_resource), which returns a `(start, end)` tuple describing their address range:

```python
memory_map = MemoryMap(addr_width=3, data_width=8)

reg_ctrl = csr.Register(csr.Field(csr.action.RW, 32), "rw")
reg_data = csr.Register(csr.Field(csr.action.RW, 32), "rw")
```

```pycon
>>> memory_map.add_resource(reg_ctrl, size=4, addr=0x0, name=("ctrl",))
(0, 4)
>>> memory_map.add_resource(reg_data, size=4, addr=0x4, name=("data",))
(4, 8)
```

<a id="memory-implicit-next-address"></a>

#### NOTE
The `addr` parameter of [`MemoryMap.add_resource()`](#amaranth_soc.memory.MemoryMap.add_resource) and [`MemoryMap.add_window()`](#amaranth_soc.memory.MemoryMap.add_window) is optional.

To simplify address assignment, each [`MemoryMap`](#amaranth_soc.memory.MemoryMap) has an *implicit next address*, starting at 0. If a resource or a window is added without an explicit address, the implicit next address is used. In any case, the implicit next address is set to the address immediately following the newly added resource or window.

### Accessing resources

Memory map resources can be iterated with [`MemoryMap.resources()`](#amaranth_soc.memory.MemoryMap.resources):

```pycon
>>> for resource, name, (start, end) in memory_map.resources():
...     print(f"name={name}, start={start:#x}, end={end:#x}, resource={resource}")
name=Name('ctrl'), start=0x0, end=0x4, resource=<...>
name=Name('data'), start=0x4, end=0x8, resource=<...>
```

A memory map can be queried with [`MemoryMap.find_resource()`](#amaranth_soc.memory.MemoryMap.find_resource) to get the name and address range of a given resource:

```pycon
>>> memory_map.find_resource(reg_ctrl)
ResourceInfo(path=(Name('ctrl'),), start=0x0, end=0x4, width=8)
```

The resource located at a given address can be retrieved with [`MemoryMap.decode_address()`](#amaranth_soc.memory.MemoryMap.decode_address):

```pycon
>>> memory_map.decode_address(0x4) is reg_data
True
```

<a id="memory-alignment"></a>

## Alignment

The value of `MemoryMap.alignment` constrains the layout of a memory map. If unspecified, it defaults to 0.

Each resource or window added to a memory map is placed at an address that is a multiple of `2 ** alignment`, and its size is rounded up to a multiple of `2 ** alignment`.

For example, the resources of this memory map are 64-bit aligned:

```python
memory_map = MemoryMap(addr_width=8, data_width=8, alignment=3)

reg_foo = csr.Register(csr.Field(csr.action.RW, 32), "rw")
reg_bar = csr.Register(csr.Field(csr.action.RW, 32), "rw")
reg_baz = csr.Register(csr.Field(csr.action.RW, 32), "rw")
```

```pycon
>>> memory_map.add_resource(reg_foo, size=4, name=("foo",))
(0, 8)
>>> memory_map.add_resource(reg_bar, size=4, name=("bar",), addr=0x9)
Traceback (most recent call last):
...
ValueError: Explicitly specified address 0x9 must be a multiple of 0x8 bytes
```

[`MemoryMap.add_resource()`](#amaranth_soc.memory.MemoryMap.add_resource) takes an optional `alignment` parameter. If a value greater than `MemoryMap.alignment` is given, it becomes the alignment of this resource:

```pycon
>>> memory_map.add_resource(reg_bar, size=4, name=("bar",), alignment=4)
(16, 32)
```

[`MemoryMap.align_to()`](#amaranth_soc.memory.MemoryMap.align_to) can be used to align the [implicit next address](#memory-implicit-next-address). Its alignment is modified if a value greater than `MemoryMap.alignment` is given.

```pycon
>>> memory_map.align_to(6)
64
>>> memory_map.add_resource(reg_baz, size=4, name=("baz",))
(64, 72)
```

#### NOTE
[`MemoryMap.align_to()`](#amaranth_soc.memory.MemoryMap.align_to) has no effect on the size of the next resource or window.

<a id="memory-windows"></a>

## Windows

A *window* is a [`MemoryMap`](#amaranth_soc.memory.MemoryMap) nested inside another memory map. Each window occupies an unique range of addresses within the memory map, and represents a bridge to a subordinate bus.

### Adding windows

Windows are added with [`MemoryMap.add_window()`](#amaranth_soc.memory.MemoryMap.add_window), which returns a `(start, end, ratio)` tuple describing their address range:

```python
reg_ctrl    = csr.Register(csr.Field(csr.action.RW, 32), "rw")
reg_rx_data = csr.Register(csr.Field(csr.action.RW, 32), "rw")
reg_tx_data = csr.Register(csr.Field(csr.action.RW, 32), "rw")

memory_map = MemoryMap(addr_width=14, data_width=32)
rx_window  = MemoryMap(addr_width=12, data_width=32)
tx_window  = MemoryMap(addr_width=12, data_width=32)
```

```pycon
>>> memory_map.add_resource(reg_ctrl, size=1, name=("ctrl",))
(0, 1)

>>> rx_window.add_resource(reg_rx_data, size=1, name=("data",))
(0, 1)
>>> memory_map.add_window(rx_window, name=("rx",))
(4096, 8192, 1)
```

The third value returned by [`MemoryMap.add_window()`](#amaranth_soc.memory.MemoryMap.add_window) represents the number of addresses that are accessed in the bus described by `rx_window` for one transaction in the bus described by `memory_map`. It is 1 in this case, as both busses have the same width.

```pycon
>>> tx_window.add_resource(reg_tx_data, size=1, name=("data",))
(0, 1)
>>> memory_map.add_window(tx_window, name=("tx",))
(8192, 12288, 1)
```

<a id="memory-accessing-windows"></a>

#### Accessing windows

Memory map windows can be iterated with [`MemoryMap.windows()`](#amaranth_soc.memory.MemoryMap.windows):

```pycon
>>> for window, name, (start, end, ratio) in memory_map.windows():
...     print(f"{name}, start={start:#x}, end={end:#x}, ratio={ratio}")
Name('rx'), start=0x1000, end=0x2000, ratio=1
Name('tx'), start=0x2000, end=0x3000, ratio=1
```

Windows can also be iterated with [`MemoryMap.window_patterns()`](#amaranth_soc.memory.MemoryMap.window_patterns), which encodes their address ranges as bit patterns compatible with the [match operator](../amaranth/guide.md#lang-matchop) and the [Case block](../amaranth/guide.md#lang-switch):

```pycon
>>> for window, name, (pattern, ratio) in memory_map.window_patterns():
...     print(f"{name}, pattern='{pattern}', ratio={ratio}")
Name('rx'), pattern='01------------', ratio=1
Name('tx'), pattern='10------------', ratio=1
```

Memory map resources can be recursively iterated with [`MemoryMap.all_resources()`](#amaranth_soc.memory.MemoryMap.all_resources), which yields instances of [`ResourceInfo`](#amaranth_soc.memory.ResourceInfo):

```pycon
>>> for res_info in memory_map.all_resources():
...     print(res_info)
ResourceInfo(path=(Name('ctrl'),), start=0x0, end=0x1, width=32)
ResourceInfo(path=(Name('rx'), Name('data')), start=0x1000, end=0x1001, width=32)
ResourceInfo(path=(Name('tx'), Name('data')), start=0x2000, end=0x2001, width=32)
```

### Address translation

When a memory map resource is accessed through a window, address translation may happen in three different modes.

#### Transparent mode

In *transparent mode*, each transaction on the primary bus results in one transaction on the subordinate bus without loss of data. This mode is selected when [`MemoryMap.add_window()`](#amaranth_soc.memory.MemoryMap.add_window) is given `sparse=None`, which will fail if the window and the memory map have a different data widths.

#### NOTE
In practice, transparent mode is identical to other modes; it can only be used with equal data widths, which results in the same behavior regardless of the translation mode. However, it causes [`MemoryMap.add_window()`](#amaranth_soc.memory.MemoryMap.add_window) to fail if the data widths are different.

#### Sparse mode

In *sparse mode*, each transaction on the wide primary bus results in one transaction on the narrow subordinate bus. High data bits on the primary bus are ignored, and any contiguous resource on the subordinate bus becomes discontiguous on the primary bus. This mode is selected when [`MemoryMap.add_window()`](#amaranth_soc.memory.MemoryMap.add_window) is given `sparse=True`.

#### Dense mode

In *dense mode*, each transaction on the wide primary bus results in several transactions on the narrow subordinate bus, and any contiguous resource on the subordinate bus stays contiguous on the primary bus. This mode is selected when [`MemoryMap.add_window()`](#amaranth_soc.memory.MemoryMap.add_window) is given `sparse=False`.

## Freezing

The state of a memory map can become immutable by calling [`MemoryMap.freeze()`](#amaranth_soc.memory.MemoryMap.freeze):

```python
memory_map = MemoryMap(addr_width=3, data_width=8)

reg_ctrl = csr.Register(csr.Field(csr.action.RW, 32), "rw")
```

```pycon
>>> memory_map.freeze()
>>> memory_map.add_resource(reg_ctrl, size=4, addr=0x0, name=("ctrl",))
Traceback (most recent call last):
...
ValueError: Memory map has been frozen. Cannot add resource <...>
```

It is recommended to freeze a memory map before passing it to external logic, as a preventive measure against TOCTTOU bugs.

### *class* amaranth_soc.memory.MemoryMap

#### freeze()

Freeze the [`MemoryMap`](#amaranth_soc.memory.MemoryMap).

Once the [`MemoryMap`](#amaranth_soc.memory.MemoryMap) is frozen, its visible state becomes immutable. Resources and
windows cannot be added anymore.

#### align_to(alignment)

Align the [implicit next address](#memory-implicit-next-address).

* **Parameters:**
  **alignment** ([`int`](https://docs.python.org/3/library/functions.html#int), power-of-2 exponent) – Address alignment. The start of the implicit next address will be a multiple of
  `2 ** max(alignment, self.alignment)`.
* **Returns:**
  Implicit next address.
* **Return type:**
  [`int`](https://docs.python.org/3/library/functions.html#int)

#### add_resource(resource, \*, name, size, addr=None, alignment=None)

Add a resource.

A resource is any device on the bus that is a destination for bus transactions, e.g.
a register or a memory block.

* **Parameters:**
  * **resource** ([`amaranth.lib.wiring.Component`](../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Component)) – The resource to be added.
  * **name** (`MemoryMap.Name`) – Name of the resource. It must not conflict with the name of other resources or windows
    present in this memory map.
  * **addr** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Address of the resource. Optional. If `None`, the [implicit next address](#memory-implicit-next-address) will be used. Otherwise, the exact specified address
    (which must be a multiple of `2 ** max(alignment, self.alignment)`) will be used.
  * **size** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Size of the resource, in minimal addressable units. Rounded up to a multiple of
    `2 ** max(alignment, self.alignment)`.
  * **alignment** ([`int`](https://docs.python.org/3/library/functions.html#int), power-of-2 exponent) – Alignment of the resource. Optional. If `None`, the memory map alignment is used.
* **Returns:**
  A tuple `(start, end)` describing the address range assigned to the resource.
* **Return type:**
  [`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple) of ([`int`](https://docs.python.org/3/library/functions.html#int), [`int`](https://docs.python.org/3/library/functions.html#int))
* **Raises:**
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If the memory map is frozen.
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If the requested address and size, after alignment, would overlap with any resources or
        windows that have already been added, or would be out of bounds.
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If `resource` has already been added to this memory map.
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If the requested name would conflict with the name of other resources or windows that
        have already been added.

#### resources()

Iterate local resources and their address ranges.

Non-recursively iterate resources in ascending order of their address.

* **Yields:**
  [`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple) of ([`amaranth.lib.wiring.Component`](../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Component), `MemoryMap.Name`,         [`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple) of ([`int`](https://docs.python.org/3/library/functions.html#int), [`int`](https://docs.python.org/3/library/functions.html#int))) – A tuple `resource, name, (start, end)` describing the address range assigned to the
  resource.

#### add_window(window, \*, name=None, addr=None, sparse=None)

Add a window.

A window is a device on a bus that provides access to a different bus, i.e. a bus bridge.
It performs address translation, such that the devices on a subordinate bus have different
addresses; the memory map reflects this address translation when resources are looked up
through the window.

* **Parameters:**
  * **window** ([`MemoryMap`](#amaranth_soc.memory.MemoryMap)) – A [`MemoryMap`](#amaranth_soc.memory.MemoryMap) describing the layout of the window. It is frozen as a side-effect
    of being added to this memory map.
  * **name** (`MemoryMap.Name`) – Name of the window. Optional. It must not conflict with the name of other resources or
    windows present in this memory map.
  * **addr** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Address of the window. Optional. If `None`, the [implicit next address](#memory-implicit-next-address) will be used after aligning it to
    `2 ** window.addr_width`. Otherwise, the exact specified address (which must be a
    multiple of `2 ** window.addr_width`) will be used.
  * **sparse** ([`bool`](https://docs.python.org/3/library/functions.html#bool)) – Address translation type. Optional. Ignored if the datapath widths of both memory maps
    are equal; must be specified otherwise.
* **Returns:**
  A tuple `(start, end, ratio)` describing the address range assigned to the window.
  When bridging buses of unequal data width, `ratio` is the amount of contiguous
  addresses on the narrower bus that are accessed for each transaction on the wider bus.
  Otherwise, it is always 1.
* **Return type:**
  [`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple) of ([`int`](https://docs.python.org/3/library/functions.html#int), [`int`](https://docs.python.org/3/library/functions.html#int), [`int`](https://docs.python.org/3/library/functions.html#int))
* **Raises:**
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If the memory map is frozen.
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If the requested address and size, after alignment, would overlap with any resources or
        windows that have already been added, or would be out of bounds.
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If `window.data_width` is wider than `data_width`.
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If the address translation mode is unspecified and `window.data_width` is different
        than `data_width`.
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If dense address translation is used and `data_width` is not an integer multiple
        of `window.data_width`.
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If dense address translation is used and the ratio of `data_width` to
        `window.data_width` is not a power of 2.
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If dense address translation is used and the ratio of `data_width` to
        `window.data_width` is lesser than 2 raised to the power of `alignment`.
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If the requested name would conflict with the name of other resources or windows that
        have already been added.
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If `window` is anonymous and the name of one of its resources or windows would
        conflict with the name of any resources or windows that have already been added.

#### windows()

Iterate local windows and their address ranges.

Non-recursively iterate windows in ascending order of their address.

* **Yields:**
  [`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple) of ([`MemoryMap`](#amaranth_soc.memory.MemoryMap), `MemoryMap.Name`, [`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple) of         ([`int`](https://docs.python.org/3/library/functions.html#int), [`int`](https://docs.python.org/3/library/functions.html#int), [`int`](https://docs.python.org/3/library/functions.html#int))) – A tuple `window, name, (start, end, ratio)` describing the address range assigned to
  the window. When bridging busses of unequal data widths, `ratio` is the amount of
  contiguous addresses on the narrower bus that are accessed for each transaction on the
  wider bus. Otherwise, it is always 1.

#### window_patterns()

Iterate local windows and patterns that match their address ranges.

Non-recursively iterate windows in ascending order of their address.

* **Yields:**
  [`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple) of ([`MemoryMap`](#amaranth_soc.memory.MemoryMap), `MemoryMap.Name`, [`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple) of         ([`str`](https://docs.python.org/3/library/stdtypes.html#str), [`int`](https://docs.python.org/3/library/functions.html#int))) – A tuple `window, name, (pattern, ratio)` describing the address range assigned to the
  window. `pattern` is a `addr_width` wide pattern that may be used in `Case`
  or `match` to determine if a value is within the address range of `window`. When
  bridging busses of unequal data widths, `ratio` is the amount of contiguous addresses
  on the narrower bus that are accessed for each transaction on the wider bus. Otherwise,
  it is always 1.

#### all_resources()

Iterate all resources and their address ranges.

Recursively iterate all resources in ascending order of their address, performing address
translation for resources that are located behind a window.

* **Yields:**
  [`ResourceInfo`](#amaranth_soc.memory.ResourceInfo) – A description of the resource and its address range.

#### find_resource(resource)

Find address range corresponding to a resource.

Recursively find the address range of a resource, performing address translation for
resources that are located behind a window.

* **Parameters:**
  **resource** ([`amaranth.lib.wiring.Component`](../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Component)) – Resource previously added to this [`MemoryMap`](#amaranth_soc.memory.MemoryMap) or one of its windows.
* **Returns:**
  A description of the resource and its address range.
* **Return type:**
  [`ResourceInfo`](#amaranth_soc.memory.ResourceInfo)
* **Raises:**
  [**KeyError**](https://docs.python.org/3/library/exceptions.html#KeyError) – If the resource is not found.

#### decode_address(address)

Decode an address to a resource.

* **Parameters:**
  **address** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Address of interest.
* **Returns:**
  A resource mapped to the provided address, or `None` if there is no such resource.
* **Return type:**
  [`amaranth.lib.wiring.Component`](../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Component) or `None`

### *class* amaranth_soc.memory.ResourceInfo

Resource metadata.

A description of a [`MemoryMap`](#amaranth_soc.memory.MemoryMap) resource with its assigned path and address range.

* **Parameters:**
  * **resource** ([`amaranth.lib.wiring.Component`](../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Component)) – A resource located in the [`MemoryMap`](#amaranth_soc.memory.MemoryMap). See [`MemoryMap.add_resource()`](#amaranth_soc.memory.MemoryMap.add_resource) for
    details.
  * **path** ([`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple) of `MemoryMap.Name`) – Path of the resource. It is composed of the names of each window sitting between
    the resource and the [`MemoryMap`](#amaranth_soc.memory.MemoryMap) from which this [`ResourceInfo`](#amaranth_soc.memory.ResourceInfo) was obtained.
    See [`MemoryMap.add_window()`](#amaranth_soc.memory.MemoryMap.add_window) for details.
  * **start** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Start of the address range assigned to the resource.
  * **end** ([`int`](https://docs.python.org/3/library/functions.html#int)) – End of the address range assigned to the resource.
  * **width** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Amount of data bits accessed at each address. It may be equal to the data width of the
    [`MemoryMap`](#amaranth_soc.memory.MemoryMap) from which this [`ResourceInfo`](#amaranth_soc.memory.ResourceInfo) was obtained, or less if the
    resource is located behind a window that uses sparse addressing.
