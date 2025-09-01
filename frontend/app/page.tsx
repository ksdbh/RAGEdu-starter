'use client';
import { useState } from 'react';

export default function Home() {
  const [q, setQ] = useState('Explain Dijkstra vs A* with an example.');
  const [a, setA] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function ask() {
    setLoading(true);
    setA(null);
    const resp = await fetch(process.env.NEXT_PUBLIC_API_URL + '/rag/answer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: q, top_k: 5 })
    });
    const data = await resp.json();
    setA(data.answer);
    setLoading(false);
  }

  return (
    <main className="p-8 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">RAGEdu</h1>
      <p className="mb-4">Course-grounded Q&A with citations (stubbed).</p>
      <textarea className="w-full border p-3 rounded mb-2" rows={4} value={q} onChange={e=>setQ(e.target.value)} />
      <button className="border px-4 py-2 rounded" onClick={ask} disabled={loading}>
        {loading ? 'Thinking…' : 'Ask'}
      </button>
      {a && <div className="mt-6 border rounded p-4 whitespace-pre-wrap">{a}</div>}
    </main>
  );
}
