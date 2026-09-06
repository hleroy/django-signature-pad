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

`uv.lock` is generated locally and is not committed, so there is nothing to
push after an upgrade: it exists only to pin your own environment.

## Publishing to PyPI and GitHub Releases

Releases are automated via the `Publish` GitHub Actions workflow using PyPI
Trusted Publishers (OIDC). To cut a release:

1. Bump the `__version__` in `src/signature_pad/__about__.py`.
2. Add a dated entry for the new version in `CHANGELOG.md` (move items from
   `[Unreleased]` and update the comparison links at the bottom).
3. Commit and tag: `git tag v0.x.y && git push --tags`.
4. The workflow runs three jobs in sequence:
   - **test**: runs the full test matrix (Python 3.10–3.13 × Django 5.0–6.0).
   - **publish**: requires manual approval in the `release` environment, then
     builds the package with `uv build` and uploads it to PyPI via OIDC.
   - **release**: creates a GitHub Release automatically, with notes extracted
     from the matching section in `CHANGELOG.md`.

To build locally for inspection:

```bash
uv build
```
