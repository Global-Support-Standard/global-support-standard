# Contributing to GSS

Thanks for contributing to the Global Support Standard.

This repo includes both specification content and a Python MVP implementation. We welcome contributions to both.

## Ways To Contribute

- **Spec and docs improvements**
  - Clarify definitions and edge cases
  - Improve examples and onboarding docs
- **MVP implementation**
  - New domain handlers
  - Better auth/security enforcement
  - Protocol engine enhancements
- **Testing and reliability**
  - Broader integration tests
  - Regression tests for protocol/security behavior

## Ground Rules

1. Open an issue for large changes before implementing.
2. Keep PRs focused. Separate spec changes from implementation changes when possible.
3. Add or update tests for behavior changes.
4. Keep docs in sync with code and API behavior.

## Local Development

```bash
git clone https://github.com/MichelN89/global-support-standard.git
cd global-support-standard
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Repository Map

- `src/gss_provider/` - FastAPI provider server
- `src/gss_cli/` - Typer CLI
- `src/gss_core/` - shared models/envelope/errors
- `protocols/` - protocol format and examples
- `docs/` - onboarding and architecture docs
- `spec/` - protocol narrative/spec references
- `tests/` - API and CLI tests

## Pull Request Checklist

Before opening a PR:

- [ ] Tests pass locally (`pytest`)
- [ ] Packaging checks pass locally (`python -m build` and `twine check dist/*`)
- [ ] New behavior is covered by tests
- [ ] README/docs updated if user-facing behavior changed
- [ ] No generated artifacts committed (`__pycache__`, `.pyc`, `.egg-info`)
- [ ] Commit messages explain intent clearly

## Commit Guidance

Good commit messages explain why the change exists.

Examples:
- `Add protocol fallback rule for missing tracking events`
- `Enforce required GSS consumer headers on protected endpoints`
- `Document two-step confirmation flow for request actions`

## Security Disclosures

If you find a security issue, avoid opening a public issue first. Reach out privately to the maintainers and include:

- impact summary
- reproduction steps
- suggested mitigation (if available)

## Code Of Conduct

Be respectful and constructive in discussions and reviews.
