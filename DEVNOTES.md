# DEVNOTES.md

## Development and testing

This project uses [uv](https://docs.astral.sh/uv/) for dependency and
environment management. Install uv first:
<https://docs.astral.sh/uv/getting-started/installation/>.

```bash
# Install dependencies (creates .venv automatically) and run tests
uv sync --group dev
uv run pytest
```

## Upgrading dependencies

```bash
# Upgrade locked versions in uv.lock
uv lock --upgrade

# Apply the new lock to the local environment
uv sync --group dev
```

## Publishing to PyPI

Releases are automated via the `Publish` GitHub Actions workflow using PyPI
Trusted Publishers (OIDC). To cut a release:

1. Bump the `__version__` in `src/signature_pad/__about__.py`.
2. Commit and tag: `git tag v0.x.y && git push --tags`.
3. The `Publish` workflow runs the test matrix; if it succeeds, the `release`
   environment requires manual approval, then the package is built with
   `uv build` and uploaded to PyPI.

To build locally for inspection:

```bash
uv build
```
