# SiliconBlue

The [`SiliconBluePlatform`](#amaranth.vendor.SiliconBluePlatform) class provides a base platform to support Lattice (earlier SiliconBlue) iCE40 devices.

The IceStorm and iCECube2 toolchains are supported.

### *class* amaranth.vendor.SiliconBluePlatform(\*, toolchain='IceStorm')

### IceStorm toolchain

Required tools:
: * `yosys`
  * `nextpnr-ice40`
  * `icepack`

The environment is populated by running the script specified in the environment variable
`AMARANTH_ENV_ICESTORM`, if present.

Available overrides:
: * `verbose`: enables logging of informational messages to standard error.
  * `read_verilog_opts`: adds options for `read_verilog` Yosys command.
  * `synth_opts`: adds options for `synth_ice40` Yosys command.
  * `script_after_read`: inserts commands after `read_rtlil` in Yosys script.
  * `script_after_synth`: inserts commands after `synth_ice40` in Yosys script.
  * `yosys_opts`: adds extra options for `yosys`.
  * `nextpnr_opts`: adds extra options for `nextpnr-ice40`.
  * `add_pre_pack`: inserts commands at the end in pre-pack Python script.
  * `add_constraints`: inserts commands at the end in the PCF file.

Build products:
: * `{{name}}.rpt`: Yosys log.
  * `{{name}}.json`: synthesized RTL.
  * `{{name}}.tim`: nextpnr log.
  * `{{name}}.asc`: ASCII bitstream.
  * `{{name}}.bin`: binary bitstream.

### iCECube2 toolchain

This toolchain comes in two variants: `LSE-iCECube2` and `Synplify-iCECube2`.

Required tools:
: * iCECube2 toolchain
  * `tclsh`

The environment is populated by setting the necessary environment variables based on
`AMARANTH_ENV_ICECUBE2`, which must point to the root of the iCECube2 installation, and
is required.

Available overrides:
: * `verbose`: enables logging of informational messages to standard error.
  * `lse_opts`: adds options for LSE.
  * `script_after_add`: inserts commands after `add_file` in Synplify Tcl script.
  * `script_after_options`: inserts commands after `set_option` in Synplify Tcl script.
  * `add_constraints`: inserts commands in SDC file.
  * `script_after_flow`: inserts commands after `run_sbt_backend_auto` in SBT
    Tcl script.

Build products:
: * `{{name}}_lse.log` (LSE) or `{{name}}_design/{{name}}.htm` (Synplify): synthesis log.
  * `sbt/outputs/router/{{name}}_timing.rpt`: timing report.
  * `{{name}}.edf`: EDIF netlist.
  * `{{name}}.bin`: binary bitstream.
