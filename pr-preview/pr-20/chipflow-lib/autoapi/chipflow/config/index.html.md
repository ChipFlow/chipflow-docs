# chipflow.config

Configuration management for ChipFlow.

This module provides configuration models and parsing functionality
for chipflow.toml configuration files.

## Submodules

* [chipflow.config.parser](parser/index.md)

## Classes

| [`Process`](#chipflow.config.Process)                   | IC manufacturing process                         |
|---------------------------------------------------------|--------------------------------------------------|
| [`VoltageRange`](#chipflow.config.VoltageRange)         | Models a voltage range for a power domain or IO. |
| [`SiliconConfig`](#chipflow.config.SiliconConfig)       | Configuration for silicon in chipflow.toml.      |
| [`SimulationConfig`](#chipflow.config.SimulationConfig) | Configuration for simulation settings.           |
| [`CompilerConfig`](#chipflow.config.CompilerConfig)     | Configuration for compiler toolchain.            |
| [`SoftwareConfig`](#chipflow.config.SoftwareConfig)     | Configuration for software build settings.       |
| [`TestConfig`](#chipflow.config.TestConfig)             | Configuration for test settings.                 |
| [`ChipFlowConfig`](#chipflow.config.ChipFlowConfig)     | Root configuration for chipflow.toml.            |
| [`Config`](#chipflow.config.Config)                     | Root configuration model for chipflow.toml.      |

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

### *class* chipflow.config.SimulationConfig

Bases: `pydantic.BaseModel`

Configuration for simulation settings.

### *class* chipflow.config.CompilerConfig

Bases: `pydantic.BaseModel`

Configuration for compiler toolchain.

### *class* chipflow.config.SoftwareConfig

Bases: `pydantic.BaseModel`

Configuration for software build settings.

### *class* chipflow.config.TestConfig

Bases: `pydantic.BaseModel`

Configuration for test settings.

### *class* chipflow.config.ChipFlowConfig

Bases: `pydantic.BaseModel`

Root configuration for chipflow.toml.

### *class* chipflow.config.Config

Bases: `pydantic.BaseModel`

Root configuration model for chipflow.toml.
