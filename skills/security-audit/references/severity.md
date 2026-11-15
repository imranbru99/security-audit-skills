# Severity

Severity describes reachability and impact for this codebase. The name of the bug class does not set it.

## Confirmed, needs validation, or drop

**Confirmed.** You can point at the source path, the attacker, the asset, and the broken control. You tried to disprove it.

**Needs validation.** The dangerous pattern is present, but the decisive control or exposure lives outside the reviewed tree (gateway, network policy, deployment config, library version you could not see). Say what would settle it. Do not upgrade this to confirmed because the pattern looks bad.

**Drop.** A compensating control closes the only path, the code is unreachable, the attacker already has the same power, or the impact stays inside the attacker's own account.

## Scale

| Rating | Use it when |
| --- | --- |
| Critical | Unauthenticated remote code execution, authentication bypass that exposes many users, or a production credential in the repo that grants administrative or data-plane access. You can see that reach in source or deployment config. |
| High | A normal user, or an unauthenticated attacker with one realistic precondition, can read or change another user's sensitive data, escalate privileges, run code in a realistic deployment, or forge a session. |
| Medium | Concrete harm that needs user interaction, a narrower data set, or a common browser/network precondition. Typical: reflected XSS, CSRF on a sensitive cookie-authenticated action, SSRF whose blast radius is unclear but the request is attacker-directed, open redirect on a login or OAuth return. |
| Low | Real weakness with limited impact. Typical: open redirect with no token to steal, sensitive field over-exposure that is not secret, internal-only debug route with no path from the outside. |
| Info | Hardening that does not, by itself, cross a trust boundary. Missing header on a page with no framed action, software version disclosure, unsigned dependency with no vulnerable use. |

## How to choose

1. Name the attacker: anonymous internet, authenticated user, same-tenant user, admin, CI, someone who can edit a dependency or a PR.
2. Name the asset: other users' data, credentials, money or quota, integrity of a release, availability of a shared service.
3. Walk the path from attacker input to that asset. Count only controls that sit on that path.
4. If the widest impact depends on a fact you do not have, cap the rating or mark needs-validation, and write the missing fact in the finding.

## Adjustments

Raise the rating when the bug is in a shared helper used by many entry points, or when the disclosed data includes passwords, session tokens, reset tokens, or cloud credentials.

Lower the rating or drop the finding when:

- The only actors who can reach it already hold the privilege the bug grants.
- The path is test-only and production builds do not compile or ship it.
- A framework default closes it (parameter binding, template auto-escaping, CSRF middleware on that route group) and the code does not opt out.
- The "secret" is an obvious fixture (`example`, `changeme`, the published AWS documentation key pair) and it is not used as a production default.

Do not raise the rating because a scanner said "critical", because the CWE number sounds severe, or because the same bug would be worse in a different architecture.

## What is not a vulnerability by itself

- A missing security header, cookie flag, or rate limit, until you can name the attack it completes.
- An integer object id, a UUID, GraphQL introspection, or a public OpenAPI document.
- A dependency advisory for a function this repo never calls and does not expose transitively in a reachable way.
- `debug` logs that do not include secrets, tokens, or personal data.
- Egress to the internet from a server that needs to call the internet.
