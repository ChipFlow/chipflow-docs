MCU SoC Example
===============

The ``mcu_soc`` example demonstrates a more complete microcontroller-style System-on-Chip with multiple peripherals, targeting the IHP SG13G2 process.

Overview
--------

This example creates a full-featured MCU with:

- **CV32E40P RISC-V CPU** - A 32-bit RISC-V processor with debug support
- **JTAG Debug Module** - Full debug capabilities via JTAG interface
- **QSPI Flash** - External flash memory for code storage
- **SRAM** - 2KB of on-chip RAM
- **Multiple GPIO Banks** - 2 banks of 8-bit GPIO (16 total)
- **Multiple UARTs** - 2 UART interfaces
- **SPI Controllers** - 3 user SPI interfaces
- **I2C Controllers** - 2 I2C bus interfaces
- **PWM Controllers** - 10 motor PWM outputs

Project Structure
-----------------

.. code-block:: text

   mcu_soc/
   ├── chipflow.toml        # Project configuration
   ├── design/
   │   ├── design.py        # Main SoC design
   │   ├── ips/             # Custom IP cores (PWM, etc.)
   │   ├── openocd/         # OpenOCD debug configuration
   │   ├── software/        # Firmware source code
   │   ├── steps/           # Custom build steps
   │   └── tests/           # Test reference data
   └── README.md

Configuration
-------------

The ``chipflow.toml`` targets the IHP SG13G2 process with a PGA144 package:

.. code-block:: toml

   [chipflow]
   project_name = "chipflow-examples"

   [chipflow.top]
   soc = "design.design:MySoC"

   [chipflow.steps]
   board = "design.steps.board:MyBoardStep"

   [chipflow.silicon]
   process = "ihp_sg13g2"
   package = "pga144"

   [chipflow.test]
   event_reference = "design/tests/events_reference.json"

Peripheral Configuration
------------------------

The MCU SoC uses parameterized peripheral counts:

.. code-block:: python

   self.user_spi_count = 3    # 3 SPI interfaces
   self.i2c_count = 2         # 2 I2C interfaces
   self.motor_count = 10      # 10 PWM channels
   self.uart_count = 2        # 2 UART interfaces
   self.gpio_banks = 2        # 2 GPIO banks
   self.gpio_width = 8        # 8 bits per bank

Interface Declaration
---------------------

The design dynamically creates interfaces based on peripheral counts:

.. code-block:: python

   interfaces = {
       "flash": Out(QSPIFlashSignature()),
       "cpu_jtag": Out(JTAGSignature())
   }

   for i in range(self.user_spi_count):
       interfaces[f"user_spi_{i}"] = Out(SPISignature())

   for i in range(self.i2c_count):
       interfaces[f"i2c_{i}"] = Out(I2CSignature())

   for i in range(self.uart_count):
       interfaces[f"uart_{i}"] = Out(UARTSignature())

   for i in range(self.gpio_banks):
       interfaces[f"gpio_{i}"] = Out(GPIOSignature(pin_count=self.gpio_width))

Memory Map
----------

.. list-table::
   :header-rows: 1

   * - Region
     - Base Address
     - Description
   * - SPI Flash
     - ``0x00000000``
     - Code storage
   * - SRAM
     - ``0x10000000``
     - 2KB on-chip RAM
   * - Debug
     - ``0xa0000000``
     - Debug module
   * - SPI Flash CSR
     - ``0xb0000000``
     - Flash control registers
   * - GPIO CSR
     - ``0xb1000000``
     - GPIO registers (offset ``0x100000`` per bank)
   * - UART CSR
     - ``0xb2000000``
     - UART registers (offset ``0x100000`` per UART)
   * - SoC ID CSR
     - ``0xb4000000``
     - SoC identification
   * - User SPI CSR
     - ``0xb5000000``
     - SPI registers (offset ``0x100000`` per SPI)
   * - I2C CSR
     - ``0xb6000000``
     - I2C registers (offset ``0x100000`` per I2C)
   * - Motor PWM CSR
     - ``0xb7000000``
     - PWM registers (offset ``0x100`` per channel)

Debug Support
-------------

The MCU SoC includes full JTAG debug support via the CV32E40P debug module:

.. code-block:: python

   debug = OBIDebugModule()
   wb_arbiter.add(debug.initiator)
   wb_decoder.add(debug.target, name="debug", addr=self.debug_base)
   m.d.comb += cpu.debug_req.eq(debug.debug_req)

   m.d.comb += [
       debug.jtag_tck.eq(self.cpu_jtag.tck.i),
       debug.jtag_tms.eq(self.cpu_jtag.tms.i),
       debug.jtag_tdi.eq(self.cpu_jtag.tdi.i),
       debug.jtag_trst.eq(self.cpu_jtag.trst.i),
       self.cpu_jtag.tdo.o.eq(debug.jtag_tdo),
   ]

OpenOCD configuration files are provided in ``design/openocd/`` for hardware debugging.

Custom IP: PWM Controller
-------------------------

The example includes a custom PWM IP for motor control in ``design/ips/pwm.py``. This demonstrates how to create custom peripherals with their own IO signatures.

Running the Example
-------------------

.. code-block:: bash

   cd mcu_soc
   pdm chipflow pin lock
   pdm sim-check
   pdm submit --wait

Key Differences from Minimal
----------------------------

1. **Different CPU**: Uses CV32E40P instead of Minerva, with full debug support
2. **More Peripherals**: Multiple instances of each peripheral type
3. **JTAG Debug**: Full hardware debugging capability
4. **Custom IP**: Includes custom PWM peripheral
5. **Different Target**: IHP SG13G2 process instead of SKY130

Customization Ideas
-------------------

- Adjust peripheral counts to match your requirements
- Add additional custom IP cores
- Modify memory sizes for your application
- Change the target process/package for different fabrication options
