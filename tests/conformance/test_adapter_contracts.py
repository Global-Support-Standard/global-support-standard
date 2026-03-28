from __future__ import annotations

from datetime import datetime, timezone

from gss_provider.mock_adapter import InMemoryShopAdapter


def test_adapter_token_issue_and_resolve() -> None:
    adapter = InMemoryShopAdapter()
    issued = adapter.issue_token(customer_id="CUST-001", method="api_key", ttl_seconds=300)
    assert issued.customer_id == "CUST-001"
    assert adapter.resolve_customer(issued.access_token) == "CUST-001"


def test_adapter_confirmation_single_use() -> None:
    adapter = InMemoryShopAdapter()
    record = adapter.create_confirmation(
        customer_id="CUST-001",
        payload={"order_id": "ORD-1"},
        ttl_seconds=300,
    )
    first = adapter.consume_confirmation(token=record.token, customer_id="CUST-001")
    second = adapter.consume_confirmation(token=record.token, customer_id="CUST-001")
    assert first is not None
    assert second is None


def test_adapter_confirmation_expiry() -> None:
    adapter = InMemoryShopAdapter()
    record = adapter.create_confirmation(
        customer_id="CUST-001",
        payload={"order_id": "ORD-1"},
        ttl_seconds=0,
    )
    assert record.expires_at <= datetime.now(timezone.utc)
    assert adapter.consume_confirmation(token=record.token, customer_id="CUST-001") is None


def test_adapter_audit_append_and_list() -> None:
    adapter = InMemoryShopAdapter()
    adapter.append_event({"customer_id": "CUST-001", "action": "returns initiate"})
    adapter.append_event({"customer_id": "CUST-002", "action": "orders get"})
    rows = adapter.list_customer_events("CUST-001")
    assert len(rows) == 1
    assert rows[0]["action"] == "returns initiate"
