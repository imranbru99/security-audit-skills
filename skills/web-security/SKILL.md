---
name: web-security
description: >-
  Finds web vulnerabilities such as XSS, CSRF, SSRF, IDOR, open redirects,
  path traversal, insecure file upload, and CORS misconfiguration, and checks
  framework escaping before reporting. Use when reviewing HTTP handlers,
  templates, browsers, cookies, uploads, or redirects, or when the user
  mentions XSS, CSRF, SSRF, IDOR, clickjacking, or web application security.
license: MIT
compatibility: Agent Skills clients. No packages or network required.
metadata:
  category: security
---

# Web application security

Review the HTTP and browser boundary. A web bug is confirmed only when attacker-controlled data crosses a boundary the framework does not already close.

Pair with `auth-security` for the ownership check, `injection-security` for SQL and command sinks, and the language skill for framework defaults. Verdicts follow `security-audit` when that skill is loaded: no trust boundary, no finding.

## When to use

Use this skill for HTML responses, cookie sessions, redirects, file downloads and uploads, server-side fetches, and CORS. Skip it for a pure CLI, library, or batch job with no HTTP or HTML surface. For a JSON API with no browser, use `api-security` and keep the SSRF and path-traversal sections from this skill.

## Method

1. List routes that return HTML, set cookies, redirect, read or write files, or call an outbound URL.
2. Note the template engine and whether auto-escape is on. Note cookie `SameSite`, `HttpOnly`, and `Secure`, and any CSRF middleware and which route groups it covers.
3. For each lead below, trace request data to the sink. Include hidden inputs, filenames, `Referer` only when the app trusts it, and values previously stored by another user (stored XSS).
4. Disprove the lead using the false-positive section before you report it.

## What to look for

### Cross-site scripting

The bug is attacker-controlled content rendered in a context whose encoding does not match that context.

| Context | Usually safe when | Still a lead |
| --- | --- | --- |
| HTML text | Framework auto-escape is on and the call site does not opt out | `dangerouslySetInnerHTML`, `v-html`, `{!! !!}`, `\|safe`, `mark_safe`, `innerHTML`, `document.write` |
| HTML attribute | Value is quoted and escaped | Unquoted attributes, URL attributes (`href`, `src`) |
| URL (`href`, `src`) | Scheme allowlist (`https`, relative paths) | `javascript:` or data URLs accepted from the user |
| JavaScript string or inline event | Data is passed as a JS value the encoder understands | HTML-escaped data dropped into `<script>` or `onclick` |
| Stored content | Render path escapes | Markdown or HTML rendered raw, SVG served same-origin and opened as a document |

CSP is a backstop. `unsafe-inline` or a nonce that the attacker can also inject does not close the bug. Report the sink, and mention CSP only as defense in depth.

### Cross-site request forgery

Confirm CSRF only when all of these are true:

- The browser will attach the credential on a cross-site request. A session cookie will. An `Authorization` header the page's own JavaScript sets will not, unless a CORS configuration also lets the attacker read the response (that is a CORS bug, not CSRF).
- The action changes state or performs a sensitive operation. Logout and one-click purchases count. A read-only GET does not, unless the GET itself changes state.
- The route does not check a synchronizer token, a double-submit cookie that is not trivially copied, or the framework CSRF middleware.
- `SameSite` does not already block the request. `Lax` and `Strict` block cross-site POST from a modern browser. They do not block a same-site attacker (another app on a sibling subdomain) and they do not block state-changing GET. `SameSite=None` does not help.

### Server-side request forgery

The server issues an HTTP, DNS, or similar request to a host the attacker chooses, including via a redirect the client follows.

Leads: webhook delivery, "import from URL", PDF renderers fetching the page, image proxies, SSO metadata URLs, health-check URLs stored per tenant.

A string denylist (`block "localhost"`, `block "169.254"`) is not a fix. An allowlist of registered hosts is the control that holds. Also check: redirects followed after the check, DNS resolution that is not pinned to the address you validated, and non-HTTP schemes (`file:`, `gopher:`, `dict:`) accepted by the client library.

Impact is the network position of the fetcher: link-local metadata, internal admin ports, or another tenant's private URL. If you cannot see that position, keep the code defect and mark the blast radius needs-validation. Do not prove it by calling a live metadata service.

### Insecure direct object reference

Report IDOR when a handler loads or mutates an object by an identifier from the request and does not bind that object to the caller or to an explicit permission. The identifier's shape (int, UUID) does not matter. The check must be in the query or in a policy that runs on every path, not only in the UI.

Horizontal: another user's object. Vertical: an admin field or route a normal user can hit (`is_admin`, `role`, price, a `/admin` handler mounted without the admin middleware).

### Open redirect

The next URL, `Location`, or OAuth `redirect_uri` is taken from the request and not restricted to an allowlist of hosts the code parses as hosts. A `startsWith("https://good.example")` check is not a host check.

