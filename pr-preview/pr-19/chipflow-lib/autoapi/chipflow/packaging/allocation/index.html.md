# chipflow.packaging.allocation

Pin allocation algorithms for package definitions.

This module provides algorithms for allocating pins from available
package pads to component interfaces, including intelligent grouping
and contiguous allocation strategies.

## Exceptions

| [`UnableToAllocate`](#chipflow.packaging.allocation.UnableToAllocate)   | Raised when pin allocation fails   |
|-------------------------------------------------------------------------|------------------------------------|

## Module Contents

### *exception* chipflow.packaging.allocation.UnableToAllocate

Bases: [`chipflow.ChipFlowError`](../../index.md#chipflow.ChipFlowError)

Raised when pin allocation fails
