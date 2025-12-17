# Cyclic redundancy checks

The [`amaranth.lib.crc`](#module-amaranth.lib.crc) module provides facilities for computing cyclic redundancy checks (CRCs)
in software and in hardware.

## Introduction

The essentials of a CRC computation are specified with an [`Algorithm`](#amaranth.lib.crc.Algorithm) object, which defines
CRC width, polynomial, initial value, input/output reflection, and output XOR. Many commonly used
CRC algorithms are available in the [`catalog`](crc/catalog.md#module-amaranth.lib.crc.catalog) module, while most other
CRC designs can be accommodated by manually constructing an [`Algorithm`](#amaranth.lib.crc.Algorithm).

An [`Algorithm`](#amaranth.lib.crc.Algorithm) is specialized for a particular data width to obtain [`Parameters`](#amaranth.lib.crc.Parameters),
which fully define a CRC computation. [`Parameters.compute()`](#amaranth.lib.crc.Parameters.compute) computes a CRC in software, while
[`Parameters.create()`](#amaranth.lib.crc.Parameters.create) creates a [`Processor`](#amaranth.lib.crc.Processor) that computes a CRC in hardware.

## Examples

<!-- from amaranth import *

m = Module() -->
```python
from amaranth.lib.crc import Algorithm
from amaranth.lib.crc.catalog import CRC16_CCITT, CRC16_USB


# Compute a CRC in hardware using the predefined CRC16-CCITT algorithm and a data word
# width of 8 bits (in other words, computing it over bytes).
m.submodules.crc16_ccitt = crc16_ccitt = CRC16_CCITT().create()

# Compute a CRC in hardware using the predefined CRC16-USB algorithm and a data word
# width of 32 bits.
m.submodules.crc16_usb = crc16_usb = CRC16_USB(32).create()

# Compute a CRC in software using a custom CRC algorithm and explicitly specified data word
# width.
algo = Algorithm(crc_width=16, polynomial=0x1021, initial_crc=0xffff,
    reflect_input=False, reflect_output=False, xor_output=0x0000)
assert algo(data_width=8).compute(b"123456789") == 0x29b1
```

## Algorithms and parameters

### *class* amaranth.lib.crc.Algorithm(\*, crc_width, polynomial, initial_crc, reflect_input, reflect_output, xor_output)

Essential parameters for cyclic redundancy check computation.

The parameter set is based on the Williams model from [“A Painless Guide to CRC Error Detection
Algorithms”](http://www.ross.net/crc/download/crc_v3.txt).

For a reference of standard CRC parameter sets, refer to:

* [reveng](https://reveng.sourceforge.io/crc-catalogue/all.htm)’s catalogue, which uses an identical parameterisation;
* [crcmod](https://crcmod.sourceforge.net/crcmod.predefined.html)’s list of predefined functions, but remove the leading ‘1’ from the polynominal,
  XOR the “Init-value” with “XOR-out” to obtain `initial_crc`, and where “Reversed” is
  `True`, set both `reflect_input` and `reflect_output` to `True`;
* [CRC Zoo](https://users.ece.cmu.edu/~koopman/crc/), which contains only polynomials; use the “explicit +1” form of polynomial but
  remove the leading ‘1’.

Many commonly used CRC algorithms are available in the [`catalog`](crc/catalog.md#module-amaranth.lib.crc.catalog)
module, which includes all entries in the [reveng catalogue](https://reveng.sourceforge.io/crc-catalogue/all.htm).

The essential parameters on their own cannot be used to perform CRC computation, and must be
combined with a specific data word width. This can be done using `algo(data_width)`, which
returns a [`Parameters`](#amaranth.lib.crc.Parameters) object.

* **Parameters:**
  * **crc_width** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Bit width of CRC word. Also known as “width” in the Williams model.
  * **polynomial** ([`int`](https://docs.python.org/3/library/functions.html#int)) – CRC polynomial to use, `crc_width` bits long, without the implicit `x ** crc_width`
    term. Polynomial is always specified with the highest order terms in the most significant
    bit positions; use `reflect_input` and `reflect_output` to perform a least
    significant bit first computation.
  * **initial_crc** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Initial value of CRC register at reset. Most significant bit always corresponds to
    the highest order term in the CRC register.
  * **reflect_input** ([`bool`](https://docs.python.org/3/library/functions.html#bool)) – If `True`, the input data words are bit-reflected, so that they are processed least
    significant bit first.
  * **reflect_output** ([`bool`](https://docs.python.org/3/library/functions.html#bool)) – If `True`, the output CRC is bit-reflected, so that the least-significant bit of
    the output is the highest-order bit of the CRC register. Note that this reflection is
    performed over the entire CRC register; for transmission you may want to treat the output
    as a little-endian multi-word value, so for example the reflected 16-bit output `0x4E4C`
    would be transmitted as the two octets `0x4C, 0x4E`, each transmitted least significant
    bit first.
  * **xor_output** ([`int`](https://docs.python.org/3/library/functions.html#int)) – The output CRC will be the CRC register XOR’d with this value, applied after any output
    bit-reflection.

#### \_\_call_\_(data_width=8)

Combine these essential parameters with a data word width to form complete parameters.

* **Returns:**
  `Parameters(self, data_width)`
* **Return type:**
  [`Parameters`](#amaranth.lib.crc.Parameters)

### *class* amaranth.lib.crc.Parameters(algorithm, data_width=8)

Complete parameters for cyclic redundancy check computation.

Contains the essential [`Algorithm`](#amaranth.lib.crc.Algorithm) parameters, plus the data word width.

A [`Parameters`](#amaranth.lib.crc.Parameters) object can be used to directly compute CRCs using
the [`compute()`](#amaranth.lib.crc.Parameters.compute) method, or to construct a hardware module using
the [`create()`](#amaranth.lib.crc.Parameters.create) method.

* **Parameters:**
  * **algorithm** ([`Algorithm`](#amaranth.lib.crc.Algorithm)) – CRC algorithm to use. Specifies the CRC width, polynomial, initial value, whether to
    reflect the input or output words, and any output XOR.
  * **data_width** ([`int`](https://docs.python.org/3/library/functions.html#int)) – Bit width of data words.

#### residue()

Obtain the residual value left in the CRC register after processing a valid trailing CRC.

#### compute(data)

Compute the CRC of all data words in `data`.

* **Parameters:**
  **data** (iterable of [`int`](https://docs.python.org/3/library/functions.html#int)) – Data words, each of which is `data_width` bits wide.

#### create()

Create a hardware CRC generator with these parameters.

* **Returns:**
  `Processor(self)`
* **Return type:**
  [`Processor`](#amaranth.lib.crc.Processor)

## CRC computation

### *class* amaranth.lib.crc.Processor

Hardware cyclic redundancy check generator.

This module generates CRCs from an input data stream, which can be used to validate an existing
CRC or generate a new CRC. It is configured by the [`Parameters`](#amaranth.lib.crc.Parameters) class, which can handle
most types of CRCs.

The CRC value is updated on any clock cycle where `valid` is asserted, with the updated
value available on the `crc` output on the subsequent clock cycle. The latency is therefore
one clock cycle, and the throughput is one data word per clock cycle.

The CRC is reset to its initial value whenever `start` is asserted. `start` and
`valid` may be asserted on the same clock cycle, in which case a new CRC computation is
started with the current value of data.

When `data_width` is 1, a classic bit-serial CRC is implemented for the given polynomial
in a Galois-type shift register. For larger values of `data_width`, a similar architecture
computes every new bit of the CRC in parallel.

The `match_detected` output may be used to validate data with a trailing CRC (also known as
a codeword in coding theory). If the most recently processed data word(s) form the valid CRC of
all the previous data words since `start` was asserted, the CRC register will always take on
a fixed value known as the [`residue`](#amaranth.lib.crc.Parameters.residue). The `match_detected` output
indicates whether the CRC register currently contains this residue.

* **Parameters:**
  **parameters** ([`Parameters`](#amaranth.lib.crc.Parameters)) – Parameters used for computation.
* **Attributes:**
  * **start** (*Signal(), in*) – Assert to indicate the start of a CRC computation, re-initialising the CRC register to
    the initial value. May be asserted simultaneously with `valid` or by itself.
  * **data** (*Signal(data_width), in*) – Data word to add to CRC when `valid` is asserted.
  * **valid** (*Signal(), in*) – Assert when `data` is valid to add the data word to the CRC.
  * **crc** (*Signal(crc_width), out*) – Registered CRC output value, updated one clock cycle after `valid` becomes asserted.
  * **match_detected** (*Signal(), out*) – Asserted if the current CRC value indicates a valid codeword has been received.

## Predefined algorithms

The following predefined CRC algorithms are available:

* [Algorithm catalog](crc/catalog.md)
  * [`CRC3_GSM`](crc/catalog.md#amaranth.lib.crc.catalog.CRC3_GSM)
  * [`CRC3_ROHC`](crc/catalog.md#amaranth.lib.crc.catalog.CRC3_ROHC)
  * [`CRC4_G_704`](crc/catalog.md#amaranth.lib.crc.catalog.CRC4_G_704)
  * [`CRC4_ITU`](crc/catalog.md#amaranth.lib.crc.catalog.CRC4_ITU)
  * [`CRC4_INTERLAKEN`](crc/catalog.md#amaranth.lib.crc.catalog.CRC4_INTERLAKEN)
  * [`CRC5_EPC_C1G2`](crc/catalog.md#amaranth.lib.crc.catalog.CRC5_EPC_C1G2)
  * [`CRC5_EPC`](crc/catalog.md#amaranth.lib.crc.catalog.CRC5_EPC)
  * [`CRC5_G_704`](crc/catalog.md#amaranth.lib.crc.catalog.CRC5_G_704)
  * [`CRC5_ITU`](crc/catalog.md#amaranth.lib.crc.catalog.CRC5_ITU)
  * [`CRC5_USB`](crc/catalog.md#amaranth.lib.crc.catalog.CRC5_USB)
  * [`CRC6_CDMA2000_A`](crc/catalog.md#amaranth.lib.crc.catalog.CRC6_CDMA2000_A)
  * [`CRC6_CDMA2000_B`](crc/catalog.md#amaranth.lib.crc.catalog.CRC6_CDMA2000_B)
  * [`CRC6_DARC`](crc/catalog.md#amaranth.lib.crc.catalog.CRC6_DARC)
  * [`CRC6_G_704`](crc/catalog.md#amaranth.lib.crc.catalog.CRC6_G_704)
  * [`CRC6_ITU`](crc/catalog.md#amaranth.lib.crc.catalog.CRC6_ITU)
  * [`CRC6_GSM`](crc/catalog.md#amaranth.lib.crc.catalog.CRC6_GSM)
  * [`CRC7_MMC`](crc/catalog.md#amaranth.lib.crc.catalog.CRC7_MMC)
  * [`CRC7_ROHC`](crc/catalog.md#amaranth.lib.crc.catalog.CRC7_ROHC)
  * [`CRC7_UMTS`](crc/catalog.md#amaranth.lib.crc.catalog.CRC7_UMTS)
  * [`CRC8_AUTOSAR`](crc/catalog.md#amaranth.lib.crc.catalog.CRC8_AUTOSAR)
  * [`CRC8_BLUETOOTH`](crc/catalog.md#amaranth.lib.crc.catalog.CRC8_BLUETOOTH)
  * [`CRC8_CDMA2000`](crc/catalog.md#amaranth.lib.crc.catalog.CRC8_CDMA2000)
  * [`CRC8_DARC`](crc/catalog.md#amaranth.lib.crc.catalog.CRC8_DARC)
  * [`CRC8_DVB_S2`](crc/catalog.md#amaranth.lib.crc.catalog.CRC8_DVB_S2)
  * [`CRC8_GSM_A`](crc/catalog.md#amaranth.lib.crc.catalog.CRC8_GSM_A)
  * [`CRC8_GSM_B`](crc/catalog.md#amaranth.lib.crc.catalog.CRC8_GSM_B)
  * [`CRC8_HITAG`](crc/catalog.md#amaranth.lib.crc.catalog.CRC8_HITAG)
  * [`CRC8_I_432_1`](crc/catalog.md#amaranth.lib.crc.catalog.CRC8_I_432_1)
  * [`CRC8_ITU`](crc/catalog.md#amaranth.lib.crc.catalog.CRC8_ITU)
  * [`CRC8_I_CODE`](crc/catalog.md#amaranth.lib.crc.catalog.CRC8_I_CODE)
  * [`CRC8_LTE`](crc/catalog.md#amaranth.lib.crc.catalog.CRC8_LTE)
  * [`CRC8_MAXIM_DOW`](crc/catalog.md#amaranth.lib.crc.catalog.CRC8_MAXIM_DOW)
  * [`CRC8_MAXIM`](crc/catalog.md#amaranth.lib.crc.catalog.CRC8_MAXIM)
  * [`CRC8_MIFARE_MAD`](crc/catalog.md#amaranth.lib.crc.catalog.CRC8_MIFARE_MAD)
  * [`CRC8_NRSC_5`](crc/catalog.md#amaranth.lib.crc.catalog.CRC8_NRSC_5)
  * [`CRC8_OPENSAFETY`](crc/catalog.md#amaranth.lib.crc.catalog.CRC8_OPENSAFETY)
  * [`CRC8_ROHC`](crc/catalog.md#amaranth.lib.crc.catalog.CRC8_ROHC)
  * [`CRC8_SAE_J1850`](crc/catalog.md#amaranth.lib.crc.catalog.CRC8_SAE_J1850)
  * [`CRC8_SMBUS`](crc/catalog.md#amaranth.lib.crc.catalog.CRC8_SMBUS)
  * [`CRC8_TECH_3250`](crc/catalog.md#amaranth.lib.crc.catalog.CRC8_TECH_3250)
  * [`CRC8_AES`](crc/catalog.md#amaranth.lib.crc.catalog.CRC8_AES)
  * [`CRC8_ETU`](crc/catalog.md#amaranth.lib.crc.catalog.CRC8_ETU)
  * [`CRC8_WCDMA`](crc/catalog.md#amaranth.lib.crc.catalog.CRC8_WCDMA)
  * [`CRC10_ATM`](crc/catalog.md#amaranth.lib.crc.catalog.CRC10_ATM)
  * [`CRC10_I_610`](crc/catalog.md#amaranth.lib.crc.catalog.CRC10_I_610)
  * [`CRC10_CDMA2000`](crc/catalog.md#amaranth.lib.crc.catalog.CRC10_CDMA2000)
  * [`CRC10_GSM`](crc/catalog.md#amaranth.lib.crc.catalog.CRC10_GSM)
  * [`CRC11_FLEXRAY`](crc/catalog.md#amaranth.lib.crc.catalog.CRC11_FLEXRAY)
  * [`CRC11_UMTS`](crc/catalog.md#amaranth.lib.crc.catalog.CRC11_UMTS)
  * [`CRC12_CDMA2000`](crc/catalog.md#amaranth.lib.crc.catalog.CRC12_CDMA2000)
  * [`CRC12_DECT`](crc/catalog.md#amaranth.lib.crc.catalog.CRC12_DECT)
  * [`CRC12_GSM`](crc/catalog.md#amaranth.lib.crc.catalog.CRC12_GSM)
  * [`CRC12_UMTS`](crc/catalog.md#amaranth.lib.crc.catalog.CRC12_UMTS)
  * [`CRC12_3GPP`](crc/catalog.md#amaranth.lib.crc.catalog.CRC12_3GPP)
  * [`CRC13_BBC`](crc/catalog.md#amaranth.lib.crc.catalog.CRC13_BBC)
  * [`CRC14_DARC`](crc/catalog.md#amaranth.lib.crc.catalog.CRC14_DARC)
  * [`CRC14_GSM`](crc/catalog.md#amaranth.lib.crc.catalog.CRC14_GSM)
  * [`CRC15_CAN`](crc/catalog.md#amaranth.lib.crc.catalog.CRC15_CAN)
  * [`CRC15_MPT1327`](crc/catalog.md#amaranth.lib.crc.catalog.CRC15_MPT1327)
  * [`CRC16_ARC`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_ARC)
  * [`CRC16_IBM`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_IBM)
  * [`CRC16_CDMA2000`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_CDMA2000)
  * [`CRC16_CMS`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_CMS)
  * [`CRC16_DDS_110`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_DDS_110)
  * [`CRC16_DECT_R`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_DECT_R)
  * [`CRC16_DECT_X`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_DECT_X)
  * [`CRC16_DNP`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_DNP)
  * [`CRC16_EN_13757`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_EN_13757)
  * [`CRC16_GENIBUS`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_GENIBUS)
  * [`CRC16_DARC`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_DARC)
  * [`CRC16_EPC`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_EPC)
  * [`CRC16_EPC_C1G2`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_EPC_C1G2)
  * [`CRC16_I_CODE`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_I_CODE)
  * [`CRC16_GSM`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_GSM)
  * [`CRC16_IBM_3740`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_IBM_3740)
  * [`CRC16_AUTOSAR`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_AUTOSAR)
  * [`CRC16_CCITT_FALSE`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_CCITT_FALSE)
  * [`CRC16_IBM_SDLC`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_IBM_SDLC)
  * [`CRC16_ISO_HDLC`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_ISO_HDLC)
  * [`CRC16_ISO_IEC_14443_3_B`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_ISO_IEC_14443_3_B)
  * [`CRC16_X25`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_X25)
  * [`CRC16_ISO_IEC_14443_3_A`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_ISO_IEC_14443_3_A)
  * [`CRC16_KERMIT`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_KERMIT)
  * [`CRC16_BLUETOOTH`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_BLUETOOTH)
  * [`CRC16_CCITT`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_CCITT)
  * [`CRC16_CCITT_TRUE`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_CCITT_TRUE)
  * [`CRC16_V_41_LSB`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_V_41_LSB)
  * [`CRC16_LJ1200`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_LJ1200)
  * [`CRC16_M17`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_M17)
  * [`CRC16_MAXIM_DOW`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_MAXIM_DOW)
  * [`CRC16_MAXIM`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_MAXIM)
  * [`CRC16_MCRF4XX`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_MCRF4XX)
  * [`CRC16_MODBUS`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_MODBUS)
  * [`CRC16_NRSC_5`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_NRSC_5)
  * [`CRC16_OPENSAFETY_A`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_OPENSAFETY_A)
  * [`CRC16_OPENSAFETY_B`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_OPENSAFETY_B)
  * [`CRC16_PROFIBUS`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_PROFIBUS)
  * [`CRC16_IEC_61158_2`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_IEC_61158_2)
  * [`CRC16_RIELLO`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_RIELLO)
  * [`CRC16_SPI_FUJITSU`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_SPI_FUJITSU)
  * [`CRC16_AUG_CCITT`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_AUG_CCITT)
  * [`CRC16_T10_DIF`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_T10_DIF)
  * [`CRC16_TELEDISK`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_TELEDISK)
  * [`CRC16_TMS37157`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_TMS37157)
  * [`CRC16_UMTS`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_UMTS)
  * [`CRC16_BUYPASS`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_BUYPASS)
  * [`CRC16_VERIFONE`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_VERIFONE)
  * [`CRC16_USB`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_USB)
  * [`CRC16_XMODEM`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_XMODEM)
  * [`CRC16_ACORN`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_ACORN)
  * [`CRC16_LTE`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_LTE)
  * [`CRC16_V_41_MSB`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_V_41_MSB)
  * [`CRC16_ZMODEM`](crc/catalog.md#amaranth.lib.crc.catalog.CRC16_ZMODEM)
  * [`CRC17_CAN_FD`](crc/catalog.md#amaranth.lib.crc.catalog.CRC17_CAN_FD)
  * [`CRC21_CAN_FD`](crc/catalog.md#amaranth.lib.crc.catalog.CRC21_CAN_FD)
  * [`CRC24_BLE`](crc/catalog.md#amaranth.lib.crc.catalog.CRC24_BLE)
  * [`CRC24_FLEXRAY_A`](crc/catalog.md#amaranth.lib.crc.catalog.CRC24_FLEXRAY_A)
  * [`CRC24_FLEXRAY_B`](crc/catalog.md#amaranth.lib.crc.catalog.CRC24_FLEXRAY_B)
  * [`CRC24_INTERLAKEN`](crc/catalog.md#amaranth.lib.crc.catalog.CRC24_INTERLAKEN)
  * [`CRC24_LTE_A`](crc/catalog.md#amaranth.lib.crc.catalog.CRC24_LTE_A)
  * [`CRC24_LTE_B`](crc/catalog.md#amaranth.lib.crc.catalog.CRC24_LTE_B)
  * [`CRC24_OPENPGP`](crc/catalog.md#amaranth.lib.crc.catalog.CRC24_OPENPGP)
  * [`CRC24_OS_9`](crc/catalog.md#amaranth.lib.crc.catalog.CRC24_OS_9)
  * [`CRC30_CDMA`](crc/catalog.md#amaranth.lib.crc.catalog.CRC30_CDMA)
  * [`CRC31_PHILIPS`](crc/catalog.md#amaranth.lib.crc.catalog.CRC31_PHILIPS)
  * [`CRC32_AIXM`](crc/catalog.md#amaranth.lib.crc.catalog.CRC32_AIXM)
  * [`CRC32_AUTOSAR`](crc/catalog.md#amaranth.lib.crc.catalog.CRC32_AUTOSAR)
  * [`CRC32_BASE91_D`](crc/catalog.md#amaranth.lib.crc.catalog.CRC32_BASE91_D)
  * [`CRC32_BZIP2`](crc/catalog.md#amaranth.lib.crc.catalog.CRC32_BZIP2)
  * [`CRC32_AAL5`](crc/catalog.md#amaranth.lib.crc.catalog.CRC32_AAL5)
  * [`CRC32_DECT_B`](crc/catalog.md#amaranth.lib.crc.catalog.CRC32_DECT_B)
  * [`CRC32_CD_ROM_EDC`](crc/catalog.md#amaranth.lib.crc.catalog.CRC32_CD_ROM_EDC)
  * [`CRC32_CKSUM`](crc/catalog.md#amaranth.lib.crc.catalog.CRC32_CKSUM)
  * [`CRC32_POSIX`](crc/catalog.md#amaranth.lib.crc.catalog.CRC32_POSIX)
  * [`CRC32_ISCSI`](crc/catalog.md#amaranth.lib.crc.catalog.CRC32_ISCSI)
  * [`CRC32_BASE91_C`](crc/catalog.md#amaranth.lib.crc.catalog.CRC32_BASE91_C)
  * [`CRC32_CASTAGNOLI`](crc/catalog.md#amaranth.lib.crc.catalog.CRC32_CASTAGNOLI)
  * [`CRC32_INTERLAKEN`](crc/catalog.md#amaranth.lib.crc.catalog.CRC32_INTERLAKEN)
  * [`CRC32_ISO_HDLC`](crc/catalog.md#amaranth.lib.crc.catalog.CRC32_ISO_HDLC)
  * [`CRC32_ADCCP`](crc/catalog.md#amaranth.lib.crc.catalog.CRC32_ADCCP)
  * [`CRC32_V_42`](crc/catalog.md#amaranth.lib.crc.catalog.CRC32_V_42)
  * [`CRC32_XZ`](crc/catalog.md#amaranth.lib.crc.catalog.CRC32_XZ)
  * [`CRC32_PKZIP`](crc/catalog.md#amaranth.lib.crc.catalog.CRC32_PKZIP)
  * [`CRC32_ETHERNET`](crc/catalog.md#amaranth.lib.crc.catalog.CRC32_ETHERNET)
  * [`CRC32_JAMCRC`](crc/catalog.md#amaranth.lib.crc.catalog.CRC32_JAMCRC)
  * [`CRC32_MEF`](crc/catalog.md#amaranth.lib.crc.catalog.CRC32_MEF)
  * [`CRC32_MPEG_2`](crc/catalog.md#amaranth.lib.crc.catalog.CRC32_MPEG_2)
  * [`CRC32_XFER`](crc/catalog.md#amaranth.lib.crc.catalog.CRC32_XFER)
  * [`CRC40_GSM`](crc/catalog.md#amaranth.lib.crc.catalog.CRC40_GSM)
  * [`CRC64_ECMA_182`](crc/catalog.md#amaranth.lib.crc.catalog.CRC64_ECMA_182)
  * [`CRC64_GO_ISO`](crc/catalog.md#amaranth.lib.crc.catalog.CRC64_GO_ISO)
  * [`CRC64_MS`](crc/catalog.md#amaranth.lib.crc.catalog.CRC64_MS)
  * [`CRC64_REDIS`](crc/catalog.md#amaranth.lib.crc.catalog.CRC64_REDIS)
  * [`CRC64_WE`](crc/catalog.md#amaranth.lib.crc.catalog.CRC64_WE)
  * [`CRC64_XZ`](crc/catalog.md#amaranth.lib.crc.catalog.CRC64_XZ)
  * [`CRC64_ECMA`](crc/catalog.md#amaranth.lib.crc.catalog.CRC64_ECMA)
  * [`CRC82_DARC`](crc/catalog.md#amaranth.lib.crc.catalog.CRC82_DARC)
