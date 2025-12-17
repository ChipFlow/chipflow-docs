# chipflow.utils

Core utility functions for ChipFlow

This module provides core utilities used throughout the chipflow library.

## Exceptions

| [`ChipFlowError`](#chipflow.utils.ChipFlowError)   | Base exception for ChipFlow errors   |
|----------------------------------------------------|--------------------------------------|

## Functions

| [`get_cls_by_reference`](#chipflow.utils.get_cls_by_reference)(reference, context)   | Dynamically import and return a class by its module:class reference string.       |
|--------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| [`ensure_chipflow_root`](#chipflow.utils.ensure_chipflow_root)()                     | Ensure CHIPFLOW_ROOT environment variable is set and return its path.             |
| [`get_src_loc`](#chipflow.utils.get_src_loc)([src_loc_at])                           | Get the source location (filename, line number) of the caller.                    |
| [`compute_invert_mask`](#chipflow.utils.compute_invert_mask)(invert_list)            | Compute a bit mask for signal inversion from a list of boolean invert flags.      |
| [`top_components`](#chipflow.utils.top_components)(config)                           | Return the top level components for the design, as configured in `chipflow.toml`. |
| [`get_software_builds`](#chipflow.utils.get_software_builds)(m, component)           | Extract software build information from a component's interfaces.                 |

## Module Contents

### *exception* chipflow.utils.ChipFlowError

Bases: [`Exception`](https://docs.python.org/3/library/exceptions.html#Exception)

Base exception for ChipFlow errors

### chipflow.utils.get_cls_by_reference(reference, context)

Dynamically import and return a class by its module:class reference string.

Args:
: reference: String in format “module.path:ClassName”
  context: Description of where this reference came from (for error messages)

Returns:
: The class object

Raises:
: ChipFlowError: If module or class cannot be found

* **Parameters:**
  * **reference** ([*str*](https://docs.python.org/3/library/stdtypes.html#str))
  * **context** ([*str*](https://docs.python.org/3/library/stdtypes.html#str))

### chipflow.utils.ensure_chipflow_root()

Ensure CHIPFLOW_ROOT environment variable is set and return its path.

If CHIPFLOW_ROOT is not set, sets it to the current working directory.
Also ensures the root is in sys.path.

Returns:
: Path to the chipflow root directory

* **Return type:**
  [pathlib.Path](https://docs.python.org/3/library/pathlib.html#pathlib.Path)

### chipflow.utils.get_src_loc(src_loc_at=0)

Get the source location (filename, line number) of the caller.

Args:
: src_loc_at: Number of frames to go back (0 = immediate caller)

Returns:
: Tuple of (filename, line_number)

* **Parameters:**
  **src_loc_at** ([*int*](https://docs.python.org/3/library/functions.html#int))

### chipflow.utils.compute_invert_mask(invert_list)

Compute a bit mask for signal inversion from a list of boolean invert flags.

Args:
: invert_list: List of booleans indicating which bits should be inverted

Returns:
: Integer mask where set bits indicate positions to invert

### chipflow.utils.top_components(config)

Return the top level components for the design, as configured in `chipflow.toml`.

Args:
: config: The parsed chipflow configuration

Returns:
: Dictionary mapping component names to instantiated Component objects

Raises:
: ChipFlowError: If component references are invalid or instantiation fails

* **Parameters:**
  **config** (*chipflow.config.models.Config*)
* **Return type:**
  Dict[[str](https://docs.python.org/3/library/stdtypes.html#str), [amaranth.lib.wiring.Component](../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Component)]

### chipflow.utils.get_software_builds(m, component)

Extract software build information from a component’s interfaces.

Args:
: m: Module containing the component
  component: Name of the component

Returns:
: Dictionary of interface names to SoftwareBuild objects

* **Parameters:**
  **component** ([*str*](https://docs.python.org/3/library/stdtypes.html#str))
