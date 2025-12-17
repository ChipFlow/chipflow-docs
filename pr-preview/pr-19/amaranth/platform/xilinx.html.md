# Xilinx

The [`XilinxPlatform`](#amaranth.vendor.XilinxPlatform) class provides a base platform to support Xilinx toolchains.

The ISE, Vivado, and Symbiflow toolchains are supported.

### *class* amaranth.vendor.XilinxPlatform(\*, toolchain=None)

### Vivado toolchain

Required tools:
: * `vivado`

The environment is populated by running the script specified in the environment variable
`AMARANTH_ENV_VIVADO`, if present.

Available overrides:
: * `script_after_read`: inserts commands after `read_xdc` in Tcl script.
  * `synth_design_opts`: sets options for `synth_design`.
  * `script_after_synth`: inserts commands after `synth_design` in Tcl script.
  * `script_after_place`: inserts commands after `place_design` in Tcl script.
  * `script_after_route`: inserts commands after `route_design` in Tcl script.
  * `script_before_bitstream`: inserts commands before `write_bitstream` in Tcl script.
  * `script_after_bitstream`: inserts commands after `write_bitstream` in Tcl script.
  * `add_constraints`: inserts commands in XDC file.
  * `vivado_opts`: adds extra options for `vivado`.

Build products:
: * `{{name}}.log`: Vivado log.
  * `{{name}}_timing_synth.rpt`: Vivado report.
  * `{{name}}_utilization_hierarchical_synth.rpt`: Vivado report.
  * `{{name}}_utilization_synth.rpt`: Vivado report.
  * `{{name}}_utilization_hierarchical_place.rpt`: Vivado report.
  * `{{name}}_utilization_place.rpt`: Vivado report.
  * `{{name}}_io.rpt`: Vivado report.
  * `{{name}}_control_sets.rpt`: Vivado report.
  * `{{name}}_clock_utilization.rpt`:  Vivado report.
  * `{{name}}_route_status.rpt`: Vivado report.
  * `{{name}}_drc.rpt`: Vivado report.
  * `{{name}}_methodology.rpt`: Vivado report.
  * `{{name}}_timing.rpt`: Vivado report.
  * `{{name}}_power.rpt`: Vivado report.
  * `{{name}}_route.dcp`: Vivado design checkpoint.
  * `{{name}}.bit`: binary bitstream with metadata.
  * `{{name}}.bin`: binary bitstream.

### ISE toolchain

Required tools:
: * `xst`
  * `ngdbuild`
  * `map`
  * `par`
  * `bitgen`

The environment is populated by running the script specified in the environment variable
`AMARANTH_ENV_ISE`, if present.

Available overrides:
: * `script_after_run`: inserts commands after `run` in XST script.
  * `add_constraints`: inserts commands in UCF file.
  * `xst_opts`: adds extra options for `xst`.
  * `ngdbuild_opts`: adds extra options for `ngdbuild`.
  * `map_opts`: adds extra options for `map`.
  * `par_opts`: adds extra options for `par`.
  * `bitgen_opts`: adds extra and overrides default options for `bitgen`;
    default options: `-g Compress`.

Build products:
: * `{{name}}.srp`: synthesis report.
  * `{{name}}.ngc`: synthesized RTL.
  * `{{name}}.bld`: NGDBuild log.
  * `{{name}}.ngd`: design database.
  * `{{name}}_map.map`: MAP log.
  * `{{name}}_map.mrp`: mapping report.
  * `{{name}}_map.ncd`: mapped netlist.
  * `{{name}}.pcf`: physical constraints.
  * `{{name}}_par.par`: PAR log.
  * `{{name}}_par_pad.txt`: I/O usage report.
  * `{{name}}_par.ncd`: place and routed netlist.
  * `{{name}}.drc`: DRC report.
  * `{{name}}.bgn`: BitGen log.
  * `{{name}}.bit`: binary bitstream with metadata.
  * `{{name}}.bin`: raw binary bitstream.

### Symbiflow toolchain

Required tools:
: * `symbiflow_synth`
  * `symbiflow_pack`
  * `symbiflow_place`
  * `symbiflow_route`
  * `symbiflow_write_fasm`
  * `symbiflow_write_bitstream`

The environment is populated by running the script specified in the environment variable
`AMARANTH_ENV_SYMBIFLOW`, if present.

Available overrides:
: * `add_constraints`: inserts commands in XDC file.

### Xray toolchain

Required tools:
: * `yosys`
  * `nextpnr-xilinx`
  * `fasm2frames`
  * `xc7frames2bit`

The environment is populated by running the script specified in the environment variable
`AMARANTH_ENV_XRAY`, if present.
