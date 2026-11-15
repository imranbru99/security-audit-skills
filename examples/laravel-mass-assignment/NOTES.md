# User update

**Two confirmed findings, one endpoint.**

1. **High — missing object authorization.** `findOrFail($id)` loads any user. The handler never compares the row to the caller and never calls a policy. Route-model binding in the secure version still does not authorize by itself; `authorize('update', $user)` does.
2. **High — mass assignment.** `$request->all()` is written onto the model. If `is_admin`, `role`, or `email_verified_at` is fillable, or `$guarded` is empty, the caller sets it. The response also returns the whole model, which is excessive data if hidden attributes include a password hash. Report that only when the model actually exposes those attributes.

**Fix.** Authorize, validate an allowlist, keep `is_admin` out of `$fillable`, and return an explicit column list.

**False positive to avoid.** Do not report mass assignment when the model `$fillable` is only `name` and `email` and the controller already passes `$request->validated()` from a form request with the same keys. Do not treat route-model binding as an authorization check.
