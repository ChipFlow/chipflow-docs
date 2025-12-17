# Quicklogic

The [`QuicklogicPlatform`](#amaranth.vendor.QuicklogicPlatform) class provides a base platform to support Quicklogic toolchains.

The Symbiflow toolchain is supported.

### *class* amaranth.vendor.QuicklogicPlatform

### Symbiflow toolchain

Required tools:
: * `symbiflow_synth`
  * `symbiflow_pack`
  * `symbiflow_place`
  * `symbiflow_route`
  * `symbiflow_write_fasm`
  * `symbiflow_write_bitstream`

The environment is populated by running the script specified in the environment variable
`AMARANTH_ENV_QLSYMBIFLOW`, if present.

Available overrides:
: * `add_constraints`: inserts commands in XDC file.
