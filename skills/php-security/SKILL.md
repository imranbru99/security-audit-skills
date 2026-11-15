---
name: php-security
description: >-
  Reviews PHP and Laravel applications for mass assignment, missing
  authorization, SQL and file inclusion, unsafe deserialization, Blade
  escaping, and middleware that does not cover the route. Use when the target
  contains PHP, composer.json, or Laravel, or when the user asks for a PHP or
  Laravel security review.
license: MIT
compatibility: Agent Skills clients. No packages or network required.
metadata:
  category: security
---

# PHP and Laravel security

Most current PHP findings are in Laravel mass assignment, route middleware groups, Blade opt-outs, and raw queries. Older PHP footguns (`extract`, `unserialize`, dynamic `include`) still matter when the code uses them. Check both.

Use `api-security`, `auth-security`, `web-security`, and `injection-security` for the general rules.

## When to use

Use this skill when the tree contains `.php` files, `composer.json`, `artisan`, or Blade templates. Skip it for a repo that only mentions PHP in a README.

## Method

1. Read `routes/web.php`, `routes/api.php`, and `bootstrap/app.php` or `app/Http/Kernel.php`. Note which middleware group wraps which routes. Laravel's `web` group includes CSRF and the session. The `api` group does not include CSRF.
2. Read models for `$fillable` and `$guarded`. `$guarded = []` means every column can be mass-assigned, including `is_admin`.
3. Search the leads below and trace them to request input.
4. Decide auth before CSRF. A bearer-token API does not need CSRF. A cookie-authenticated SPA on the `api` group often does.

## What to look for

### Laravel authorization and mass assignment

- `Model::find($id)` or `findOrFail($id)` followed by `update`, `delete`, or a JSON return, with no policy and no `user_id` constraint. Route-model binding (`User $user`) does not authorize. It only loads the row.
- `$request->all()`, `$request->input()`, or `request()->all()` passed to `create`, `update`, `fill`, or `forceFill`. `forceFill` bypasses `$fillable`.
- `$fillable` containing `is_admin`, `role`, `owner_id`, `balance`, or `email_verified_at`.
- A policy or `FormRequest::authorize` that `return true`, or a controller that never calls `$this->authorize` / `Gate`.
- Admin routes in `routes/web.php` outside the `auth` and role middleware.
- `withoutMiddleware(VerifyCsrfToken::class)` or a CSRF exception for a cookie-authenticated POST.

Report mass assignment and missing object authorization as two findings when the fixes differ: an allowlist of fields, and a policy or a scoped query. They often share an endpoint. Cross-reference them.

### SQL

- `DB::raw`, `whereRaw`, `selectRaw`, `orderByRaw` with interpolated variables.
- `"SELECT ... $id"` passed to `DB::select` or PDO `query`.
- Eloquent `where('email', $email)` binds. That is safe.
- Dynamic column names from the request passed to `orderBy`. Allowlist them.

PDO prepared statements are safe when the value is a bound parameter. A value interpolated into the SQL string before `prepare` is not a bound parameter. Emulated prepares are still safe if the driver quotes bound parameters; the bug is concatenation.

### XSS and Blade

- `{!! $userHtml !!}` renders raw HTML. `{{ $var }}` is escaped.
- `{!! !!}` of a translation or markdown field that users can edit.
- Responses built with string-concatenated HTML outside Blade.
- User-controlled SVG or HTML uploaded and served from the same origin with a browser-renderable content type.

### PHP language leads

