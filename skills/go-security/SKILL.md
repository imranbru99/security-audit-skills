---
name: go-security
description: >-
  Reviews Go services for SQL and command injection, path traversal, template
  escaping, TLS and randomness mistakes, ignored authorization errors, and
  net/http defaults. Use when the target contains Go source or go.mod, or when
  the user asks for a Go security review.
license: MIT
compatibility: Agent Skills clients. No packages or network required.
metadata:
  category: security
---

# Go security

Go's standard library is safe when the secure API is the one actually called. Reviews miss bugs when `path.Join` is trusted to contain traversal, when `html/template` is confused with `text/template`, and when an `err` from an auth check is ignored.

Use `injection-security`, `web-security`, `auth-security`, and `crypto-misuse` for the general rules.

## When to use

Use this skill when the tree contains `.go` files or `go.mod`. Skip it for a repository that only vendors a Go binary you cannot read.

## Method

1. Find `main`, route registration, and middleware. In `net/http`, a middleware that is not wrapped around the handler does not run.
2. Search the leads below. For each hit, read the two or three functions around it, not just the line.
3. Check `go.mod` when behavior depends on a library default (JWT, ORM, router).
4. Ignored errors on a security check are findings, not style.

## What to look for

### SQL and commands

- `fmt.Sprintf`, `+`, or `strings.Builder` used to put request data into `Query`, `Exec`, or `db.Raw`. `database/sql` placeholders (`$1`, `?`, depending on the driver) passed as extra arguments are safe.
- `ORDER BY` built from a query parameter. Allowlist the column.
- `exec.Command("sh", "-c", userString)` and `exec.Command(name, args...)` where `name` comes from the request. A fixed name and a separate arg slice is safe from shell injection. The user still must not control the executable path.
- `text/template` executed with user data that includes actions, or `template.HTML`, `template.JS`, `template.URL` around user strings. `html/template` escapes contextual HTML. `template.HTML` is an opt-out. `text/template` does not escape.

### Paths and archives

`filepath.Join(root, name)` cleans `..` but a later absolute element resets the join, and `..` still escapes `root` after `Clean`. `path.Join` is the URL path package; do not use it for filesystem containment.

The check that holds:

```go
func underRoot(root, name string) (string, error) {
    if name == "" || strings.ContainsRune(name, 0) {
        return "", errors.New("bad path")
    }
    root = filepath.Clean(root)
    full := filepath.Clean(filepath.Join(root, name))
    rel, err := filepath.Rel(root, full)
    if err != nil || rel == ".." || strings.HasPrefix(rel, ".."+string(os.PathSeparator)) {
        return "", errors.New("bad path")
    }
    return full, nil
}
```

`http.Dir` and `http.ServeFile` do not grant access outside the rooted directory when the root is a constant and the name is cleaned by `http.Dir`. Read the call. Serving `filepath.Join("/var/exports", r.URL.Query().Get("f"))` via `os.Open` is not the same as `http.Dir`.

`archive/zip` and `tar` member names need the same root check before `os.Create`.

### HTTP server

- `http.ListenAndServe` with no `ReadHeaderTimeout`, `ReadTimeout`, or `WriteTimeout` on an internet-facing server. Slowloris-style resource use. Rate Low or Medium based on exposure, not High by itself.
- Missing auth middleware on a new `HandleFunc`. Look at the mux, not the function name.
- `httputil.ReverseProxy` with `Director` rewriting to a user-supplied host (SSRF). Also check `req.URL` taken from the inbound request without clearing `Forwarded` headers the director did not mean to trust.
- `http.Client` calls to a user URL. Redirects are followed (up to 10). A denylist checked only on the first URL is not enough.
- `tls.Config{InsecureSkipVerify: true}`.
- CORS handler reflecting `Origin` with credentials. Often a third-party middleware; read its options.

### Auth mistakes that are idiomatic in Go

- `user, _ := authenticate(r)` and then using `user`. The ignored error is the bug if failure still proceeds.
- Comparing a MAC or token with `bytes.Equal` or `==` on the secret. Use `subtle.ConstantTimeCompare` on equal-length digests. `subtle.ConstantTimeCompare` returns 1 on match, not a boolean people sometimes invert. Read the branch.
- `math/rand` for tokens. Use `crypto/rand`. `math/rand/v2` is still not a CSPRNG.
- JWT middleware that parses and does not restrict algorithms, or that takes the signing key from the request. See `auth-security`.

### Race conditions

Report a race only when it crosses a trust boundary: two requests that both pass an authorization or balance check before either write. A data race the race detector would flag on a counter is a bug, not automatically a vulnerability. If you cannot describe the insecure interleaving, do not report it as a security finding.

## Verify before you report

1. Quote the call and the import path. `path` versus `filepath`, `text/template` versus `html/template`, and `math/rand` versus `crypto/rand` decide the verdict.
2. For SQL, show that the value is inside the statement string rather than a placeholder argument.
3. For path traversal, show the root check is missing or uses only `Join`.
4. For ignored errors, show the next line uses the result anyway.
5. Do not start the service on a public interface to prove it.

## Severity

| Lead | Typical rating |
| --- | --- |
| SQL or shell injection from a request | High, or Critical if unauthenticated and the process or database role is powerful |
| Path escape that reads secrets or another user's files | High |
| `template.HTML` or `text/template` of stored user content rendered for others | High |
| `InsecureSkipVerify` on a credentialed client | High |
| Token from `math/rand` | High if the range is guessable; Medium if the space is large but the generator is known-weak. Say which. |
| Ignored auth error that treats the user as authenticated | High |
| Missing server timeouts on a public listener | Low or Medium |
| Non-constant-time token compare | Low or Medium |

## Examples

```go
// Unsafe: Join cleans the string and still leaves the export root.
func download(w http.ResponseWriter, r *http.Request) {
    name := r.URL.Query().Get("file")
    http.ServeFile(w, r, filepath.Join("/var/app/exports", name))
}
```

Use `underRoot` above, then `http.ServeFile` on the returned path. `ServeFile` will not fix a path that has already escaped.

```go
// Unsafe: request data is SQL text.
q := fmt.Sprintf("SELECT id FROM users WHERE email = '%s'", email)
row := db.QueryRowContext(ctx, q)

// Safe.
row := db.QueryRowContext(ctx, "SELECT id FROM users WHERE email = $1", email)
```

The placeholder style depends on the driver. The safe property is the separate argument, not the glyph.

## False positives

- `database/sql` queries with placeholders and no formatted identifiers.
- `html/template` without `template.HTML`, `template.JS`, or `template.URL` around user strings.
- `filepath.Rel` containment written correctly, including the absolute-path reset case.
- `crypto/rand` tokens of at least 16 bytes.
- `exec.Command` of a constant program and a constant arg list.
- `http.Dir("/var/www")` used as the file server root with no extra path concatenation.
- An ignored error on a log or metrics call that does not change authorization.
- `go.mod` `// indirect` modules you did not connect to a sink. Use `supply-chain-security` for the dependency review itself.

## Related skills

`injection-security`, `web-security`, `auth-security`, `crypto-misuse`, `secrets-exposure`.
