# Shopify Test Store Project

This is a webshop project inside the GSS repo, wired for a Shopify test store.

It demonstrates the intended production boundary:

- GSS packages provide protocol contracts and orchestration.
- The webshop project owns credentialing, token/session behavior, and infra choices.

## Current Implementation

- Implemented:
  - `describe`
  - `auth login` (shop-owned local session token for development)
  - `orders list/get` (Shopify Admin API)
  - `shipping track`
- Strictly not supported (for now):
  - `account get`
  - `payments get`

Unsupported actions return `ACTION_NOT_SUPPORTED`.

## Setup

1. Copy env template:

```bash
cp webshop/shopify-test-store/.env.example .env
```

2. Fill Shopify values:
- `SHOPIFY_SHOP_DOMAIN`
- `SHOPIFY_ADMIN_TOKEN`

3. Run provider:

```bash
gss-shopify-provider
```

Provider runs by default at `http://127.0.0.1:8010/v1`.

## Quick Test

```bash
gss mockshop.local describe
GSS_DEFAULT_ENDPOINT=http://127.0.0.1:8010/v1 gss mystore.myshopify.com auth login --method api_key --customer-id CUST-001
GSS_DEFAULT_ENDPOINT=http://127.0.0.1:8010/v1 gss mystore.myshopify.com orders list
```

## Important Note

The auth flow in this project is intentionally development-oriented. For production, replace login/session behavior with your real customer auth integration.
