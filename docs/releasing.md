# Releasing (Preparation Stage)

This project is currently in release preparation mode. The steps below validate package quality and release readiness without publishing artifacts.

## Preconditions

- All tests pass locally.
- Changelog updated in `CHANGELOG.md`.
- Version updated in `pyproject.toml` if a release is intended.
- CI is green on `main`.

## Local Verification

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
pytest
python -m build
twine check dist/*
```

## Release Candidate Checklist

- [ ] Version in `pyproject.toml` matches intended release tag.
- [ ] `CHANGELOG.md` has release notes.
- [ ] `README.md` and docs reflect current behavior.
- [ ] `python -m build` produces valid `sdist` and `wheel`.
- [ ] `twine check dist/*` passes with no warnings.

## Publishing (Next Cycle)

Publishing to TestPyPI/PyPI is intentionally out of scope for this phase. When enabling publishing:

1. Add trusted publishing or API token secrets.
2. Create dedicated release workflow triggered by tags.
3. Publish to TestPyPI first, verify install, then publish to PyPI.
