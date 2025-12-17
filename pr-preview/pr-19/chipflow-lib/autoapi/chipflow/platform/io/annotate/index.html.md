# chipflow.platform.io.annotate

Amaranth annotation utilities for ChipFlow.

## Functions

| [`submodule_metadata`](#chipflow.platform.io.annotate.submodule_metadata)(fragment, component_name[, recursive])   | Generator that finds `component_name` in `fragment` and yields metadata.   |
|--------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------|

## Module Contents

### chipflow.platform.io.annotate.submodule_metadata(fragment, component_name, recursive=False)

Generator that finds `component_name` in `fragment` and yields metadata.

Yields the `wiring.Component` instances of that component’s submodule, along
with their names and metadata.

Can only be run once for a given component (or its children).

Args:
: fragment: The fragment to search in.
  component_name: The name of the component to find.
  recursive: If True, name is a tuple of the hierarchy of names. Otherwise,
  <br/>
  > name is the string name of the first level component.

Yields:
: Tuple of (component, name, metadata) for each submodule.

* **Parameters:**
  * **fragment** (*amaranth.Fragment*)
  * **component_name** ([*str*](https://docs.python.org/3/library/stdtypes.html#str))
* **Return type:**
  [collections.abc.Generator](https://docs.python.org/3/library/collections.abc.html#collections.abc.Generator)[Tuple[[amaranth.lib.wiring.Component](../../../../../../amaranth/stdlib/wiring.md#amaranth.lib.wiring.Component), [str](https://docs.python.org/3/library/stdtypes.html#str) | [tuple](https://docs.python.org/3/library/stdtypes.html#tuple), [dict](https://docs.python.org/3/library/stdtypes.html#dict)]]
