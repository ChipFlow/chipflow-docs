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

def copy_docs(repos: List[Tuple[str, str]]):
    # Ensure vendor directory exists
    root_path = Path(os.environ['PDM_PROJECT_ROOT'])
    vendor = root_path / 'vendor'
    vendor.mkdir(exist_ok=True)

    for repo_info in repos:
        repo_path = Path(repo_info[0])
        ref = repo_info[1]

        # Extract repo name from path (equivalent to ${repo##*/} in bash)
        name = repo_path.name

        repodir = vendor / name
        docs_dest_path = root_path /'docs/source' / name

        # Check if repo already exists
        if repodir.exists():
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

    # assemble a
    print("Documentation copy completed successfully")
