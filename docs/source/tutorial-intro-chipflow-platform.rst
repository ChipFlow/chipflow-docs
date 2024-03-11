.. role:: bash(code)
   :language: bash

Introduction to the ChipFlow platform
=====================================

This tutorial gives an overview of how we can configure an SoC (system on chip) with the ChipFlow platform:

* Simulate an example SoC
* Add a peripheral
* Optionally run on an FPGA

.. important:: 

    To test designs on an FPGA, you will need a `ULX3S 85F <https://www.crowdsupply.com/radiona/ulx3s>`_.
    Other development boards will be supported in the future. It should be possible to run this tutorial
    on the smaller 12F by applying `these <https://gitlab.com/roman3017/example-socs/-/commit/a9c9639c61e4508704620e489584f67a9b8d0da1>`_
    changes.

.. important::

    This tutorial assumes you are running on macOS 11 or later or Ubuntu 22.04 or later.
    The tutorial will work on other Linux distributions, but instructions are not included here.


Preparing your local environment
--------------------------------

.. admonition:: Installing on macOS

    You will need to install Python3 and git. Use `Brew <https://brew.sh/>`_ for this: ::

        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        brew install python3 pipx
        brew install git

.. admonition:: Installing on Ubuntu

    You will need to install git: ::

	sudo apt install git pipx

We use `PDM <https://pdm.fming.dev/>`_ to manage dependencies and ensure reproduable builds of your design.

First install PDM: ::

    pipx ensurepath
	pipx install pdm

You may need to restart your shell session for PDM to become available, using: ::
    
    exec "$SHELL"
   
To program the FPGA board we use `openFPGAloader <https://trabucayre.github.io/openFPGALoader/guide/install.html>`_.

.. admonition:: Installing on macOS

    Install using brew: ::

        brew install openfpgaloader

.. admonition:: Installing on Ubuntu

    Install openFPGAloader using apt: ::

        sudo add-apt-repository ppa:chipflow/ppa
        sudo apt update
        sudo apt install openfpgaloader

Getting started
---------------

First use `Git <https://git-scm.com/>`_ to get the example sources.  ::

	git clone https://github.com/ChipFlow/example-socs

Then set up your environment: ::

    cd example-socs
    make init


The example project
-------------------

The project contains:

