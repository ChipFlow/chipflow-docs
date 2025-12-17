# Lattice

The [`LatticePlatform`](#amaranth.vendor.LatticePlatform) class provides a base platform to support Lattice toolchains (not including iCE40 devices, which are supported by [`SiliconBluePlatform`](siliconblue.md#amaranth.vendor.SiliconBluePlatform)). Currently supported devices include ECP5, MachXO2, MachXO3L, and Nexus.

The Trellis and Diamond toolchains are supported.

### *class* amaranth.vendor.LatticePlatform(\*, toolchain=None)

### Trellis toolchain (ECP5, MachXO2, MachXO3)

Required tools:
: * `yosys`
  * `nextpnr-ecp5` or `nextpnr-machxo2`
  * `ecppack`

The environment is populated by running the script specified in the environment variable
`AMARANTH_ENV_TRELLIS`, if present.

Available overrides:
: * `verbose`: enables logging of informational messages to standard error.
  * `read_verilog_opts`: adds options for `read_verilog` Yosys command.
  * `synth_opts`: adds options for `synth_<family>` Yosys command.
  * `script_after_read`: inserts commands after `read_rtlil` in Yosys script.
  * `script_after_synth`: inserts commands after `synth_<family>` in Yosys script.
  * `yosys_opts`: adds extra options for `yosys`.
  * `nextpnr_opts`: adds extra options for `nextpnr-<family>`.
  * `ecppack_opts`: adds extra options for `ecppack`.
  * `add_preferences`: inserts commands at the end of the LPF file.

Build products:
: * `{{name}}.rpt`: Yosys log.
  * `{{name}}.json`: synthesized RTL.
  * `{{name}}.tim`: nextpnr log.
  * `{{name}}.config`: ASCII bitstream.
  * `{{name}}.bit`: binary bitstream.
  * `{{name}}.svf`: JTAG programming vector.

### Oxide toolchain (Nexus)

Required tools:
: * `yosys`
  * `nextpnr-nexus`
  * `prjoxide`

The environment is populated by running the script specified in the environment variable
`AMARANTH_ENV_OXIDE`, if present.

Available overrides:
: * `verbose`: enables logging of informational messages to standard error.
  * `read_verilog_opts`: adds options for `read_verilog` Yosys command.
  * `synth_opts`: adds options for `synth_nexus` Yosys command.
  * `script_after_read`: inserts commands after `read_rtlil` in Yosys script.
  * `script_after_synth`: inserts commands after `synth_nexus` in Yosys script.
  * `yosys_opts`: adds extra options for `yosys`.
  * `nextpnr_opts`: adds extra options for `nextpnr-nexus`.
  * `prjoxide_opts`: adds extra options for `prjoxide`.
  * `add_preferences`: inserts commands at the end of the PDC file.

Build products:
: * `{{name}}.rpt`: Yosys log.
  * `{{name}}.json`: synthesized RTL.
  * `{{name}}.tim`: nextpnr log.
  * `{{name}}.config`: ASCII bitstream.
  * `{{name}}.bit`: binary bitstream.
  * `{{name}}.xcf`: JTAG programming vector.

### Diamond toolchain (ECP5, MachXO2, MachXO3)

Required tools:
: * `pnmainc`
  * `ddtcmd`

The environment is populated by running the script specified in the environment variable
`AMARANTH_ENV_DIAMOND`, if present. On Linux, diamond_env as provided by Diamond
itself is a good candidate. On Windows, the following script (named `diamond_env.bat`,
for instance) is known to work:

```default
@echo off
set PATH=C:\lscc\diamond\%DIAMOND_VERSION%\bin\nt64;%PATH%
```

Available overrides:
: * `script_project`: inserts commands before `prj_project save` in Tcl script.
  * `script_after_export`: inserts commands after `prj_run Export` in Tcl script.
  * `add_preferences`: inserts commands at the end of the LPF file.
  * `add_constraints`: inserts commands at the end of the XDC file.

Build products:
: * `{{name}}_impl/{{name}}_impl.htm`: consolidated log.
  * `{{name}}.jed`: JEDEC fuse file (MachXO2, MachXO3 only).
  * `{{name}}.bit`: binary bitstream.
  * `{{name}}.svf`: JTAG programming vector (ECP5 only).
  * `{{name}}_flash.svf`: JTAG programming vector for FLASH programming (MachXO2, MachXO3 only).
  * `{{name}}_sram.svf`: JTAG programming vector for SRAM programming (MachXO2, MachXO3 only).

### Radiant toolchain (Nexus)

Required tools:
: * `radiantc`

The environment is populated by running the script specified in the environment variable
`AMARANTH_ENV_RADIANT`, if present. On Linux, radiant_env as provided by Radiant
itself is a good candidate. On Windows, the following script (named `radiant_env.bat`,
for instance) is known to work:

```default
@echo off
set PATH=C:\lscc\radiant\%RADIANT_VERSION%\bin\nt64;%PATH%
```

Available overrides:
: * `script_project`: inserts commands before `prj_save` in Tcl script.
  * `script_after_export`: inserts commands after `prj_run Export` in Tcl script.
  * `add_constraints`: inserts commands at the end of the SDC file.
  * `add_preferences`: inserts commands at the end of the PDC file.

Build products:
: * `{{name}}_impl/{{name}}_impl.htm`: consolidated log.
  * `{{name}}.bit`: binary bitstream.
  * `{{name}}.xcf`: JTAG programming vector. (if using `programmer`)
