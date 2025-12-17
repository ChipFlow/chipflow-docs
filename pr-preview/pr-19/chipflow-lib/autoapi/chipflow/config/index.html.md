# chipflow.config

Configuration management for ChipFlow.

This module provides configuration models and parsing functionality
for chipflow.toml configuration files.

## Submodules

* [chipflow.config.parser](parser/index.md)

## Classes

| [`Process`](#chipflow.config.Process)               | IC manufacturing process                         |
|-----------------------------------------------------|--------------------------------------------------|
| [`VoltageRange`](#chipflow.config.VoltageRange)     | Models a voltage range for a power domain or IO. |
| [`SiliconConfig`](#chipflow.config.SiliconConfig)   | Configuration for silicon in chipflow.toml.      |
| [`ChipFlowConfig`](#chipflow.config.ChipFlowConfig) | Root configuration for chipflow.toml.            |
| [`Config`](#chipflow.config.Config)                 | Root configuration model for chipflow.toml.      |

## Package Contents

### *class* chipflow.config.Process(\*args, \*\*kwds)

Bases: [`enum.Enum`](https://docs.python.org/3/library/enum.html#enum.Enum)

IC manufacturing process

### *class* chipflow.config.VoltageRange

Bases: `chipflow.serialization.SelectiveSerializationModel`

Models a voltage range for a power domain or IO.

Optional fields (min, max, typical) are omitted from serialization when None.

### *class* chipflow.config.SiliconConfig

Bases: `pydantic.BaseModel`

Configuration for silicon in chipflow.toml.

### *class* chipflow.config.ChipFlowConfig

Bases: `pydantic.BaseModel`

Root configuration for chipflow.toml.

### *class* chipflow.config.Config

Bases: `pydantic.BaseModel`

Root configuration model for chipflow.toml.
