# chipflow.packaging.standard

Standard package definitions for common package types.

This module provides concrete package definitions for:
- Quad packages (QFN, LQFP, TQFP, etc.)
- Bare die packages

## Classes

| [`BareDiePackageDef`](#chipflow.packaging.standard.BareDiePackageDef)   | Definition of a package with pins on four sides.   |
|-------------------------------------------------------------------------|----------------------------------------------------|
| [`QuadPackageDef`](#chipflow.packaging.standard.QuadPackageDef)         | Definition of a quad flat package.                 |

## Module Contents

### *class* chipflow.packaging.standard.BareDiePackageDef

Bases: [`chipflow.packaging.base.LinearAllocPackageDef`](../base/index.md#chipflow.packaging.base.LinearAllocPackageDef)

Definition of a package with pins on four sides.

Sides are labeled north, south, east, west with an integer
identifier within each side, indicating pads across or down
from top-left corner.

This is typically used for direct die attach without traditional
packaging.

Attributes:
: width: Number of die pads on top and bottom sides
  height: Number of die pads on left and right sides

#### model_post_init(\_\_context)

Initialize pin ordering

#### *property* bringup_pins *: [chipflow.packaging.pins.BringupPins](../pins/index.md#chipflow.packaging.pins.BringupPins)*

Bringup pins for bare die package

* **Return type:**
  [chipflow.packaging.pins.BringupPins](../pins/index.md#chipflow.packaging.pins.BringupPins)

### *class* chipflow.packaging.standard.QuadPackageDef

Bases: [`chipflow.packaging.base.LinearAllocPackageDef`](../base/index.md#chipflow.packaging.base.LinearAllocPackageDef)

Definition of a quad flat package.

A package with ‘width’ pins on the top and bottom and ‘height’
pins on the left and right. Pins are numbered anti-clockwise
from the top left pin.

This includes many common package types:

- QFN: quad flat no-leads (bottom pad = substrate)
- BQFP: bumpered quad flat package
- BQFPH: bumpered quad flat package with heat spreader
- CQFP: ceramic quad flat package
- EQFP: plastic enhanced quad flat package
- FQFP: fine pitch quad flat package
- LQFP: low profile quad flat package
- MQFP: metric quad flat package
- NQFP: near chip-scale quad flat package
- SQFP: small quad flat package
- TQFP: thin quad flat package
- VQFP: very small quad flat package
- VTQFP: very thin quad flat package
- TDFN: thin dual flat no-lead package
- CERQUAD: low-cost CQFP

Attributes:
: width: The number of pins across on the top and bottom edges
  height: The number of pins high on the left and right edges

#### model_post_init(\_\_context)

Initialize pin ordering

#### *property* bringup_pins *: [chipflow.packaging.pins.BringupPins](../pins/index.md#chipflow.packaging.pins.BringupPins)*

Bringup pins for quad package

* **Return type:**
  [chipflow.packaging.pins.BringupPins](../pins/index.md#chipflow.packaging.pins.BringupPins)
