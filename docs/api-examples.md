# API Examples

These examples show how to call the provider HTTP API directly.

Default base URL: `http://127.0.0.1:8000/v1`

## 1) Describe shop

```bash
curl -s http://127.0.0.1:8000/v1/describe | jq
```

## 2) Login and capture token

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"method":"api_key","customer_id":"CUST-001"}' | jq -r '.data.access_token')
```

## 3) List orders

```bash
curl -s "http://127.0.0.1:8000/v1/orders" \
  -H "Authorization: Bearer $TOKEN" \
  -H "GSS-Consumer-Id: support-squad-ai" \
  -H "GSS-Consumer-Type: ai_agent" \
  -H "GSS-Version: 1.0" | jq
```

## 4) Get one order

```bash
curl -s "http://127.0.0.1:8000/v1/orders/ORD-1001" \
  -H "Authorization: Bearer $TOKEN" \
  -H "GSS-Consumer-Id: support-squad-ai" \
  -H "GSS-Consumer-Type: ai_agent" \
  -H "GSS-Version: 1.0" | jq
```

## 5) Evaluate protocol

```bash
curl -s -X POST http://127.0.0.1:8000/v1/protocols/get \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -H "GSS-Consumer-Id: support-squad-ai" \
  -H "GSS-Consumer-Type: ai_agent" \
  -H "GSS-Version: 1.0" \
  -d '{"trigger":"delivery-not-received","context":{"order_id":"ORD-1002","days_since_expected":1}}' | jq
```

## 6) Two-step returns flow

### Step A: initiate

```bash
CONFIRMATION_TOKEN=$(curl -s -X POST http://127.0.0.1:8000/v1/returns/initiate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -H "GSS-Consumer-Id: support-squad-ai" \
  -H "GSS-Consumer-Type: ai_agent" \
  -H "GSS-Version: 1.0" \
  -d '{"order_id":"ORD-1001","item_id":"ITEM-1","reason":"defective"}' | jq -r '.data.confirmation_token')
```

### Step B: confirm

```bash
curl -s -X POST http://127.0.0.1:8000/v1/returns/confirm \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -H "GSS-Consumer-Id: support-squad-ai" \
  -H "GSS-Consumer-Type: ai_agent" \
  -H "GSS-Version: 1.0" \
  -d "{\"token\":\"$CONFIRMATION_TOKEN\"}" | jq
```

## 7) Read audit log

```bash
curl -s "http://127.0.0.1:8000/v1/account/audit-log" \
  -H "Authorization: Bearer $TOKEN" \
  -H "GSS-Consumer-Id: support-squad-ai" \
  -H "GSS-Consumer-Type: ai_agent" \
  -H "GSS-Version: 1.0" | jq
```
