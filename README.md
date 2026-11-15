# security-audit-skills

<p align="center">
  <img src="docs/images/hero.png" alt="security-audit-skills: defensive source review for Claude Code, Cursor, Codex, Gemini CLI, Copilot, and OpenCode. A confirmed finding names the attacker, the missing check, and the fix." width="100%">
</p>

Skills that make a coding agent review code the way a careful security engineer would. The agent maps trust boundaries, traces attacker-controlled input to a real asset, tries to disprove every lead, and reports only what survives, with a severity and the smallest fix.

A generic "check OWASP" prompt produces a long list of theoretical issues. These skills are specific about framework defaults, the APIs that are already safe, the evidence a finding needs, and the false positives a reviewer should drop. They are defensive source review of code you are allowed to read. They follow the [Agent Skills](https://agentskills.io/specification) `SKILL.md` format.

There is no hosted application and no scanner to operate. You install the skill directories, then ask the agent for a review in the editor you already use.

## Who this is for

| You | What you get |
| --- | --- |
| A product team without an application-security engineer on every pull request | A first pass that already knows which Django, Laravel, React, and Go defaults close the bug, so a human reads survivors instead of a raw list. |
| An application-security team | The same verdict rule across Claude Code, Cursor, Codex, Gemini CLI, Copilot, and OpenCode. Diffs arrive pre-sorted into confirmed, needs-validation, and coverage. |
| A consultancy or a freelance reviewer | One method for web, API, auth, injection, secrets, crypto, CI, and infrastructure, with a write-up shape you can hand to a client. |
| A platform or infrastructure owner | Terraform, Kubernetes, Docker, IAM, lockfiles, and GitHub Actions reviewed against what the application actually does. |
| A maintainer or a security champion | Worked examples of the bug and the fix, so the next reviewer does not rediscover `filepath.Join` or Laravel mass assignment from scratch. |
| Someone asking a design question | Guidance mode. A direct answer. The full audit does not start unless you ask for it. |

You can install all 13 skills, or only the ones that match the stack. Each specialist stands alone. When `security-audit` is also installed, its rule wins: no trust boundary, no finding.

## What you can ask for

<p align="center">
  <img src="docs/images/modes.png" alt="Three modes: Guidance for a question, Focused for a diff or one bug class, Full when you ask for an audit or a report." width="100%">
</p>

| Job | What to say | What comes back |
| --- | --- | --- |
| Pull-request review | "Review this diff. Confirmed findings only, plus what you did not follow." | Leads that start at the changed lines and the helpers they call. |
| One bug class | "Look only for authorization and injection in `services/billing`." | That surface, with the specialist skill loaded. |
| Threat model | "Threat-model tenancy and payments before you hunt." | Actors, assets, entry points, and abuse cases in a fixed shape. |
| Suspected bug | "Triage this report. Confirm it or kill it from source." | A verdict, or the missing fact that blocks one. |
| Full repository review | "Full security review. Do not claim the app is secure." | Six phases, a coverage table, and an explicit gap. |
| Secrets and logs | "Find credentials and tokens in source, CI, and client bundles." | Live-looking secrets called out, documentation keys and `changeme` dropped. |
| Dependency advisory | "Does this CVE matter here?" | Reachable call path, or needs-validation if the version or the call is not in the tree. |
| CI and release | "Can a pull request run code with this repository's secrets?" | Trigger, checkout ref, token permissions, and whether secrets are in the job. |
| Infrastructure change | "Review the Terraform and the Kubernetes manifests in this PR." | Open admin ports, public buckets, and roles wider than the app. |
| Language pass | "Python security review" or "Laravel security review." | The escape hatches for that framework, not a generic OWASP list. |
| Design review, before code | "We want customer webhook URLs. What has to be true?" | The control that holds, in guidance mode, without a report file. |
| Teaching | Open `examples/` and ask the agent to review a fixture. | The rating in `NOTES.md`, including the false positive the fixture exists to prevent. |
| The same standard everywhere | Install once under `~/.agents/skills/` or `~/.claude/skills/`. | Every repository you open inherits the catalog. |
| One service, one client | Copy `skills/*` into that project's `.agents/skills/` or `.claude/skills/`. | The team shares the method in git. |

A forty-line diff and a full repository audit are different jobs. If you leave that ambiguous, `security-audit` asks one question instead of launching every phase.

## Where the time goes

These ranges are planning estimates for a team whose agent does not already have this checklist. They are not telemetry, not a customer study, and not a promise of hours saved. The skills absorb the repeated part of the review. A person still owns scope, the facts that live outside the repository, and the decision to ship.

| Review | Repeated work the skills take on | What you still spend time on |
| --- | --- | --- |
| Security-sensitive pull request | The first 30–90 minutes of re-deriving framework defaults, killing false positives, and rewriting "please sanitize" into a real note. | Reading the survivors and deciding whether the fix is enough. |
| New boundary: billing, tenancy, uploads, webhooks | The half-day of rebuilding actors, assets, and abuse cases into a shape someone else can review. | Correcting assumptions the source cannot prove, such as a gateway you did not put in the tree. |
| Full pass on a service | The opening day that disappears into "where are the routes, and which middleware actually wraps them?" | Residual risk, production exposure, and anything this repository does not contain. |
| An agent or scanner dump | The back-and-forth on theoretical XSS, unreachable CVEs, and missing headers with no scenario. | Keeping or dropping each item that survived the disproof step. |
| A second reviewer, or a second tool | Re-explaining the verdict rule so two agents do not contradict each other. | One catalog, shared by every client that can load `SKILL.md`. |

The expensive failure mode these skills are written against is a confident list of non-bugs. Triaging that list costs more than the review. The procedure spends the agent's time on the path, then stops.

## How a review runs

<p align="center">
  <img src="docs/images/workflow.png" alt="Six phases: Scope, Map, Model, Hunt, Disprove, Report." width="100%">
</p>

1. **Scope.** Diff, feature, or whole tree. Record the revision and what is out of bounds.
2. **Map.** Routes, identity, data stores, outbound calls, and the controls already present: ORM, template auto-escape, CSRF middleware, cookie flags.
3. **Threat model.** Actor, entry point, asset, and the control that should stop them. The worksheet is [skills/security-audit/references/threat-model.md](skills/security-audit/references/threat-model.md).
4. **Hunt.** Authentication, object authorization, injection and templates, secrets, crypto that makes a security decision, then CI and infrastructure when those files are in scope.
5. **Disprove.** A grep hit is a lead. Bound parameters, auto-escaped templates, middleware order, and dead code kill it or they do not.
6. **Report.** Confirmed findings, then needs-validation, then coverage. Severity comes from reach and impact, in [skills/security-audit/references/severity.md](skills/security-audit/references/severity.md). The write-up shape is [skills/security-audit/references/report-template.md](skills/security-audit/references/report-template.md).

The agent is instructed to redact secrets, to avoid proving a lead by calling a deployed host, and to avoid claiming the review was exhaustive.

## The skills

<p align="center">
  <img src="docs/images/skills.png" alt="Thirteen skills. security-audit orchestrates. Eight bug-class skills and four language skills supply the detail." width="100%">
</p>

<!-- skills-table:start -->
| Skill | What it is for |
| --- | --- |
| [`security-audit`](skills/security-audit/SKILL.md) | Full or focused review: scope, threat model, hunt order, verification gate, severity, and the report. Start here. |
| [`web-security`](skills/web-security/SKILL.md) | XSS, CSRF, SSRF, IDOR, open redirect, path traversal, uploads, CORS, clickjacking. Includes the framework escapes that make a pattern safe. |
| [`api-security`](skills/api-security/SKILL.md) | Object and function authorization, mass assignment, excessive data exposure, webhook signatures, GraphQL auth, expensive unauthenticated operations. |
| [`auth-security`](skills/auth-security/SKILL.md) | Passwords, sessions, JWT, OAuth and OIDC, password reset, and the ownership check that login does not replace. |
| [`injection-security`](skills/injection-security/SKILL.md) | SQL, command, NoSQL, LDAP, template, header, and deserialization sinks, and the APIs that bind parameters instead. |
| [`secrets-exposure`](skills/secrets-exposure/SKILL.md) | Credentials and sensitive data in source, logs, errors, and client bundles, including fixtures that only look like secrets. |
| [`supply-chain-security`](skills/supply-chain-security/SKILL.md) | Lockfiles, install scripts, dependency advisories that are actually reachable, and CI that runs untrusted code with a privileged token. |
| [`iac-security`](skills/iac-security/SKILL.md) | Terraform, Kubernetes, Docker, and IAM: world-open admin ports, public buckets, and workload roles that can do more than the app does. |
| [`crypto-misuse`](skills/crypto-misuse/SKILL.md) | Password hashing, token randomness, AEAD, TLS verification, and secret comparison. A cache-key hash is not in scope. |
| [`python-security`](skills/python-security/SKILL.md) | Django, Flask, FastAPI, and stdlib traps: `raw()`, `mark_safe`, `shell=True`, `pickle`, `yaml.load`, `DEBUG`, `assert` used as auth. |
| [`javascript-security`](skills/javascript-security/SKILL.md) | Node and browser JavaScript and TypeScript: DOM XSS, prototype pollution, `child_process`, Prisma raw queries, Next.js server routes. |
| [`go-security`](skills/go-security/SKILL.md) | Go services: SQL text, `filepath.Join` traversal, `text/template` versus `html/template`, `math/rand`, ignored auth errors. |
| [`php-security`](skills/php-security/SKILL.md) | PHP and Laravel: mass assignment, policies, Blade `{!! !!}`, raw SQL, `unserialize`, and middleware groups that skip CSRF. |
<!-- skills-table:end -->

Descriptions stay short so a client can keep the whole catalog in context and load a skill body only when the review needs it.

### What each skill is prepared to catch

**Web.** Stored and reflected XSS, including the context the encoder missed (`href` schemes, unescaped HTML sinks). CSRF only when the browser will actually send the credential. SSRF through webhooks, importers, and redirect-following clients. IDOR when the handler loads by id and never binds the row to the caller. Open redirects on login and OAuth returns. Path traversal and zip slip. Uploads served back as active content. CORS that reflects `Origin` with credentials. Clickjacking of a sensitive HTML action. Password-reset links built from the `Host` header.

**API.** Broken object and function authorization. Mass assignment of `role`, `owner_id`, `balance`, or `price`. Password hashes, reset tokens, and MFA seeds in JSON. Unsigned or replayable webhooks. API keys in query strings. Debug and pprof routes. GraphQL fields and `node(id)` loaders that skip the check the rest of the schema uses. Unbounded expensive operations. A missing rate limit is reported only when you can name the cost.

**Auth.** Fast hashes of passwords. Session fixation. Remember-me tokens stored in plaintext. JWT secrets in source, unpinned algorithms, and `kid` used as a path or a query. OAuth `redirect_uri` checks that are only a prefix, missing `state`, and public clients without PKCE. Reset tokens from `rand()`, reset links that trust the user id, and email-change flows that skip the current session. Client-supplied tenant ids and `admin` claims from an identity provider you do not control.

**Injection.** SQL built with f-strings, `fmt.Sprintf`, or `whereRaw`. The DB-API form that looks unsafe and is not (`execute(sql, params)`). Dynamic `ORDER BY`. Shell strings versus argument arrays. NoSQL operator injection on a login. Template source controlled by the attacker. Header and mail injection. `pickle`, `unserialize`, and unsafe YAML on attacker bytes.

**Secrets.** Private keys, cloud tokens, and connection strings in git, images, and workflow files. The published AWS documentation key pair, recognized as a fixture. Tokens in logs, error pages, and `NEXT_PUBLIC_` / `VITE_` bundles. Debug modes that dump the environment. A fake default used when the environment variable is missing.

**Supply chain.** Missing lockfiles. New packages with install scripts. Dependency-confusion layouts. A CVE whose function this repository never calls. `pull_request_target` that checks out the pull-request head and runs it with a write token or a secret. Workflows that interpolate a pull-request title into `run:`.

**Infrastructure.** SSH, RDP, Kubernetes API, and databases open to `0.0.0.0/0`, rated from the route table if it is in the tree. Public buckets holding state or backups. Workload roles with full admin. Privileged pods and host Docker sockets. State files committed to git.

**Crypto.** MD5 or bare SHA-256 used as a password hash. `Math.random`, `math/rand`, and `mt_rand` used for tokens. ECB, a static nonce, and encryption without authentication. `InsecureSkipVerify`, `verify=False`, and `rejectUnauthorized: false` on a connection that carries a credential. Secret comparison with `==` where that comparison is the control.

**Python.** Django `raw` / `extra` / `mark_safe`, `@csrf_exempt` on a cookie-authenticated view, `DEBUG` in the settings module production imports, Flask `render_template_string` of request data, FastAPI routes whose dependency only checks that a header exists, `assert` used as authorization, `shell=True`, `pickle.loads`, and `requests.get` of a user URL.

**JavaScript and TypeScript.** `dangerouslySetInnerHTML` and `javascript:` URLs. Next.js server routes that trust a client id. Recursive merges that copy `__proto__` or `constructor.prototype` onto a shared object, reported as High only when a gadget exists. `child_process.exec` of request data. Prisma `$queryRawUnsafe`. Middleware registered after the route.

**Go.** Statement text passed to `Query`. `filepath.Join` followed by `ServeFile`, which still leaves the root. `text/template` and `template.HTML`. `http.Client` redirects. An ignored error from `authenticate`. `math/rand` where `crypto/rand` is required. Missing server timeouts, rated as the exposure they actually are.

**PHP and Laravel.** `findOrFail($id)` plus `$request->all()`. `forceFill` and an empty `$guarded`. Policies that return true. Blade `{!! !!}`. `whereRaw` with interpolation. `unserialize` of a cookie. `==` on a reset token. `APP_DEBUG=true` in the production environment. Cookie-session routes sitting on the `api` middleware group, which does not check CSRF.

## Installation

Clone the repository and copy skill directories. Copy `skills/<name>/`, not `examples/`. The examples are intentionally vulnerable teaching fixtures.

```bash
git clone https://github.com/<owner>/security-audit-skills.git
cd security-audit-skills
```

| Client | Project path | User path |
| --- | --- | --- |
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Cursor | `.cursor/skills/` or `.agents/skills/` | `~/.cursor/skills/` or `~/.agents/skills/` |
| Codex | `.agents/skills/` | `~/.agents/skills/` |
| Gemini CLI | `.gemini/skills/` or `.agents/skills/` | `~/.gemini/skills/` or `~/.agents/skills/` |
| GitHub Copilot | `.github/skills/` or `.agents/skills/` | the user skills directory for your Copilot client |
| OpenCode | `.opencode/skills/` | `~/.opencode/skills/` |

`.agents/skills/` is the cross-client location. Claude Code reads `.claude/skills/`. Cursor reads its own directory and `.agents/skills/`.

```bash
# Every skill, for the repo you are reviewing. Cursor, Codex, and Gemini CLI.
cp -R skills/* /path/to/your-app/.agents/skills/

# Claude Code, same project.
cp -R skills/* /path/to/your-app/.claude/skills/

# One skill, for your user account, on every repository.
cp -R skills/security-audit ~/.agents/skills/
cp -R skills/security-audit ~/.claude/skills/

# A Python service, project-local, without the skills you will not use.
cp -R skills/security-audit skills/python-security skills/web-security \
  skills/auth-security skills/injection-security skills/secrets-exposure \
  /path/to/your-app/.agents/skills/
```

Restart the client if it only discovers skills at session start. A skill is a directory with a `SKILL.md` file. The `name` in the frontmatter matches the directory name.

The [skills CLI](https://github.com/vercel-labs/skills) installs the same directories from a published remote:

```bash
npx skills add <owner>/security-audit-skills --skill security-audit
```

Repeat `--skill` for each specialist, or follow that CLI's prompt to add the full set. The `cp` commands work from this tree with no registry.

Suggested sets:

| Stack in the tree | Install |
| --- | --- |
| Any review | `security-audit` |
| Django, Flask, or FastAPI | add `python-security`, `web-security`, `auth-security`, `injection-security`, `secrets-exposure` |
| React, Next.js, or Express | add `javascript-security`, `web-security`, `api-security`, `auth-security` |
| Go service | add `go-security`, `api-security`, `injection-security`, `crypto-misuse` |
| Laravel | add `php-security`, `web-security`, `auth-security`, `injection-security` |
| Terraform, Kubernetes, or Docker | add `iac-security`, `secrets-exposure` |
| GitHub Actions or a lockfile change | add `supply-chain-security`, `secrets-exposure` |

## Prompts that hold up

```text
Review this diff for security issues. Use security-audit.
Report confirmed findings only, plus one line on what you did not review.
```

```text
Focused review of services/billing. Threat-model tenancy and payments,
then check authorization and injection. Severity on each confirmed finding.
```

```text
Full security review of this repository. Load the Python, web, auth,
and secrets skills. Do not claim the app is secure. Separate
needs-validation from confirmed.
```

```text
The GitHub Actions workflows and the dependency change in this PR.
Use supply-chain-security. I care about untrusted code reaching secrets.
```

```text
Triage the attached note about SQL injection. Quote the execute call.
If it is a bound parameter, say so and stop.
```

```text
Guidance only: we are about to let customers register a webhook URL.
What has to be true before this is safe to ship? Do not write a report.
```

Name the revision, the directory, or the diff. Name the stack if the tree is mixed (`Laravel`, `Next.js`, `Terraform`). Ask for the disproof attempt and the coverage gap. Treat needs-validation as a missing fact, such as a gateway config, a library major, or a network path.

## What a confirmed finding looks like

<p align="center">
  <img src="docs/images/finding.png" alt="Required finding shape: location, attacker, boundary, evidence, what was disproved, the fix, and a regression check. The example is SQL built with an f-string." width="100%">
</p>

Every confirmed finding states location, attacker, boundary, impact, evidence, why the obvious false positive does not apply, the fix, and a regression check. The SQL fixture is written out in [examples/sample-finding.md](examples/sample-finding.md).

The fixtures under [examples/](examples/) are the cases the skills are written to catch. Each directory has a vulnerable file, a secure counterpart, and the conclusion a careful review should reach.

| Case | Where a careful review should land |
| --- | --- |
| SQL built with an f-string | High. Binding the parameter closes it. A `LIKE` wildcard is not a second injection bug. |
| Order fetch that checks login and not ownership | High IDOR. A UUID does not fix it. |
| `filepath.Join(root, user)` then `ServeFile` | High path escape. `Join` cleans `..` and still leaves the root. |
| Laravel `findOrFail($id)` plus `$request->all()` | Two High findings: missing authorization, and mass assignment. |
| `requests.post(user_url)` | Confirmed SSRF. Blast radius depends on where the process can connect. |
| `dangerouslySetInnerHTML` of a stored comment | High stored XSS. The text-child author field beside it is escaped. |
| `jwt.verify(token, "secret")` | High hardcoded signing key. `alg: none` only if that library major still accepts it. |
| Security group SSH from `0.0.0.0/0` | Confirmed. High if the subnet is public, Medium if the route table is not in the tree. |
| `pull_request_target` checking out the PR head and running `npm ci` | High or Critical, depending on the token and the secrets in the job. |
| A token committed next to AWS's published example key pair | One real finding, one known fixture. Do not rotate the documentation key. |

### Severity, in one screen

| Rating | The situation |
| --- | --- |
| Critical | Unauthenticated remote code execution, broad authentication bypass, or a production admin credential you can see in the tree. |
| High | A normal user, or an unauthenticated attacker with one realistic precondition, reads or changes someone else's sensitive data, escalates, or forges a session. |
| Medium | Concrete harm that needs interaction or a narrower blast radius. Reflected XSS, CSRF on a sensitive cookie action, an open redirect on an OAuth return. |
| Low | A real weakness with limited impact. |
| Info | Hardening that does not itself cross a trust boundary. |

If the decisive control lives outside the repository, the status is needs-validation. The skill does not assume the control is missing, and it does not assume the control exists.

### False positives the skills are told to drop

- SQL or shell that really does bind parameters, including the Python DB-API form people misread.
- XSS in a template engine that escapes by default, until the code opts out.
- CSRF on a bearer-token API, or on a POST whose session cookie is `SameSite=Lax` or `Strict`, with no same-site attacker in scope.
- "IDOR" that is only "the id is an integer," when the query also constrains the owner.
- A CVE whose function this application never calls.
- `AKIAIOSFODNN7EXAMPLE` together with Amazon's published example secret.
- A missing header, cookie flag, or rate limit, until it completes a named attack.

## What this repository will not do

It will not scan production, attack a system you did not put in front of it, or use a credential it finds. It will not guarantee that a review found every bug. Coverage is part of the report because a quiet search is not a clean bill of health. It will not replace a human decision on residual risk, a pen test of a deployed system, or a compliance attestation.

## Repository layout

```text
skills/<name>/SKILL.md                 skill instructions
skills/security-audit/references/      severity, threat model, report template
examples/<case>/                       vulnerable file, secure file, NOTES.md
docs/images/                           README figures
scripts/render_readme_images.py        regenerates docs/images
scripts/check_skills.py                frontmatter, headings, banners, README index
```

`make check` runs the skill checker. Regenerate the figures with `python3 scripts/render_readme_images.py` after you change their layout. They are drawings of the method, committed so the README renders on GitHub.

## Contributing

New skills and corrections are welcome. The bar is in [CONTRIBUTING.md](CONTRIBUTING.md): a real bug class, a verification step, a false-positive section, a vulnerable and a secure example, and no exploit procedure. Run `make check` before opening a pull request.

An issue about a skill that recommends an unsafe fix, or that would hide a real bug or report a fake one, is as useful as a new bug class. See [SECURITY.md](SECURITY.md).

## License

[MIT](LICENSE).

## 🤝 Let's Connect & Collaborate

I am open to Senior Remote Full-Stack Roles, AI Platform Architecture Contracts, and Enterprise Technical Advisory.

Timezone: UTC+6 (Dhaka / Rangpur, Bangladesh) — flexible overlap with US, UK, and European business hours.

Delivery mode: async-ready, Slack, Discord, Jira, GitHub, and production-first accountability.

| Channel | Address / Handle | Quick action |
| --- | --- | --- |
| 🌐 Primary portfolio | [imrandev.bd](https://imrandev.bd) | [Visit site ↗](https://imrandev.bd) |
| 📦 Packagist packages | [packagist.org/packages/imrandevbd](https://packagist.org/packages/imrandevbd/) | [View packages ↗](https://packagist.org/packages/imrandevbd/) |
| 💼 LinkedIn profile | [linkedin.com/in/imranbru99](https://www.linkedin.com/in/imranbru99) | [Connect ↗](https://www.linkedin.com/in/imranbru99) |
| 🐙 GitHub profile | [github.com/imranbru99](https://github.com/imranbru99) | [Follow ↗](https://github.com/imranbru99) |
| 💬 WhatsApp direct | [+880 1576-918420](https://wa.me/8801576918420) | [Chat now ↗](https://wa.me/8801576918420) |
| 📧 Direct email | [me@imrandev.bd](mailto:me@imrandev.bd) | [Send email ↗](mailto:me@imrandev.bd) |
| 🐦 X (Twitter) | [@imrandev_bd](https://x.com/imrandev_bd) | [Follow ↗](https://x.com/imrandev_bd) |
| 📺 YouTube tech | [@ImranDevBD](https://www.youtube.com/@ImranDevBD) | [Subscribe ↗](https://www.youtube.com/@ImranDevBD) |
