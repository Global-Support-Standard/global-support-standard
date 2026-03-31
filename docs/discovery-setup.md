# Discovery Setup (Simple)

Use this guide to make sure `gss <shop-domain> ...` works without manual endpoint exports.

## How CLI discovery works

The CLI resolves endpoints in this order:

1. `GSS_SHOP_<SHOP_DOMAIN>_ENDPOINT`
2. `GSS_DEFAULT_ENDPOINT`
3. `https://<shop-domain>/.well-known/gss.json`
4. DNS TXT `_gss.<shop-domain>`
5. local fallback `http://127.0.0.1:8000/v1`

## Option A (recommended): `.well-known/gss.json`

Place this on the webshop's own domain:

- URL: `https://<shop-domain>/.well-known/gss.json`
- Content type: `application/json`

Example:

```json
{
  "endpoint": "https://gss-provider.example.com/v1/<shop-domain>"
}
```

## Option B: DNS TXT fallback

Create a TXT record:

- Host: `_gss.<shop-domain>`
- Value: `endpoint=https://gss-provider.example.com/v1/<shop-domain>`

## SaaS provider pattern (multi-tenant)

For each customer shop domain:

1. Keep one shared runtime (for example `https://gss-provider.example.com`)
2. Route by tenant/shop in path (for example `/v1/<shop-domain>`)
3. Ask customer to publish either:
   - `/.well-known/gss.json` on their shop domain, or
   - `_gss.<shop-domain>` TXT record

The discovery source is always the customer domain. This keeps domain ownership and trust clear.

## Self-hosted webshop pattern

If a webshop hosts its own GSS provider:

1. Deploy provider endpoint (for example `https://shop.com/v1`)
2. Publish:
   - `https://shop.com/.well-known/gss.json` with `{"endpoint":"https://shop.com/v1"}`
   - optionally `_gss.shop.com` TXT as backup

## Quick verification

```bash
gss <shop-domain> describe
```

If discovery is configured correctly, this works without setting endpoint env vars.
