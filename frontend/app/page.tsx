'use client';
import { useState } from 'react';

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
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function ask() {
    setLoading(true);
    setA(null);
    setCitations([]);
    setError(null);
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? '';
      const resp = await fetch(apiUrl + '/rag/answer', {
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
      <p className="mb-4">Course-grounded Q&A with citations (stubbed).</p>

      <textarea
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
        <small className="text-gray-600">API: {process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'}</small>
      </div>

      {error && <div className="mt-4 text-red-600">Error: {error}</div>}

      {a && (
        <div className="mt-6 border rounded p-4 whitespace-pre-wrap">
          <h2 className="font-semibold mb-2">Answer</h2>
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
                    {c.excerpt ? <div className="text-sm text-gray-700 mt-1">{c.excerpt}</div> : null}
                    {/* Render any other metadata in a small monospace block for inspection */}
                    {Object.keys(c).length > 0 ? (
                      <pre className="text-xs bg-gray-50 p-2 rounded mt-2 overflow-auto">{JSON.stringify(c, null, 2)}</pre>
                    ) : null}
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
