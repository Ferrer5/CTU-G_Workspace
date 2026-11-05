import { Link } from 'react-router-dom';

export default function NotAllowedPage() {
  return (
    <main className="app-bg flex min-h-screen items-center justify-center px-4">
      <section className="surface-glass w-full max-w-lg rounded-2xl p-8 text-center">
        <h1 className="fg-strong text-2xl font-bold">Not allowed</h1>
        <p className="fg-muted mt-3">
          Your account does not have the permission required to open this page.
        </p>
        <Link className="btn btn-primary mt-6 inline-flex" to="/dashboard">
          Return to dashboard
        </Link>
      </section>
    </main>
  );
}
