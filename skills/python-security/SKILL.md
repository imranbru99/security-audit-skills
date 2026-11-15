---
name: python-security
description: >-
  Reviews Python applications for framework-specific security bugs in Django,
  Flask, FastAPI, and the standard library, including sinks that look safe and
  are not. Use when the target contains Python, requirements, or pyproject, or
  when the user asks for a Python security review.
license: MIT
compatibility: Agent Skills clients. No packages or network required.
metadata:
  category: security
---

# Python security

Python web apps fail in the gaps between a safe default and an escape hatch: `raw()`, `mark_safe`, `shell=True`, `pickle`, `yaml.load`, and `DEBUG`. Review those hatches. Do not re-report the default as a bug.

Use `injection-security`, `web-security`, `auth-security`, and `secrets-exposure` for the general rules. This skill is the Python-specific correction.

## When to use

Use this skill when the tree contains `.py` files, `requirements.txt`, `pyproject.toml`, `Pipfile`, or Django/Flask/FastAPI project layout. Prefer it together with the bug-class skill that matches the sink.

## Method

1. Identify the framework from imports and project files. Note the major version only if the verdict depends on it.
2. Find the global protections: Django middleware list, `DEBUG`, `ALLOWED_HOSTS`, Flask `SECRET_KEY`, FastAPI dependencies that are actually attached to the router.
3. Search the leads below and trace each hit back to request data.
4. Apply the false-positive list before reporting. Django's ORM and template auto-escape close many leads.

## What to look for

### Framework defaults that change the verdict

| Stack | Usually safe | Opt-out that reopens the bug |
| --- | --- | --- |
| Django ORM | `.filter(field=value)`, lookups | `.raw()`, `.extra()`, `RawSQL`, string-built `WHERE` |
| Django templates | Auto-escape on | `\|safe`, `mark_safe(...)` around untrusted HTML, `{% autoescape off %}`. `format_html` escapes its arguments; it is unsafe when the format string itself is untrusted |
| Django CSRF | `CsrfViewMiddleware` on cookie-session views | `@csrf_exempt` on a state-changing view |
| Django `DEBUG` | Off in production settings | `DEBUG = True` in the settings module that production imports |
| Flask / Jinja2 | Auto-escape on for `.html` in current Flask | `render_template_string(request.args[...])`, `\|safe` |
| FastAPI | Type coercion on declared body models | Route with no auth dependency; a dependency that only checks "header present" |

`assert user.is_admin` is not an authorization check. Python strips `assert` when run with `-O`. Report it if the only guard is an assert.

### Injection and code execution

- `cursor.execute(f"...")`, `execute("..." % values)`, or `execute("...".format(...))`. DB-API `execute(sql, params)` with placeholders is safe. Read the arguments.
- SQLAlchemy `text(f"SELECT ... {value}")`. `text("... :name")` plus a bound dict is safe.
- Django `order_by(request.GET["sort"])` without an allowlist.
- `subprocess` with `shell=True`, `os.system`, `os.popen`.
- `eval`, `exec`, `pickle.loads`, `shelve`, `dill`, `cloudpickle` on request bytes or a cache the attacker can write.
- `yaml.load` with `Loader`, `UnsafeLoader`, or no loader. `safe_load` and `SafeLoader` parse data only. PyYAML before 5.1 defaults `yaml.load` to an unsafe loader; 5.1 warns; 6.0 raises if `Loader` is omitted. `Loader=yaml.Loader` is still unsafe. Check the call that is in the file, not the package name.
- `jinja2.Template(user_string)` and Flask `render_template_string(user_string)`. That is server-side template injection, not XSS.
- `format` strings that name attributes (`"{0.__class__}".format(obj)`) when the format string is user-controlled.

### Web and auth

