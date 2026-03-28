from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from gss_provider.contracts import ConfirmationRecord, IssuedToken, ShopRuntimeAdapter


class InMemoryShopAdapter(ShopRuntimeAdapter):
    """
    Test/local-only adapter.

    Production deployments should provide their own adapter implementing
    ShopRuntimeAdapter with shop-owned persistence and security controls.
    """

    def __init__(self) -> None:
        self._tokens: dict[str, tuple[str, datetime]] = {}
        self._confirmations: dict[str, ConfirmationRecord] = {}
        self._audit: list[dict[str, Any]] = []

    def issue_token(self, *, customer_id: str, method: str, ttl_seconds: int) -> IssuedToken:
        token = f"tok-{customer_id}-{uuid4().hex[:16]}"
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)
        self._tokens[token] = (customer_id, expires_at)
        return IssuedToken(
            access_token=token,
            token_type="bearer",
            expires_in_seconds=ttl_seconds,
            customer_id=customer_id,
            method=method,
        )

    def resolve_customer(self, token: str) -> str | None:
        row = self._tokens.get(token)
        if not row:
            return None
        customer_id, expires_at = row
        if expires_at <= datetime.now(timezone.utc):
            del self._tokens[token]
            return None
        return customer_id

    def create_confirmation(
        self,
        *,
        customer_id: str,
        payload: dict[str, Any],
        ttl_seconds: int,
    ) -> ConfirmationRecord:
        token = f"conf-{uuid4().hex[:16]}"
        record = ConfirmationRecord(
            token=token,
            customer_id=customer_id,
            payload=payload,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds),
        )
        self._confirmations[token] = record
        return record

    def consume_confirmation(self, *, token: str, customer_id: str) -> ConfirmationRecord | None:
        record = self._confirmations.get(token)
        if not record:
            return None
        if record.customer_id != customer_id or record.expires_at <= datetime.now(timezone.utc):
            del self._confirmations[token]
            return None
        # single-use token by contract
        del self._confirmations[token]
        return record

    def append_event(self, event: dict[str, Any]) -> None:
        self._audit.append(dict(event))

    def list_customer_events(self, customer_id: str) -> list[dict[str, Any]]:
        return [row for row in self._audit if row.get("customer_id") == customer_id]
