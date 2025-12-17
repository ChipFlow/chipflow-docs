# CSR fields

The [`amaranth_soc.csr.action`](#module-amaranth_soc.csr.action) module provides built-in [`FieldAction`](reg.md#amaranth_soc.csr.reg.FieldAction) implementations intended for common use cases, which are split in three categories: [basic fields](#csr-action-basic) for numerical values, [flag fields](#csr-action-flag) for arrays of bits, and [reserved fields](#csr-action-reserved) to serve as placeholders for compatibility.

<a id="csr-action-basic"></a>

## Basic fields

Such fields are either exclusively writable by a CSR bus initiator (e.g. [`W`](#amaranth_soc.csr.action.W), [`RW`](#amaranth_soc.csr.action.RW)) or the peripheral itself (e.g. [`R`](#amaranth_soc.csr.action.R)). This effectively removes the possibility of a write conflict between a CSR bus initiator and the peripheral.

### *class* amaranth_soc.csr.action.R

A read-only [`FieldAction`](reg.md#amaranth_soc.csr.reg.FieldAction).

* **Parameters:**
  **shape** ([shape-like object](../../amaranth/guide.md#lang-shapelike)) – Shape of the field.
* **Members:**
  * **port** (`In(csr.reg.FieldPort.Signature(shape, "r"))`) – Field port.
  * **r_data** (`In(shape)`) – Read data. Drives `port.r_data`.
  * **r_stb** (`Out(1)`) – Read strobe. Driven by `port.r_stb`.

### *class* amaranth_soc.csr.action.W

A write-only [`FieldAction`](reg.md#amaranth_soc.csr.reg.FieldAction).

* **Parameters:**
  **shape** ([shape-like object](../../amaranth/guide.md#lang-shapelike)) – Shape of the field.
* **Members:**
  * **port** (`In(csr.reg.FieldPort.Signature(shape, "w"))`) – Field port.
  * **w_data** (`Out(shape)`) – Write data. Driven by `port.w_data`.
  * **w_stb** (`Out(1)`) – Write strobe. Driven by `port.w_stb`.

### *class* amaranth_soc.csr.action.RW

A read/write [`FieldAction`](reg.md#amaranth_soc.csr.reg.FieldAction), with built-in storage.

Storage is updated with the value of `port.w_data` one clock cycle after `port.w_stb` is
asserted.

* **Parameters:**
  * **shape** ([shape-like object](../../amaranth/guide.md#lang-shapelike)) – Shape of the field.
  * **init** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Storage initial value.
* **Members:**
  * **port** (`In(csr.reg.FieldPort.Signature(shape, "rw"))`) – Field port.
  * **data** (`Out(shape)`) – Storage output.

#### *property* init

Storage initial value.

* **Return type:**
  [`int`](https://docs.python.org/3/library/functions.html#int)

<a id="csr-action-flag"></a>

## Flag fields

Flag fields may be concurrently written by a CSR bus initiator and the peripheral. Each bit of a flag field may be set or cleared independently of others.

### Suggested use cases

- [`RW1C`](#amaranth_soc.csr.action.RW1C) flags may be used when a peripheral needs to notify the CPU of a given condition, such as an error or a pending interrupt. To acknowledge the notification, the CPU would then write 1 to the flag bit.
- [`RW1S`](#amaranth_soc.csr.action.RW1S) flags may be used for self-clearing bits, such as the enable bit of a one-shot timer. When the timer reaches its maximum value, it would automatically disable itself by clearing its enable bit.
- A pair of [`RW1C`](#amaranth_soc.csr.action.RW1C) and [`RW1S`](#amaranth_soc.csr.action.RW1S) flags may be used to target the same range of bits (e.g. that drives an array of GPIO pins). This allows a CSR bus initiator to set and clear bits in one write transaction (which is guaranteed to be atomic). If a single [`RW`](#amaranth_soc.csr.action.RW) field was used instead, a read-modify-write transaction would be needed, and would require locking to insure its atomicity in a multi-tasked environment.

### *class* amaranth_soc.csr.action.RW1C

A read/write-one-to-clear [`FieldAction`](reg.md#amaranth_soc.csr.reg.FieldAction), with built-in storage.

Storage bits are:

> * cleared by high bits in `port.w_data`, one clock cycle after `port.w_stb` is asserted;
> * set by high bits in `set`, one clock cycle after they are asserted.

If a storage bit is set and cleared on the same clock cycle, setting it has precedence.

* **Parameters:**
  * **shape** ([shape-like object](../../amaranth/guide.md#lang-shapelike)) – Shape of the field.
  * **init** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Storage initial value.
* **Members:**
  * **port** (`In(csr.reg.FieldPort.Signature(shape, "rw"))`) – Field port.
  * **data** (`Out(shape)`) – Storage output.
  * **set** (`In(shape)`) – Mask to set storage bits.

#### *property* init

Storage initial value.

* **Return type:**
  [`int`](https://docs.python.org/3/library/functions.html#int)

### *class* amaranth_soc.csr.action.RW1S

A read/write-one-to-set [`FieldAction`](reg.md#amaranth_soc.csr.reg.FieldAction), with built-in storage.

Storage bits are:

> * set by high bits in `port.w_data`, one clock cycle after `port.w_stb` is asserted;
> * cleared by high bits in `clear`, one clock cycle after they are asserted.

If a storage bit is set and cleared on the same clock cycle, setting it has precedence.

* **Parameters:**
  * **shape** ([shape-like object](../../amaranth/guide.md#lang-shapelike)) – Shape of the field.
  * **init** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Storage initial value.
* **Members:**
  * **port** (`In(csr.reg.FieldPort.Signature(shape, "rw"))`) – Field port.
  * **data** (`Out(shape)`) – Storage output.
  * **clear** (`In(shape)`) – Mask to clear storage bits.

#### *property* init

Storage initial value.

* **Return type:**
  [`int`](https://docs.python.org/3/library/functions.html#int)

<a id="csr-action-reserved"></a>

## Reserved fields

Reserved fields may be defined to provide placeholders for past, future or undocumented functions of a peripheral.

### Suggested use cases

#### Reserved for future use (as value)

A [`ResRAWL`](#amaranth_soc.csr.action.ResRAWL) field can be used as a placeholder to ensure forward compatibility of software binaries with future SoC revisions, where it may be replaced with a [basic field](#csr-action-basic).

The value returned by reads (and written back) must have defined semantics (e.g. a no-op) that can be relied upon in future SoC revisions. When writing to this field, software drivers targeting the current SoC revision must set up an atomic read-modify-write transaction.

#### Reserved for future use (as flag)

If a field is expected to be implemented as a [flag](#csr-action-flag) in a future SoC revision, it can be defined as a [`ResRAW0`](#amaranth_soc.csr.action.ResRAW0) field in the current revision to ensure forward compatibility of software binaries.

Software drivers targeting the current SoC revision should ignore the value returned by reads. Writing a value of 0 must be a no-op if the field is implemented in a future SoC revision.

#### Defined but deprecated

If a field was deprecated in a previous SoC revision, it can be replaced with a [`ResR0WA`](#amaranth_soc.csr.action.ResR0WA) field to ensure backward compatibility of software binaries.

The value of 0 returned by reads (and written back) must retain the semantics defined in the SoC revision where this field was deprecated.

#### Defined but unimplemented

If a field is only implemented in some variants of a peripheral, it can be replaced by a [`ResR0W0`](#amaranth_soc.csr.action.ResR0W0) field in the others.

### *class* amaranth_soc.csr.action.ResRAW0

A reserved read-any/write-zero [`FieldAction`](reg.md#amaranth_soc.csr.reg.FieldAction).

* **Parameters:**
  **shape** ([shape-like object](../../amaranth/guide.md#lang-shapelike)) – Shape of the field.
* **Members:**
  **port** (`In(csr.reg.FieldPort.Signature(shape, "nc"))`) – Field port.

### *class* amaranth_soc.csr.action.ResRAWL

A reserved read-any/write-last [`FieldAction`](reg.md#amaranth_soc.csr.reg.FieldAction).

* **Parameters:**
  **shape** ([shape-like object](../../amaranth/guide.md#lang-shapelike)) – Shape of the field.
* **Members:**
  **port** (`In(csr.reg.FieldPort.Signature(shape, "nc"))`) – Field port.

### *class* amaranth_soc.csr.action.ResR0WA

A reserved read-zero/write-any [`FieldAction`](reg.md#amaranth_soc.csr.reg.FieldAction).

* **Parameters:**
  **shape** ([shape-like object](../../amaranth/guide.md#lang-shapelike)) – Shape of the field.
* **Members:**
  **port** (`In(csr.reg.FieldPort.Signature(shape, "nc"))`) – Field port.

### *class* amaranth_soc.csr.action.ResR0W0

A reserved read-zero/write-zero [`FieldAction`](reg.md#amaranth_soc.csr.reg.FieldAction).

* **Parameters:**
  **shape** ([shape-like object](../../amaranth/guide.md#lang-shapelike)) – Shape of the field.
* **Members:**
  **port** (`In(csr.reg.FieldPort.Signature(shape, "nc"))`) – Field port.