Rate phishing redirects on whether a token, authorization code, or password-reset link can ride the redirect. A generic `?next=` on a marketing page with no credential is Low.

### Path traversal and files

User input concatenated or joined into a filesystem path, archive entry name, or object-storage key. The safe pattern is: resolve the path, then verify it is still inside the intended root (`filepath.Rel` / `Path.relative` and reject `..`).

Also look for uploads stored under a web root with the original filename, content-type taken from the client, and SVG or HTML uploaded and then served same-origin. Client-supplied `Content-Type` is not a control.

Null-byte truncation is a lead only on stacks that actually truncate C strings. Do not report it on current Python, Go, or modern Node.

### CORS, clickjacking, headers

Report reflected `Origin` plus `Access-Control-Allow-Credentials: true` when a browser-authenticated API returns sensitive data. `Access-Control-Allow-Origin: *` cannot be used with credentials; browsers reject that combination, so do not report it as "credentialed wildcard."

Report clickjacking when a sensitive HTML action can be framed and neither `frame-ancestors` nor `X-Frame-Options` is set. Do not report it on JSON APIs or on pages with no sensitive action.

Cookie flags: missing `HttpOnly` matters when an XSS sink exists or is likely in the same origin; otherwise it is defense in depth. Missing `Secure` matters when the app is served over HTTPS and the cookie would also be sent on HTTP.

### Host header and cache

If password-reset or OAuth links are built from `Host` or `X-Forwarded-Host` without an allowlist, report password-reset poisoning. If a cache keys on the URL and not on `Host` while the app varies on `Host`, report cache poisoning only when you can see both the cache behavior and the variance. Otherwise needs-validation.

## Verify before you report

1. Show the request field or stored field the attacker sets.
2. Show the sink and the encoder, or the absence of an ownership, CSRF, allowlist, or path-root check.
3. Confirm the framework default does not close it. Read the route group, not just the handler. For XSS, name the output context.
4. State the victim: another user's browser, the server's network, another user's object, or a login redirect that carries a code.
5. If a gateway, CDN, or CSP lives outside the repo and would change the verdict, mark needs-validation and say which fact is missing.

Do not attach a proof-of-concept request aimed at a deployed host. Describe the source path. A benign local marker is enough to explain an encoding failure.

## Severity

| Bug | Typical rating | Raise or lower |
| --- | --- | --- |
| Stored XSS in a page other users see | High | Critical if it runs in an admin browser and the session cookie is readable or the action is privileged. Lower if the content is only shown back to the author. |
| Reflected XSS | Medium | High if it sits on a privileged page or steals a token the script can read. |
| CSRF on a sensitive cookie action | Medium | High when the action changes a password, email, or payout destination and SameSite does not block it. |
| SSRF with attacker-controlled host | High if internal or metadata reach is in the deployment config; Medium if reach is unknown | Lower if a real allowlist constrains the host. |
| IDOR on sensitive objects | High | Medium for non-sensitive fields. See `auth-security`. |
| Open redirect | Low, or Medium on an OAuth or reset flow | |
| Path traversal to files outside the root | High if those files are sensitive or executable; Medium if you only show escape from the folder | |
| Missing header with no scenario | Info or drop | |

## Examples

Stored XSS, unsafe and safe:

```jsx
// Unsafe: comment.body is rendered as HTML.
<div dangerouslySetInnerHTML={{ __html: comment.body }} />

// Safe: React escapes text children.
<div>{comment.body}</div>
```

If the product must render a subset of HTML, sanitize on write or on render with a maintained HTML sanitizer, configured to drop scripts, event handlers, and unexpected URL schemes. Escaping the whole string is the default.

CSRF is a missing check, not a special token library. On a cookie-authenticated POST, reject the request unless the framework CSRF check or an explicit token check ran for that route.

## False positives

- Auto-escaped templates, until you find the opt-out or a context the escaper does not cover (JavaScript string, URL scheme).
- React, Vue, Django, Rails, and Laravel default escaping. Report the opt-out, not the template engine.
- CSRF on bearer-token APIs, or on POST routes whose session cookie is `SameSite=Lax` or `Strict`, unless a same-site attacker is in scope or the method is a state-changing GET.
- IDOR from "the id is in the URL" when the query also filters on the caller's user id or a policy runs and denies.
- SSRF when the host is a fixed constant or a server-side allowlist, not user input. User choice among allowlisted hosts is not SSRF.
- Open redirect when the target is chosen from a fixed map of keys.
- Clickjacking and cookie-flag findings with no sensitive action and no XSS path. Mention them as Info only if the user asked for hardening.
- Path traversal after a correct root check (`Clean` plus a relative-path test that rejects `..`).

## Related skills

`auth-security` for object and role checks. `api-security` for JSON APIs, mass assignment, and webhook signatures. `injection-security` when the web input reaches SQL, a shell, or a template engine. Language skills for the framework's escape and middleware defaults.
