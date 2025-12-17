# chipflow.packaging.utils

Utility functions for package and pin lock management.

## Functions

| [`load_pinlock`](#chipflow.packaging.utils.load_pinlock)()   | Load the pin lock file from the chipflow root.     |
|--------------------------------------------------------------|----------------------------------------------------|
| [`lock_pins`](#chipflow.packaging.utils.lock_pins)([config]) | Create or update the pin lock file for the design. |

## Module Contents

### chipflow.packaging.utils.load_pinlock()

Load the pin lock file from the chipflow root.

Returns:
: LockFile model

Raises:
: ChipFlowError: If lockfile not found or malformed

* **Return type:**
  [chipflow.packaging.lockfile.LockFile](../lockfile/index.md#chipflow.packaging.lockfile.LockFile)

### chipflow.packaging.utils.lock_pins(config=None)

Create or update the pin lock file for the design.

This allocates package pins to component interfaces and writes
the allocation to pins.lock. Will attempt to reuse previous
pin positions if pins.lock already exists.

Args:
: config: Optional Config object. If not provided, will be parsed from chipflow.toml

Raises:
: ChipFlowError: If configuration is invalid or pin allocation fails

* **Parameters:**
  **config** (*Optional* *[*[*chipflow.config.Config*](../../config/index.md#chipflow.config.Config) *]*)
* **Return type:**
  None
