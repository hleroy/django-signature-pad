# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Dependabot configuration for the `github-actions` ecosystem (weekly, grouped
  into a single PR) so that SHA-pinned actions stay current. A frozen pin also
  freezes the action's bundled tooling, which is how the 0.10.0 publish failed
- `workflow_dispatch` entry point on the publish workflow, taking an existing
  tag as input. A tag push runs the workflow file as of the tagged commit, so
  a fix to the workflow itself previously required moving the tag; dispatching
  from `main` publishes the tagged source using the branch's workflow instead

### Changed

- Exempt Dependabot pull requests from the mandatory-changelog rule in
  `CLAUDE.md`, since the bot cannot edit `CHANGELOG.md` and the weekly grouped
  bump would otherwise breach the rule every week; grouped action bumps are
  now recorded as a single bullet when cutting a release. Also require action
  pin comments to carry the full version (`# v7.0.1`) rather than a bare major
  (`# v4`), which Dependabot leaves stale when it updates the SHA

### Fixed

- Correct the `actions/checkout` pin comments, which still read `# v4` after
  Dependabot moved the SHA to v7.0.1. Dependabot rewrites a full-version
  comment alongside the SHA but leaves a bare major alone, so the annotation
  had become a lie about what the pin contained

## [0.10.0] - 2026-08-11

### Added

- Test against Django 6.1 and Python 3.14, both of which were missing from the
  CI matrix
- README section on Content Security Policy: the widget ships no inline
  JavaScript or CSS and works under `script-src 'self'`, and nonce-based
  policies should render the assets with `{% csp_nonce_attr form.media %}`
  (Django 6.1+) rather than `{{ form.media }}`

### Changed

- **Breaking:** require Django 5.2 or later. Django 5.0 (end of life April
  2025) and 5.1 (end of life December 2025) are no longer supported or tested;
  the CI matrix now covers only Django versions that upstream still maintains
  (5.2 LTS, 6.0, 6.1)
- **Breaking:** require Python 3.11 or later. Python 3.10 reaches end of life
  in October 2026 and has been dropped ahead of that date
- Declare `Framework :: Django :: 5.2` and `:: 6.1` classifiers, which were
  missing even though those versions were supported
- Bump the `django-upgrade` pre-commit hook to 1.31.1 and its target to 5.2
  to match the new floor; the 5.2 target is only accepted from
  django-upgrade 1.23.0 onwards
- Bump the `signature_pad` CDN reference from 5.0.4 to 5.1.4 in the example
  project (template and admin `Media`) and in the README installation notes;
  the SRI hash in `base.html` was regenerated for the new file

### Fixed

- Set the Ruff `target-version` to `py311` so that it matches
  `requires-python`; the previous `py312` target allowed pyupgrade to rewrite
  code to syntax unavailable on the oldest supported interpreter
- Bump `pypa/gh-action-pypi-publish` to v1.14.2, which ships Twine 7 and can
  therefore read the `Metadata-Version: 2.5` that hatchling 1.29+ writes; the
  previously pinned revision aborted the upload with
  `InvalidDistribution: '2.5' is not a valid metadata version`

## [0.9.1] - 2026-06-03

### Added

- `CLAUDE.md` documenting project overview, software stack, security practices,
  publishing workflow, and mandatory commit rules including changelog updates
- Publish-pipeline guard that aborts the release if the built wheel does not
  contain the `signature_pad` package code, preventing another empty-wheel
  upload to PyPI

### Changed

- Automate GitHub Release creation as a third workflow job (`release`) that
  runs after a successful PyPI publish; release notes are extracted from the
  matching `CHANGELOG.md` section
- Update DEVNOTES to document the full three-job release sequence

### Fixed

- Build a non-empty wheel. The `packages` setting lived under the global
  `[tool.hatch.build]` table, which made hatchling strip the `src/` prefix in
  the sdist as well. When `uv build` then built the wheel from that sdist, the
  configured `src/signature_pad` path no longer existed, so the 0.9.0 wheel
  shipped with metadata only and no Python modules (`ModuleNotFoundError` on
  install). Scope the setting to `[tool.hatch.build.targets.wheel]` so the
  sdist keeps the `src/` layout and the wheel-from-sdist build finds the
  package.

## [0.9.0] - 2026-04-29

### Security

- Harden PNG data URL validation: enforce strict base64 decoding, anchor the
  format regex with `\Z` to reject trailing newlines, and limit padding to at
  most two `=` characters
- Expose `validate_png_data_url` as a standalone Django validator that can be
  imported directly from `signature_pad`
- Run PNG validation at the form level (not only at the model level) by
  attaching validators in `formfield()`, so plain `forms.Form` usage is now
  protected as well
- Add Subresource Integrity (SRI) hashes to the CDN-hosted JS and CSS in the
  example project
- Add `SECURITY.md` describing the private vulnerability reporting process

### Changed

- Switch dependency and environment management to [uv](https://docs.astral.sh/uv/);
  remove `requirements.txt` in favour of `[dependency-groups]` in
  `pyproject.toml` and a committed `uv.lock`
- Replace manual `hatch publish` workflow with a tag-triggered GitHub Actions
  release pipeline using PyPI Trusted Publishers (OIDC), a manual-approval
  `release` environment, and SHA-pinned third-party actions
- Pin the `hatchling` build backend to `>=1.29.0,<2`
- Update DEVNOTES and README to reflect the uv-based workflow
- Reduce pre-commit autoupdate cadence from weekly to quarterly

### Added

- GitHub Actions CI workflow running the test matrix
  (Python 3.10–3.13 × Django 5.0–6.0) on push and pull request

## [0.8.0] - 2026-02-21

### Added

- Django 6.0 support

## [0.7.0] - 2025-07-20

Initial tracked release.

[Unreleased]: https://github.com/hleroy/django-signature-pad/compare/v0.10.0...HEAD
[0.10.0]: https://github.com/hleroy/django-signature-pad/compare/v0.9.1...v0.10.0
[0.9.1]: https://github.com/hleroy/django-signature-pad/compare/v0.9.0...v0.9.1
[0.9.0]: https://github.com/hleroy/django-signature-pad/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/hleroy/django-signature-pad/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/hleroy/django-signature-pad/releases/tag/v0.7.0
