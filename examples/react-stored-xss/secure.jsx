// Safe counterpart to vulnerable.jsx. Text children are escaped.

export function Comment({ comment }) {
  return (
    <article>
      <h3>{comment.author}</h3>
      <div>{comment.body}</div>
    </article>
  );
}
