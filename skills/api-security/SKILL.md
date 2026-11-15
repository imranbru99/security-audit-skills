---
name: api-security
description: >-
  Reviews HTTP and GraphQL APIs for broken object and function authorization,
  mass assignment, excessive data exposure, webhook authentication gaps, and
  unbounded expensive operations. Use when reviewing routes, controllers,
  resolvers, API schemas, or when the user mentions API security, REST,
  GraphQL, BOLA, mass assignment, or webhooks.
license: MIT
compatibility: Agent Skills clients. No packages or network required.
metadata:
  category: security
---

# API security

Review the API as a set of operations on objects, not as a list of URLs. The questions are: who can call this, which object can they name, which fields can they set, and which fields come back.

Use `auth-security` for session and token internals, `web-security` for browser CSRF, CORS, and SSRF, and `injection-security` when a parameter reaches a query.

## When to use

Use this skill for REST, JSON-RPC, GraphQL, gRPC reflected through an HTTP gateway, and webhooks. Use it on a diff that adds a route, a serializer, a resolver, or a webhook handler. Skip static sites with no data API.

## Method

1. Enumerate operations from the router, OpenAPI spec, GraphQL schema, or RPC service. Note which are unauthenticated.
2. For each operation that takes an object id, a filter, or a foreign key, find the authorization check. "Logged in" is not object authorization.
3. Compare write models to the fields a client may send, and response models to the fields a client should see.
4. For webhooks and callbacks, find the signature or shared-secret check and what bytes it covers.
5. Disprove each lead. Middleware and generated resolvers count.

## What to look for

### Broken object authorization

The handler loads by id, slug, or GraphQL global id and does not constrain the row to the caller, the tenant, or a permission.

```text
GET /api/invoices/1042
GET /api/users/me          <- the "me" alias is fine; /api/users/1042 is a different operation
POST /graphql  { customer(id: "1042") { ssn } }
```

A filter in the UI is not a control. A UUID is not a control. A check that runs only on `GET` while `PUT` and `DELETE` update by id is a finding on the unchecked methods.

Multi-tenant apps: the tenant id must come from the session or token, not from a client-supplied header or body field, unless that field is signed or checked against membership.

### Broken function authorization

Admin or staff operations registered on the user router. Role checked in the client. GraphQL fields on an admin type that resolve for any authenticated user because the field has no directive and the parent resolver's check is not re-applied.

Look for `role`, `isAdmin`, `is_staff`, and feature flags taken from the request body.

### Mass assignment

The handler binds the request object onto a persistence model.

Leads: `Object.assign(user, req.body)`, `user.update(request.all())`, Pydantic or Jackson models that include `role`, `is_admin`, `owner_id`, `price`, `balance`, or `email_verified`, and GraphQL input types that expose those fields.

The fix is an allowlist of fields the operation may change, plus authorization if the subject is not "self." Hiding the field in the form is not a fix.

### Excessive data exposure

Serializers that return the ORM object. Password hashes, reset tokens, MFA secrets, internal notes, other tenants' ids, and raw payment identifiers in a JSON response are findings when the caller should not have them. A hash is still a secret if it is a password hash.

GraphQL: a type that exposes an email or token because some other query legitimately returns it, reused here without a field-level check.

### Webhooks and callbacks

A state-changing webhook with no signature, a signature over the parsed JSON rather than the raw body, or a comparison with `==` / `!=` (see `crypto-misuse`). Timestamp and replay: if the signature does not cover a timestamp, or the handler does not reject old timestamps, duplicates can replay the event. Report replay when the operation is not idempotent (ships a second order, grants credit).

SSRF via a customer-supplied callback URL is `web-security`.

### Auth on the edge of the API

- API keys in query strings (they land in access logs and `Referer`). Header or `Authorization` is the expected place.
- `GET` that changes state.
- Versioned routes where `/v1` is guarded and `/v2` or an old alias is not.
- Method override headers (`X-HTTP-Method-Override`) that turn a CSRF-safe GET into a write. Report only if the override is honored.
- Debug or metrics routes mounted in the same server and left unauthenticated (`/debug`, pprof, GraphiQL in production). pprof and debug endpoints that expose heap or env are High when reachable.

