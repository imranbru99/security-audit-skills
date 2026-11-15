# Threat model

Build this before a full review, and before a focused review of auth, tenancy, payments, or file access. Six to twelve abuse cases are enough. Skip components that do not exist.

## Map

- **Assets.** Secrets, personal data, other users' objects, money or quota, admin actions, release integrity, availability of a shared worker.
- **Actors.** Anonymous internet, authenticated user, user in another tenant, admin, third-party webhook sender, malicious package or PR author, someone with a stolen laptop token. Drop actors the deployment model excludes, and say you dropped them.
- **Entry points.** Routes, webhooks, queue consumers, CLI, uploaded files, CI events, admin RPC. Note which ones are unauthenticated.
- **Trust boundaries.** Browser to app, app to database, tenant to tenant, app to outbound URL, PR code to CI secrets, developer laptop to production credentials.
- **Controls already on the path.** Auth middleware and the routes it does not cover, ORM versus string queries, template engine and its escape hatches, CSRF or SameSite, signature checks, allowlists, sandboxing.

## Abuse case

Write cases in this shape:

> As **actor**, I send **input** into **entry point** to affect **asset**. The control that should stop me is **control**. It fails if **condition**.

A case with no asset or no control is a guess. Park it until the code says which control was supposed to exist.

## Ordering

Review high-impact boundaries first:

1. Identity and session creation.
2. Access to objects the attacker does not own (horizontal) and actions above their role (vertical).
3. Untrusted data reaching a query, a command, a template, a file path, or an outbound request.
4. Credentials in source, logs, and client bundles.
5. Build, dependency, and deploy path, when that path is in scope.

## Assumptions

Write assumptions down. "The API gateway strips the `X-User-Id` header" is an assumption unless the gateway config is in the tree. If the app trusts that header and the gateway config is absent, the finding is needs-validation, not a confirmed bypass and not a pass.

## After the model

Turn each abuse case into a hunt: file, function, and the check you expect to find. A case you did not trace is a coverage gap, not a silent pass.
