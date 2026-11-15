# Examples

These directories are teaching fixtures for the skills. Each `vulnerable` file is intentionally unsafe. Each `secure` file is the same behavior with the control that closes the path. `NOTES.md` is the conclusion a careful review should reach, including the false positive the skill is supposed to avoid.

Do not deploy these files, do not point them at real data, and do not extend them into exploits.

| Directory | What a review should catch | Skills |
| --- | --- | --- |
| `python-sql-search` | Search text concatenated into SQL | `injection-security`, `python-security` |
| `node-idor` | Order lookup with login but no ownership check | `api-security`, `auth-security` |
| `go-file-download` | `filepath.Join` that still leaves the export root | `go-security`, `web-security` |
| `laravel-mass-assignment` | User update that trusts the id and the request body | `php-security`, `api-security` |
| `python-webhook-ssrf` | Server fetch of a caller-supplied URL | `web-security`, `python-security` |
| `react-stored-xss` | Comment body rendered as HTML | `web-security`, `javascript-security` |
| `node-jwt` | Session token verified with a hardcoded secret and no pinned algorithm | `auth-security`, `javascript-security` |
| `terraform-ssh-world` | SSH open to `0.0.0.0/0` | `iac-security` |
| `github-action-pr-target` | `pull_request_target` running PR code with a write token | `supply-chain-security` |
| `hardcoded-secret` | A committed credential, and a scanner hit that is only AWS's documentation key | `secrets-exposure` |

`sample-finding.md` is the write-up shape for the SQL fixture. Match that tone: attacker, path, impact, why it survived, fix.
