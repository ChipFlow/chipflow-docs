# Installation

<a id="install-playground"></a>

## In-browser playground

You can try Amaranth out without installing anything by visiting the [Amaranth Playground](https://amaranth-lang.org/play/). The playground webpage contains a [fully functional Python interpreter](https://pyodide.org/en/stable/) and an Amaranth toolchain that can simulate a design, display waveforms, and generate Verilog code. It works on all modern browsers that support [WebAssembly](https://webassembly.org/), including Firefox, Chrome, and Edge.

<a id="install-sysreqs"></a>

## System requirements

<!-- This version requirement needs to be synchronized with the one in pyproject.toml! -->

Amaranth HDL requires Python 3.8; it works on [CPython](https://www.python.org/) 3.8 (or newer), and works faster on [PyPy3.8](https://www.pypy.org/) 7.3.7 (or newer). Installation requires [pip](https://pip.pypa.io/en/stable/) 23.0 (or newer).

For most workflows, Amaranth requires [Yosys](https://yosyshq.net/yosys/) 0.40 (or newer). A [compatible version of Yosys](https://pypi.org/project/amaranth-yosys/) is distributed via [PyPI](https://pypi.org/) for most popular platforms, so it is usually not necessary to install Yosys separately.

Simulating Amaranth code requires no additional software. However, a waveform viewer like [Surfer](https://surfer-project.org/) or [GTKWave](https://gtkwave.sourceforge.net/) is invaluable for debugging. As an alternative, the [Amaranth Playground](https://amaranth-lang.org/play/) can be used to display waveforms for simple designs.

Synthesizing, placing and routing an Amaranth design for an FPGA requires the FPGA family specific toolchain. The open source iCE40, ECP5, MachXO2/3, Nexus, and Gowin toolchains are distributed via [PyPI](https://pypi.org/) for most popular platforms by the [YoWASP](https://yowasp.org/) project.

<!-- TODO: Link to FPGA family docs here -->

<a id="install-deps"></a>

## Installing prerequisites

Windows

[Install Python](https://docs.python.org/3/using/windows.html#using-on-windows), either from Windows Store or using the full installer. If using the full installer, make sure to install a 64-bit version of Python.

Before continuing, make sure you have the latest version of [pip](https://pip.pypa.io/en/stable/) installed by running:

```doscon
> pip install --upgrade pip
```

macOS

Install [Homebrew](https://brew.sh). Then, install Python by running:

```console
$ brew install python
```

Before continuing, make sure you have the latest version of [pip](https://pip.pypa.io/en/stable/) installed by running:

```console
$ pip install --upgrade pip
```

Debian

Install Python by running:

```console
$ sudo apt-get install python3-pip
```

On architectures other than x86_64 and AArch64, install Yosys by running:

```console
$ sudo apt-get install yosys
```

If Yosys 0.40 (or newer) is not available, [build Yosys from source](https://github.com/YosysHQ/yosys/#building-from-source).

Before continuing, make sure you have the latest version of [pip](https://pip.pypa.io/en/stable/) installed by running:

```console
$ pip3 install --user --upgrade pip
```

Arch Linux

Install Python and pip by running:

```console
$ sudo pacman -S python python-pip
```

Other Linux

Install Python from the package repository of your distribution.

On architectures other than x86_64 and AArch64, install Yosys from the package repository of your distribution.

If Yosys 0.40 (or newer) is not available, [build Yosys from source](https://github.com/YosysHQ/yosys/#building-from-source).

Before continuing, make sure you have the latest version of [pip](https://pip.pypa.io/en/stable/) installed by running:

```console
$ pip3 install --user --upgrade pip
```

<a id="install"></a>

## Installing Amaranth

The latest release of Amaranth should work well for most applications. A development snapshot—any commit from the `main` branch of Amaranth—should be similarly reliable, but is likely to include experimental API changes that will be in flux until the next release. With that in mind, development snapshots can be used to try out new functionality or to avoid bugs fixed since the last release.

<a id="install-release"></a>

### Latest release

Windows

To install the latest release of Amaranth, run:

```doscon
> pip install --upgrade amaranth[builtin-yosys]
```

macOS

To install the latest release of Amaranth, run:

```console
$ pip install --user --upgrade 'amaranth[builtin-yosys]'
```

Linux

If you **did not** install Yosys manually in the [previous step](#install-deps), to install the latest release of Amaranth, run:

```console
$ pip3 install --user --upgrade 'amaranth[builtin-yosys]'
```

If you **did** install Yosys manually in the previous step, run:

```console
$ pip3 install --user --upgrade amaranth
```

Arch Linux

To install the latest release of Amaranth, run:

```console
$ sudo pacman -S python-amaranth
```

<a id="install-snapshot"></a>

### Development snapshot

Windows

To install the latest development snapshot of Amaranth, run:

```doscon
> pip install "amaranth[builtin-yosys] @ git+https://github.com/amaranth-lang/amaranth.git"
```

macOS

To install the latest development snapshot of Amaranth, run:

```console
$ pip install --user 'amaranth[builtin-yosys] @ git+https://github.com/amaranth-lang/amaranth.git'
```

Linux

If you **did not** install Yosys manually in the [previous step](#install-deps), to install the latest release of Amaranth, run:

```console
$ pip3 install --user 'amaranth[builtin-yosys] @ git+https://github.com/amaranth-lang/amaranth.git'
```

If you **did** install Yosys manually in the previous step, run:

```console
$ pip3 install --user 'amaranth @ git+https://github.com/amaranth-lang/amaranth.git'
```

<a id="install-develop"></a>

### Editable development snapshot

Windows

To install an editable development snapshot of Amaranth for the first time, run:

```doscon
> git clone https://github.com/amaranth-lang/amaranth
> cd amaranth
> pip install --editable .[builtin-yosys]
```

Any changes made to the `amaranth` directory will immediately affect any code that uses Amaranth. To update the snapshot, run:

```doscon
> cd amaranth
> git pull --ff-only origin main
> pip install --editable .[builtin-yosys]
```

Run the `pip install --editable .[builtin-yosys]` command any time package dependencies may have been added or changed (notably after updating the snapshot with `git`). Otherwise, code using Amaranth may crash because of a dependency version mismatch.

macOS

To install an editable development snapshot of Amaranth for the first time, run:

```console
$ git clone https://github.com/amaranth-lang/amaranth
$ cd amaranth
$ pip install --user --editable '.[builtin-yosys]'
```

Any changes made to the `amaranth` directory will immediately affect any code that uses Amaranth. To update the snapshot, run:

```console
$ cd amaranth
$ git pull --ff-only origin main
$ pip install --user --editable '.[builtin-yosys]'
```

Run the `pip install --editable .[builtin-yosys]` command any time package dependencies may have been added or changed (notably after updating the snapshot with `git`). Otherwise, code using Amaranth may crash because of a dependency version mismatch.

Linux

If you **did** install Yosys manually in the [previous step](#install-deps), omit `[builtin-yosys]` from the following commands.

To install an editable development snapshot of Amaranth for the first time, run:

```console
$ git clone https://github.com/amaranth-lang/amaranth
$ cd amaranth
$ pip3 install --user --editable '.[builtin-yosys]'
```

Any changes made to the `amaranth` directory will immediately affect any code that uses Amaranth. To update the snapshot, run:

```console
$ cd amaranth
$ git pull --ff-only origin main
$ pip3 install --user --editable '.[builtin-yosys]'
```

Run the `pip3 install --editable .[builtin-yosys]` command any time package dependencies may have been added or changed (notably after updating the snapshot with `git`). Otherwise, code using Amaranth may crash because of a dependency version mismatch.

## Installing board definitions
