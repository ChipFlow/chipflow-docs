Chip Configurator
=================

The `ChipFlow Configurator <https://configurator.chipflow.io>`_ is a web-based tool for
designing and visualizing custom chip layouts. It provides an intuitive interface
for configuring IP blocks, pin assignments, and bus connections.

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

3. **Explore the Chip Layout**

   The main view shows your chip layout with:

   - **Analog IP blocks** positioned around the perimeter (shell)
   - **Digital IP blocks** in the center (core)
   - **Pin assignments** shown on the edges
   - **Bus connections** between IP blocks

4. **Navigate the View**

   - **Pan**: Click and drag to move around
   - **Zoom**: Use mouse wheel or pinch gestures to zoom in/out

   .. image:: _screenshots/04-zoomed-out.png
      :alt: Zoomed out view showing full chip
      :width: 100%

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

Export Designs
^^^^^^^^^^^^^^

Export your complete chip design as a JSON file containing:

- Full configuration settings
- IP block positions and parameters
- Pin allocation details
- Bus connection information

Click the **Export Design** button in the sidebar to download your design.

Next Steps
----------

- Explore different chip templates to see various configurations
- Try enabling/disabling IP blocks to see how pin allocation changes
- Export a design and examine the JSON structure
- Check out the :doc:`/chipflow-lib/index` to learn how to use your design in code
