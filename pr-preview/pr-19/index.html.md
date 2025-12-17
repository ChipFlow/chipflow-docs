![image](chipflow-lib/_assets/chipflow-logo.svg)

# ChipFlow IC Design Platform

ChipFlow is an open-source platform for designing, testing, and manufacturing custom silicon.
It provides a streamlined workflow from design to fabrication using Python and the Amaranth HDL.

# Contents

# Getting Started

* [Chip Configurator](configurator/index.md)
  * [Getting Started](configurator/index.md#getting-started)
  * [Working in Your Codespace](configurator/index.md#working-in-your-codespace)
  * [Key Features](configurator/index.md#key-features)
  * [Resources](configurator/index.md#resources)
* [Getting Started with ChipFlow](chipflow-lib/getting-started.md)
  * [What is ChipFlow?](chipflow-lib/getting-started.md#what-is-chipflow)
  * [Prerequisites](chipflow-lib/getting-started.md#prerequisites)
  * [Clone chipflow-examples](chipflow-lib/getting-started.md#clone-chipflow-examples)
  * [Install the dependencies](chipflow-lib/getting-started.md#install-the-dependencies)
  * [Set up authentication](chipflow-lib/getting-started.md#set-up-authentication)
  * [Running a chip build](chipflow-lib/getting-started.md#running-a-chip-build)
* [Introduction to the ChipFlow platform](tutorial-intro-chipflow-platform.md)
  * [Preparing your local environment](tutorial-intro-chipflow-platform.md#preparing-your-local-environment)
  * [Getting started](tutorial-intro-chipflow-platform.md#getting-started)
  * [The example project](tutorial-intro-chipflow-platform.md#the-example-project)
  * [The design](tutorial-intro-chipflow-platform.md#the-design)
  * [Run the design in simulation](tutorial-intro-chipflow-platform.md#run-the-design-in-simulation)
  * [Run the design on a ULX3S board (optional)](tutorial-intro-chipflow-platform.md#run-the-design-on-a-ulx3s-board-optional)
  * [Add a peripheral to the design](tutorial-intro-chipflow-platform.md#add-a-peripheral-to-the-design)
  * [See our new peripheral in action](tutorial-intro-chipflow-platform.md#see-our-new-peripheral-in-action)
  * [Building for Silicon](tutorial-intro-chipflow-platform.md#building-for-silicon)
  * [What’s on the roadmap?](tutorial-intro-chipflow-platform.md#what-s-on-the-roadmap)
  * [Join the Alpha Program](tutorial-intro-chipflow-platform.md#join-the-alpha-program)
  * [Troubleshooting](tutorial-intro-chipflow-platform.md#troubleshooting)

# Examples

* [ChipFlow Examples](examples/index.md)
  * [Available Examples](examples/index.md#available-examples)
  * [Getting Started](examples/index.md#getting-started)

# Reference

* [ChipFlow Library Documentation](chipflow-lib/index.md)
  * [Getting Started with ChipFlow](chipflow-lib/getting-started.md)
  * [ChipFlow Architecture Overview](chipflow-lib/architecture.md)
  * [Simulation Guide](chipflow-lib/simulation-guide.md)
  * [Intro to `chipflow.toml`](chipflow-lib/chipflow-toml-guide.md)
  * [project_name](chipflow-lib/chipflow-toml-guide.md#project-name)
  * [clock_domains](chipflow-lib/chipflow-toml-guide.md#clock-domains)
  * [process](chipflow-lib/chipflow-toml-guide.md#process)
  * [package](chipflow-lib/chipflow-toml-guide.md#package)
  * [The `chipflow` command](chipflow-lib/chipflow-commands.md)
  * [Using Pin Signatures and Software Drivers](chipflow-lib/using-pin-signatures.md)
  * [Platform API Reference](platform-api.md)
  * [Pin Signature Architecture (Contributor Guide)](chipflow-lib/contributor-pin-signature-internals.md)
* [Digital IP Library](chipflow-digital-ip/index.md)
  * [Base Peripherals](chipflow-digital-ip/base.md)
  * [I/O Peripherals](chipflow-digital-ip/io.md)
  * [Memory Peripherals](chipflow-digital-ip/memory.md)
  * [Processors](chipflow-digital-ip/processors.md)
* [Indices and tables](chipflow-digital-ip/index.md#indices-and-tables)
* [Amaranth Language and Toolchain](amaranth/index.md)
  * [Introduction](amaranth/intro.md)
  * [Installation](amaranth/install.md)
  * [Getting started](amaranth/start.md)
  * [Tutorial](amaranth/tutorial.md)
  * [Language guide](amaranth/guide.md)
  * [Language reference](amaranth/reference.md)
  * [Standard library](amaranth/stdlib.md)
  * [Simulator](amaranth/simulator.md)
  * [Platform integration](amaranth/platform.md)
  * [Changelog](amaranth/changes.md)
  * [Contributing](amaranth/contrib.md)
* [Amaranth System-on-a-Chip toolkit](amaranth-soc/index.md)
  * [Memory maps](amaranth-soc/memory.md)
  * [Wishbone](amaranth-soc/wishbone.md)
  * [CSR](amaranth-soc/csr.md)
  * [GPIO](amaranth-soc/gpio.md)
* [Support](support.md)
