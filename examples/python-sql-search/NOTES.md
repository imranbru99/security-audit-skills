# SQL search

**Confirmed.** High, assuming `search_users` is reachable from a request and the database role can read customer rows. The f-string is the statement text. `cursor.execute` receives no parameter tuple.

**Fix.** Constant SQL, value passed beside it, wildcards inside the bound value. The placeholder glyph depends on the driver (`?` for sqlite3, `%s` for psycopg2's parameter API). The safe property is the separate argument, not the glyph.

**False positive to avoid.** Do not call `execute(sql, params)` injection when the value really is in `params`. Do not report the `%` characters in the bound LIKE pattern as SQL injection. A name containing `%` widens the match; that is a separate Low issue only if the product treats search as an authorization boundary.
