# Session JWT

**Confirmed.** High when this function is what accepts a browser or API session. The HMAC secret is the string `secret` in source. Anyone who can read the repository can forge a session if the library verifies HS256 with that secret. That does not require a live forge to report.

**Needs validation.** Whether `jwt.verify` without `algorithms` accepts the `none` algorithm depends on the installed `jsonwebtoken` major. Check `package.json` and the lockfile. Report an unpinned algorithm as part of the fix even when `none` is rejected, and do not claim `none` is accepted until the version says so.

**Fix.** Pin `algorithms`, set the issuer and audience the application actually issues, and load a random secret of at least 32 characters from the environment. Rotate the old secret. Sessions signed with `secret` remain forgeable until rotation.

**False positive to avoid.** Do not report "uses JWT" or "JWT is stateless" as a vulnerability. Do not report a missing algorithm pin as Critical `none` acceptance without the version check.