### GraphQL specifics

- Resolver auth missing because the schema field was added without the directive the rest of the schema uses.
- `node(id:)` loaders that fetch by global id and skip the type's auth.
- Unbounded list fields and nested queries that can exhaust the database. Report when there is no depth, cost, or pagination limit and the query is available to anonymous or low-trust callers. Introspection enabled is Info, not a vulnerability.
- Batching that bypasses a per-request rate limit.

### Resource consumption

Report missing rate limits only for operations with a concrete cost: login and OTP guesses, password reset mail, expensive exports, invitation floods, or unauthenticated work that fans out to a third party the operator pays for. "No rate limit on the API" is not a finding.

## Verify before you report

1. Identify the operation and the principal the code believes the caller is.
2. Show the load or mutation. Quote the filter. If the filter is only `_id: req.params.id`, the ownership check is absent unless a policy layer adds one. Look for that layer before reporting.
3. For mass assignment, name the dangerous field and show it is set from the client and persisted.
4. For excessive data, name the field in the response and why this caller should not receive it.
5. For webhooks, show the missing or mismatched signature check. Do not forge a signed event against a live endpoint.
6. If an API gateway is supposed to authorize and its config is not in the repo, mark needs-validation. If the app also trusts a client-supplied user id header, say that clearly.

## Severity

| Bug | Typical rating |
| --- | --- |
| Any authenticated user reads or changes another user's private object | High |
| Client sets `role`, `balance`, `price`, or `owner_id` and the server persists it | High |
| Password hash, reset token, or MFA seed in a response | High |
| Staff-only operation missing the role check | High if a normal user can reach it; drop if only admins can call the route |
| Unsigned webhook that changes state | High when the sender is untrusted and the effect is a payment, grant, or deploy; Medium for low-impact notifications |
| Expensive unauthenticated operation with no bound | Medium |
| API key in the query string | Low, or Medium when access logs are widely readable |
| GraphQL introspection, missing pagination on a small table | Info or Low |

## Examples

Mass assignment:

```javascript
// Unsafe: isAdmin and ownerId ride along with name.
app.patch("/api/users/:id", requireUser, async (req, res) => {
  const user = await User.findById(req.params.id);
  Object.assign(user, req.body);
  await user.save();
  res.json(user);
});

// Safe: this caller may change only these fields on their own row.
const { name } = req.body;
if (String(req.params.id) !== String(req.user.id)) {
  return res.status(403).end();
}
await User.updateOne({ _id: req.user.id }, { $set: { name } });
```

Webhook:

```javascript
// Unsafe: anyone who can reach the route can mark the order paid.
app.post("/webhooks/billing", express.json(), async (req, res) => {
  await orders.markPaid(req.body.orderId);
  res.sendStatus(204);
});
```

The fix checks a signature over the raw body with a constant-time compare, rejects stale timestamps, and only then changes the order. Parsing JSON before verifying means the verifier must use the original bytes, not a re-serialization.

## False positives

- Object id in the URL when the query also constrains `user_id` or `tenant_id` to the authenticated principal.
- Admin routes behind a middleware you traced and that runs for that method.
- Binding `req.body` onto a DTO that contains only safe fields, then copying those fields explicitly.
- Returning a user's own email to themselves.
- GraphQL introspection, CORS `*` on a response that does not use cookies and holds no secrets.
- Missing rate limit on an ordinary authenticated read.
- A webhook signature that covers the raw body, uses a constant-time compare, and the route rejects missing signatures. Do not report "custom crypto" if the construction is HMAC-SHA256 of the body with the timestamp included and checked.

## Related skills

`auth-security` for how the principal is established. `web-security` for CSRF, CORS, and SSRF. `injection-security` for query parameters that become queries. `secrets-exposure` for keys logged by the framework's request logger.
