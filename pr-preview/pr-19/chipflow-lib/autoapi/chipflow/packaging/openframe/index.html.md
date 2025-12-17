# chipflow.packaging.openframe

Openframe package definition.

This module provides the package definition for the ChipFoundry Openframe
harness, commonly used with open-source silicon projects.

## Classes

| [`OFPin`](#chipflow.packaging.openframe.OFPin)                             | Pin identifier for Openframe package                     |
|----------------------------------------------------------------------------|----------------------------------------------------------|
| [`OpenframePackageDef`](#chipflow.packaging.openframe.OpenframePackageDef) | Definition of the ChipFoundry Openframe harness package. |

## Module Contents

### *class* chipflow.packaging.openframe.OFPin

Bases: `NamedTuple`

Pin identifier for Openframe package

### *class* chipflow.packaging.openframe.OpenframePackageDef

Bases: [`chipflow.packaging.base.LinearAllocPackageDef`](../base/index.md#chipflow.packaging.base.LinearAllocPackageDef)

Definition of the ChipFoundry Openframe harness package.

This is a standardized package/carrier used for open-source
silicon projects, particularly with the ChipFoundry chipIgnite
and OpenMPW programs.

Attributes:
: name: Package name (default “openframe”)

#### model_post_init(\_\_context)

Initialize pin ordering from GPIO list

#### *property* bringup_pins *: [chipflow.packaging.pins.BringupPins](../pins/index.md#chipflow.packaging.pins.BringupPins)*

Bringup pins for Openframe package

* **Return type:**
  [chipflow.packaging.pins.BringupPins](../pins/index.md#chipflow.packaging.pins.BringupPins)
