# Sample finding

This is the write-up the skills should produce for `examples/python-sql-search/`. It is the tone and the evidence bar, not a template to fill with guesses.

### High — Search text is concatenated into the SQL statement

- **Location:** `examples/python-sql-search/vulnerable.py`, `search_users`
- **Attacker and precondition:** Anyone who can call the function with a `name` string. In the application this is the public search field. No authentication is required at this function.
- **Trust boundary:** Request data crosses into the database as SQL syntax, using the application database role.
- **Impact:** The caller can change the statement the database runs. With the application role able to read `users` and `orders`, that includes other customers' rows. The exact extra statements depend on the database, and the review does not need to demonstrate them to confirm the defect.
- **Evidence:** `search_users` builds the statement with an f-string and passes that string to `cursor.execute` as the only argument. There is no parameter tuple. Nothing between the caller and this function constrains quotes or SQL keywords.
- **Why this survived an attempt to disprove it:** This is not DB-API parameter binding. A placeholder form would be `execute(sql, (value,))`. The `%` wildcards are inside the interpolated string, so they do not make the value a bound parameter. No ORM is involved.
- **Fix:** Keep the SQL text constant and bind the search string. Put the `LIKE` wildcards in the bound value. See `secure.py`.
- **Regression check:** A test that calls `search_users` with a name containing a single quote and asserts the statement text passed to the cursor stays constant while the quote appears only in the parameter tuple.

**Needs validation:** none for this fixture. The database role's privileges in production would raise or lower severity if the role cannot read other tenants' tables. The code defect is confirmed either way.

**Not a second finding:** a user who includes `%` or `_` will match more rows inside the `LIKE` pattern. That is Low, and it is not SQL injection. Do not fold it into this issue.
