# ChipFlow documentation

ChipFlow documentation repository, publishing to the
[chipflow.github.io repository](https://github.com/ChipFlow/chipflow.github.io/)
via GitHub actions.


## Build and view docs locally

Install Poetry into your environment if you don't have it already:

```bash
pip3 install pipx 
pipx install pdm
```

Install the [Python requirements](pyproject.toml):

```bash
pdm install
```

Build the documentation locally:

```bash
pdm run build
```

Automatically rebuild the documentation on change and preview them at the same time:

```bash
pdm run autobuild
```

In your web browser go to http://localhost:8000 to see the documentation.
