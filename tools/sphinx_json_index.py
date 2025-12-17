"""
Sphinx extension to generate a structured JSON index of documentation.

This extension generates a docs-index.json file that provides machine-readable
metadata about all documentation pages, including titles, paths, and navigation
structure. This is useful for AI agents and tools that need to understand the
documentation structure programmatically.
"""
import json
from pathlib import Path
from sphinx.application import Sphinx
from sphinx.util import logging

logger = logging.getLogger(__name__)


def build_json_index(app: Sphinx, exception):
    """Generate docs-index.json after build completes."""
    if exception:
        return

    # Only run for HTML builders
    if app.builder.name not in ('html', 'dirhtml'):
        logger.info("Skipping JSON index generation (not an HTML builder)")
        return

    outdir = Path(app.outdir)

    index = {
        "project": app.config.project,
        "version": app.config.version,
        "description": getattr(app.config, 'llms_txt_description', '').strip(),
        "pages": []
    }

    # Iterate through all documents
    for docname in sorted(app.env.found_docs):
        try:
            doc = app.env.get_doctree(docname)
            title = ""
            for node in doc.traverse():
                if node.__class__.__name__ == 'title':
                    title = node.astext()
                    break

            # Determine the HTML path based on builder type
            if app.builder.name == 'dirhtml':
                html_path = f"{docname}/index.html" if docname != 'index' else "index.html"
            else:
                html_path = f"{docname}.html"

            page_info = {
                "path": html_path,
                "title": title or docname,
                "docname": docname,
            }

            # Add toctree children if available
            if hasattr(app.env, 'toctree_includes') and docname in app.env.toctree_includes:
                page_info["children"] = app.env.toctree_includes[docname]

            index["pages"].append(page_info)
        except Exception as e:
            logger.warning(f"Could not process {docname}: {e}")

    # Write JSON index
    output_path = outdir / "docs-index.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    logger.info(f"Generated JSON index with {len(index['pages'])} pages at {output_path}")


def setup(app: Sphinx):
    app.connect('build-finished', build_json_index)
    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
