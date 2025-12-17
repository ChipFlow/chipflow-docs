# Intro to `chipflow.toml`

The `chipflow.toml` file provides configuration for your design with the ChipFlow platform.

Let’s start with a typical example:

```toml
[chipflow]
project_name = "test-chip"

[chipflow.top]
soc = "my_design.design:MySoC"

[chipflow.silicon]
process = "gf130bcd"
package = "pga144"
```

<!-- # Assert that example-chipflow.toml matches the current config schema. If
# this test fails, then its likely that the content in this file will need
# to be updated.
from chipflow.config.parser import _parse_config_file
_parse_config_file("docs/example-chipflow.toml") -->

## `[chipflow]` table

Required

The top level configuration for inputs to the ChipFlow tools.

# project_name

Required

The `project_name` is a human-readable identifier for this project. If not set, the tool and library will use the project name configured in `pyproject.toml`.

```TOML
[chipflow]
project_name = 'my_project'
```

# clock_domains

Optional

A list of top-level clock domains for your design. If omitted, defaults to the Amaranth default `sync`, and sync is always assumed to be the name of the core clock for bringup.

```TOML
[chipflow]
clock_domains = ['sync', 'peripheral']
```

## `[chipflow.top]` table

Required

This section outlines the design modules that need to be instantiated.
A new top module will be automatically generated, incorporating all specified modules along with their interfaces.
Each entry follows the format <instance name> = <module class path>.

The instance name is the name the python object will be given in your design, and the [module class path](#term-module-class-path)

```TOML
[chipflow.top]
soc = "my_design.design:MySoC"
```

<a id="term-module-class-path"></a>

module class path
: The module class path offers a way to locate Python objects as entry points.
  It consists of a module’s [qualified name](https://docs.python.org/3/glossary.html#term-qualified-name) followed by a colon (:) and then the [qualified name](https://docs.python.org/3/glossary.html#term-qualified-name) of the class within that module.

<a id="chipflow-toml-steps"></a>

## `[chipflow.steps]` table

Optional

The `steps` section allows overriding or addition to the standard steps available from chipflow.

For example, if you want to override the standard silicon preparation step, you could derive from `chipflow.steps.silicon.SiliconStep`, add your custom functionality
and add the following to your chipflow.toml, with the appropriate [module class path](#term-module-class-path):

```TOML
[chipflow.steps]
silicon = "my_design.steps.silicon:SiliconStep"
```

You probably won’t need to change these if you’re starting from an example repository.

## `[chipflow.silicon]`

Required

The `silicon` section sets the Foundry `process` (i.e. PDK) that we are targeting for manufacturing, and the physical `package` (including pad ring) we want to place our design inside.

You’ll choose the `process` and `package` based in the requirements of your design.

```TOML
[chipflow.silicon]
process = "ihp_sg13g2"
package = "pga144"
```

# process

Required

Foundry process to use

| Process<br/><br/><br/><br/>   | Supported<br/><br/><br/>pad rings<br/><br/>   | Notes<br/><br/><br/><br/>   |
|-------------------------------|-----------------------------------------------|-----------------------------|
| sky130                        | caravel                                       | Skywater 130nm              |
| gf180                         | caravel                                       | GlobalFoundries 180nm       |
| gf130bcd                      | pga144                                        | GlobalFoundries 130nm BCD   |
| ihp_sg13g2                    | pga144                                        | IHP SG13G2 130nm SiGe       |

# package

Required

The form of IC packaging to use

| Pad ring                          | Pad count                 | Pad locations             | Notes                                                                                                            |
|-----------------------------------|---------------------------|---------------------------|------------------------------------------------------------------------------------------------------------------|
|                                   |                           |                           |                                                                                                                  |
| pga144                            | 144                       | `1` … `144`               |                                                                                                                  |
| TBA<br/><br/><br/><br/><br/><br/> | <br/><br/><br/><br/><br/> | <br/><br/><br/><br/><br/> | If you require a different<br/><br/><br/>pad ring, then please contact<br/><br/><br/>customer support.<br/><br/> |

## Power connections

The package definition provides default locations for pins needed for bringup and test, like core power, ground, clock and reset, along with JTAG.

These can be determined by calling BasePackageDef.bringup_pins.

For ports that require their own power lines, you can set `allocate_power` and `power_voltage` in their IOSignature.

<a id="term-loc"></a>

loc
: This is the physical location of the pad on your chosen pad ring. How these are indexed varies by the pad ring.

<a id="term-type"></a>

type
: The [type](#term-type) for each pad can be set to one of [clock](#term-clock) or [reset](#term-reset).

<a id="term-clock"></a>

clock
: External clock input.

<a id="term-reset"></a>

reset
: External reset input.
