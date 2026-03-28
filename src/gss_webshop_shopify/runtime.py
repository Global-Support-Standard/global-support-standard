from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

from gss_provider.contracts import ConfirmationRecord, IssuedToken, ShopRuntimeAdapter


class ShopOwnedRuntimeAdapter(ShopRuntimeAdapter):
    """
    Shop-owned runtime state adapter for the Shopify project.

    Replace with production-grade persistence (Redis/DB/KMS-backed) in the webshop
    deployment. This in-memory adapter is intentionally local-dev oriented.
    """

    def __init__(self) -> None:
        self._tokens: dict[str, tuple[str, datetime]] = {}
        self._confirmations: dict[str, ConfirmationRecord] = {}
        self._audit_events: list[dict[str, Any]] = []

    def issue_token(self, *, customer_id: str, method: str, ttl_seconds: int) -> IssuedToken:
        token = f"shop-{customer_id}-{uuid4().hex[:16]}"
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
        token = f"shop-conf-{uuid4().hex[:16]}"
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
            self._confirmations.pop(token, None)
            return None
        self._confirmations.pop(token, None)
        return record

    def append_event(self, event: dict[str, Any]) -> None:
        self._audit_events.append(dict(event))

    def list_customer_events(self, customer_id: str) -> list[dict[str, Any]]:
        return [e for e in self._audit_events if e.get("customer_id") == customer_id]
