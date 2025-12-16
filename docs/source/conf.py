# Configuration file for the Sphinx documentation builder.
import os
import sys
from pathlib import Path
from itertools import starmap

top_path = Path('../../')
sys.path.append(str((top_path / 'tools').absolute()))

from tools import copy_docs

# Repos we will be assembling
repos = [
    ('amaranth-lang/amaranth', 'tags/v0.5.4'),
    ('chipflow/amaranth-soc', 'origin/reference-docs-chipflow'),
    ('chipflow/chipflow-lib', 'origin/main'),
    ('chipflow/chipflow-digital-ip', 'origin/main')
]

# copy in the doc sources from our repos
repo_list = copy_docs(repos)

# add our repos to path
for r in repo_list:
    sys.path.append(str(r))

# Fix platform-api.rst to remove autodoc directives (requires chipflow to be installed)
# Replace with overview content
platform_api_content = """Platform API Reference
======================

This page provides an overview of the ChipFlow platform API.

Platforms
---------

The ChipFlow library provides several platform implementations for different build targets:

**SimPlatform** (``chipflow.platform.sim``)
   Platform for building and running CXXRTL simulations. Use this during development to test your design.

**SiliconPlatform** (``chipflow.platform.silicon``)
   Platform for targeting ASIC fabrication. Supports various foundry processes including SKY130, GF180, GF130BCD, and IHP_SG13G2.

**SoftwarePlatform** (``chipflow.platform.software``)
   Platform for building RISC-V software to run on your design.

Build Steps
-----------

Steps are the building blocks of the ChipFlow build system:

**SimStep** (``chipflow.platform.sim_step``)
   Handles simulation workflow: building the simulator, running simulations, and checking results.

**SiliconStep** (``chipflow.platform.silicon_step``)
   Handles ASIC preparation: elaborating designs to RTLIL and submitting to the ChipFlow cloud builder.

**SoftwareStep** (``chipflow.platform.software_step``)
   Handles RISC-V software compilation.

**BoardStep** (``chipflow.platform.board_step``)
   Handles board-level operations.

IO Signatures
-------------

IO Signatures define standard interfaces for your design. They provide a consistent way to connect peripherals and specify electrical characteristics.

Base Signatures
~~~~~~~~~~~~~~~

- **IOSignature** - Base class for all IO signatures
- **OutputIOSignature** - For output-only signals
- **InputIOSignature** - For input-only signals
- **BidirIOSignature** - For bidirectional signals

Protocol Signatures
~~~~~~~~~~~~~~~~~~~

Pre-defined signatures for common protocols:

- **UARTSignature** - UART serial interface
- **GPIOSignature** - General purpose I/O
- **SPISignature** - SPI bus interface
- **I2CSignature** - I2C bus interface
- **QSPIFlashSignature** - Quad SPI flash interface
- **JTAGSignature** - JTAG debug interface

IO Configuration
----------------

**IOModel**
   Configures electrical characteristics of IO pads (drive mode, trip point, inversion).

**IOModelOptions**
   Available options for IO configuration.

**IOTripPoint**
   Voltage threshold configuration for input signals.

Utility Functions
-----------------

**setup_amaranth_tools()**
   Sets up the Amaranth toolchain for your environment.

**top_components()**
   Returns dictionary of instantiated top-level components from configuration.

**get_software_builds()**
   Returns software build configurations from the design.
"""
platform_api_path = Path('chipflow-lib/platform-api.rst')
if platform_api_path.exists():
    platform_api_path.write_text(platform_api_content)

# -- Project information

project = 'ChipFlow'
copyright = '2022, ChipFlow'
author = 'ChipFlow'

release = 'alpha'
version = '0.1.0'

# -- General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autodoc.typehints',
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx_copybutton',
    'myst_parser',
    'sphinx.ext.todo',
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
    'sphinx_rtd_theme',
    'sphinxcontrib.platformpicker',
    'sphinxcontrib.yowasp_wavedrom',
    'sphinxext.rediraffe',
    'autoapi.extension',
    'sphinx_design',
]

rst_prolog = """
.. role:: amaranth

.. role:: amaranth-soc

.. role:: chipflow-lib

.. role:: py(code)
   :language: python
"""

rst_epilog = """
.. |required| replace:: :bdg-primary-line:`Required`
.. |optional| replace:: :bdg-secondary-line:`Optional`
"""

html_theme = 'furo'
html_logo = 'chipflow-lib/_assets/chipflow-logo.svg'
html_title = "ChipFlow Platform Documentation"
html_static_path = ['chipflow-lib/_assets', 'amaranth/_static', 'amaranth-soc/_static']

html_theme_options = {
    "dark_css_variables": {
        "admonition-font-size": "0.9 rem",
    },
    "light_css_variables": {
        "admonition-font-size": "0.9 rem",
    },
}

autodoc_typehints = 'description'

autoapi_dirs = [
        top_path / "vendor/chipflow-lib/chipflow_lib/platforms",
        top_path / "vendor/chipflow-lib/chipflow_lib",
        top_path / "vendor/chipflow-lib/chipflow",
        ]
autoapi_generate_api_docs = True
autoapi_template_dir = "chipflow-lib/_templates/autoapi"
# autoapi_verbose_visibility = 2
autoapi_keep_files = True
autoapi_options = [
    'members',
    'show-inheritance',
    'show-module-summary',
    'imported-members',
]
autoapi_root = "chipflow-lib/autoapi"

# Exclude autoapi templates and in-progress stuff
exclude_patterns = [
    autoapi_template_dir,
    "chipflow-lib/unfinished",
    "chipflow-lib/UNFINISHED_IDEAS.md",
    "amaranth/cover.rst",
    "amaranth-soc/cover.rst",
]


intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
}
intersphinx_disabled_domains = ['std']

rediraffe_redirects = {
    "simulator.rst": "amaranth/simulator.rst",
}

templates_path = ['chipflow-lib/_templates']

# -- Options for HTML output

html_theme = "furo"

# Favicon is not from `_static`, it gets copied:
html_favicon = "favicon.png"

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_js_files = [
    'js/init.js',
]

# -- Options for EPUB output
epub_show_urls = 'footnote'

autodoc_member_order = "bysource"
autodoc_default_options = {
    "members": True,
    'ignore-module-all': True
}
autodoc_preserve_defaults = True
autodoc_inherit_docstrings = False

napoleon_google_docstring = False
napoleon_numpy_docstring = True
napoleon_use_ivar = True
napoleon_include_init_with_doc = True
napoleon_include_special_with_doc = True
napoleon_custom_sections = [
    ("Attributes", "params_style"), # by default displays as "Variables", which is confusing
    ("Members", "params_style"), # `lib.wiring` signature members
    "Platform overrides"
]


linkcheck_ignore = [
    r"^http://127\.0\.0\.1:8000$",
    # Picked up automatically by ReST and doesn't have an index.
    r"^https://amaranth-lang\.org/schema/$",
]

linkcheck_anchors_ignore_for_url = [
    r"^https://matrix\.to/",
    r"^https://web\.libera\.chat/",
    # React page with README content included as a JSON payload.
    r"^https://github\.com/[^/]+/[^/]+/$",
]

suppress_warnings = [ "ref.python" ]

# Silence the warnings globally; otherwise they may fire on object destruction and crash completely
# unrelated tests.
import amaranth._unused
amaranth._unused.MustUse._MustUse__silence = True
