# CLAUDE.md

## Project overview

`django-signature-pad` is a Django reusable app that provides a model field,
form widget, and standalone validator for capturing handwritten signatures.
Signatures are stored as base64-encoded PNG data URLs. The JavaScript side is
powered by the [signature_pad](https://github.com/szimek/signature_pad) library.

The package targets Django 5.2–6.1 and Python 3.11–3.14. It is published on
PyPI under the MIT licence.

## Repository layout

```
src/signature_pad/      # installable package
  __about__.py          # single source of truth for __version__
  fields.py             # SignaturePadField (model), SignaturePadWidget, validate_png_data_url
  apps.py               # AppConfig
  static/               # bundled JS and CSS for the widget
  templates/            # widget HTML template
tests/                  # pytest test suite
example_project/        # runnable Django project for manual testing
.github/workflows/      # CI, test matrix, publish + release pipeline
```

## Software stack

| Concern                     | Tool                                                          |
|-----------------------------|---------------------------------------------------------------|
| Runtime                     | Python 3.11–3.14, Django 5.2–6.1                             |
| Dependency / env management | [uv](https://docs.astral.sh/uv/)                             |
| Build backend               | hatchling ≥1.29,<2                                           |
| Linter                      | Ruff                                                          |
| Formatter                   | Ruff format                                                   |
| Template linter/formatter   | djLint                                                        |
| Test runner                 | pytest + pytest-django                                        |
| Coverage                    | coverage + django-coverage-plugin                             |
| Pre-commit hooks            | pre-commit (quarterly autoupdate)                             |
| CI                          | GitHub Actions                                                |
| Publishing                  | PyPI Trusted Publishers (OIDC) via `pypa/gh-action-pypi-publish` |

## Development setup

```bash
# Install uv first: https://docs.astral.sh/uv/getting-started/installation/
uv sync --group dev       # creates .venv and installs all dev dependencies
uv run pytest             # run the test suite
```

## Code quality

Pre-commit runs automatically on every commit. To run manually:

```bash
uv run pre-commit run --all-files
```

Hooks in order: trailing-whitespace, end-of-file-fixer, JSON/TOML/YAML checks,
detect-private-key, django-upgrade (target 5.2), Ruff lint + format, djLint
reformat + lint, pytest.

Ruff is configured in `pyproject.toml` (line length 119, target py312). Do not
suppress Ruff or djLint warnings without a code comment explaining why.

## Upgrading dependencies

```bash
uv lock --upgrade         # regenerate uv.lock with latest compatible versions
uv sync --group dev       # apply to local environment
```

Commit the updated `uv.lock` together with any `pyproject.toml` changes.

## Security practices

### Input validation (`fields.py`)

`validate_png_data_url` is the canonical validator. It enforces:

1. **Format**: strict regex `^data:image/png;base64,[A-Za-z0-9+/]+={0,2}\Z`
   (`\Z` rejects trailing newlines; `$` does not).
2. **Base64 integrity**: `base64.b64decode(..., validate=True)` — strict mode,
   no silent padding repair.
3. **PNG magic bytes**: decoded data must start with `\x89PNG\r\n\x1a\n`.
4. **Size cap**: `SignaturePadField` enforces a `max_size_kb` limit (default
   100 KB) to prevent DoS via oversized payloads.

Validation runs at **both** the model level (`clean()`) and the form level
(`formfield()` attaches the validators), so plain `forms.Form` usage is
protected without a model.

### Dependency pinning

All third-party GitHub Actions are pinned to a full commit SHA (not a mutable
tag) to prevent supply-chain attacks. When updating an action, replace the SHA
and add a comment with the human-readable tag/version.

### CDN resources

The example project loads `signature_pad` from a CDN with Subresource Integrity
(SRI) hashes. Update the hash whenever the CDN URL or library version changes.

### Vulnerability reporting

Use GitHub's private advisory feature (see `SECURITY.md`). Do not open public
issues for security bugs.

## Publishing workflow

Releases use a tag-triggered three-job pipeline defined in
`.github/workflows/publish.yml`:

```
push tag v* → test (matrix) → publish (PyPI, manual approval) → release (GitHub Release)
```

### Job details

- **test**: reuses `test.yml`; runs the full matrix
  (Python 3.11–3.14 × Django 5.2–6.1).
- **publish**: runs in the `release` environment (requires manual approval in
  the GitHub UI); builds with `uv build`; uploads to PyPI via OIDC — no API
  token stored anywhere.
- **release**: runs after `publish`; extracts the current version's section
  from `CHANGELOG.md` using a Python snippet; creates the GitHub Release with
  those notes via `gh release create`.

### Cutting a release

1. Bump `__version__` in `src/signature_pad/__about__.py`.
2. Update `CHANGELOG.md`: move `[Unreleased]` items into a new dated section,
   add a fresh `## [Unreleased]` above it, update the comparison links at the
   bottom of the file.
3. Commit (message: `release: <version>`), tag, and push:
   ```bash
   git tag v<version>
   git push --tags
   ```
4. Approve the `publish` step in the GitHub Actions UI when prompted.

## Commit rules

### Every commit

> **IMPORTANT: updating `CHANGELOG.md` is mandatory for every single commit,
> no exceptions. Never create a commit without a corresponding changelog entry.**

Always update `CHANGELOG.md` as part of the commit:

- **Regular commit** (bug fix, feature, refactor, docs, CI, etc.): add a bullet
  under the appropriate subsection (`Added`, `Changed`, `Fixed`, `Security`, …)
  inside the `## [Unreleased]` block. Create the subsection heading if it does
  not exist yet.
- **Release commit**: replace `## [Unreleased]` with a versioned heading using
  today's date and the version string from `src/signature_pad/__about__.py`,
  e.g. `## [0.9.0] - 2026-04-29`. Also add a new empty `## [Unreleased]`
  section above it, and update the comparison links at the bottom of the file.

The changelog format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

### Commit message format

Use the Conventional Commits style:

```
<type>: <short imperative summary>
```

Common types: `feat`, `fix`, `refactor`, `test`, `docs`, `ci`, `build`,
`security`, `release`.

Keep the subject line under 72 characters. No trailing period.
