// INTENTIONALLY VULNERABLE — teaching fixture for security-audit-skills.
// Do not deploy. Do not render untrusted HTML.

export function Comment({ comment }) {
  return (
    <article>
      <h3>{comment.author}</h3>
      <div dangerouslySetInnerHTML={{ __html: comment.body }} />
    </article>
  );
}