- `mark_safe` and `\|safe` on user content. Stored XSS.
- `HttpResponse` built with an HTML string concatenation of request data, bypassing the template engine.
- Django `@csrf_exempt` on login, password change, or payment views. The API exemption is normal for token auth; say which auth the view uses before reporting CSRF.
- `django.contrib.auth` views replaced by a custom login that compares `password == user.password`.
- `SECRET_KEY` hardcoded, or Flask `secret_key = "dev"`. Session forgery if the key is known. High when sessions are cookie-signed with that key.
- `ALLOWED_HOSTS = ["*"]` together with a reset-link or absolute URL built from the request host. Report host poisoning, not the setting alone.
- FastAPI route that trusts `X-User-Id` or a path id with `Depends` only checking that a JWT parses, not that the subject owns the row.
- Pydantic response model that returns the ORM object including `password` or `is_superuser` to the client. Prefer an explicit response model.

### Requests, files, and TLS

- `requests.get(user_url)`, `urllib.request.urlopen(user_url)`, `httpx` the same way, with redirects left on. SSRF. Also `verify=False`.
- `open(os.path.join(root, request.args["name"]))` without a resolved-path check. `pathlib.Path` division does not stop `..`.
- `zipfile` or `tarfile.extractall` on an upload without checking member names (zip slip). Reject absolute paths and `..` after normalization.
- `tempfile.mktemp` (race). Use `NamedTemporaryFile` or `mkstemp`. Low unless the race crosses a trust boundary you can name.
- `DEBUG = True` or Flask `debug=True` in the production entrypoint. High: interactive debugger or env dump.

### Deserialization footnote

JSON is safe as a parser. It is not safe as authorization: do not trust a `role` field in a JSON body. `pickle` is not a parser for untrusted data. Report `pickle.loads` on a request, a queue, or a user-writable cache as code execution.

## Verify before you report

1. Confirm the framework and that this settings module is the one production loads (`manage.py`, `wsgi.py`, `settings/prod.py`). A `DEBUG = True` in `settings/dev.py` that production does not import is not a finding.
2. For SQL, quote the `execute` arguments. Distinguish a placeholder from Python formatting.
3. For XSS, confirm auto-escape is on and then show the `mark_safe` / `\|safe` opt-out, or show HTML built without a template.
4. For SSRF, show the URL source and that redirects are followed or the host is not allowlisted.
5. Do not run the payload. `pickle` and template injection are reportable from the call.

## Severity

Use the bug-class skill's scale. Python-specific anchors:

| Lead | Typical rating |
| --- | --- |
| `pickle.loads` or template-string render of request data | High or Critical (code execution), based on who can call it |
| `DEBUG = True` in the production settings | High |
| Django `raw` / string `execute` with request data | High when the DB role can read or write sensitive data |
| `mark_safe` of stored user HTML | High |
| `shell=True` with request data | High or Critical |
| `SECRET_KEY` default in the repo, used to sign sessions | High |
| `assert` as the only admin check | High if the view is reachable |
| `verify=False` on a call that sends a credential | High |

## Examples

```python
# Unsafe: the f-string is the query text. A quote in name changes the statement.
def search_users(cursor, name: str):
    cursor.execute(f"SELECT id, email FROM users WHERE name LIKE '%{name}%'")

# Safe: the wildcard is inside the bound value, not inside the SQL structure.
def search_users(cursor, name: str):
    cursor.execute("SELECT id, email FROM users WHERE name LIKE ?", (f"%{name}%",))
```

```python
# Unsafe authorization.
def admin_view(request):
    assert request.user.is_staff
    return render(request, "admin.html")

# Safe authorization.
def admin_view(request):
    if not request.user.is_staff:
        raise PermissionDenied
    return render(request, "admin.html")
```

## False positives

- Django `.filter` / `.exclude` with user strings as values.
- `execute(sql, params)` and SQLAlchemy bound parameters.
- Jinja auto-escape without `\|safe`, and Django templates without `mark_safe`.
- `yaml.safe_load`.
- `subprocess.run([...], shell=False)` with a constant executable and a path that has been constrained to a root.
- `DEBUG = True` only in a development settings module production does not import. Mention it if the Dockerfile or gunicorn command points at that module.
- `requests.get` of a constant URL.
- Bandit findings you did not trace. Bandit does not understand Django CSRF middleware or your wrapper around `subprocess`.

## Related skills

`injection-security`, `web-security`, `auth-security`, `secrets-exposure`, `crypto-misuse`. For dependency pins and `pip` install scripts, use `supply-chain-security`.
