'use client';
import { useState } from 'react';
import { API_BASE } from '../lib/api';

type Citation = {
  // The backend currently returns a free-form object for citations; these fields are common
  title?: string;
  url?: string;
  excerpt?: string;
  [k: string]: any;
};

type RagResponse = {
  answer: string;
  citations: Citation[];
  metadata: Record<string, any>;
};

export default function Home() {
  const [q, setQ] = useState('Explain Dijkstra vs A* with an example.');
  const [a, setA] = useState<string | null>(null);
  const [citations, setCitations] = useState<Citation[]>([]);
  const [mode, setMode] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function ask() {
    if (!q.trim()) {
      setError("Please enter a question.");
      return;
    }
    setMode(null);
    setLoading(true);
    setA(null);
    setCitations([]);
    setError(null);
    try {
      const resp = await fetch(API_BASE + '/rag/answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q, top_k: 5 })
      });

      if (!resp.ok) {
        const txt = await resp.text();
        throw new Error(`API error: ${resp.status} ${txt}`);
      }

      const data = (await resp.json()) as RagResponse;
      setA(data.answer);
      setMode(data.metadata?.mode ?? null);
      setCitations(Array.isArray(data.citations) ? data.citations : []);
    } catch (err: any) {
      setError(err?.message ?? 'Unknown error');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="p-8 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">RAGEdu</h1>
      <p className="mb-4">Local Q&A demo. Answers and sample sources are simulated; no course documents have been ingested.</p>
      <nav className="mb-4" aria-label="Demo pages">
        <a href="/auth">Mock sign-in</a> · <a href="/demo">Alternate Q&A</a> · <a href="/quiz">Quiz demo</a> · <a href="/quest-map">Quest map demo</a>
      </nav>
      <label htmlFor="question">Your question</label>

      <textarea
        id="question"
        className="w-full border p-3 rounded mb-2"
        rows={4}
        value={q}
        onChange={e => setQ(e.target.value)}
      />

      <div className="flex gap-2 items-center">
        <button
          className="border px-4 py-2 rounded"
          onClick={ask}
          disabled={loading}
        >
          {loading ? 'Thinking…' : 'Ask'}
        </button>
        <small className="text-gray-600">Offline demo · no external model calls</small>
      </div>

      {error && <div role="alert" className="mt-4 text-red-600">Error: {error}</div>}

      {a && (
        <div className="mt-6 border rounded p-4 whitespace-pre-wrap">
          <h2 className="font-semibold mb-2">{mode === "demo" ? "Demo answer" : "Answer"}</h2>
          <div>{a}</div>

          <div className="mt-4">
            <h3 className="font-semibold">Citations</h3>
            {citations.length === 0 ? (
              <div className="text-sm text-gray-600">No citations returned (stubbed).</div>
            ) : (
              <ul className="list-disc ml-5 mt-2">
                {citations.map((c, i) => (
                  <li key={i} className="mb-2">
                    {c.title ? <div className="font-medium">{c.title}</div> : null}
                    {c.url ? (
                      <div>
                        <a href={c.url} target="_blank" rel="noreferrer" className="text-blue-600 underline">
                          {c.url}
                        </a>
                      </div>
                    ) : null}
                    <div>Page: {c.page ?? "?"}</div>
                    <p>{c.snippet ?? c.excerpt ?? "No passage available."}</p>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </main>
  );
}
