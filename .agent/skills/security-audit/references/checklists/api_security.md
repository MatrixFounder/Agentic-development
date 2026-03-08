# OWASP API Security Top 10:2023 — Checklist

> **Source:** OWASP API Security Top 10 (2023 Final).
> **Scope:** REST APIs, GraphQL, gRPC, WebSocket endpoints.

## API1: Broken Object Level Authorization (BOLA)
- [ ] **IDOR:** Can User A access User B's objects by manipulating IDs in URLs/params?
- [ ] **UUID vs Sequential:** Are resource identifiers unpredictable (UUIDs, not auto-increment)?
- [ ] **Server-Side Auth:** Is authorization checked server-side for every object access (not just client-side filtering)?
- [ ] **Batch Endpoints:** Do bulk/list endpoints enforce per-object authorization?

## API2: Broken Authentication
- [ ] **Credential Stuffing:** Are rate limits and account lockout applied to login endpoints?
- [ ] **Token Strength:** Are tokens (JWT, API keys) sufficiently long and random?
- [ ] **Token Expiry:** Do access tokens have short TTLs? Are refresh tokens rotated on use?
- [ ] **API Key Scope:** Are API keys scoped to specific endpoints/operations?
- [ ] **mTLS:** Is mutual TLS used for service-to-service authentication?

## API3: Broken Object Property Level Authorization (BOPLA)
- [ ] **Mass Assignment:** Can users set fields they shouldn't (e.g., `role`, `isAdmin`, `price`) via POST/PUT?
- [ ] **Excessive Data Exposure:** Does the API return more fields than the client needs (e.g., `password_hash`, `ssn`)?
- [ ] **Allowlist Fields:** Are writable fields explicitly allowlisted (not blocklisted)?
- [ ] **GraphQL Introspection:** Is introspection disabled in production?

## API4: Unrestricted Resource Consumption
- [ ] **Rate Limiting:** Are per-user, per-IP, and per-endpoint rate limits configured?
- [ ] **Pagination:** Are list endpoints paginated with max page size enforced server-side?
- [ ] **File Upload Limits:** Are file size, count, and type validated?
- [ ] **Query Complexity:** Are GraphQL query depth and complexity limited?
- [ ] **Batch Size:** Are batch/bulk operations limited in size?

## API5: Broken Function Level Authorization (BFLA)
- [ ] **Admin Endpoints:** Are admin/management endpoints separated and access-controlled?
- [ ] **HTTP Method:** Can changing GET→PUT→DELETE bypass authorization?
- [ ] **Endpoint Discovery:** Are undocumented/debug endpoints exposed? (`/admin`, `/debug`, `/internal`)
- [ ] **Role Enforcement:** Is RBAC/ABAC enforced consistently across all endpoints?

## API6: Unrestricted Access to Sensitive Business Flows
- [ ] **Abuse Scenarios:** Can the API be used for scraping, scalping, spamming, or enumeration?
- [ ] **Bot Detection:** Are CAPTCHA/fingerprinting/behavioral analysis applied to sensitive flows?
- [ ] **Business Logic:** Can the purchase flow be manipulated (negative quantities, price tampering)?

## API7: Server-Side Request Forgery (SSRF)
- [ ] **URL Validation:** Are user-supplied URLs validated against an allowlist?
- [ ] **Internal Network:** Can the API be tricked into accessing internal services (169.254.169.254, localhost)?
- [ ] **DNS Rebinding:** Are DNS resolution results cached and validated?
- [ ] **Redirect Following:** Does the API follow redirects to internal resources?

## API8: Security Misconfiguration
- [ ] **CORS:** Is `Access-Control-Allow-Origin` restricted (not `*`)?
- [ ] **Error Messages:** Do API errors expose stack traces, SQL queries, or internal paths?
- [ ] **HTTP Methods:** Are unnecessary HTTP methods (TRACE, OPTIONS) disabled?
- [ ] **Security Headers:** Are `Strict-Transport-Security`, `Content-Security-Policy`, `X-Content-Type-Options` set?
- [ ] **TLS:** Is TLS 1.2+ enforced? Are weak cipher suites disabled?
- [ ] **Default Credentials:** Are default API keys/passwords changed?

## API9: Improper Inventory Management
- [ ] **API Versioning:** Are deprecated API versions still accessible? Are they sunset properly?
- [ ] **Shadow APIs:** Are there undocumented endpoints serving traffic?
- [ ] **Environment Isolation:** Are staging/dev APIs accessible from the internet?
- [ ] **Documentation:** Is the API specification (OpenAPI/Swagger) up to date?

## API10: Unsafe Consumption of APIs
- [ ] **Third-Party Validation:** Is data from third-party APIs validated and sanitized?
- [ ] **Timeout/Retry:** Are timeouts configured for external API calls? Is retry logic bounded?
- [ ] **Circuit Breaker:** Is a circuit breaker pattern used for unreliable external APIs?
- [ ] **TLS Verification:** Is TLS certificate verification enabled for outbound API calls (`verify=True`)?
- [ ] **Redirect Following:** Are redirects from third-party APIs limited and validated?
