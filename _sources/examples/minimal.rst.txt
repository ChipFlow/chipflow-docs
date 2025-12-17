Minimal SoC Example
===================

The ``minimal`` example demonstrates the simplest possible ChipFlow SoC design. It includes a RISC-V CPU core with basic peripherals.

Overview
--------

This example creates a System-on-Chip with:

- **Minerva RISC-V CPU** - A 32-bit RISC-V processor with multiply/divide support
- **QSPI Flash** - External flash memory for code storage
- **SRAM** - 1KB of on-chip RAM
- **GPIO** - 8-bit general purpose I/O
- **GPIO (Open Drain)** - 4-bit open-drain GPIO for I2C-style interfaces
- **UART** - Serial communication at 115200 baud

Project Structure
-----------------

.. code-block:: text

   minimal/
   ├── chipflow.toml        # Project configuration
   ├── design/
   │   ├── design.py        # Main SoC design
   │   ├── software/        # Firmware source code
   │   ├── steps/           # Custom build steps
   │   └── tests/           # Test reference data
   └── README.md

Configuration
-------------

The ``chipflow.toml`` defines the project:

.. code-block:: toml

   [chipflow]
   project_name = "chipflow-examples-minimal"

   [chipflow.top]
   soc = "design.design:MySoC"

   [chipflow.steps]
   board = "design.steps.board:MyBoardStep"

   [chipflow.silicon]
   process = "sky130"
   package = "openframe"

   [chipflow.test]
   event_reference = "design/tests/events_reference.json"

Design Overview
---------------

The design is defined in ``design/design.py``. Here's the key structure:

.. code-block:: python

   class MySoC(wiring.Component):
       def __init__(self):
           super().__init__({
               "flash": Out(QSPIFlashSignature()),
               "uart_0": Out(UARTSignature()),
               "gpio_0": Out(GPIOSignature(pin_count=8)),
               "gpio_open_drain": Out(GPIOSignature(
                   pin_count=4,
                   sky130_drive_mode=Sky130DriveMode.OPEN_DRAIN_STRONG_UP
               ))
           })

The component declares its external interfaces using IO Signatures. These signatures tell ChipFlow how to map the design to physical pins.

Memory Map
----------

The SoC uses the following memory map:

.. list-table::
   :header-rows: 1

   * - Region
     - Base Address
     - Description
   * - SPI Flash
     - ``0x00000000``
     - Code storage (boot address at 1MB offset)
   * - SRAM
     - ``0x10000000``
     - 1KB on-chip RAM
   * - CSR Base
     - ``0xb0000000``
     - Control/Status registers
   * - GPIO CSR
     - ``0xb1000000``
     - GPIO peripheral registers
   * - UART CSR
     - ``0xb2000000``
     - UART peripheral registers
   * - SoC ID CSR
     - ``0xb4000000``
     - SoC identification registers

Running the Example
-------------------

.. code-block:: bash

   cd minimal
   pdm chipflow pin lock
   pdm sim-check
   pdm submit --wait

Key Concepts Demonstrated
-------------------------

1. **IO Signatures**: Using ``QSPIFlashSignature``, ``UARTSignature``, and ``GPIOSignature`` to define peripheral interfaces.

2. **Wishbone Bus**: Connecting CPU, memory, and peripherals using Wishbone arbiters and decoders.

3. **CSR Registers**: Using the CSR bus for low-speed peripheral configuration.

4. **Software Builds**: Attaching firmware to the design with ``SoftwareBuild``.

Next Steps
----------

- Modify the GPIO pin count or add more peripherals
- Change the target process in ``chipflow.toml``
- Explore the :doc:`mcu-soc` example for a more complete design
