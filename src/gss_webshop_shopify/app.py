from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import uvicorn
from fastapi import FastAPI, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from gss_core.envelope import fail, ok
from gss_core.errors import GssError, err
from gss_core.models import AuthLoginRequest, OrdersListQuery
from gss_provider.auth import validate_headers
from gss_webshop_shopify.runtime import ShopOwnedRuntimeAdapter
from gss_webshop_shopify.settings import ShopifyProviderSettings, load_settings
from gss_webshop_shopify.shopify_client import ShopifyAdminClient, map_shopify_order


def create_shopify_app(
    *,
    settings: ShopifyProviderSettings | None = None,
    runtime: ShopOwnedRuntimeAdapter | None = None,
    client: ShopifyAdminClient | None = None,
) -> FastAPI:
    cfg = settings or load_settings()
    state = runtime or ShopOwnedRuntimeAdapter()
    shopify = client or ShopifyAdminClient(
        shop_domain=cfg.shop_domain,
        admin_token=cfg.admin_token,
        api_version=cfg.api_version,
    )
    app = FastAPI(title="GSS Shopify Webshop Provider", version="0.1.0")

    def _request_id(request: Request) -> str:
        return request.headers.get("GSS-Request-Id", f"req-{uuid4().hex}")

    def _ctx(
        *,
        authorization: str | None,
        consumer_id: str | None,
        consumer_type: str | None,
        version: str | None,
        request_id: str | None,
    ):
        return validate_headers(
            adapter=state,
            authorization=authorization,
            consumer_id=consumer_id,
            consumer_type=consumer_type,
            gss_version=version,
            request_id=request_id,
        )

    @app.exception_handler(GssError)
    async def gss_error_handler(request: Request, exc: GssError) -> JSONResponse:
        rid = _request_id(request)
        return JSONResponse(status_code=exc.status_code, content=fail(exc.code, exc.message, rid, exc.details))

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        rid = _request_id(request)
        return JSONResponse(
            status_code=422,
            content=fail("VALIDATION_ERROR", "Request validation failed", rid, {"errors": exc.errors()}),
        )

    @app.get("/v1/describe")
    def describe_shop(request: Request) -> dict[str, Any]:
        rid = _request_id(request)
        return ok(
            {
                "shop": cfg.shop_domain or "shopify-test-store",
                "name": "Shopify Test Store",
                "gss_version": "1.0",
                "domains": ["orders", "shipping", "account", "payments", "auth", "protocols"],
                "auth_methods": ["oauth2", "api_key"],
                "endpoint": cfg.endpoint,
                "compliance": {
                    "level": cfg.compliance_level,
                    "certified": cfg.certified,
                    "test_suite_version": cfg.test_suite_version,
                    "responsibility_boundary": (
                        "GSS defines contracts. This webshop implementation owns auth/session/audit infrastructure."
                    ),
                },
            },
            rid,
        )

    @app.post("/v1/auth/login")
    def auth_login(payload: AuthLoginRequest, request: Request) -> dict[str, Any]:
        rid = _request_id(request)
        issued = state.issue_token(customer_id=payload.customer_id, method=payload.method, ttl_seconds=cfg.token_ttl_seconds)
        return ok(
            {
                "access_token": issued.access_token,
                "token_type": issued.token_type,
                "expires_in_seconds": issued.expires_in_seconds,
                "customer_id": issued.customer_id,
                "method": issued.method,
            },
            rid,
        )

    @app.get("/v1/orders")
    def orders_list(
        request: Request,
        status: str | None = None,
        since: str | None = None,
        limit: int = 20,
        authorization: str | None = Header(default=None, alias="Authorization"),
        consumer_id: str | None = Header(default=None, alias="GSS-Consumer-Id"),
        consumer_type: str | None = Header(default=None, alias="GSS-Consumer-Type"),
        gss_version: str | None = Header(default=None, alias="GSS-Version"),
        gss_request_id: str | None = Header(default=None, alias="GSS-Request-Id"),
    ) -> dict[str, Any]:
        ctx = _ctx(
            authorization=authorization,
            consumer_id=consumer_id,
            consumer_type=consumer_type,
            version=gss_version,
            request_id=gss_request_id,
        )
        if not shopify.configured:
            raise err("SERVICE_UNAVAILABLE", "Shopify credentials not configured", status_code=503)
        query = OrdersListQuery(status=status, since=since, limit=limit)
        orders = [map_shopify_order(row) for row in shopify.list_orders(limit=query.limit, status=query.status)]
        state.append_event(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "customer_id": ctx.customer_id,
                "consumer_id": ctx.consumer_id,
                "consumer_type": ctx.consumer_type.value,
                "action": "orders list",
                "action_level": "read",
                "result": "ok",
            }
        )
        return ok(orders, ctx.request_id)

    @app.get("/v1/orders/{order_id}")
    def orders_get(
        order_id: str,
        request: Request,
        authorization: str | None = Header(default=None, alias="Authorization"),
        consumer_id: str | None = Header(default=None, alias="GSS-Consumer-Id"),
        consumer_type: str | None = Header(default=None, alias="GSS-Consumer-Type"),
        gss_version: str | None = Header(default=None, alias="GSS-Version"),
        gss_request_id: str | None = Header(default=None, alias="GSS-Request-Id"),
    ) -> dict[str, Any]:
        ctx = _ctx(
            authorization=authorization,
            consumer_id=consumer_id,
            consumer_type=consumer_type,
            version=gss_version,
            request_id=gss_request_id,
        )
        if not shopify.configured:
            raise err("SERVICE_UNAVAILABLE", "Shopify credentials not configured", status_code=503)
        order = shopify.get_order(order_id=order_id)
        if not order:
            raise err("NOT_FOUND", f"Order '{order_id}' not found", status_code=404)
        return ok(map_shopify_order(order), ctx.request_id)

    @app.get("/v1/shipping/track/{order_id}")
    def shipping_track(
        order_id: str,
        request: Request,
        authorization: str | None = Header(default=None, alias="Authorization"),
        consumer_id: str | None = Header(default=None, alias="GSS-Consumer-Id"),
        consumer_type: str | None = Header(default=None, alias="GSS-Consumer-Type"),
        gss_version: str | None = Header(default=None, alias="GSS-Version"),
        gss_request_id: str | None = Header(default=None, alias="GSS-Request-Id"),
    ) -> dict[str, Any]:
        ctx = _ctx(
            authorization=authorization,
            consumer_id=consumer_id,
            consumer_type=consumer_type,
            version=gss_version,
            request_id=gss_request_id,
        )
        if not shopify.configured:
            raise err("SERVICE_UNAVAILABLE", "Shopify credentials not configured", status_code=503)
        order = shopify.get_order(order_id=order_id)
        if not order:
            raise err("NOT_FOUND", f"Order '{order_id}' not found", status_code=404)
        fulfillments = order.get("fulfillments", [])
        latest = fulfillments[0] if fulfillments else {}
        return ok(
            {
                "order_id": str(order.get("id")),
                "carrier": latest.get("tracking_company"),
                "tracking_number": latest.get("tracking_number"),
                "tracking_url": latest.get("tracking_url"),
                "status": order.get("fulfillment_status") or "pending",
            },
            ctx.request_id,
        )

    @app.get("/v1/account/get")
    def account_get() -> dict[str, Any]:
        raise err(
            "ACTION_NOT_SUPPORTED",
            "account get is not implemented for this shop yet",
            status_code=501,
        )

    @app.get("/v1/payments/get/{order_id}")
    def payments_get(order_id: str) -> dict[str, Any]:
        raise err(
            "ACTION_NOT_SUPPORTED",
            f"payments get for order '{order_id}' is not implemented for this shop yet",
            status_code=501,
        )

    return app


app = create_shopify_app()


def run() -> None:
    cfg = load_settings()
    uvicorn.run("gss_webshop_shopify.app:app", host=cfg.host, port=cfg.port, reload=cfg.debug)
