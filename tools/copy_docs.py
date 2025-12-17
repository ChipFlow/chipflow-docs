#!/usr/bin/env python3
"""
Clones repositories and copies their documentation into the docs/source directory.
"""
import os
import subprocess
import re
import glob
import shutil
from pathlib import Path
from typing import List, Tuple


def has_local_changes(repodir: Path) -> bool:
    """Check if a git repository has uncommitted changes or is on a non-detached branch."""
    # Check for uncommitted changes
    status_result = subprocess.run(
        ['git', '-C', repodir, 'status', '--porcelain'],
        capture_output=True,
        text=True
    )
    if status_result.stdout.strip():
        return True

    # Check if we're on a branch (not detached HEAD)
    branch_result = subprocess.run(
        ['git', '-C', repodir, 'symbolic-ref', '-q', 'HEAD'],
        capture_output=True,
        text=True
    )
    if branch_result.returncode == 0:
        # We're on a branch, check if it has commits ahead of origin
        return True

    return False


def copy_docs(repos: List[Tuple[str, str]]) -> List[Path]:
    """"
    Pull in docs from other repos.

    Clones the repos at the given refs in $PDM_PROJECT_ROOT/vendor
    Then copies the doc dirs into this one, tranforming `:role:` references appropriatly

    Args:
        repos: List of tuples containing git repo and ref

    Returns:
        A list of the repo locations
    """

    # Ensure vendor directory exists
    root_path = Path(os.environ['PDM_PROJECT_ROOT'])
    vendor = root_path / 'vendor'
    vendor.mkdir(exist_ok=True)

    repo_list = []

    for repo_info in repos:
        repo_path = Path(repo_info[0])
        ref = repo_info[1]

        # Extract repo name from path (equivalent to ${repo##*/} in bash)
        name = repo_path.name

        repodir = vendor / name
        docs_dest_path = root_path /'docs/source' / name

        # Check if repo already exists
        if repodir.exists():
            if has_local_changes(repodir):
                print(f"{repo_path} has local changes, skipping update")
            else:
                print(f"{repo_path} already there, updating")
                # Git fetch
                subprocess.run(['git', '-C', repodir, 'fetch'], check=True)
                # Checkout ref
                subprocess.run(['git', '-C', repodir, 'checkout', '-f', '--detach', ref], check=True)
        else:
            print(f"Cloning {repo_path} {ref} as {repodir}")
            # Clone the repository with gh
            subprocess.run(['gh', 'repo', 'clone', repo_path, repodir], check=True)
            # Checkout ref
            subprocess.run(['git', '-C', repodir, 'checkout', '-f', '--detach', ref], check=True)

        repo_list.append(repodir)

        print(f"Binding in {repo_path} docs as {name}")

        if docs_dest_path.exists():
            shutil.rmtree(docs_dest_path)

        shutil.copytree(repodir / 'docs', docs_dest_path)

        # Replace :doc: references with :{name}: in all rst files
        doc_files = []
        for root, _, files in docs_dest_path.walk(on_error=print):
            rst_files = filter(lambda f: (root / f).suffix == '.rst' , files)
            for file in (root/f for f in rst_files):
                try:
                    content = file.read_text(encoding='utf-8')

                    if ':doc:' in content:
                        # Replace :doc: with :name:
                        new_content = content.replace(':doc:', f':{name}:')
                        file.write_text(new_content, encoding='utf-8')
                        print(f"Updated references in {file}")
                except (UnicodeDecodeError, IsADirectoryError):
                    # Skip binary files or directories
                    pass

    # Override chipflow-lib/platform-api.rst with our custom version that has
    # correct toctree paths (the vendor version has broken cross-references)
    platform_api_path = root_path / 'docs/source/chipflow-lib/platform-api.rst'
    if platform_api_path.exists():
        platform_api_content = """\
Platform API Reference
======================

This section provides the API reference for the ChipFlow platform library.

.. toctree::
   :maxdepth: 3

   /chipflow-lib/autoapi/chipflow/index
"""
        platform_api_path.write_text(platform_api_content, encoding='utf-8')
        print(f"Replaced {platform_api_path} with custom version")

    # Fix heading levels in chipflow-toml-guide.rst
    # The vendor file has project_name, clock_domains, process, package as top-level
    # headings (===) but they should be subsections (^^^)
    toml_guide_path = root_path / 'docs/source/chipflow-lib/chipflow-toml-guide.rst'
    if toml_guide_path.exists():
        content = toml_guide_path.read_text(encoding='utf-8')
        # Fix heading levels for config options that should be subsections
        # These use === but should use ^^^ to be nested under their parent sections
        replacements = [
            ('project_name\n============', 'project_name\n^^^^^^^^^^^^'),
            ('clock_domains\n=============', 'clock_domains\n^^^^^^^^^^^^^'),
            ('process\n=======', 'process\n^^^^^^^'),
            ('package\n=======', 'package\n^^^^^^^'),
        ]
        for old, new in replacements:
            content = content.replace(old, new)
        # Also rename the document title to be more descriptive
        content = content.replace(
            'Intro to ``chipflow.toml``\n==========================',
            '``chipflow.toml`` Reference\n==========================='
        )
        toml_guide_path.write_text(content, encoding='utf-8')
        print(f"Fixed heading levels in {toml_guide_path}")

    # Fix cross-references in using-pin-signatures.rst to link to autoapi docs
    pin_sig_path = root_path / 'docs/source/chipflow-lib/using-pin-signatures.rst'
    if pin_sig_path.exists():
        content = pin_sig_path.read_text(encoding='utf-8')
        # Add cross-references for Pin Signatures section (plain text to :py:class:)
        # These are in the "Available Pin Signatures" list
        sig_replacements = [
            ('``UARTSignature()``', ':py:class:`~chipflow.platform.UARTSignature`'),
            ('``GPIOSignature(pin_count)``', ':py:class:`~chipflow.platform.GPIOSignature`'),
            ('``SPISignature()``', ':py:class:`~chipflow.platform.SPISignature`'),
            ('``I2CSignature()``', ':py:class:`~chipflow.platform.I2CSignature`'),
            ('``QSPIFlashSignature()``', ':py:class:`~chipflow.platform.QSPIFlashSignature`'),
            ('``JTAGSignature()``', ':py:class:`~chipflow.platform.JTAGSignature`'),
            ('``IOModelOptions``', ':py:class:`~chipflow.platform.IOModelOptions`'),
            ('``SoftwareDriverSignature``', ':py:class:`~chipflow.platform.SoftwareDriverSignature`'),
            ('``attach_data()``', ':py:func:`~chipflow.platform.attach_data`'),
            ('``SoftwareBuild``', ':py:class:`~chipflow.platform.SoftwareBuild`'),
            # Fix existing broken :class: references to use full path
            (':class:`Sky130DriveMode`', ':py:class:`~chipflow.platform.Sky130DriveMode`'),
            (':class:`IOTripPoint`', ':py:class:`~chipflow.platform.IOTripPoint`'),
        ]
        for old, new in sig_replacements:
            content = content.replace(old, new)
        pin_sig_path.write_text(content, encoding='utf-8')
        print(f"Fixed cross-references in {pin_sig_path}")

    print("Documentation copy completed successfully")

    return repo_list
