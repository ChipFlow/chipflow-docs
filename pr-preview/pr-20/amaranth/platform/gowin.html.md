# Gowin

The [`GowinPlatform`](#amaranth.vendor.GowinPlatform) class provides a base platform to support Gowin toolchains.

The Apicula and Gowin toolchains are supported.

### *class* amaranth.vendor.GowinPlatform(\*, toolchain='Apicula')

### Apicula toolchain

Required tools:
: * `yosys`
  * `nextpnr-gowin`
  * `gowin_pack`

The environment is populated by running the script specified in the environment variable
`AMARANTH_ENV_APICULA`, if present.

Build products:
: * `{{name}}.fs`: binary bitstream.

### Gowin toolchain

Required tools:
: * `gw_sh`

The environment is populated by running the script specified in the environment variable
`AMARANTH_ENV_GOWIN`, if present.

Build products:
: * `{{name}}.fs`: binary bitstream.
