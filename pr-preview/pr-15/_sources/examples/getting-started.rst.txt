Getting Started with ChipFlow Examples
======================================

This guide will walk you through setting up the ChipFlow examples repository and running your first chip build.

Prerequisites
-------------

Before you begin, ensure you have the following installed:

- **Python 3.11+**: `Python Downloads <https://www.python.org/downloads/>`_
- **Git**: `Git Downloads <https://git-scm.com/downloads>`_
- **PDM**: `PDM Installation <https://pdm-project.org/en/latest/#installation>`_

We also recommend:

- **VS Code**: `VS Code Downloads <https://code.visualstudio.com/download>`_
- **GitHub Desktop**: `GitHub Desktop Downloads <https://desktop.github.com/download/>`_

Clone the Repository
--------------------

Using Git command line:

.. code-block:: bash

   git clone https://github.com/ChipFlow/chipflow-examples.git
   cd chipflow-examples

Or using GitHub Desktop:

1. Go to the `chipflow-examples repository <https://github.com/ChipFlow/chipflow-examples>`_
2. Click the green "Code" button
3. Select "Open with GitHub Desktop"
4. Follow the prompts to clone

Install Dependencies
--------------------

Once you have the repository cloned, install the dependencies:

.. code-block:: bash

   cd chipflow-examples
   pdm lock -d
   pdm install

Set Up Your API Key
-------------------

To submit designs to the ChipFlow cloud builder, you need an API key:

1. Go to https://build.chipflow.com/user/detail
2. Click "Create/Refresh API Key"
3. Copy your new API key (you won't see it again!)

Create a ``.env`` file in the ``chipflow-examples`` directory:

.. code-block:: bash

   echo "CHIPFLOW_API_KEY=your_api_key_here" > .env

Replace ``your_api_key_here`` with your actual API key.

Running Your First Build
------------------------

Let's try the ``minimal`` example:

.. code-block:: bash

   cd minimal

First, lock the pin assignments:

.. code-block:: bash

   pdm chipflow pin lock

Run the simulation to test the design:

.. code-block:: bash

   pdm sim-check

You should see the simulation being built and run, with test output like:

.. code-block:: text

   -- build_sim_cxxrtl
   -- build_sim
   pdm chipflow software
   -- gather_dependencies
   -- build_software_elf
   -- build_software
   cd build/sim && ./sim_soc
   SoC type: CA7F100F
   Flash ID: CA7CA7FF
   Quad mode
   Event logs are identical

Submitting to ChipFlow
----------------------

Once your simulation passes, submit your design to be built:

.. code-block:: bash

   pdm submit

This returns a build URL where you can monitor progress:

.. code-block:: text

   INFO:chipflow_lib.steps.silicon:Submitting c23dab6-dirty for project chipflow-examples-minimal
   INFO:chipflow_lib.steps.silicon:Submitted design: {'build_id': '3f51a69c-b3e3-4fd3-88fd-52826ac5e5dd'}
   Design submitted successfully! Build URL: https://build.chipflow.com/build/3f51a69c-b3e3-4fd3-88fd-52826ac5e5dd

To stream build logs to your terminal:

.. code-block:: bash

   pdm submit --wait

Next Steps
----------

- Explore the :doc:`minimal` example to understand the basic structure
- Try the :doc:`mcu-soc` example for a more complete design
- Read the :doc:`../chipflow-lib/chipflow-toml-guide` to understand configuration options
- Check the :doc:`../chipflow-lib/simulation-guide` for simulation details
