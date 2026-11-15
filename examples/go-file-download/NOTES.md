# Export download

**Confirmed.** High if files outside `/var/app/exports` include secrets or other users' data, which a path of `..` segments or an absolute path reaches. `filepath.Join` calls `Clean`. `Join("/var/app/exports", "../../etc/passwd")` leaves the export root. An absolute second element discards the root entirely. `http.ServeFile` then opens that path. It does not re-apply a jail.

**Fix.** Resolve the path and reject a `filepath.Rel` result of `..` or a path that starts with `..` plus a separator. Then serve the checked path.

**False positive to avoid.** `http.Dir` rooted at a constant directory does contain names for a file server. This handler does not use `http.Dir`. `filepath.Join` of a constant name is fine. Do not report a null-byte variant as a second bug on current Go; the secure helper rejects NUL as hygiene, and Go paths do not truncate on NUL the way old C libraries did.
