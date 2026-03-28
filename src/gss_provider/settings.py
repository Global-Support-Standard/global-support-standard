from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProviderSettings:
    protocol_dir: Path
    endpoint: str
    host: str
    port: int
    debug: bool
    token_ttl_seconds: int
    confirmation_ttl_seconds: int
    compliance_level: str
    certified: bool
    test_suite_version: str


def load_settings() -> ProviderSettings:
    project_root = Path(__file__).resolve().parents[2]
    return ProviderSettings(
        protocol_dir=Path(os.getenv("GSS_PROTOCOL_DIR", str(project_root / "protocols"))),
        endpoint=os.getenv("GSS_PROVIDER_ENDPOINT", "http://127.0.0.1:8000/v1"),
        host=os.getenv("GSS_PROVIDER_HOST", "127.0.0.1"),
        port=int(os.getenv("GSS_PROVIDER_PORT", "8000")),
        debug=os.getenv("GSS_PROVIDER_DEBUG", "0").lower() in {"1", "true", "yes"},
        token_ttl_seconds=int(os.getenv("GSS_TOKEN_TTL_SECONDS", "3600")),
        confirmation_ttl_seconds=int(os.getenv("GSS_CONFIRMATION_TTL_SECONDS", "900")),
        compliance_level=os.getenv("GSS_COMPLIANCE_LEVEL", "basic"),
        certified=os.getenv("GSS_CERTIFIED", "false").lower() in {"1", "true", "yes"},
        test_suite_version=os.getenv("GSS_TEST_SUITE_VERSION", "unverified"),
    )
