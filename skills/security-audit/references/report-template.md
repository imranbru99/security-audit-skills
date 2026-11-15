# Report template

Use this structure. Lead with confirmed findings. Keep needs-validation separate. Omit rejected leads unless the user asked why something is safe.

```markdown
# Security review — <target>

## Scope
- Mode: focused | full
- Target and revision:
- In scope:
- Out of scope:
- Specialist skills used:

## Result
- Confirmed: <n> (highest: <rating>)
- Needs validation: <n>
- Coverage: <one sentence on what was not reviewed>

## Confirmed

### <Rating> — <one-line effect, not the bug class alone>

- Location: `path:line`
- Attacker and precondition:
- Trust boundary:
- Impact:
- Evidence: the path from input to the missing or broken control. Name the file and the function.
- Why this survived an attempt to disprove it:
- Fix: the smallest change that closes this path.
- Regression check: a test or assertion that fails on the old behavior.

## Needs validation

### <title>
- What is visible in source:
- Fact that would confirm or kill it:
- What not to do meanwhile: do not attack production; do not try discovered credentials.

## Coverage
| Surface | Reviewed | Notes |
| --- | --- | --- |
| Authentication and session | yes/no/partial | |
| Object and function authorization | | |
| Injection sinks | | |
| Browser and HTTP | | |
| Secrets and logging | | |
| Crypto used for a security decision | | |
| Dependencies and CI | | |
| Infrastructure config | | |
```

## Tone

Name the effect: "Any logged-in user can read another customer's invoice by changing `id`." Do not write "there might potentially be an IDOR if input is not sanitized."

Quote the missing check. Do not paste exploit payloads, live secrets, or a working request against a deployed host. A local fixture description is enough: "a quote in `q` changes the SQL text" or "the handler never compares `order.userId` to the session."

Redact secrets. If a credential is real, the fix is to rotate it, remove it from history, and stop the leak. Do not print the value to prove you found it.

## A finding that should not ship

> Potential SQL injection. User input is passed to the database. Please sanitize all input. Severity: Critical.

That report has no path, no control that was checked, and a fix ("sanitize") that often creates a second bug. Rewrite it or drop it.
