# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ChipFlow is a platform for designing and building hardware systems, particularly System-on-Chips (SoCs), using Python. This repository contains documentation for the ChipFlow ecosystem, which includes:

- Hardware description libraries (Amaranth HDL)
- Support for SoC design (amaranth-soc)
- ChipFlow-specific libraries and platforms
- Example designs (minimal SoC, MCU SoC)

## Build Commands

- **Install dependencies**: `pdm install`
- **Build documentation**: `pdm run docs`
- **Auto-rebuild documentation**: `pdm run autodocs`
- **View documentation**: Visit http://localhost:8000 when running autodocs

## Testing

- **Python tests**: `pytest`
- **Run specific test**: `pytest tests/test_file.py::test_function_name`

## Code Style Guidelines

- **Python**: PEP-8 style, Python 3.10+
- **Linting**: `ruff check .`
- **Type checking**: `pyright`

## Repository Structure

- **docs/source/**: Documentation source files in reStructuredText format
- **vendor/**: Cloned repositories for documentation integration
  - amaranth: Hardware description library
  - amaranth-soc: SoC design library
  - chipflow-lib: ChipFlow platform libraries
- **chipflow-examples/**: Example ChipFlow designs
  - minimal/: Minimal SoC with RISC-V core
  - mcu_soc/: MCU-style SoC with peripherals

## Documentation Management

The `copy-docs.sh` script clones and integrates documentation from:
- amaranth-lang/amaranth
- chipflow/amaranth-soc
- chipflow/chipflow-lib

Documentation is built using Sphinx with extensions for:
- Multi-project documentation
- API documentation
- Custom styling
- Interactive elements