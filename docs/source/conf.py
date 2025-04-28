# Configuration file for the Sphinx documentation builder.
from pathlib import Path
# -- Project information

project = 'ChipFlow'
copyright = '2022, ChipFlow'
author = 'ChipFlow'

release = 'alpha'
version = '0.1.0'

# -- General configuration
top_dir = Path(__file__).parent / ".." / ".."
extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosummary',
    'sphinx_copybutton',
    'myst_parser',
    'sphinx.ext.todo',
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx_rtd_theme',
    'sphinxcontrib.platformpicker',
    'sphinxcontrib.yowasp_wavedrom',
    'sphinx.ext.autodoc',
    'sphinxext.rediraffe',
]
"""
    "sphinx_design",
    "sphinx_design_elements",
"""

rst_prolog = """
.. role:: amaranth

.. role:: amaranth-soc

.. role:: chipflow-lib

.. role:: py(code)
   :language: python
"""


intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
}
intersphinx_disabled_domains = ['std']

exclude_patterns = [
        'amaranth/index.rst',
        'amaranth/cover.rst',
        'amaranth-soc/index.rst',
        'amaranth-soc/cover.rst',
        ]

rediraffe_redirects = {
    "simulator.rst": "amaranth/simulator.rst",
}

templates_path = ['_templates']

# -- Options for HTML output

html_theme = "furo"

# Favicon is not from `_static`, it gets copied:
html_favicon = "favicon.png"

# These folders are copied to the documentation's HTML output
html_static_path = ["_static"]

html_logo = "_static/logo.png"

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


# Silence the warnings globally; otherwise they may fire on object destruction and crash completely
# unrelated tests.
import amaranth._unused
amaranth._unused.MustUse._MustUse__silence = True
