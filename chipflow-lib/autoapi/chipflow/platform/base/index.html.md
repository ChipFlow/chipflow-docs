# chipflow.platform.base

Base classes and utilities for ChipFlow platform steps.

## Classes

| [`StepBase`](#chipflow.platform.base.StepBase)   | Base class for ChipFlow build steps.   |
|--------------------------------------------------|----------------------------------------|

## Functions

| [`setup_amaranth_tools`](#chipflow.platform.base.setup_amaranth_tools)()   | Configure environment for Amaranth/WASM tools.   |
|----------------------------------------------------------------------------|--------------------------------------------------|

## Module Contents

### chipflow.platform.base.setup_amaranth_tools()

Configure environment for Amaranth/WASM tools.

### *class* chipflow.platform.base.StepBase(config={})

Bases: [`abc.ABC`](https://docs.python.org/3/library/abc.html#abc.ABC)

Base class for ChipFlow build steps.

#### build_cli_parser(parser)

Build the cli parser for this step

#### run_cli(args)

Called when this step’s is used from chipflow command

#### build(\*args)

builds the design
