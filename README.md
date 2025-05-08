# ChipFlow documentation

ChipFlow documentation repository, publishing to
https://chipflow-docs.docs.chipflow-infra.com via GitHub actions.

Releases are published to https://docs.chipflow.io


## Build and view docs locally

Install PDM into your environment if you don't have it already:

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
pdm docs
```

Automatically rebuild the documentation on change and preview them at the same time:

```bash
pdm autodocs
```

In your web browser go to http://localhost:8000 to see the documentation.
