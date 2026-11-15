---
name: supply-chain-security
description: >-
  Reviews dependencies, lockfiles, install scripts, build pipelines, and
  GitHub Actions for supply-chain weaknesses an attacker can actually reach.
  Use when reviewing manifests, lockfiles, CI workflows, or release steps, or
  when the user mentions dependencies, CVEs, supply chain, actions, or
  malicious packages.
license: MIT
compatibility: Agent Skills clients. No packages or network required.
metadata:
  category: security
---

# Dependency and supply-chain security

Review the path from a third-party change to privileged execution: install scripts, CI tokens, and code the build runs. A CVE number is a lead. Reachability makes it a finding.

## When to use

Use this skill when the scope includes `package.json`, `package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `requirements.txt`, `poetry.lock`, `Pipfile.lock`, `go.sum`, `composer.lock`, `Dockerfile` build steps, or `.github/workflows`. Use it when the user asks whether a dependency advisory matters.

Do not open with a full dependency audit of a 40-line application diff unless that diff changes dependencies, install behavior, or workflow files.

## Method

1. See how code enters the build: direct dependencies, transitive lock entries, actions, base images, curl-pipe installers.
2. See what that code is allowed to do: install scripts, CI `permissions`, secrets in the job, release credentials.
3. For a CVE, identify the vulnerable function and whether this repo calls it, or pulls it in through a framework feature that is enabled.
4. For a new dependency in a diff, look at the name, the source repository, and whether an install script runs. One signal is a lead. A name one character off a popular package, plus a fresh publish, plus a postinstall script, is a finding to block until a human looks. Do not accuse a package of malware from the name alone.

## What to look for

### Dependencies

- No lockfile, or a lockfile not used in CI (`npm install` instead of `npm ci`, `pip install -r requirements.txt` with no hashes while CI floats).
- Version ranges on security-sensitive packages that CI resolves from the network on every build.
- Multiple public registries for the same ecosystem without a pinned scope (dependency confusion). `pip install --extra-index-url` against a public index, and npm scopes that fall back to the public registry, are leads.
- `postinstall`, `setup.py`, or binary download scripts in a dependency the app just added. Read them if the package is small enough. A script that fetches a remote shell is a High finding.
- Typosquats in a diff: new package whose name is a neighbor of a common one and whose repo URL is missing or unrelated.
- Unpinned or tag-pinned third-party Git dependencies (`git+https://...@main`).

Advisories: report a CVE when the vulnerable code path is reachable in this application's configuration. If the advisory is about a function the app never calls, say that and do not rate it as a production incident. If you cannot tell, needs-validation, with the function name to check. Do not copy a scanner's Critical rating onto an unused transitive function.

### GitHub Actions and CI

The pattern that matters most:

- `pull_request_target`, or any trigger that runs with the base repository's secrets, checks out the PR head (`github.event.pull_request.head.sha` or `ref`), and then runs that code (`npm install`, `npm test`, a build script). Untrusted code plus a privileged token is High or Critical depending on the token and the secrets in the job.
- `pull_request` from forks is untrusted too, but the default `GITHUB_TOKEN` for `pull_request` from forks is read-only and secrets are not injected. Do not report "PR runs tests" when the workflow is `pull_request`, permissions are read, and no secrets are present.
- Workflow permissions broader than the job needs (`contents: write`, `id-token: write`, `packages: write`) on a job that runs untrusted code.
- Secrets passed into a step that executes repository code from a fork.
- `actions/checkout` of untrusted ref in a privileged workflow.
- Third-party actions pinned to a floating tag (`@v1`) in a workflow that has secrets. Pinning to a full commit SHA is the control. Report floating tags as Low hardening unless the action runs with secrets and is not from the first-party owner you already trust; then Medium. Do not rate every `@v4` on a no-secret lint workflow as High.
- `curl | bash` in a workflow or Dockerfile from a URL that is not pinned to a digest.

### Build and publish

- Release job that publishes on tag creation and also runs a script from the repo with the publish token. That is normal; the finding is when untrusted PR code can reach that token.
- Docker build context that sends `.git`, `.env`, or a secret file into the image. `.dockerignore` missing those paths is a finding if the files exist and the image is distributed.
- Provenance or signature missing is Info unless the project claims signed releases and the pipeline does not sign.

### Maintainer and account takeovers

You usually cannot see these from one repo. Report a concrete gap you can see: a single person can publish without a second factor being mentioned is not something source can prove. Source can prove that CI publishes using a long-lived token stored as a secret instead of a short-lived trusted publisher. Prefer the latter in the fix when the ecosystem supports it (npm trusted publishers, PyPI trusted publishing). Do not invent an account compromise.

## Verify before you report

1. For CI, quote the trigger, the checkout ref, the permissions, and whether secrets are in scope for that job.
2. For a dependency, name the package and the version or range, and the script or call site.
3. For a CVE, name the vulnerable symbol and the call path, or mark needs-validation.
4. Do not install the suspicious package on a developer machine to "see what it does," and do not execute its install script. Read the script if it is already in the lockfile cache or the vendored tree. Otherwise describe the lead and stop.
5. Do not report a floating action tag and a `pull_request_target` bug as the same finding. They have different fixes.

## Severity

| Situation | Typical rating |
| --- | --- |
| Untrusted PR code runs with secrets or a write token | Critical if secrets include deploy or registry credentials; High if the token can still modify the repository |
| Install script or image build fetches and runs remote code from an unpinned URL | High |
| Dependency confusion or a clear typosquat added in the diff | High until removed |
| Reachable CVE with a known severe impact | Use the advisory impact, capped by what this deployment can actually do |
| Unreachable CVE | Info or drop |
| No lockfile on a deployed service | Medium |
| Floating third-party action tag on a privileged workflow | Medium; Low when the workflow has no secrets and read-only permissions |

## Examples

Privileged workflow running PR code:

```yaml
# Unsafe: pull_request_target runs in the base repo. Checking out the PR
# head and installing it executes attacker code with this job's token.
on:
  pull_request_target:
permissions:
  contents: write
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}
      - run: npm ci && npm test
```

```yaml
# Safe: untrusted code stays on pull_request, with a read-only token and no secrets.
on:
  pull_request:
permissions:
  contents: read
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci && npm test
```

Keep deploy workflows on a separate trusted trigger (push to the default branch or a protected tag), not on the PR job.

## False positives

- `pull_request` workflows that do not receive secrets and use the default read-only fork token.
- A CVE in a package that is present but whose vulnerable function cannot be called in this configuration. Explain that.
- Dev-dependencies used only on a developer laptop, when they are not installed in CI or the production image. If CI runs them on untrusted PRs with secrets, they are in scope.
- Floating tags on first-party lint actions in a workflow with `contents: read` and no secrets. Mention SHA pinning as Info if you mention it at all.
- `npm audit` output you did not trace.
- A private package name that looks short. Confusion requires a registry that will resolve the attacker's package. If the install is locked to one private registry, say so and drop the lead.

## Related skills

`secrets-exposure` for tokens in workflow files and logs. `iac-security` for images and cluster build. `injection-security` if a workflow interpolates untrusted PR titles into a `run:` script (`${{ github.event.pull_request.title }}` inside `run` is command injection).
