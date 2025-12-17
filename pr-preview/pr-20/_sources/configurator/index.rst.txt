Chip Configurator
=================

The `ChipFlow Configurator <https://configurator.chipflow.io>`_ is a web-based tool for
designing and visualizing custom chip layouts. It provides an intuitive interface
for configuring IP blocks, pin assignments, and bus connections - then generates
a complete development environment for you to build and simulate your design.

.. image:: _screenshots/01-main-view.png
   :alt: ChipFlow Configurator main view
   :width: 100%

Getting Started
---------------

1. **Open the Configurator**

   Visit `configurator.chipflow.io <https://configurator.chipflow.io>`_ in your browser.

2. **Select a Template**

   Use the dropdown selector to choose a chip template. Templates define the chip's
   pin count, available IP blocks, and layout constraints.

   .. image:: _screenshots/03-config-selector.png
      :alt: Template selector dropdown
      :width: 100%

3. **Configure Your Design**

   - Enable or disable IP blocks using the sidebar controls
   - View pin assignments on the chip edges
   - See bus connections between components

4. **Navigate the View**

   - **Pan**: Click and drag to move around
   - **Zoom**: Use mouse wheel or pinch gestures to zoom in/out

   .. image:: _screenshots/04-zoomed-out.png
      :alt: Zoomed out view showing full chip
      :width: 100%

5. **Generate Your Design**

   When you're happy with your configuration, click the **Generate Design** button.
   This will:

   - Create a GitHub repository with your design
   - Launch a GitHub Codespace with everything pre-configured
   - Open a welcome page with next steps

Working in Your Codespace
-------------------------

After clicking "Generate Design", you'll be taken to a GitHub Codespace with your
chip design ready to build and simulate. The welcome page shows your design summary
and provides the commands you need.

Build Your Design
^^^^^^^^^^^^^^^^^

Generate Verilog and compile the simulation:

.. code-block:: bash

   chipflow sim build

Run Simulation
^^^^^^^^^^^^^^

Execute the simulation and see results:

.. code-block:: bash

   chipflow sim run

Submit for Fabrication
^^^^^^^^^^^^^^^^^^^^^^

When your design is ready, submit it for silicon fabrication:

.. code-block:: bash

   chipflow silicon submit

Next Steps in the Codespace
^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. **Build your design** - Run ``chipflow sim build`` to generate Verilog and compile
2. **Run simulation** - Execute ``chipflow sim run`` to test your design
3. **Explore results** - Check generated Verilog, waveforms, and test output
4. **Iterate and refine** - Modify your design and rebuild as needed
5. **Submit for fabrication** - Run ``chipflow silicon submit`` when ready

Key Features
------------

Interactive Layout
^^^^^^^^^^^^^^^^^^

- Drag, zoom, and pan the chip visualization
- Click on IP blocks to see their details
- Real-time updates as you make changes

Configurable IP Blocks
^^^^^^^^^^^^^^^^^^^^^^

- Enable or disable individual IP blocks
- Scale and customize IP block parameters
- View pin assignments and signal mappings

Visual Bus Routing
^^^^^^^^^^^^^^^^^^

- Color-coded connections between components
- Toggle bus visibility in the sidebar
- See which blocks share common buses

One-Click Development Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Generates a complete GitHub repository
- Pre-configured Codespace with all tools installed
- Ready to build, simulate, and submit your design

Resources
---------

- `ChipFlow Documentation <https://docs.chipflow.io>`_ - Complete guides and API reference
- `Report Issues <https://github.com/ChipFlow/chipflow-central/issues>`_ - Found a problem? Let us know
