---
name: auth-security
description: >-
  Reviews authentication and authorization, including passwords, sessions,
  JWT, OAuth and OIDC, password reset, and object-level access checks. Use
  when reviewing login, tokens, cookies, guards, or policies, or when the user
  mentions auth, authn, authz, sessions, JWT, OAuth, SSO, or access control.
license: MIT
compatibility: Agent Skills clients. No packages or network required.
metadata:
  category: security
---

# Authentication and authorization

Authentication answers who the caller is. Authorization answers what that caller may do to this object. Review them separately. A perfect login does not fix a missing ownership check.

Use `crypto-misuse` for password hashing, randomness, and signature comparison. Use `api-security` for mass assignment and response shaping. Use `web-security` for CSRF and cookie flags as browser behavior.

## When to use

Use this skill whenever a request is associated with an identity, a token, a session, or a role, including "this route is public on purpose." Public routes still need a check that they are not accidentally private operations.

## Method

1. Find where the principal is created: login, signup, SSO callback, API key lookup, service-to-service identity.
2. Find where it is enforced: middleware, dependency, decorator, gateway. List routes not covered by that enforcer.
3. For each object operation, find the check that binds the object to the principal. If it is missing, that is the finding, not "weak auth" in the abstract.
4. Walk account lifecycle: reset, email change, MFA, logout, session revocation, invite acceptance.
5. Treat identity-provider claims as untrusted for authorization unless the app maps them through its own membership store. An `admin: true` claim from a customer-controlled IdP is not an admin check.

## What to look for

### Passwords

