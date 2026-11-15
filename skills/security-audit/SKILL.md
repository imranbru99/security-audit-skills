---
name: security-audit
description: >-
  Reviews source for vulnerabilities that cross a real trust boundary, using
  scope, threat modeling, data-flow tracing, an attempt to disprove each lead,
  and a severity rubric. Use when the user asks for a security audit, security
  review, vulnerability assessment, threat model, code review for security, or
  triage of a suspected security bug. Answer a narrow question in guidance
  mode. Run the full workflow only when they ask for a review, audit, or report.
license: MIT
compatibility: Agent Skills clients. No packages or network required.
metadata:
  category: security
---

# Security audit

Find bugs that let an attacker cross a trust boundary. Report the source path, the impact, and the smallest fix. A candidate with no attacker, no asset, and no broken control is not a finding.

This is defensive review of code the user is allowed to read. Do not attack deployed systems, scan third parties, or use credentials you find. Do not write exploits. Verify from source, existing tests, and local reasoning. Redact secrets in anything you write back.

## When to use

| Mode | When | What you produce |
| --- | --- | --- |
| Guidance | A question, a suspected bug, or a design choice. | A direct answer. No report, no extra files. |
| Focused | A diff, a feature, or one bug class. | Findings for that scope, plus what you did not follow. |
| Full | The user explicitly asks to audit or security-review a codebase, or asks for a report. | The workflow below. |

If the request is ambiguous, ask one question: focused review of the change, or a full review of the repo. Do not start a full review silently.

Load a specialist skill when its surface is in scope. Each specialist is written to stand alone if it is the only one installed.

| Skill | Load it for |
| --- | --- |
| `web-security` | HTML, browsers, cookies, redirects, uploads, SSRF |
| `api-security` | HTTP/GraphQL APIs, webhooks, response shaping |
| `auth-security` | Login, sessions, JWT, OAuth, access checks |
| `injection-security` | Queries, commands, templates, parsers |
| `secrets-exposure` | Keys, tokens, PII in source, logs, clients |
| `supply-chain-security` | Dependencies, lockfiles, CI, release |
| `iac-security` | Terraform, Kubernetes, Docker, IAM |
| `crypto-misuse` | Hashing, encryption, TLS, randomness, MACs |
| `python-security` | Python, Django, Flask, FastAPI |
| `javascript-security` | JavaScript, TypeScript, Node, browser apps |
| `go-security` | Go services and libraries |
| `php-security` | PHP and Laravel |

If a specialist is not installed, review that surface from this skill and say which skill you did not have.

## Rules

1. A grep hit is a lead. The finding is the data-flow path.
2. Try to kill every lead before you report it. Framework defaults, middleware, and generated code kill more leads than they create.
3. Prefer the smallest fix that closes the path. "Sanitize input" is not a fix.
4. Severity comes from [references/severity.md](references/severity.md), not from the scariness of the CWE title.
5. If the decisive control is outside the repo, mark needs-validation. Do not assume the control is missing, and do not assume it exists.
6. Do not claim the application is secure. State what you reviewed.
7. On a diff, start at the changed lines and follow data outward. Do not wander the whole repository unless the user asked for a full review or the change touches a shared auth, crypto, or parsing helper.

## Workflow

Copy this list and keep it in the working notes for any full or focused review:

```
- [ ] Scope
- [ ] Map entry points, assets, controls
- [ ] Threat model the boundaries that matter
- [ ] Hunt
- [ ] Disprove each lead
- [ ] Rate and report
```

### 1. Scope

Record the revision (commit, dirty tree, or diff), what is in bounds, and what is not (production cloud account, closed-source SaaS, a service with no code here). For a PR, the default scope is the diff plus the helpers it calls.

### 2. Map

Do this before searching for sinks. Write enough that another reviewer could see the architecture:

- Stack, framework, and where routes or handlers are registered.
- How a request becomes a user identity. Which routes skip that check.
- Data stores, outbound HTTP, file storage, background jobs, admin surfaces.
- Controls that change later verdicts: ORM, template auto-escape, CSRF middleware, cookie flags, `helmet`-style headers, prepared statements, global auth middleware.

Missing this map is how reviews turn into a list of dangerous function names.

### 3. Threat model

For a full review, or a review of auth, tenancy, payments, uploads, or webhooks, write the model in [references/threat-model.md](references/threat-model.md). For a small diff, write the two or three abuse cases the diff creates or weakens. An abuse case names an actor, an entry point, an asset, and the control that should stop it.

### 4. Hunt

Work in this order. Skip a row that does not exist in the target.

