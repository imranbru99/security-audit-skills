# Pull request workflow

**Confirmed.** High, and Critical if this job's environment includes cloud or registry secrets. `pull_request_target` runs in the base repository with that repository's token. The checkout ref is the PR head. `npm ci` and `npm test` execute that code, including install scripts. `contents: write` lets the job change the repository.

**Fix.** Test untrusted code on `pull_request` with `contents: read` and without secrets. Put deploys on a separate workflow triggered by a push to a protected branch or tag. Pin third-party actions to a commit SHA when those workflows have secrets. A floating `@v4` on this no-secret test job is Info, not the finding.

**False positive to avoid.** A `pull_request` workflow that never receives secrets and uses the default read-only fork token is the safe pattern. Do not report it because it runs the PR's tests. Do not merge this finding with "dependencies are unpinned" unless the install itself is the bug you traced.
