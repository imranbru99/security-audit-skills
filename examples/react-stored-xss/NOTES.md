# Stored comment

**Confirmed.** High when `comment.body` is attacker-controlled and the comment is shown to other users. `dangerouslySetInnerHTML` inserts HTML. The author heading is a text child and is escaped; do not report `comment.author` as XSS from this component.

**Fix.** Render the body as text. If the product must allow a subset of formatting, sanitize with a maintained HTML sanitizer that drops scripts, event handlers, and unexpected URL schemes, then keep tests for those cases. A CSP with `unsafe-inline` does not replace the fix.

**False positive to avoid.** JSX text expressions (`{comment.body}`) are escaped. Do not report React itself as an XSS engine. A body that is only ever rendered back to the same author, with no way to share the comment, is self-XSS and is Low or a drop unless it can be planted on another user.
