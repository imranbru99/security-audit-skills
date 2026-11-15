---
name: injection-security
description: >-
  Traces untrusted input into SQL, command, NoSQL, LDAP, XPath, template,
  header, and mail injection sinks, and separates those sinks from APIs that
  bind parameters. Use when reviewing queries, shell calls, dynamic templates,
  or parsers, or when the user mentions injection, SQLi, command injection,
  SSTI, or NoSQL injection.
license: MIT
compatibility: Agent Skills clients. No packages or network required.
metadata:
  category: security
---

# Injection

Injection is untrusted data parsed as code, query, or structure. The fix is to keep data out of the structure: bind parameters, pass argument arrays, or encode for the exact context. Filtering characters is a last resort and usually fails.

Use the language skill for the local API names. Use `web-security` for HTML encoding. A sink the attacker cannot influence is not a finding.

## When to use

Use this skill when request data, database data another user wrote, file contents, or queue payloads are concatenated into a command, query, template, filter, path, or header. Skip it when the review is only IAM or CI and there is no parser in scope.

## Method

1. Find sinks: query execution, process spawn, template compile of a string, LDAP or XPath filters, mail headers, response headers, deserializers of attacker bytes.
2. Walk backward to sources. Include second-order data: a value stored earlier and concatenated later.
3. Classify the API. Binding parameters is safe. Interpolating into the statement text is not, even if a comment says "escaped."
4. Check dynamic identifiers separately. Table names, column names, and `ORDER BY` cannot be bound as values. They need an allowlist.
5. Try to disprove. Constants, bound parameters, and ORM expression builders are the usual reasons to drop the lead.

## What to look for

### SQL

Unsafe: string concatenation, f-strings, `fmt.Sprintf`, percent-formatting, or `+` used to build the SQL text that is executed.

Safe: the SQL string is constant (or has only allowlisted identifiers) and attacker values are passed beside it.

```python
# Unsafe.
cursor.execute(f"SELECT id FROM users WHERE email = '{email}'")

# Safe. The placeholder is not Python formatting. The value is a parameter.
cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
```

Watch the API. In Python DB-API drivers, `%s` inside the SQL string passed to `execute(sql, params)` is often a placeholder, while `"... %s" % email` is injection. Read the call. `execute(sql % user)` is unsafe. `execute(sql, (user,))` is the safe form for that driver.

ORM leads: Django `raw`, `extra`, `RawSQL`; SQLAlchemy `text()` built by concatenation; any `.where(f"...")`. ORM filters like `.filter(email=email)` bind. `order_by(request_arg)` does not.

Casting with `int()` prevents injection for that one value if a failed cast aborts the request. It does not make a dynamic `ORDER BY` or `LIMIT` clause safe unless the integer is a bound value. It does not help string fields.

Second-order: the value is stored safely, then a later job interpolates it. Follow jobs and admin exports, not only the request handler.

### Command

Unsafe: `os.system`, `subprocess` with `shell=True`, `exec.Command("sh", "-c", userString)`, `child_process.exec`, backticks, or string building of a command line.

Safe: argument vector, no shell. `subprocess.run(["convert", path, "out.png"], shell=False)` still needs a path check if `path` may be a flag or point outside the work directory. `shell=False` stops shell metacharacters; it does not stop a dangerous argv.

Do not report a command built entirely from constants.

### NoSQL and LDAP

MongoDB and similar: the query object is built from JSON the client sent, so operators (`$gt`, `$ne`, `$where`) are data. If `username` is supposed to be a string and the code passes `req.body.username` straight into `find`, an object changes the query. The fix is a schema that requires a string (or an explicit cast that rejects non-strings) before the query.

`$where` and `mapReduce` with client JavaScript are code execution leads. Report them when the argument is attacker-controlled.

LDAP and XPath: concatenation into the filter is the same bug. The fix is the library's escaped-filter or parameterized API, not stripping `*`.

### Template injection

If the attacker controls the template source (`render_template_string(user)`, `jinja2.Template(user)`, `eval` of a template), treat it as code execution in that template engine, not as XSS. The fix is a constant template and data passed as context.

