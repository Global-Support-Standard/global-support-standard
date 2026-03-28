# Registry Conformance Checklist

Use this checklist to verify that a GSS registry implementation is safe and compatible.

## How to use

- Mark each item as pass/fail.
- A production registry should pass all required items.
- If any required item fails, do not label the registry as trusted.

## A. Registration and Challenge Flow (required)

- [ ] Registration request accepts `shop_domain`, `endpoint`, `gss_version`, `contact_email`.
- [ ] Registry does not auto-verify on registration alone.
- [ ] Registry returns a challenge (`challenge_id`, `challenge_token`, `expires_at`, `methods_allowed`).
- [ ] Challenge expires within configured TTL (recommended 15-30 minutes).
- [ ] Expired challenges return `CHALLENGE_EXPIRED`.

## B. Domain Ownership Verification (required)

- [ ] DNS TXT verification works using `_gss-verify.<shop-domain>`.
- [ ] Well-known verification works at `/.well-known/gss-verification`.
- [ ] Verification only succeeds when challenge id and token both match.
- [ ] Unverified domains cannot become `verified` status.
- [ ] Unverified domains are never returned as trusted discovery results.

## C. Conflict and Anti-Troll Controls (required)

- [ ] Claiming an already verified domain triggers conflict handling.
- [ ] Registry returns `VERIFICATION_CONFLICT` on conflicting ownership claims.
- [ ] Endpoint changes require re-verification.
- [ ] Registration/verification attempts are rate limited.
- [ ] Abuse thresholds block repeated malicious attempts (`ABUSE_BLOCKED`).

## D. Re-verification and Lifecycle (required)

- [ ] Verified entries include `next_reverify_at`.
- [ ] Registry re-verifies entries periodically (recommended 30-90 days).
- [ ] Failed re-verification transitions entry to non-trusted state (`suspended` or equivalent).
- [ ] Consumers can distinguish `verified`, `pending`, and `suspended`.

## E. API and Schema Compatibility (required)

- [ ] Registration request matches `schemas/registry/registration-request.schema.json`.
- [ ] Challenge response matches `schemas/registry/challenge-response.schema.json`.
- [ ] Verification response matches `schemas/registry/verification-response.schema.json`.
- [ ] Error responses match `schemas/registry/error-response.schema.json`.

## F. Discovery Trust Semantics (required)

- [ ] Consumer docs state trust order: `.well-known` -> DNS TXT -> registry.
- [ ] Registry docs explicitly describe itself as fallback, not source of truth over domain-controlled methods.
- [ ] Registry responses expose enough metadata for clients to warn on low trust states.

## G. Observability and Operations (recommended)

- [ ] Registration and verification attempts are logged with request IDs.
- [ ] Security-relevant events (conflicts, abuse blocks, re-verification failures) are auditable.
- [ ] Transparency log exists for historical claim tracking.
- [ ] On-call/runbook exists for domain ownership disputes.

## Final Conformance Gate

A registry implementation is considered conformant only if:

- all required items in sections A-F pass, and
- no high-severity security finding remains open.
