ChipFlow Examples
=================

The `chipflow-examples <https://github.com/ChipFlow/chipflow-examples>`_ repository contains example designs demonstrating how to build chips using the ChipFlow platform.

These examples show you how to:

- Structure a ChipFlow project
- Configure your design with ``chipflow.toml``
- Run simulations to test your design
- Submit your design to the ChipFlow cloud builder

Available Examples
------------------

**Minimal SoC** (:doc:`minimal`)
   A minimal System-on-Chip with a RISC-V core. This is the simplest starting point for understanding ChipFlow projects.

**MCU SoC** (:doc:`mcu-soc`)
   A more complete MCU-style SoC with additional peripherals. Demonstrates a more realistic design with GPIO, UART, and other interfaces.

Getting Started
---------------

See :doc:`getting-started` for instructions on how to clone the examples repository and run your first chip build.

.. toctree::
   :maxdepth: 2
   :hidden:

   getting-started
   minimal
   mcu-soc
