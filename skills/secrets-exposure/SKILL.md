---
name: secrets-exposure
description: >-
  Finds secrets and sensitive data in source, configuration, logs, error
  messages, and client bundles, and separates live credentials from fixtures.
  Use when reviewing env files, CI, logging, or client code, or when the user
  mentions secrets, API keys, credentials, tokens, PII, or data exposure.
license: MIT
compatibility: Agent Skills clients. No packages or network required.
metadata:
  category: security
---

# Secrets and sensitive data

A secret in the wrong place is a vulnerability when someone who should not have it can read it, or when it will be copied into logs, images, or a client bundle. Report the location and the rotation step. Do not print the secret, and do not call the provider to see if it works.

## When to use

Use this skill when the tree contains config, CI, mobile or frontend bundles, logging, error handlers, or analytics. Use it on any full review, and on diffs that add env reads, log lines, or client-side config. Skip it only when the scope is a pure algorithm with no data and no configuration.

## Method

1. Search for key material and for log/error paths. Treat search hits as leads.
2. Decide what the value is: live credential, build-time public config, test fixture, or documentation example.
3. Decide who can read it: anyone with the repo, anyone who can open the client, anyone with log access, or only the process environment in production.
4. If it is a real credential, the fix is to rotate, purge the copy, and change the path that leaked it. Redact the value in the report.

## What to look for

### In the repository

Leads, not findings until you judge the value:

- Private keys (`-----BEGIN ... PRIVATE KEY-----`), cloud access key ids, API tokens with recognizable prefixes (`sk_live_`, `ghp_`, `xoxb-`, `AKIA`), connection strings with passwords.
- `.env` committed, `terraform.tfvars` with secrets, kube manifests with `data:` instead of a referenced secret manager, CI yaml with a raw token.
- Secrets baked into `Dockerfile` `ENV` or a committed image layer, or passed as build args that remain in history.
- The same value in git history. If the current tree removed it and history still has it, say so. Do not rewrite history unless the user asked; recommend rotation first, then history cleanup.

Known fixture, not a live key: AWS's published example pair `AKIAIOSFODNN7EXAMPLE` with secret `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`. Say that explicitly if those exact values are what you found. Any other `AKIA` value is a lead.

Obvious fakes (`changeme`, `your-api-key-here`, `sk_test_placeholder`, `secret` used only in unit tests that never ship) are not production incidents. If a fake is the default when the env var is missing, report the insecure default, not a leaked key.

### In logs, errors, and analytics

- Authorization headers, cookies, password fields, reset tokens, and request bodies logged by a middleware.
- Exceptions that echo those fields, or a debug page (`APP_DEBUG`, Django `DEBUG`, Whoops) that dumps the environment.
- Tokens in URLs, which then appear in access logs and `Referer`.
- Analytics or error trackers receiving the full URL or the full request.

### In the client

- A secret in frontend source, a mobile app, or a shipped config that is not actually public. "Public" API keys that are designed to be public (some map tiles, publishable payment keys) are not findings if the vendor documents them as publishable and the server enforces origin or quota. A secret key (`sk_live_`, cloud secret, private key) in the client is a finding.
- Server environment spread into `NEXT_PUBLIC_` / `VITE_` / `REACT_APP_` variables. The prefix is the leak. Trace which values are inlined.

### Sensitive data that is not a credential

Report when an API, page, or log returns another person's personal data, a password hash, a reset token, an MFA seed, or a full payment number to a caller who should not have it. That finding is often shared with `api-security`. Do not report "stores email addresses" as a vulnerability.

Encryption at rest that is missing is a finding only when the product or the regulation in scope requires it and the data is sensitive. Do not invent a compliance requirement.

## Verify before you report

1. Show the file and the name of the variable. Redact the value to a short prefix or to `[redacted]`.
2. Say who can read that location (repo readers, website visitors, log readers).
3. Say whether the value looks live, fixture, or public-by-design, and why.
4. Do not call the cloud API, send the token, or decrypt production data to confirm it. If liveness cannot be judged from source, mark needs-validation and tell the owner to rotate if there is any chance it is real.
5. For logs, show the log call and the field, and that the path runs on real requests rather than a test double.

## Severity

| Situation | Typical rating |
| --- | --- |
| Production private key, cloud secret, or admin token readable by repo collaborators or the public | Critical if it clearly grants broad access; High if it is a live-looking third-party token with narrower scope |
| Same secret shipped in a client bundle | High or Critical, matching the key's power |
| Password, reset token, or session token in logs | High when logs are broadly accessible; Medium when logs are restricted but the value is sensitive |
| Debug mode that dumps env in a production config | High |
| `.env.example` with fake values, AWS documentation example pair, unit-test placeholders | Drop, unless that value is the runtime default |
| Publishable vendor key used as documented | Drop |

When unsure whether a key is live, do not rate it Critical. Rate the exposure as High or needs-validation and make the first line of the fix "rotate this credential."

## Examples

```python
# Unsafe default: a missing env var silently uses a repo constant.
API_KEY = os.environ.get("API_KEY", "sk_live_fallback_in_source")

# Safe: fail closed. The real value stays in the environment or a secret manager.
API_KEY = os.environ["API_KEY"]
```

```javascript
// Unsafe: the session cookie is written on every error path.
console.error("request failed", { headers: req.headers, body: req.body });

// Safe: log an id and a status, not credentials.
console.error("request failed", { requestId, status: err.status });
```

## False positives

- Example and documentation keys, including the AWS example pair named above.
- Test fixtures that are not compiled into a production artifact. Confirm the build does not copy `testdata/` secrets. If it does, the finding is the build context, and it is real.
- Public keys, publishable client tokens, and key ids that are not secret by themselves. The private half is the secret.
- A password field in a login form, or a secret read from the environment inside the server and never written out.
- Hashes of non-secret content (asset checksums, git shas).
- `localhost` database URLs with no password in development compose files, when production config is separate and you can see it. If the compose file is also the production deploy, a default password is a finding.

## Related skills

`supply-chain-security` when the secret is available to pull-request CI. `iac-security` for secrets in Terraform state and manifests. `auth-security` for signing keys. `crypto-misuse` if the "encryption" of the secret is reversible and the key sits beside the ciphertext.
