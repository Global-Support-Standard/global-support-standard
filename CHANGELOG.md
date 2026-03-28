# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project follows Semantic Versioning.

## [Unreleased]

### Added
- Stateless shop adapter contracts for auth, confirmations, and audit storage.
- Provider app factory with injectable runtime adapter and settings.
- Protocol trigger/path validation hardening.
- CI packaging checks (`python -m build` and `twine check`).
- Release documentation and security policy docs.

### Changed
- Provider runtime now delegates operational state to adapter interfaces.
- CLI token handling is now explicitly optional/dev-oriented via environment flags.

## [0.1.0] - 2026-03-28

### Added
- Initial GSS Python MVP with FastAPI provider, Typer CLI, protocol engine, tests, and docs.
