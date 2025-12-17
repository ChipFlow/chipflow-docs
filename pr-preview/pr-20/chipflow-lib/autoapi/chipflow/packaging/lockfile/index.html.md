# chipflow.packaging.lockfile

Lock file models for pin assignments.

The lock file captures the complete pin allocation for a design,
allowing pins to be locked and reused across design iterations.

## Classes

| [`Package`](#chipflow.packaging.lockfile.Package)   | Serializable identifier for a defined packaging option.   |
|-----------------------------------------------------|-----------------------------------------------------------|
| [`LockFile`](#chipflow.packaging.lockfile.LockFile) | Representation of a pin lock file.                        |

## Module Contents

### *class* chipflow.packaging.lockfile.Package

Bases: `pydantic.BaseModel`

Serializable identifier for a defined packaging option.

Attributes:
: package_type: Package type (discriminated union of all PackageDef types)

### *class* chipflow.packaging.lockfile.LockFile

Bases: `pydantic.BaseModel`

Representation of a pin lock file.

The lock file stores the complete pin allocation for a design,
allowing pins to remain consistent across design iterations.

Attributes:
: process: Semiconductor process being used
  package: Information about the physical package
  port_map: Mapping of components to interfaces to ports
  metadata: Amaranth metadata, for reference
