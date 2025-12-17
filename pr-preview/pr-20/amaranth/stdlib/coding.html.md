# Code conversion

The [`amaranth.lib.coding`](#module-amaranth.lib.coding) module provides building blocks for conversion between different encodings of binary numbers.

## One-hot coding

### *class* amaranth.lib.coding.Encoder

Encode one-hot to binary.

If one bit in `i` is asserted, `n` is low and `o` indicates the asserted bit.
Otherwise, `n` is high and `o` is `0`.

* **Parameters:**
  **width** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Bit width of the input
* **Attributes:**
  * **i** (*Signal(width), in*) – One-hot input.
  * **o** (*Signal(range(width)), out*) – Encoded natural binary.
  * **n** (*Signal, out*) – Invalid: either none or multiple input bits are asserted.

### *class* amaranth.lib.coding.Decoder

Decode binary to one-hot.

If `n` is low, only the `i`-th bit in `o` is asserted.
If `n` is high, `o` is `0`.

* **Parameters:**
  **width** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Bit width of the output.
* **Attributes:**
  * **i** (*Signal(range(width)), in*) – Input binary.
  * **o** (*Signal(width), out*) – Decoded one-hot.
  * **n** (*Signal, in*) – Invalid, no output bits are to be asserted.

## Priority coding

### *class* amaranth.lib.coding.PriorityEncoder

Priority encode requests to binary.

If any bit in `i` is asserted, `n` is low and `o` indicates the least significant
asserted bit.
Otherwise, `n` is high and `o` is `0`.

* **Parameters:**
  **width** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Bit width of the input.
* **Attributes:**
  * **i** (*Signal(width), in*) – Input requests.
  * **o** (*Signal(range(width)), out*) – Encoded natural binary.
  * **n** (*Signal, out*) – Invalid: no input bits are asserted.

### *class* amaranth.lib.coding.PriorityDecoder

Decode binary to priority request.

Identical to [`Decoder`](#amaranth.lib.coding.Decoder).

## Gray coding

### *class* amaranth.lib.coding.GrayEncoder

Encode binary to Gray code.

* **Parameters:**
  **width** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Bit width.
* **Attributes:**
  * **i** (*Signal(width), in*) – Natural binary input.
  * **o** (*Signal(width), out*) – Encoded Gray code.

### *class* amaranth.lib.coding.GrayDecoder

Decode Gray code to binary.

* **Parameters:**
  **width** ([*int*](https://docs.python.org/3/library/functions.html#int)) – Bit width.
* **Attributes:**
  * **i** (*Signal(width), in*) – Gray code input.
  * **o** (*Signal(width), out*) – Decoded natural binary.
