# chipflow.packaging.port_desc

Port description models for pin allocation.

This module provides models for describing port-to-pin mappings
and managing the overall port map for an IC package.

## Classes

| [`PortDesc`](#chipflow.packaging.port_desc.PortDesc)   | Description of a port and its pin assignment.   |
|--------------------------------------------------------|-------------------------------------------------|
| [`PortMap`](#chipflow.packaging.port_desc.PortMap)     | Mapping of components to interfaces to ports.   |

## Module Contents

### *class* chipflow.packaging.port_desc.PortDesc

Bases: `pydantic.BaseModel`, `Generic`[`chipflow.packaging.pins.Pin`]

Description of a port and its pin assignment.

Attributes:
: type: Type of port (e.g., ‘io’, ‘clock’, ‘reset’, ‘power’, ‘heartbeat’)
  pins: List of pins assigned to this port, or None if not yet allocated
  port_name: Name of the port
  iomodel: IO model configuration for this port

#### *property* width

Width of the port (number of pins)

#### *property* direction

Direction of the port

#### *property* invert *: [collections.abc.Iterable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[bool](https://docs.python.org/3/library/functions.html#bool)] | [None](https://docs.python.org/3/library/constants.html#None)*

Inversion settings for port wires

* **Return type:**
  [collections.abc.Iterable](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable)[[bool](https://docs.python.org/3/library/functions.html#bool)] | None

### *class* chipflow.packaging.port_desc.PortMap

Bases: `pydantic.BaseModel`

Mapping of components to interfaces to ports.

This represents the complete pin allocation for an IC package,
organized hierarchically by component and interface.

#### get_ports(component, interface)

Get ports for a specific component and interface.

Args:
: component: Component name
  interface: Interface name

Returns:
: Dictionary of port names to PortDesc, or None if not found

* **Parameters:**
  * **component** ([*str*](https://docs.python.org/3/library/stdtypes.html#str))
  * **interface** ([*str*](https://docs.python.org/3/library/stdtypes.html#str))
* **Return type:**
  [Interface](../../../../../amaranth-soc/csr/bus.md#amaranth_soc.csr.bus.Interface) | None

#### get_clocks()

Get all clock ports in the port map

* **Return type:**
  List[[PortDesc](#chipflow.packaging.port_desc.PortDesc)]

#### get_resets()

Get all reset ports in the port map

* **Return type:**
  List[[PortDesc](#chipflow.packaging.port_desc.PortDesc)]
