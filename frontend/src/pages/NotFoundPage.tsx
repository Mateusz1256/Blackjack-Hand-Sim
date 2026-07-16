import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <section className="panel">
      <h2>Page Not Found</h2>
      <p className="muted">The requested workspace route does not exist.</p>
      <Link className="text-link" to="/">
        Return to overview
      </Link>
    </section>
  );
}
