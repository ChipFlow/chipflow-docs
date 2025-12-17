"""
Sphinx extension to enhance LLM discoverability.

This extension adds:
1. <script type="text/llms.txt"> tags to HTML pages for inline LLM discovery
   (following Vercel's proposal)
2. Post-processing of llms.txt to organize pages into logical sections
"""
import re
from pathlib import Path
from sphinx.application import Sphinx
from sphinx.util import logging

logger = logging.getLogger(__name__)

# Default section mappings - can be overridden in conf.py
DEFAULT_SECTION_MAPPINGS = {
    "Getting Started": [
        r"^index\.html\.md$",
        r"^chipflow-lib/getting-started",
        r"^chipflow-lib/index",
        r"^tutorial",
        r"^examples/getting-started",
    ],
    "User Guide": [
        r"^chipflow-lib/(?!autoapi)",
        r"^examples/",
        r"^configurator/",
    ],
    "API Reference": [
        r"^chipflow-lib/autoapi/",
        r"^platform-api",
    ],
    "Digital IP Library": [
        r"^chipflow-digital-ip/",
    ],
    "Amaranth Language": [
        r"^amaranth/(?!.*soc)",
    ],
    "Amaranth SoC": [
        r"^amaranth-soc/",
    ],
    "Optional": [
        r"^amaranth/changes",
        r"^support",
    ],
}


def add_llms_script_tag(app: Sphinx, pagename: str, templatename: str,
                        context: dict, doctree) -> None:
    """Add <script type="text/llms.txt"> to HTML pages."""

    description = getattr(app.config, 'llms_txt_description', '')
    if not description:
        description = "Documentation for this project."
    description = description.strip()

    project = app.config.project or "Documentation"

    # Create the inline llms.txt content
    llms_script = f'''<script type="text/llms.txt">
# {project}

> {description}

For complete documentation in LLM-friendly format:
- [Documentation Index](/llms.txt) - Sitemap of all pages
- [Full Documentation](/llms-full.txt) - Complete docs in one file
- [JSON Index](/docs-index.json) - Structured metadata
</script>'''

    # Add to metatags which Sphinx/Furo will include in <head>
    if 'metatags' not in context:
        context['metatags'] = ''
    context['metatags'] = context.get('metatags', '') + llms_script


def reorganize_llms_txt(app: Sphinx, exception) -> None:
    """Post-process llms.txt to organize pages into logical sections."""
    if exception:
        return

    outdir = Path(app.outdir)
    llms_txt_path = outdir / "llms.txt"

    if not llms_txt_path.exists():
        logger.warning("llms.txt not found, skipping reorganization")
        return

    # Read current llms.txt
    content = llms_txt_path.read_text(encoding='utf-8')

    # Parse the header (everything before ## Pages)
    header_match = re.match(r'^(.*?)(?=^## Pages|\Z)', content, re.MULTILINE | re.DOTALL)
    if not header_match:
        logger.warning("Could not parse llms.txt header")
        return

    header = header_match.group(1).strip()

    # Extract all page links
    page_pattern = re.compile(r'^- \[([^\]]+)\]\(([^)]+)\)(?::\s*(.*))?$', re.MULTILINE)
    pages = [(m.group(1), m.group(2), m.group(3) or '') for m in page_pattern.finditer(content)]

    if not pages:
        logger.warning("No pages found in llms.txt")
        return

    # Get section mappings from config or use defaults
    section_mappings = getattr(app.config, 'llms_sections', DEFAULT_SECTION_MAPPINGS)

    # Categorize pages into sections
    sections = {name: [] for name in section_mappings.keys()}
    sections["Other"] = []  # Catch-all

    for title, path, description in pages:
        categorized = False
        for section_name, patterns in section_mappings.items():
            for pattern in patterns:
                if re.search(pattern, path):
                    sections[section_name].append((title, path, description))
                    categorized = True
                    break
            if categorized:
                break
        if not categorized:
            sections["Other"].append((title, path, description))

    # Build new llms.txt with sections
    new_content = header + "\n\n"

    for section_name, section_pages in sections.items():
        if not section_pages:
            continue

        new_content += f"## {section_name}\n\n"
        for title, path, description in section_pages:
            if description:
                new_content += f"- [{title}]({path}): {description}\n"
            else:
                new_content += f"- [{title}]({path})\n"
        new_content += "\n"

    # Write reorganized llms.txt
    llms_txt_path.write_text(new_content.strip() + "\n", encoding='utf-8')
    logger.info(f"Reorganized llms.txt with {len(sections)} sections")


def setup(app: Sphinx):
    # Config value for custom section mappings
    app.add_config_value('llms_sections', DEFAULT_SECTION_MAPPINGS, 'html')

    # Add script tag to each HTML page
    app.connect('html-page-context', add_llms_script_tag)

    # Reorganize llms.txt after build (run after sphinx-llm)
    app.connect('build-finished', reorganize_llms_txt, priority=900)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
