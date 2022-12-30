# Configuration file for the Sphinx documentation builder.

# -- Project information

project = 'ChipFlow'
copyright = '2022, ChipFlow'
author = 'ChipFlow'

release = 'alpha'
version = '0.1.0'

# -- General configuration

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'myst_parser',
    'sphinx_copybutton',
]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
intersphinx_disabled_domains = ['std']

templates_path = ['_templates']

# -- Options for HTML output

html_theme = "furo"

# Logo/favicon are not from `_static`, they get copied:
html_logo = "logo.png"
html_favicon = "favicon.png"

html_theme_options = {
    "analytics_anonymize_ip": True,
    "light_css_variables": {
        "font-stack": "Poppins, Verdana, sans-serif",
        "color-brand-primary": "#7C4FA0",
        "color-brand-content": "#7C4FA0",
    },
    "sidebar_hide_name": True,
}

# These folders are copied to the documentation's HTML output
html_static_path = ["_static"]

html_css_files = [
    'css/custom.css',
]

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_js_files = [
    'js/init.js',
]

# -- Options for EPUB output
epub_show_urls = 'footnote'