- Compared in application code against a plaintext or reversible value.
- Hashed with a fast hash (MD5, SHA-1, SHA-256) or encrypted instead of hashed. Use a password hash (argon2id, bcrypt, scrypt) via a maintained library.
- Truncated by the hash function in a way the code does not account for (bcrypt's 72-byte limit) only if the code claims longer secrets are fully used.
- Logged, placed in query strings, or returned in API errors.
- Reset or login that reveals whether the account exists, when the rest of the product treats that as sensitive. Report account enumeration only if the responses differ and the account list is sensitive. Identical generic errors are not a finding.

### Sessions

- Session id not regenerated after login (fixation), when the id was attacker-settable before login.
- Remember-me or session token stored in the database in plaintext and selected by that value. Store a hash; look up by hash.
- Logout that does not invalidate the server-side session, when the session is server-side. Stateless JWT logout is a different problem: report long-lived tokens with no revocation list only if the lifetime is long enough to matter (days) and the app has a logout control that implies revocation.
- Cookie flags: see `web-security`. Do not make missing `HttpOnly` a Critical finding on its own.

### JWT and opaque tokens

Confirm the library and version before claiming an algorithm is accepted.

Leads worth opening:

- Signature not verified, or verified with a secret hardcoded in the client or the repo.
- `algorithms` not pinned, or `none` explicitly allowed.
- `exp`, `iss`, and `aud` not checked when the token is accepted from outside a single service you control.
- `kid` or `jku` used to choose a key file, a URL, or a database row. Treat that as path traversal, SSRF, or SQL injection, not as a crypto footnote.
- Encryption (`alg` for JWE) confused with signing. A token the app can decrypt is not a token it has authenticated unless there is also a signature or an AEAD the server alone can produce.
- Public key used as an HMAC secret (algorithm confusion). Report it when verification accepts both HMAC and RSA for the same key material, or when the code branches on the token's `alg` header to pick the method. The fix is to pin the algorithm on the server and ignore the header's suggestion.

Do not forge tokens against a live service to prove the lead.

### OAuth and OIDC

- `redirect_uri` matched by prefix, substring, or an open wildcard, or taken from the query string at authorization time and not checked against a registered list.
- `state` missing on the authorization request, or not checked on the callback. That is CSRF on the login binding.
- Public clients (mobile, SPA) using the code flow without PKCE.
- ID token accepted without checking signature, `iss`, `aud`, and `exp`.
- Access token treated as a user id without introspection or signature verification.
- Authorization code or token written to logs.

### Authorization

For every handler that reads or writes an object:

- The object id comes from the client.
- The code must load the object in a way that includes the principal (`WHERE id = ? AND user_id = ?`) or must call a policy that knows both.
- A role check (`isAdmin`) authorizes an action, not an object. Admins who may see all objects are fine when the code actually distinguishes that role. A comment that says "admin only" is not a check.
- Feature flags and tenant ids taken from the client are leads, same as missing filters.

Horizontal access (another user) and vertical access (a higher role) are separate findings when the fixes differ.

Deny by default. A route added outside the guarded group is a finding even if the handler is empty of "vulnerable looking" code, if it exposes a private operation.

### Account recovery and email change

- Reset token from `rand()`, `Math.random()`, or a timestamp.
- Token stored plaintext, logged, or placed in a URL that is then copied into logs by default request logging. Prefer a high-entropy token, stored hashed, single-use, short expiry.
- User id in the reset request is trusted and the token is not bound to that user.
- Reset link host comes from the `Host` header (poisoning). Use a configured origin.
- Email change does not require the current session secret or does not confirm the new mailbox, and the product uses email for reset. Report account takeover only when that chain is actually open.
- Token compared with `==` in languages where that operator is not a constant-time or type-safe compare (PHP `==` is a lead; see `php-security`).

### Service and internal auth

- Trust of `X-User-Id`, `X-Forwarded-For` as an identity, or any header the edge is supposed to strip, when the app is also reachable without that edge.
- Shared service tokens committed to the repo. That is `secrets-exposure` plus this skill if the token is the only authorization.

## Verify before you report

1. Name the principal and the object or action.
2. Show the check that is missing or the check that uses attacker-controlled data (client role, client tenant, unsigned claim).
3. Show that the route is actually exposed. A function with no route is not a finding until something calls it with attacker input.
4. For JWT and OAuth, name the library behavior you relied on. If the version is unknown and the verdict depends on it, mark needs-validation.
5. Do not log in to production, stuff sessions, or mint tokens to prove the point.

## Severity

| Bug | Typical rating |
| --- | --- |
| Authentication bypass on routes that expose other users | Critical if unauthenticated and broad; High if it still needs a low-trust account |
| Missing object-level check on sensitive data | High |
| Client-controlled role or tenant persisted or trusted | High |
| Forged session because the signature is not checked or the secret is public | Critical or High, matching who can call it |
| Session fixation with a settable pre-login id | Medium, High if the id is easy to plant and the session is privileged |
| Reset token with low entropy or no binding to the user | High |
| Open OAuth redirect or missing `state` | Medium, High if it binds the victim to the attacker's IdP account |
| Account enumeration via error text | Low when account existence is sensitive; otherwise drop |
| Long JWT lifetime with no revocation | Low or Medium, based on lifetime and token power. Not High by itself |

## Examples

Object authorization:

```javascript
// Unsafe: any logged-in user who knows the id.
const order = await Order.findById(req.params.id);

// Safe: the row must belong to the caller. Missing row and forbidden
// row both end as 404 so the handler does not become an existence oracle
// for sequential ids. The filter is the control, not the status code.
const order = await Order.findOne({ _id: req.params.id, userId: req.user.id });
if (!order) return res.status(404).end();
```

JWT verification must pin the algorithm and the expected issuer and audience, and the secret or public key must come from configuration, not from the token. See `examples/node-jwt/` in this collection when you are reviewing inside the repo.

## False positives

- A numeric id with a real ownership filter.
- 403 versus 404. Do not report an existence oracle for random, unguessable ids. Do not recommend a status-code change as the fix for a missing filter.
- JWT in `localStorage` with no XSS sink. Mention the storage choice only as an amplifier if XSS is confirmed.
- Missing MFA. That is a product requirement, not a code bug, unless the code claims MFA and the check is skippable.
- OAuth `state` on a confidential server-side flow that already binds the transaction in a server session and checks it. Still report a missing check if the callback trusts the code without that binding.
- Admin-only tools when the enforcer really wraps those routes.
- "JWT is stateless" as a finding with no excessive lifetime or missing verification.

## Related skills

`crypto-misuse` for hashes, HMAC, and randomness. `web-security` for cookies, CSRF, and open redirects. `api-security` for the operation inventory. `secrets-exposure` for hardcoded signing keys.
