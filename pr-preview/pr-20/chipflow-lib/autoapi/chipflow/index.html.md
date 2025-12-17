# chipflow

Chipflow library

This is the main entry point for the ChipFlow library, providing tools for
building ASIC designs using the Amaranth HDL framework.

## Submodules

* [chipflow.auth](auth/index.md)
* [chipflow.auth_command](auth_command/index.md)
* [chipflow.common](common/index.md)
* [chipflow.config](config/index.md)
* [chipflow.packages](packages/index.md)
* [chipflow.packaging](packaging/index.md)
* [chipflow.platform](platform/index.md)
* [chipflow.utils](utils/index.md)

## Exceptions

| [`ChipFlowError`](#chipflow.ChipFlowError)   | Base exception for ChipFlow errors   |
|----------------------------------------------|--------------------------------------|

## Functions

| [`ensure_chipflow_root`](#chipflow.ensure_chipflow_root)()   | Ensure CHIPFLOW_ROOT environment variable is set and return its path.   |
|--------------------------------------------------------------|-------------------------------------------------------------------------|

## Package Contents

### *exception* chipflow.ChipFlowError

Bases: [`Exception`](https://docs.python.org/3/library/exceptions.html#Exception)

Base exception for ChipFlow errors

### chipflow.ensure_chipflow_root()

Ensure CHIPFLOW_ROOT environment variable is set and return its path.

If CHIPFLOW_ROOT is not set, sets it to the current working directory.
Also ensures the root is in sys.path.

Returns:
: Path to the chipflow root directory

* **Return type:**
  [pathlib.Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)
