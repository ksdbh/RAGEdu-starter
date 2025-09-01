import React, { useState } from "react";

export type Citation = {
  title?: string;
  page?: number | string;
  snippet?: string;
};

export function getConfidenceLabel(confidence: any): "low" | "medium" | "high" {
  if (confidence === null || confidence === undefined) return "low";
  if (typeof confidence === "string") {
    const v = confidence.toLowerCase();
    if (v === "low" || v === "medium" || v === "high") return v as "low" | "medium" | "high";
  }
  if (typeof confidence === "number") {
    if (confidence < 0.33) return "low";
    if (confidence < 0.66) return "medium";
    return "high";
  }
  // fallback
  return "medium";
}

export default function Demo(): JSX.Element {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState<string | null>(null);
  const [citations, setCitations] = useState<Citation[]>([]);
  const [confidence, setConfidence] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const apiBase = process.env.NEXT_PUBLIC_API_URL || "";

  async function ask() {
    setError(null);
    setAnswer(null);
    setCitations([]);
    setConfidence(null);

    if (!question.trim()) {
      setError("Please enter a question");
      return;
    }

    setLoading(true);
    try {
      const url = `${apiBase.replace(/\/+$/, "")}/rag/answer`;
      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || res.statusText || "Request failed");
      }

      const data = await res.json();

      // backend may return different shapes; be defensive
      setAnswer(data.answer ?? data.text ?? "");
      setCitations(Array.isArray(data.citations) ? data.citations : []);
      setConfidence(data.confidence ?? null);
    } catch (err: any) {
      setError(err?.message ?? String(err));
    } finally {
      setLoading(false);
    }
  }

  function renderConfidenceChip() {
    const label = getConfidenceLabel(confidence);
    const bg = label === "high" ? "#d1fae5" : label === "medium" ? "#fef3c7" : "#fee2e2";
    const color = label === "high" ? "#065f46" : label === "medium" ? "#92400e" : "#991b1b";
    return (
      <span
        style={{
          display: "inline-block",
          padding: "2px 8px",
          borderRadius: 9999,
          background: bg,
          color,
          fontSize: 12,
          fontWeight: 600,
        }}
        data-testid="confidence-chip"
      >
        {label}
      </span>
    );
  }

  return (
    <div style={{ maxWidth: 780, margin: "24px auto", padding: 16, fontFamily: "Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial" }}>
      <h2 style={{ margin: "0 0 12px 0" }}>RAG Demo</h2>

      <div style={{ marginBottom: 12 }}>
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about the uploaded documents..."
          rows={4}
          style={{ width: "100%", padding: 12, fontSize: 14, borderRadius: 6, border: "1px solid #e5e7eb" }}
          data-testid="question-input"
        />
      </div>

      <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 16 }}>
        <button
          onClick={ask}
          disabled={loading}
          style={{
            background: loading ? "#94a3b8" : "#0ea5a4",
            color: "white",
            padding: "8px 14px",
            borderRadius: 6,
            border: "none",
            cursor: loading ? "not-allowed" : "pointer",
            fontWeight: 600,
          }}
          data-testid="ask-button"
        >
          {loading ? "Thinking..." : "Ask"}
        </button>
        <div style={{ color: "#6b7280", fontSize: 13 }}>Tip: keep questions short and specific.</div>
      </div>

      <div>
        {error ? (
          <div style={{ color: "#b91c1c", background: "#fff1f2", padding: 10, borderRadius: 6 }} data-testid="error-box">
            {error}
          </div>
        ) : null}

        {!answer && !error && (
          <div style={{ color: "#6b7280", padding: 12 }} data-testid="empty-state">Enter a question and click Ask to see a generated answer with citations.</div>
        )}

        {answer !== null && (
          <div style={{ marginTop: 12 }}>
            <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 8 }}>
              <h3 style={{ margin: 0 }}>Answer</h3>
              {renderConfidenceChip()}
            </div>
            <div style={{ padding: 12, background: "#f8fafc", borderRadius: 6, whiteSpace: "pre-wrap" }} data-testid="answer-text">
              {answer || "(no answer returned)"}
            </div>

            <div style={{ marginTop: 14 }}>
              <h4 style={{ marginBottom: 8 }}>Citations</h4>
              {citations.length === 0 ? (
                <div style={{ color: "#6b7280" }}>No citations returned.</div>
              ) : (
                <ol style={{ paddingLeft: 18 }} data-testid="citations-list">
                  {citations.map((c, idx) => (
                    <li key={idx} style={{ marginBottom: 10 }}>
                      <div style={{ fontWeight: 700 }}>{c.title ?? "(untitled)"}</div>
                      <div style={{ color: "#6b7280", fontSize: 13 }}>Page: {c.page ?? "?"}</div>
                      <div style={{ marginTop: 6, background: "#ffffff", padding: 8, borderRadius: 4, border: "1px solid #e6edf3" }}>{c.snippet ?? "(no snippet)"}</div>
                    </li>
                  ))}
                </ol>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
