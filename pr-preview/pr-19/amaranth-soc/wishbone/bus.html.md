# Wishbone bus

#### WARNING
This manual is a work in progress and is seriously incomplete!

<a id="module-amaranth_soc.wishbone.bus"></a>

The [`amaranth_soc.wishbone.bus`](#module-amaranth_soc.wishbone.bus) module provides Wishbone bus primitives.

### *class* amaranth_soc.wishbone.bus.CycleType

Wishbone Registered Feedback cycle type.

#### CLASSIC *= 0*

#### CONST_BURST *= 1*

#### INCR_BURST *= 2*

#### END_OF_BURST *= 7*

### *class* amaranth_soc.wishbone.bus.BurstTypeExt

Wishbone Registered Feedback burst type extension.

#### LINEAR *= 0*

#### WRAP_4 *= 1*

#### WRAP_8 *= 2*

#### WRAP_16 *= 3*

### *class* amaranth_soc.wishbone.bus.Feature

Optional Wishbone interface signals.

#### ERR *= 'err'*

#### RTY *= 'rty'*

#### STALL *= 'stall'*

#### LOCK *= 'lock'*

#### CTI *= 'cti'*

#### BTE *= 'bte'*

### *class* amaranth_soc.wishbone.bus.Signature

Wishbone interface signature.

See the [Wishbone specification](https://opencores.org/howto/wishbone) for description
of the Wishbone signals. The `RST_I` and `CLK_I` signals are provided as a part of
the clock domain that drives the interface.

The correspondence between the Amaranth-SoC signals and the Wishbone signals changes depending
on whether the interface acts as an initiator or a target.

* **Parameters:**
  * **addr_width** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Width of the address signal.
  * **data_width** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Width of the data signals (“port size” in Wishbone terminology).
    One of 8, 16, 32, 64.
  * **granularity** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Granularity of select signals (“port granularity” in Wishbone terminology).
    One of 8, 16, 32, 64.
    Optional. If `None` (by default), the granularity is equal to `data_width`.
  * **features** (iterable of [`Feature`](#amaranth_soc.wishbone.bus.Feature)) – Selects additional signals that will be a part of this interface.
    Optional.
* **Members:**
  * **adr** (`unsigned(addr_width)`) – Corresponds to Wishbone signal `ADR_O` (initiator) or `ADR_I` (target).
  * **dat_w** (`unsigned(data_width)`) – Corresponds to Wishbone signal `DAT_O` (initiator) or `DAT_I` (target).
  * **dat_r** (`unsigned(data_width)`) – Corresponds to Wishbone signal `DAT_I` (initiator) or `DAT_O` (target).
  * **sel** (`unsigned(data_width // granularity)`) – Corresponds to Wishbone signal `SEL_O` (initiator) or `SEL_I` (target).
  * **cyc** (`unsigned(1)`) – Corresponds to Wishbone signal `CYC_O` (initiator) or `CYC_I` (target).
  * **stb** (`unsigned(1)`) – Corresponds to Wishbone signal `STB_O` (initiator) or `STB_I` (target).
  * **we** (`unsigned(1)`) – Corresponds to Wishbone signal `WE_O`  (initiator) or `WE_I`  (target).
  * **ack** (`unsigned(1)`) – Corresponds to Wishbone signal `ACK_I` (initiator) or `ACK_O` (target).
  * **err** (`unsigned(1)`) – Optional. Corresponds to Wishbone signal `ERR_I` (initiator) or `ERR_O` (target).
  * **rty** (`unsigned(1)`) – Optional. Corresponds to Wishbone signal `RTY_I` (initiator) or `RTY_O` (target).
  * **stall** (`unsigned(1)`) – Optional. Corresponds to Wishbone signal `STALL_I` (initiator) or `STALL_O` (target).
  * **lock** (`unsigned(1)`) – Optional. Corresponds to Wishbone signal `LOCK_O` (initiator) or `LOCK_I` (target).
    Amaranth-SoC Wishbone support assumes that initiators that don’t want bus arbitration to
    happen in between two transactions need to use `lock` feature to guarantee this. An
    initiator without the `lock` feature may be arbitrated in between two transactions even
    if `cyc` is kept high.
  * **cti** (`unsigned(1)`) – Optional. Corresponds to Wishbone signal `CTI_O` (initiator) or `CTI_I` (target).
  * **bte** (`unsigned(1)`) – Optional. Corresponds to Wishbone signal `BTE_O` (initiator) or `BTE_I` (target).

#### addr_width

Width of the address signal.

* **Return type:**
  [`int`](https://docs.python.org/3/library/functions.html#int)

#### data_width

Width of the data signals (“port size” in Wishbone terminology).

* **Return type:**
  One of 8, 16, 32, 64.

#### granularity

Granularity of select signals (“port granularity” in Wishbone terminology).

* **Return type:**
  One of 8, 16, 32, 64.

#### features

Additional signals that will be a part of this interface.

* **Return type:**
  [`frozenset`](https://docs.python.org/3/library/stdtypes.html#frozenset) of [`Feature`](#amaranth_soc.wishbone.bus.Feature)

#### create(\*, path=None, src_loc_at=0)

Create a compatible interface.

See [`amaranth.lib.wiring.Signature.create()`](../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Signature.create) for details.

* **Return type:**
  [`Interface`](#amaranth_soc.wishbone.bus.Interface)

#### \_\_eq_\_(other)

Compare signatures.

Two signatures are equal if they have the same address width, data width, granularity and
features.

### *class* amaranth_soc.wishbone.bus.Interface

Wishbone bus interface.

#### NOTE
The data width of the underlying [`MemoryMap`](../memory.md#amaranth_soc.memory.MemoryMap) of the interface is equal to port
granularity, not port size. If port granularity is less than port size, then the address
width of the underlying memory map is extended to reflect that.

* **Parameters:**
  * **addr_width** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Width of the address signal. See [`Signature`](#amaranth_soc.wishbone.bus.Signature).
  * **data_width** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Width of the data signals. See [`Signature`](#amaranth_soc.wishbone.bus.Signature).
  * **granularity** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Granularity of select signals. Optional. See [`Signature`](#amaranth_soc.wishbone.bus.Signature).
  * **features** (iterable of [`Feature`](#amaranth_soc.wishbone.bus.Feature)) – Describes additional signals of this interface. Optional. See [`Signature`](#amaranth_soc.wishbone.bus.Signature).
  * **path** (iter([`str`](https://docs.python.org/3/library/stdtypes.html#str))) – Path to this Wishbone interface. Optional. See [`amaranth.lib.wiring.PureInterface`](../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.PureInterface).

#### addr_width

Width of the address signal.

* **Return type:**
  [`int`](https://docs.python.org/3/library/functions.html#int)

#### data_width

Width of the data signals (“port size” in Wishbone terminology).

* **Return type:**
  One of 8, 16, 32, 64.

#### granularity

Granularity of select signals (“port granularity” in Wishbone terminology).

* **Return type:**
  One of 8, 16, 32, 64.

#### features

Additional signals that are part of this interface.

* **Return type:**
  [`frozenset`](https://docs.python.org/3/library/stdtypes.html#frozenset) of [`Feature`](#amaranth_soc.wishbone.bus.Feature)

#### memory_map

Memory map of the bus.

* **Return type:**
  [`MemoryMap`](../memory.md#amaranth_soc.memory.MemoryMap) or `None`

### *class* amaranth_soc.wishbone.bus.Decoder

Wishbone bus decoder.

An address decoder for subordinate Wishbone buses.

* **Parameters:**
  * **addr_width** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Address width. See [`Signature`](#amaranth_soc.wishbone.bus.Signature).
  * **data_width** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Data width. See [`Signature`](#amaranth_soc.wishbone.bus.Signature).
  * **granularity** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Granularity. See [`Signature`](#amaranth_soc.wishbone.bus.Signature)
  * **features** (iterable of [`Feature`](#amaranth_soc.wishbone.bus.Feature)) – Optional signal set. See [`Signature`](#amaranth_soc.wishbone.bus.Signature).
  * **alignment** ([`int`](https://docs.python.org/3/library/functions.html#int), power-of-2 exponent) – Window alignment. Optional. See [`MemoryMap`](../memory.md#amaranth_soc.memory.MemoryMap).
* **Members:**
  **bus** (`In(wishbone.Signature(addr_width, data_width, granularity, features))`) – Wishbone bus providing access to subordinate buses.

#### align_to(alignment)

Align the implicit address of the next window.

See [`align_to()`](../memory.md#amaranth_soc.memory.MemoryMap.align_to) for details.

* **Returns:**
  Implicit next address.
* **Return type:**
  [`int`](https://docs.python.org/3/library/functions.html#int)

#### add(sub_bus, \*, name=None, addr=None, sparse=False)

Add a window to a subordinate bus.

See [`add_window()`](../memory.md#amaranth_soc.memory.MemoryMap.add_window) for details.

#### NOTE
The [`Decoder`](#amaranth_soc.wishbone.bus.Decoder) can perform either *sparse* or *dense* address translation:

> - If dense address translation is used (the default), the subordinate bus must have
>   the same data width as the [`Decoder`](#amaranth_soc.wishbone.bus.Decoder); the window will be contiguous.
> - If sparse address translation is used, the subordinate bus may have data width less
>   than the data width of the [`Decoder`](#amaranth_soc.wishbone.bus.Decoder); the window may be discontiguous.

In either case, the granularity of the subordinate bus must be equal to or less than
the granularity of the [`Decoder`](#amaranth_soc.wishbone.bus.Decoder).

* **Returns:**
  A tuple `(start, end, ratio)` describing the address range assigned to the window.
  When bridging buses of unequal data width, `ratio` is the amount of contiguous
  addresses on the narrower bus that are accessed for each transaction on the wider bus.
  Otherwise, it is always 1.
* **Return type:**
  [`tuple`](https://docs.python.org/3/library/stdtypes.html#tuple) of ([`int`](https://docs.python.org/3/library/functions.html#int), [`int`](https://docs.python.org/3/library/functions.html#int), [`int`](https://docs.python.org/3/library/functions.html#int))
* **Raises:**
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If the subordinate bus granularity is greater than the [`Decoder`](#amaranth_soc.wishbone.bus.Decoder) granularity.
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If dense address translation is used and the subordinate bus data width is not equal
        to the [`Decoder`](#amaranth_soc.wishbone.bus.Decoder) data width.
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If sparse address translation is used and the subordinate bus data width is not the
        equal to the subordinate bus granularity.
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If the subordinate bus as an optional output signal that is not present in the
        [`Decoder`](#amaranth_soc.wishbone.bus.Decoder) interface.

### *class* amaranth_soc.wishbone.bus.Arbiter

Wishbone bus arbiter.

A round-robin arbiter for initiators accessing a shared Wishbone bus.

* **Parameters:**
  * **addr_width** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Address width. See [`Signature`](#amaranth_soc.wishbone.bus.Signature).
  * **data_width** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Data width. See [`Signature`](#amaranth_soc.wishbone.bus.Signature).
  * **granularity** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Granularity. See [`Signature`](#amaranth_soc.wishbone.bus.Signature)
  * **features** (iterable of [`Feature`](#amaranth_soc.wishbone.bus.Feature)) – Optional signal set. See [`Signature`](#amaranth_soc.wishbone.bus.Signature).
* **Members:**
  **bus** (`Out(wishbone.Signature(addr_width, data_width, granularity, features))`) – Shared Wishbone bus.

#### add(intr_bus)

Add an initiator bus to the arbiter.

* **Raises:**
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If the initiator bus address width is not equal to the [`Arbiter`](#amaranth_soc.wishbone.bus.Arbiter) address width.
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If the initiator bus granularity is lesser than the [`Arbiter`](#amaranth_soc.wishbone.bus.Arbiter) granularity.
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If the initiator bus data width is not equal to the [`Arbiter`](#amaranth_soc.wishbone.bus.Arbiter) data width.
  * [**ValueError**](https://docs.python.org/3/library/exceptions.html#ValueError) – If the [`Arbiter`](#amaranth_soc.wishbone.bus.Arbiter) has an optional output signal that is not present in the
        initiator bus.
