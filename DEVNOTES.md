# DEVNOTES.md

## Development and testing

For development and testing, setup a virtual environment with the required dependencies:

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Install django-signature-pad package in editable mode
pip install -e .
```

## Building and deploying to PyPI

Install `hatch`:

```bash
 pipx install hatch
```

### Building the Package

`hatch build`

This will generate distribution archives in the `dist/` directory.

### Uploading to TestPyPI

Test Your Package: Before uploading to the official PyPI, you can test your package on TestPyPI.

`hatch publish -r test`

Install your package from TestPyPI to ensure everything works as expected:

`pip install --index-url https://test.pypi.org/simple/ django-signature-pad`

### Uploading to PyPI

Upload to PyPI: If the test succeeds, upload your package to PyPI.

`hatch publish`

## Notes

- Versioning: Update the `version` parameter in `pyproject.toml` and `__init__.py`
