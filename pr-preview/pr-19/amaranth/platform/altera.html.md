# Altera

The [`AlteraPlatform`](#amaranth.vendor.AlteraPlatform) class provides a base platform to support Altera toolchains.

The Quartus and Mistral toolchains are supported.

### *class* amaranth.vendor.AlteraPlatform(\*, toolchain='Quartus')

### Quartus toolchain

Required tools:
: * `quartus_map`
  * `quartus_fit`
  * `quartus_asm`
  * `quartus_sta`

The environment is populated by running the script specified in the environment variable
`AMARANTH_ENV_QUARTUS`, if present.

Available overrides:
: * `add_settings`: inserts commands at the end of the QSF file.
  * `add_constraints`: inserts commands at the end of the SDC file.
  * `nproc`: sets the number of cores used by all tools.
  * `quartus_map_opts`: adds extra options for `quartus_map`.
  * `quartus_fit_opts`: adds extra options for `quartus_fit`.
  * `quartus_asm_opts`: adds extra options for `quartus_asm`.
  * `quartus_sta_opts`: adds extra options for `quartus_sta`.

Build products:
: * `*.rpt`: toolchain reports.
  * `{{name}}.sof`: bitstream as SRAM object file.
  * `{{name}}.rbf`: bitstream as raw binary file.

### Mistral toolchain

Required tools:
: * `yosys`
  * `nextpnr-mistral`

The environment is populated by running the script specified in the environment variable
`AMARANTH_ENV_MISTRAL`, if present.

> * `verbose`: enables logging of informational messages to standard error.
> * `read_verilog_opts`: adds options for `read_verilog` Yosys command.
> * `synth_opts`: adds options for `synth_intel_alm` Yosys command.
> * `script_after_read`: inserts commands after `read_rtlil` in Yosys script.
> * `script_after_synth`: inserts commands after `synth_intel_alm` in Yosys script.
> * `yosys_opts`: adds extra options for `yosys`.
> * `nextpnr_opts`: adds extra options for `nextpnr-mistral`.
