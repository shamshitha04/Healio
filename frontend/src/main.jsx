import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import "./styles.css";

function FatalScreen({ error }) {
  return (
    <main className="min-h-screen bg-red-50 p-6 text-red-950">
      <section className="mx-auto mt-12 max-w-2xl rounded-lg border border-red-200 bg-white p-5 shadow-sm">
        <h1 className="text-2xl font-black">Healio could not start</h1>
        <p className="mt-3 text-sm font-semibold leading-6 text-red-800">
          The frontend hit a startup error. Open the browser console for the full
          stack trace, then restart the dev server after fixing it.
        </p>
        {error?.message && (
          <pre className="mt-4 overflow-auto rounded-lg bg-red-950 p-4 text-sm font-semibold text-red-50">
            {error.message}
          </pre>
        )}
      </section>
    </main>
  );
}

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error) {
    console.error("Healio frontend crashed:", error);
  }

  render() {
    if (this.state.error) {
      return <FatalScreen error={this.state.error} />;
    }

    return this.props.children;
  }
}

const rootElement = document.getElementById("root");

if (!rootElement) {
  document.body.innerHTML =
    '<main style="padding:24px;font-family:system-ui,sans-serif"><h1>Healio could not start</h1><p>Missing root element in index.html.</p></main>';
} else {
  createRoot(rootElement).render(
    <React.StrictMode>
      <ErrorBoundary>
        <App />
      </ErrorBoundary>
    </React.StrictMode>,
  );
}
