# chipflow.packaging.grid_array

Grid array package definitions.

This module provides package definitions for grid array packages
like BGA (Ball Grid Array) and PGA (Pin Grid Array) types.

## Classes

| [`GAPin`](#chipflow.packaging.grid_array.GAPin)               | Pin identifier for grid array packages (row letter, column number)   |
|---------------------------------------------------------------|----------------------------------------------------------------------|
| [`GALayout`](#chipflow.packaging.grid_array.GALayout)         | Layout type for grid array packages                                  |
| [`GAPackageDef`](#chipflow.packaging.grid_array.GAPackageDef) | Definition of a grid array package.                                  |

## Module Contents

### *class* chipflow.packaging.grid_array.GAPin

Bases: `NamedTuple`

Pin identifier for grid array packages (row letter, column number)

### *class* chipflow.packaging.grid_array.GALayout

Bases: [`enum.StrEnum`](https://docs.python.org/3/library/enum.html#enum.StrEnum)

Layout type for grid array packages

### *class* chipflow.packaging.grid_array.GAPackageDef

Bases: [`chipflow.packaging.base.BasePackageDef`](../base/index.md#chipflow.packaging.base.BasePackageDef)[[`GAPin`](#chipflow.packaging.grid_array.GAPin)]

Definition of a grid array package.

Pins or pads are arranged in a regular array of ‘width’ by ‘height’.
Pins are identified by a 2-tuple of (row, column), counting from
the bottom left when looking at the underside of the package.
Rows are identified by letter (A-Z), columns by number.

The grid may be complete or have missing pins (e.g., center cutout).

This includes many package types:

- CPGA: Ceramic Pin Grid Array
- OPGA: Organic Pin Grid Array
- SPGA: Staggered Pin Grid Array
- CABGA: Chip Array Ball Grid Array
- CBGA/PBGA: Ceramic/Plastic Ball Grid Array
- CTBGA: Thin Chip Array Ball Grid Array
- CVBGA: Very Thin Chip Array Ball Grid Array
- DSBGA: Die-Size Ball Grid Array
- FBGA: Fine Ball Grid Array / Fine Pitch Ball Grid Array
- FCmBGA: Flip Chip Molded Ball Grid Array
- LBGA: Low-Profile Ball Grid Array
- LFBGA: Low-Profile Fine-Pitch Ball Grid Array
- MBGA: Micro Ball Grid Array
- MCM-PBGA: Multi-Chip Module Plastic Ball Grid Array
- nFBGA: New Fine Ball Grid Array
- SuperBGA (SBGA): Super Ball Grid Array
- TABGA: Tape Array BGA
- TBGA: Thin BGA
- TEPBGA: Thermally Enhanced Plastic Ball Grid Array
- TFBGA: Thin and Fine Ball Grid Array
- UFBGA/UBGA: Ultra Fine Ball Grid Array
- VFBGA: Very Fine Pitch Ball Grid Array
- WFBGA: Very Very Thin Profile Fine Pitch Ball Grid Array
- wWLB: Embedded Wafer Level Ball Grid Array

Attributes:
: width: Number of columns
  height: Number of rows
  layout_type: Pin layout configuration
  channel_width: For PERIMETER/CHANNEL/ISLAND layouts
  island_width: For ISLAND layout, size of center island
  missing_pins: Specific pins to exclude (overrides layout)
  additional_pins: Specific pins to add (overrides layout)

#### model_post_init(\_\_context)

Initialize pin ordering

#### *property* bringup_pins *: [chipflow.packaging.pins.BringupPins](../pins/index.md#chipflow.packaging.pins.BringupPins)*

Bringup pins for grid array package

* **Return type:**
  [chipflow.packaging.pins.BringupPins](../pins/index.md#chipflow.packaging.pins.BringupPins)

#### *property* heartbeat *: Dict[[int](https://docs.python.org/3/library/functions.html#int), [GAPin](#chipflow.packaging.grid_array.GAPin)]*

Numbered set of heartbeat pins for the package

* **Return type:**
  Dict[[int](https://docs.python.org/3/library/functions.html#int), [GAPin](#chipflow.packaging.grid_array.GAPin)]
