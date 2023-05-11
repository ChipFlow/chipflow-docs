# ChipFlow documentation

ChipFlow documentation repository.

Uses https://readthedocs.org/ and publishes to https://docs.chipflow.io/.

## Build and view docs locally

Install Poetry into your environment if you don't have it already:

```bash
pip3 install pipx 
pipx install poetry
```

Install the [Python requirements](pyproject.toml):

```bash
poetry install
```

Build the documentation locally:

```bash
poetry run make -C docs/ html
```

Automatically rebuild the documentation on change and preview them at the same time:

```bash
poetry run sphinx-autobuild docs/source/ docs/build/html/
```

In your web browser go to http://localhost:8000 to see the documentation.