User content rendered by a fixed template is XSS, handled in `web-security`, unless the template marks it safe.

### Header and mail injection

User data interpolated into `Set-Cookie`, `Location` (also an open redirect), or mail headers without stripping CR/LF. Report header injection when the response header or mail header is actually built from that data. Modern frameworks that set headers through a map do not concatenate; check before reporting.

### Deserialization

`pickle.loads`, Java `ObjectInputStream`, PHP `unserialize`, YAML `load` (unsafe), and .NET binary formatter on attacker bytes are code-execution leads when the library is known to instantiate types from the payload. The fix is to not deserialize untrusted data with those APIs. Use a data-only format (JSON) and a schema. Do not try to produce a gadget chain. If the code path is present, the finding is the unsafe API on untrusted input, rated for code execution when that API allows it.

## Verify before you report

1. Quote the sink call and the argument that is attacker-controlled.
2. Show there is no binding, allowlist, or shell-free argv between the source and the sink.
3. For ORMs and DB-API, state which form the call uses. Misreading `%s` is a common false positive either way; look at the arguments.
4. Name the impact you can actually justify: read or write through that database role, command execution as that OS user, or query-operator bypass. Do not claim full RCE for a SQL sink unless the database user can run OS commands and the code reaches that feature.
5. Do not send attack strings to a running environment. A source trace is the verification.

## Severity

| Sink | Typical rating |
| --- | --- |
| SQL injection on a database role that can read or write sensitive tables | High. Critical if unauthenticated and the role is administrative or the data is broadly sensitive. |
| Command injection via a shell | High or Critical, matching who can hit the route and which user the process runs as. |
| NoSQL operator injection that bypasses a login or an ownership filter | High |
| Template source injection | High or Critical (code execution in the app) |
| CR/LF header injection | Medium when it changes a cookie or a redirect; Low when it only splits a non-security header |
| Dynamic `ORDER BY` with an allowlist missing | Low or Medium, based on whether it leaks rows or only sorts them |

Lower the rating if the only actor who can supply the data is an admin who can already run queries in a console you saw in the same app.

## Examples

Command arguments:

```python
# Unsafe: metacharacters are parsed by the shell.
os.system("convert " + filename + " out.png")

# Safe: no shell. Still check that filename stays inside the upload root.
subprocess.run(["convert", filename, "out.png"], check=True)
```

NoSQL login:

```javascript
// Unsafe: password can be an object, not a string.
await User.findOne({ username: req.body.username, password: req.body.password });

// Safe: both fields must be strings before they are used as values.
const username = z.string().parse(req.body.username);
const password = z.string().parse(req.body.password);
const user = await User.findOne({ username });
if (!user || !(await verifyPassword(password, user.passwordHash))) {
  return res.status(401).end();
}
```

The safe login does not ask the database to compare the password. It loads by the username string and verifies a password hash in application code.

## False positives

- Bound parameters, including DB-API placeholders and ORM value filters.
- `text("... :email")` with a real parameter dict, not an f-string.
- `int()` (or a schema integer) around the only interpolated value, with the failure path aborting the request, and no identifier interpolation beside it.
- Allowlisted sort columns compared against a fixed set before interpolation.
- `subprocess` argument arrays with `shell=False` and no attacker-controlled executable path. If the attacker chooses the executable, that is still a finding.
- Shell on a constant command string.
- `pickle` or `unserialize` on data the server itself wrote and the attacker cannot replace (signed or local admin file). If the attacker can replace the bytes, it is a finding.
- YAML `safe_load` / `SafeLoader`. `yaml.load` without a loader is unsafe on PyYAML defaults in older versions; check the call and the version instead of assuming.
- HTML escaping reported as "injection." Move that to `web-security` unless the template source itself is attacker-controlled.

## Related skills

`python-security`, `javascript-security`, `go-security`, and `php-security` name the local APIs. `web-security` covers HTML sinks. `auth-security` covers the case where injection bypasses a login check.
