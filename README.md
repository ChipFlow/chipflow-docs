# ChipFlow docs

ChipFlow docs repository. 
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

Build the docs locally:

```bash
poetry run make -C docs/ html
```

Preview the docs with Python webserver:

```bash
poetry run python -m http.server --directory docs/build/html/
```

In your web browser go to http://localhost:8000