1. **Authentication.** Account creation, login, reset, session or token issue, and the middleware that is supposed to require them. Look for routes registered outside the guard.
2. **Authorization.** Every object read and every state change. The check must bind the object to the caller (or to a role that may see all objects). An integer id, a UUID, or "the user is logged in" is not that check.
3. **Injection and templates.** Untrusted data in SQL, NoSQL, shell, file paths, template source, HTML, response headers, and outbound URLs. Open the specialist skill for the sink you found.
4. **Sensitive data.** Secrets in source and config, tokens in logs, password hashes or reset tokens in API responses, overly broad queries.
5. **Crypto that makes a security decision.** Password storage, session randomness, signature compare, TLS verification, encryption mode. Hashing a cache key is not in this row.
6. **Build and deploy,** only if CI, IaC, or dependency manifests are in scope.

Search queries are leads. Start from entry points and walk toward sinks, and from sinks back to the request. A sink with no path from attacker-controlled input is not a finding. Attacker-controlled input includes HTTP fields, uploaded files, webhook bodies, queue messages, imported archives, OAuth claims from an identity provider you do not trust with authorization, and anything another tenant can write.

### 5. Disprove

For every lead, answer these before it becomes a finding. Details are in **Verify before you report** below.

### 6. Rate and report

Use [references/severity.md](references/severity.md) and write the result with [references/report-template.md](references/report-template.md).

In guidance mode, give the same facts in prose. Do not create a report file unless the user asked for one.

Put confirmed findings first, ordered by severity. Then needs-validation. Then a coverage table. Do not pad the report with informational hardening to look thorough.

## Verify before you report

A confirmed finding needs all four:

1. **Source.** The attacker controls the input, or a required security check is absent on a path they can call.
2. **Path.** You traced that input or missing check through the code that actually runs, including middleware and framework conventions (route groups, global filters, ORM parameter binding, template escaping).
3. **Outcome.** Confidentiality, integrity, or a real availability or cost boundary fails for someone other than the attacker, or for the attacker's own session in a way they did not already have (for example, account takeover).
4. **Survival.** You looked for the control that would make this a false positive and it is not on this path.

If step 2 or 4 depends on code, config, or a library version you cannot see, the status is needs-validation.

Useful checks, when they exist in the repo:

- Route registration and middleware order, not just the handler.
- Tests that already encode the security property. A missing test is not a vulnerability. A test that locks in the unsafe behavior is evidence.
- The dependency manifest, when the verdict depends on a framework default or a CVE.

Do not run the target against production data, hit metadata services, or turn a lead into a live exploit to "be sure."

## Severity

Follow [references/severity.md](references/severity.md).

Short form: unauthenticated remote code execution or a live production admin credential in the tree is Critical. Cross-user data or privilege change is High. A concrete bug that needs interaction or has a narrower blast radius is Medium. Limited impact is Low. A missing hardening control with no scenario is Info or a drop.

## False positives

Drop or downgrade these unless the rest of the path is real:

- Dangerous API used only on constants.
- SQL or shell built with an API that binds parameters (`?`, DB-API placeholders passed separately from the SQL string, ORM filters that bind). An f-string or concatenation into the query text is still a lead.
- XSS in a template engine that escapes by default, unless the code opts out (`|safe`, `mark_safe`, `dangerouslySetInnerHTML`, `v-html`, `{!! !!}`, `template.HTML`).
- CSRF on a route authenticated only by a header the browser will not attach cross-site, or on a POST whose session cookie is `SameSite=Lax` or `Strict` with no same-site attacker in scope.
- IDOR because an id is numeric. Report it when the handler loads by id and never binds the row to the caller.
- A CVE whose vulnerable function is not reachable.
- Placeholder secrets that are obviously fake. The published AWS sample pair `AKIAIOSFODNN7EXAMPLE` / `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` is a fixture, not a live key. The same pattern with any other value is a lead.
- Missing rate limit, security header, or cookie flag, until it completes a named attack.
- Scanner output you did not trace.

## Reporting

Use [references/report-template.md](references/report-template.md).

Every confirmed finding states location, attacker, boundary, impact, evidence, why it is not a false positive, the fix, and a regression check. Redact secrets to a prefix or to "redacted" plus where it sits.

The fix should say what to change in code or config. Rotating a leaked credential is part of the fix when a real secret is in history. Do not propose "add a WAF" as the only fix for an injection bug in source.

## Related skills

Use the specialist whose surface you are reviewing. When two skills could apply, use the specialist for the framework detail and this skill for the verdict rule: no boundary, no finding.

Examples of the expected end state live in the collection's `examples/` directory when you are working inside this repository. Those files are intentionally vulnerable fixtures, not code to reuse.
