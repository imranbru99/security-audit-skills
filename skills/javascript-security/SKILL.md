---
name: javascript-security
description: >-
  Reviews JavaScript and TypeScript on the server and in the browser for
  prototype pollution, DOM XSS, command execution, path handling, and
  framework defaults in Express, Next.js, and React. Use when the target
  contains package.json or JS/TS source, or when the user asks for a
  JavaScript or TypeScript security review.
license: MIT
compatibility: Agent Skills clients. No packages or network required.
metadata:
  category: security
---

# JavaScript and TypeScript security

Types do not bind a SQL parameter or escape HTML. Review the runtime sink. A `.tsx` file is not safe because it typechecks, and a `string` type does not stop a query operator if the value was parsed from JSON.

Use `web-security`, `api-security`, `injection-security`, and `auth-security` for the general rules.

## When to use

Use this skill for Node.js services, Express, Fastify, Nest, Next.js, React, Vue, and browser bundles. Skip it for a repo with no JavaScript or TypeScript.

## Method

1. Read `package.json` for the framework, the auth library, and whether `jsonwebtoken` or a template engine is present. Note majors only when the verdict depends on them.
2. Find the server entry and the global middleware: auth, CSRF, body parser, CORS.
3. Walk request data into HTML, SQL, child processes, `fs` paths, `fetch`, and object merges.
4. For the browser, distinguish React/Vue default escaping from `dangerouslySetInnerHTML`, `v-html`, and assigning to the DOM.

## What to look for

### Browser and React / Vue / Next

- `dangerouslySetInnerHTML`, `v-html`, `element.innerHTML`, `insertAdjacentHTML`, `document.write` with data that is not a constant.
- `href` or `src` set from user data without a scheme allowlist. A `javascript:` URL is XSS even when the text around it is escaped.
- Next.js: a Server Action or route handler that trusts a client-supplied id with no session check. `"use server"` does not mean "authorized."
- Next.js: `NEXT_PUBLIC_` secrets. See `secrets-exposure`.
- Markdown rendered with `rehype-raw` or an HTML-capable renderer and no sanitizer.
- `postMessage` listener that does not check `origin` and then writes to the DOM or to storage. Report it when the message data reaches a sink; a listener that ignores the payload is not a finding.
- Prototype pollution gadget in the browser only matters if you can name the gadget (a merge into an object that later affects a sink). See below.

### Prototype pollution

Lead: a merge that copies request keys onto a shared object.

```javascript
function merge(target, source) {
  for (const key of Object.keys(source)) {
    if (source[key] && typeof source[key] === "object") {
      if (!target[key] || typeof target[key] !== "object") target[key] = {};
      merge(target[key], source[key]);
    } else {
      target[key] = source[key];
    }
  }
  return target;
}
```

`JSON.parse('{"__proto__": {"admin": true}}')` does not by itself change `Object.prototype`. It creates an own property named `__proto__`, which `Object.keys` lists. A flat `target[key] = value` then changes that target's prototype, so a later check of `target.admin` can pass, without changing `Object.prototype`. The recursive merge above is the global case: reading `target["__proto__"]` returns `Object.prototype`, and the recursive call copies the attacker's fields onto it. Walking `constructor` then `prototype` does the same. `for...in` reaches those keys too. `Object.assign` is the flat case, not the recursive one.

Confirm a security outcome: the polluted property bypasses an auth check, changes a template, or selects a command. If there is no gadget, rate Low or needs-validation. Do not rate every deep merge Critical.

Fixes that hold: merge into `Object.create(null)` or a `Map`, reject `__proto__`, `constructor`, and `prototype`, or use a library's safe merge and a schema that only copies known keys. The schema is the better fix when the object is a request body. Mass assignment is the usual real bug; pollution is the mechanism.

### Node sinks

