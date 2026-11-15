# Webhook delivery

**Confirmed.** High when this process can reach link-local metadata, internal admin ports, or other tenants. Medium when the deployment's network position is not in the repo: the code defect is still confirmed, and the blast radius is the fact that needs validation.

`deliver` issues `POST` to the URL argument. `requests` follows redirects by default. Nothing constrains the host.

**Fix.** Allowlist registered hosts, require HTTPS, reject embedded credentials and unexpected ports, and disable redirects. A tenant who may register a new host needs a stronger check than this fixture shows: resolve the name, refuse private and link-local addresses, connect to the address you resolved, and do not follow redirects. A string denylist of `localhost` or `169.254.169.254` is not that check.

**False positive to avoid.** A URL chosen from a server-side map of constant hosts is not SSRF. Do not confirm this by requesting a live metadata service. Read the call.

**Out of scope for this file.** An unsigned webhook receiver is `api-security`. This file is the client that performs the fetch.