* ``.github/workflows/*`` - Runs linting and tests in GitHub Actions.
* ``chipflow.toml`` - Configuration telling the ChipFlow library how to load your Python design and allows you to configure the ChipFlow platform.
* ``Makefile`` - Contains helpful shortcuts to the CLI tools used in the project.
* ``my_design/design.py`` - This has the actual chip design.
* ``my_design/steps/*`` - These control how your design will be presented to the ChipFlow build steps, ``sim``(ulation), (FPGA)``board`` and ``silicon``.
* ``my_design/sim/*`` - The C++ and `doit build file <https://pydoit.org/>`_ which builds the binary which will simulate our design.
* ``my_design/software/*`` - The C++ and `doit build file <https://pydoit.org/>`_ for the software/BIOS which we will load onto our design when it's running in simulation or on a board.
* ``tests/*`` - This has some pytest integration tests which cover simulation and board/silicon builds.

The design
----------

The chip design is contained within the `MySoC` class in ``my_design/design.py``, and is described 
using the `Amaranth hardware definition language <https://github.com/amaranth-lang/amaranth>`_.
Amaranth is already well-used for FPGA boards, and at ChipFlow we will be using it 
to produce silicon chips.

Something a little unusual about our example Amaranth design is that we change 
how the peripherals are physically accessed for use with simulation, a board, or 
silicon.

For example, here's where we add ``QSPIFlash`` to our design:

.. code-block:: python

    m.submodules.rom_provider = rom_provider = platform.providers.QSPIFlashProvider()
    self.rom = SPIMemIO(
        flash=rom_provider.pins
    )

The provider implementations, which are provided by ChipFlow, look a bit different for each context:

QSPIFlash for a Board
~~~~~~~~~~~~~~~~~~~~~

For a board, in our case a ULX3S board, we need a means of accessing the clock pin (``USRMCLK``) and buffer primitives (``OBZ``, ``BB``) to access the other pins:

.. code-block:: python

    class QSPIFlashProvider(Elaboratable):
        def __init__(self):
            self.pins = QSPIPins()

        def elaborate(self, platform):
            m = Module()

            flash = platform.request("spi_flash", dir=dict(cs='-', copi='-', cipo='-', wp='-', hold='-'))
            # Flash clock requires a special primitive to access in ECP5
            m.submodules.usrmclk = Instance(
                "USRMCLK",
                i_USRMCLKI=self.pins.clk_o,
                i_USRMCLKTS=ResetSignal(),  # tristate in reset for programmer accesss
                a_keep=1,
            )
            # IO pins and buffers
            m.submodules += Instance(
                "OBZ",
                o_O=flash.cs.io,
                i_I=self.pins.csn_o,
                i_T=ResetSignal(),
            )
            # Pins in order
            data_pins = ["copi", "cipo", "wp", "hold"]

            for i in range(4):
                m.submodules += Instance(
                    "BB",
                    io_B=getattr(flash, data_pins[i]).io,
                    i_I=self.pins.d_o[i],
                    i_T=~self.pins.d_oe[i],
                    o_O=self.pins.d_i[i]
                )
            return m

This is specific to the ECP5 family of boards, and the code would look different for others.

QSPIFlash for Simulation
~~~~~~~~~~~~~~~~~~~~~~~~

For simulation, we add a C++ model which will mock/simulate the flash:

.. code-block:: python

    class QSPIFlashProvider(Elaboratable):
        def __init__(self):
            self.pins = QSPIPins()

        def elaborate(self, platform):
            return platform.add_model("spiflash_model", self.pins, edge_det=['clk_o', 'csn_o'])

QSPIFlash for Silicon
~~~~~~~~~~~~~~~~~~~~~

For Silicon we just hook up the IO.

.. code-block:: python

    class QSPIFlashProvider(Elaboratable):
        def __init__(self):
            self.pins = QSPIPins()

        def elaborate(self, platform):
            m = Module()
            m.d.comb += [
                platform.request("flash_clk").eq(self.pins.clk_o),
                platform.request("flash_csn").eq(self.pins.csn_o),
            ]
            for index in range(4):
                pin = platform.request(f"flash_d{index}")
                m.d.comb += [
                    self.pins.d_i[index].eq(pin.i),
                    pin.o.eq(self.pins.d_o[index]),
                    pin.oe.eq(self.pins.d_oe[index])
                ]
            return m

Run the design in simulation
----------------------------

Running our design and its software in simulation allows us to loosely check 
that it's working. 

First we need to build a local simulation binary. The simulation uses 
blackbox C++ models of external peripherals, such as the flash, to interact 
with:

.. code-block:: bash

    make sim-build

After running this, we will have a simulation binary at ``build/sim/sim_soc``. 

We can't run it just yet, as it needs the software/BIOS too. To build the 
software we run:

.. code-block:: bash

    make software-build

Now that we have our simulation binary, and a BIOS, we can run it:

.. code-block:: bash

    make sim-run

You should see console output like this:

.. code-block:: bash

    🐱: nyaa~!
    SoC type: CA7F100F
    SoC version: 2024D6E6
    Flash ID: CA7CA7FF
    Entering QSPI mode
    Initialised!

Which means the processor is up and running. You can use Ctrl+C to interrupt it.

Run the design on a ULX3S board (optional)
------------------------------------------

We can also run our design on an FPGA board, although currently only the ULX3S 
is supported. If you don't have one, you can 
:ref:`skip to the next section <add-peripheral>`.

First we need to build the design into a bitstream for the board:

.. code-block:: bash

    make board-build

This will write a file ``build/top.bit``. As for the simulation, we need the 
software/BIOS too. 

If we haven't already, build the bios:

.. code-block:: bash

    make software-build

Now, we load the software/BIOS and design onto board (program its bitstream):

.. code-block:: bash

    make board-load-software-ulx3s
    make board-load-ulx3s

Your board should now be running. For us to check that it's working, we can 
connect to it via its serial port:

Connecting to your board
~~~~~~~~~~~~~~~~~~~~~~~~

First you need to find the serial port for your board, this is a little tricky but you should only need to do this once.


.. admonition:: Look for your serial port on macOS 

  Run the following command ::

    ls /dev/tty*

  you should see something similar to this: ::

    /dev/tty.Bluetooth-Incoming-Port 
    /dev/tty.usbserial-K00219

  In this case for our board its ``/dev/tty.usbserial-K00219``. Your device will likely be named similarly.
   

.. admonition:: Look for your serial port on Ubuntu/WSL2

  Run the following command ::

    ls /dev/ttyUSB*

  you should see something similar to this: ::

    /dev/ttyUSB0


  In this case for our board its ``/dev/ttyUSB0``. Yours will likely be named similarly.


Below we will refer to the name of your serial port as ``$TTYUSB``. This is the full path you saw, starting with ``/dev/``. 

For ease you can set this in your terminal using ``export TTYUSB=/dev/<the tty device you found>``.

Connect to the port via the screen utility, at baud ``115200``, with the command:

.. code-block:: bash

  screen $TTYUSB 115200

Now, press the ``PWR`` button on your board, which will restart the design, 
and give you a chance to see its output. It should look like:

.. code-block:: bash

  🐱: nyaa~!
  SoC type: CA7F100F
  SoC version: 613015FF
  Flash ID: EF401800
  Entering QSPI mode
  Initialised!

To exit screen, use ``CTRL-A``, then ``CTRL-\``.

.. _add-peripheral:

Add a peripheral to the design
------------------------------

We're going to add a very simple peripheral - buttons! This will allow us to press
buttons on our board and see the result, as well as something in simlation.

Add buttons to the design
~~~~~~~~~~~~~~~~~~~~~~~~~

In ``my_design/design.py`` we need to add another GPIO peripheral to read the 
button values.

You can uncomment the following:

Add an address space:

.. code-block:: python

    self.uart_base = 0xb2000000
    self.timer_base = 0xb3000000
    self.soc_id_base = 0xb4000000
    self.btn_gpio_base = 0xb5000000

Add the button peripheral:

.. code-block:: python

        soc_type = 0xCA7F100F
        self.soc_id = SoCID(type_id=soc_type)
        self._decoder.add(self.soc_id.bus, addr=self.soc_id_base)

        m.submodules.gpio_provider = gpio_provider = platform.providers.ButtonGPIOProvider()
        self.btn = GPIOPeripheral(
            pins=gpio_provider.pins
        )
        self._decoder.add(self.btn.bus, addr=self.btn_gpio_base)


Link up the button submodule:

.. code-block:: python

        m.submodules.uart = self.uart
        m.submodules.timer = self.timer
        m.submodules.soc_id = self.soc_id
        m.submodules.btn = self.btn


Add the button to our software generator:

.. code-block:: python

        sw.add_periph("uart", "UART0", self.uart_base)
        sw.add_periph("plat_timer", "TIMER0", self.timer_base)
        sw.add_periph("soc_id", "SOC_ID", self.soc_id_base)
        sw.add_periph("gpio", "BTN_GPIO", self.btn_gpio_base)


Update our software
~~~~~~~~~~~~~~~~~~~

So far, we have added the buttons to our design, but nothing will happen if we 
press them! So we update our software so it reacts to the button presses:

In ``my_design/software/main.c`` we uncomment the button press listening code:


.. code-block:: c

	while (1) {
		// Listen for button presses
		next_buttons = BTN_GPIO->in;
		if ((next_buttons & 1U) && !(last_buttons & 1U))
			puts("button 1 pressed!\n");
		if ((next_buttons & 2U) && !(last_buttons & 2U))
			puts("button 2 pressed!\n");
		last_buttons = next_buttons;
	};


Because we called ``sw.add_periph("gpio", "BTN_GPIO", self.btn_gpio_base)`` in our design above, here in our software we'll have a ``BTN_GPIO`` pointer to the peripheral address.

The pointer will be of a type matching the peripheral fields, and its `in` field contains the input value of the GPIO.

Using this, we'll now see "button X pressed!" when one of the buttons is pressed.


Update our simulation
~~~~~~~~~~~~~~~~~~~~~

We're going to simulate the buttons being pressed in the simulation on a timer.

It is possible to listen for keypresses on the keyboard, but that would introduce 
too many dependencies for our simple example.

So, in ``my_design/sim/main.cc`` we will uncomment the button presses code:

.. code-block:: cpp

    while (1) {
        tick();
        idx = (idx + 1) % 1000000;

        // Simulate button presses
        if (idx == 100000) // at t=100000, press button 1
            top.p_buttons.set(0b01U);
        else if (idx == 150000) // at t=150000, release button 1
            top.p_buttons.set(0b00U);
        else if (idx == 300000) // at t=300000, press button 2
            top.p_buttons.set(0b10U);
        else if (idx == 350000) // at t=350000, release button 2
            top.p_buttons.set(0b00U);
    }


See how we're pressing and releasing button 1, followed by button 2, on a loop, forever.

See our new peripheral in action
--------------------------------

See the changes in simulation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We can now take a look at our changes in simulation:

.. code-block:: bash

    # Rebuild our software 
    make software-build

    # Rebuild our simulation
    make sim-build

    # Run our simulation
    make sim-run

We should now see the output with button presses:

.. code-block:: bash

 🐱: nyaa~!
 SoC type: CA7F100F
 SoC version: DCBBADEA
 Flash ID: CA7CA7FF
 Entering QSPI mode
 Initialised!
 button 1 pressed!
 button 2 pressed!
 button 1 pressed!


See the changes on our board (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To see the changes on our board, we need to load the updated
software and design:

.. code-block:: bash

    # Rebuild our software 
    make software-build

    # Rebuild our board
    make board-build

    # Load software onto board
    make board-load-software-ulx3s

    # Load design onto board
    make board-load-ulx3s

Now, as in our first example, we need to connect to the board and 
see its output.

When we press the physical buttons on the board, we should see it:

.. code-block:: bash

 🐱: nyaa~!
 SoC type: CA7F100F
 SoC version: DCBBADEA
 Flash ID: EF401800
 Entering QSPI mode
 Initialised!
 button 2 pressed!
 button 2 pressed!
 button 1 pressed!
 button 2 pressed!



Building for Silicon
--------------------

For this first Alpha, we aren't *quite* ready to start accepting designs on our API. This is coming very soon though!

`Sign up <https://chipflow.io/beta>`_ to be notified when the next Alpha release is available.

If you are using this tutorial to test out new designs, reach out to us on `our Gitter channel <https://gitter.im/ChipFlow/community>`_. We would love to add your designs to our test sets!


What's on the roadmap?
----------------------

We still have a lot of work to do - some things on our roadmap:

* Silicon build API
* Integration tests to test your design in Python.
* Improved simulation tooling.
* Many more high-quality Amaranth Peripheral IP modules to include in your designs.

Join the beta
-------------

If you're interested in the platform, you can `join the beta <https://chipflow.io/beta>`_ 
and help us build the future of Python-powered chip design.


Troubleshooting
---------------
* Python version issues:
	If you choose to run ``pdm install`` within a venv, PDM will reuse
	that venv instead of creating a new one.
	Ensure that you use a venv with Python 3.8 or greater.