- `unserialize` on cookies, request bodies, or cache entries the attacker can write. Prefer `json_decode` and a schema. Do not build a gadget chain; the unsafe call on untrusted bytes is the finding.
- `include`, `require`, or `file_get_contents` with a request path or URL. Dynamic include is code execution when the attacker chooses a remote or uploaded file. `allow_url_include` and `allow_url_fopen` make the remote case worse; if you cannot see `php.ini`, say so.
- `eval`, `assert` with a string, `preg_replace` with the `/e` modifier (legacy), `create_function`.
- `extract($_GET)` or `extract($_POST)`, which overwrites local variables.
- `==` or `!=` to compare tokens, reset codes, or HMAC strings. PHP type juggling makes some strings compare equal. Use `hash_equals` for secrets and `===` for other checks where type matters.
- `md5` or `sha1` as a password hash, and `rand` or `mt_rand` for reset tokens. See `crypto-misuse`. `random_bytes` and `password_hash` / `password_verify` are the safe standard-library choices.
- `APP_DEBUG=true` or `app.debug` true in the environment file that production loads. Whoops-style pages dump environment variables. High when that file is the production config.
- `file_get_contents($request->url)` or Guzzle with a user URL. SSRF.

### Sessions and auth libraries

- Session cookie settings in `config/session.php`: `secure`, `http_only`, `same_site`. Report a concrete CSRF or XSS chain, not the config line alone. See `web-security`.
- Sanctum or Passport used as "the SPA is safe" while API routes accept the session cookie and lack CSRF. Read the guard on the route.
- Password reset notifications that build the URL from the request host instead of `config('app.url')`.

## Verify before you report

1. Show the route and the middleware group. A policy in `AuthServiceProvider` that is never referenced from this route does not count.
2. For mass assignment, name the dangerous column and show it is fillable and present in the request dump the handler passes to `update` or `create`.
3. For SQL, quote the raw call. Eloquent value bindings are not findings.
4. For Blade, show `{!! !!}` or another raw sink, and that the value can contain another user's content or an attacker's stored content.
5. For `==` on a secret, show the operands. Comparing two integers with `==` is not the bug.
6. Do not send a forged request to a deployed Laravel app.

## Severity

| Lead | Typical rating |
| --- | --- |
| Missing ownership check on another user's model | High |
| `forceFill` or `$guarded = []` letting a user set `is_admin` or `role` | High |
| Raw SQL with request interpolation | High |
| `{!! !!}` of stored user HTML shown to other users | High |
| `unserialize` of a cookie or request body | High or Critical (code execution) if the call is reachable |
| Dynamic `include` of a request path | High or Critical |
| `APP_DEBUG=true` in production config | High |
| CSRF exempt on a cookie-authenticated state change | Medium or High, matching the action |
| `==` compare of a reset token | Medium or High, based on token entropy and the type-juggling exposure |
| `mt_rand` reset token | High |

## Examples

```php
// Unsafe: any caller who knows the id can set is_admin if it is fillable.
public function update(Request $request, $id)
{
    $user = User::findOrFail($id);
    $user->update($request->all());
    return response()->json($user);
}
```

```php
// Safe: the policy binds the row to the caller, and only these fields are written.
public function update(Request $request, User $user)
{
    $this->authorize('update', $user);
    $data = $request->validate([
        'name' => ['required', 'string', 'max:100'],
        'email' => ['required', 'email'],
    ]);
    $user->update($data);
    return response()->json($user->only(['id', 'name', 'email']));
}
```

The model `$fillable` should be `name` and `email`, not `is_admin`. Validation is the allowlist; `$fillable` is the backstop when another call site forgets.

## False positives

- `{{ }}` in Blade, and Eloquent `where` / `create` with an explicit attribute list.
- CSRF "missing" on `routes/api.php` when the guard is a bearer token and the browser does not send it automatically.
- Route-model binding described as IDOR when a policy or a global scope constrains the tenant and you traced that scope.
- `unserialize` of a session payload Laravel itself produced and the attacker cannot replace. If the session driver stores the payload in a cookie the user can edit, and there is no integrity check, that is a finding.
- `==` between a constant and a strict internal enum you already cast to int.
- `password_hash` / `password_verify` with `PASSWORD_DEFAULT`.
- Mass assignment when `$fillable` is the safe list and the handler uses `$request->validated()` from a `FormRequest` that lists the same fields.
- A scanner result for `eval` inside `vendor/` that application code never reaches. Use `supply-chain-security` for Composer packages instead of treating `vendor` as the app.

## Related skills

`auth-security`, `api-security`, `web-security`, `injection-security`, `crypto-misuse`, `secrets-exposure`.
