from __future__ import annotations

from fastapi.testclient import TestClient

from gss_webshop_shopify.app import create_shopify_app
from gss_webshop_shopify.settings import ShopifyProviderSettings
from gss_webshop_shopify.shopify_client import ShopifyAdminClient


class FakeShopifyClient(ShopifyAdminClient):
    def __init__(self) -> None:
        super().__init__(shop_domain="example.myshopify.com", admin_token="token", api_version="2024-10")

    def list_orders(self, *, limit: int = 20, status: str | None = None):  # type: ignore[override]
        return [
            {
                "id": 1001,
                "name": "#1001",
                "created_at": "2026-03-28T10:00:00Z",
                "financial_status": "paid",
                "fulfillment_status": "fulfilled",
                "total_price": "79.99",
                "currency": "EUR",
                "line_items": [{"id": 1, "title": "Headphones", "quantity": 1, "price": "79.99", "sku": "SKU-1"}],
                "customer": {"email": "c@example.com"},
            }
        ]

    def get_order(self, *, order_id: str):  # type: ignore[override]
        if order_id == "404":
            return None
        return {
            "id": int(order_id),
            "name": f"#{order_id}",
            "created_at": "2026-03-28T10:00:00Z",
            "financial_status": "paid",
            "fulfillment_status": "fulfilled",
            "total_price": "79.99",
            "currency": "EUR",
            "line_items": [{"id": 1, "title": "Headphones", "quantity": 1, "price": "79.99", "sku": "SKU-1"}],
            "customer": {"email": "c@example.com"},
            "fulfillments": [{"tracking_company": "PostNL", "tracking_number": "TRK-1", "tracking_url": "https://t"}],
        }


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "GSS-Consumer-Id": "support-squad-ai",
        "GSS-Consumer-Type": "ai_agent",
        "GSS-Version": "1.0",
    }


def test_shopify_describe_has_compliance() -> None:
    app = create_shopify_app()
    client = TestClient(app)
    res = client.get("/v1/describe")
    assert res.status_code == 200
    payload = res.json()["data"]
    assert "compliance" in payload
    assert "certified" in payload["compliance"]


def test_shopify_orders_list_and_not_supported_actions() -> None:
    settings = ShopifyProviderSettings(
        endpoint="http://127.0.0.1:8010/v1",
        host="127.0.0.1",
        port=8010,
        debug=False,
        shop_domain="example.myshopify.com",
        admin_token="token",
        api_version="2024-10",
        token_ttl_seconds=3600,
        compliance_level="basic",
        certified=False,
        test_suite_version="unverified",
    )
    app = create_shopify_app(settings=settings, client=FakeShopifyClient())
    client = TestClient(app)
    token = client.post("/v1/auth/login", json={"method": "api_key", "customer_id": "CUST-1"}).json()["data"]["access_token"]

    orders = client.get("/v1/orders", headers=_headers(token))
    assert orders.status_code == 200
    assert len(orders.json()["data"]) == 1

    account = client.get("/v1/account/get")
    assert account.status_code == 501
    assert account.json()["error"]["code"] == "ACTION_NOT_SUPPORTED"
