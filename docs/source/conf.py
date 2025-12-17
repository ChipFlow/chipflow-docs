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
]

rst_prolog = """
.. role:: amaranth

.. role:: amaranth-soc

.. role:: chipflow-lib

.. role:: py(code)
   :language: python
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
