# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `CLAUDE.md` documenting project overview, software stack, security practices,
  publishing workflow, and mandatory commit rules including changelog updates

### Changed

- Automate GitHub Release creation as a third workflow job (`release`) that
  runs after a successful PyPI publish; release notes are extracted from the
  matching `CHANGELOG.md` section
- Update DEVNOTES to document the full three-job release sequence

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

[Unreleased]: https://github.com/hleroy/django-signature-pad/compare/v0.9.0...HEAD
[0.9.0]: https://github.com/hleroy/django-signature-pad/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/hleroy/django-signature-pad/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/hleroy/django-signature-pad/releases/tag/v0.7.0