- `child_process.exec` and `execSync` with a string built from request data. `execFile` / `spawn` with an argument array and no shell is the safe shape. `spawn(cmd, { shell: true })` is not safe.
- `eval`, `new Function`, `vm.runInNewContext` on request data. `vm` is not a security sandbox. Do not report it as "isolated."
- `fs` paths from request data without a root check. `path.join(root, req.query.file)` does not stay under `root` when the join result is absolute or uses `..`. Resolve and check the relative path.
- `res.redirect(req.query.next)` open redirect.
- SQL via a template string passed to `mysql.query`, `pg.query`, or `knex.raw`. Prisma's tagged `$queryRaw` binds interpolated values. `$queryRawUnsafe`, and any string built before the call, do not.
- Mongo `find(req.body.filter)` or a password field taken from the body as a value that might be an object. See `injection-security`.
- `fetch(req.body.url)` SSRF. Redirects are followed by default in Node's `fetch`.
- `tls.checkServerIdentity` overridden, or `rejectUnauthorized: false`.
- `cors({ origin: true })` or a reflected origin with `credentials: true` on a cookie API. See `web-security`.
- Express route mounted before `authMiddleware`, or `app.use(auth)` after the route was registered. Order is the control.

### JWT libraries

Pin `algorithms`. A hardcoded secret is a finding regardless of version. Do not claim the library accepts `alg: none` unless you checked that major version's verify path. If `package.json` and the lock disagree or the version is a range, mark the algorithm claim needs-validation and still report a weak or committed secret.

### ReDoS

Report a regular expression only when it is applied to attacker-controlled input, the pattern has nested quantifiers you can see, and it runs on the request path. Do not paste a pathological string into a live service. Rate Medium when one request can block the Node event loop for a long time. A complicated email regex on a short, length-capped field is usually a drop.

## Verify before you report

1. Show the source value and the sink function. TypeScript types are not evidence of runtime validation; `as string` and `any` are leads in the wrong direction.
2. For React XSS, confirm the data is not escaped by the default renderer. Text children are escaped.
3. For prototype pollution, name the gadget or lower the rating.
4. For Next.js, confirm whether the code runs on the server. A client component that only hides a button is not an access check. The server route must check.
5. Check middleware order in the actual entry file.
6. Do not run `node -e` payloads against a deployed URL.

## Severity

| Lead | Typical rating |
| --- | --- |
| `exec` of request data | High or Critical |
| Stored `dangerouslySetInnerHTML` of another user's content | High |
| Server route missing an ownership check | High |
| Prisma `$queryRawUnsafe` or string SQL with request data | High |
| Prototype pollution with an auth or command gadget | High; Low with no gadget |
| `rejectUnauthorized: false` toward a credentialed host | High |
| Open redirect | Low or Medium, as in `web-security` |
| ReDoS on an uncapped request field | Medium |

## Examples

```jsx
// Unsafe.
export function Comment({ comment }) {
  return <div dangerouslySetInnerHTML={{ __html: comment.body }} />;
}

// Safe.
export function Comment({ comment }) {
  return <div>{comment.body}</div>;
}
```

```javascript
// Unsafe: shell parses fileName.
exec(`convert ${fileName} out.png`);

// Safe: argument vector, and fileName still needs a path-root check.
execFile("convert", [fileName, "out.png"]);
```

## False positives

- React/Vue text interpolation without an HTML sink.
- `execFile` / `spawn` with `shell: false` and a fixed command.
- Prisma tagged templates and other builders that bind parameters.
- `JSON.parse` of a body that is then validated by a schema (`zod`, `joi`, `valibot`) which rejects non-strings and unknown keys, when the handler uses the parsed result and not `req.body` again.
- A deep merge of two server-side constants.
- `Math.random` used for a UI animation. Not a token.
- TypeScript `strict` mode as a security control. It is not one.
- Dependency audit output you did not trace. Use `supply-chain-security`.

## Related skills

`web-security` for XSS context, CSRF, and CORS. `api-security` for mass assignment, which in JavaScript is often `Object.assign(model, req.body)`. `injection-security` for SQL and NoSQL. `crypto-misuse` for `Math.random` tokens and `crypto.timingSafeEqual`.
