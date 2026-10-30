'use client';

import { useEffect, useState } from 'react';
import { API_BASE } from '../lib/api';

type Citation = {
  title: string;
  page?: number;
  snippet: string;
  source?: string;
};
type Configuration = {
  mode: 'demo' | 'local';
  courses: { course_id: string; documents: number; passages: number }[];
};
type RagResponse = {
  answer: string;
  citations: Citation[];
  metadata: { mode: string; status: string };
};

export default function Study() {
  const [configuration, setConfiguration] = useState<Configuration | null>(null);
  const [course, setCourse] = useState('');
  const [question, setQuestion] = useState('What does Dijkstra require?');
  const [result, setResult] = useState<RagResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    async function configure() {
      try {
        const response = await fetch(API_BASE + '/rag/status', { signal: controller.signal });
        if (!response.ok) throw new Error('Course configuration is unavailable. Please retry later.');
        const data = await response.json() as Configuration;
        if (!['demo', 'local'].includes(data.mode) || !Array.isArray(data.courses)) {
          throw new Error('Course configuration is invalid. Please retry later.');
        }
        if (!controller.signal.aborted) {
          setConfiguration(data);
          setCourse(data.courses[0]?.course_id ?? '');
        }
      } catch (err) {
        if (!controller.signal.aborted) setError(err instanceof Error ? err.message : 'Could not load courses.');
      }
    }
    void configure();
    return () => controller.abort();
  }, []);

  async function ask() {
    setResult(null);
    setError(null);
    if (!question.trim()) {
      setError('Please enter a question.');
      return;
    }
    setLoading(true);
    try {
      const response = await fetch(API_BASE + '/rag/answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: question, top_k: 5, ...(configuration?.mode === 'local' ? { course_id: course } : {}) }),
      });
      if (!response.ok) throw new Error('Could not search course materials. Please try again.');
      const data = await response.json() as RagResponse;
      setResult({ ...data, citations: Array.isArray(data.citations) ? data.citations : [] });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed.');
    } finally {
      setLoading(false);
    }
  }

  const isLocal = configuration?.mode === 'local';
  const noCourses = isLocal && configuration.courses.length === 0;
  return (
    <main className="p-8 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">RAGEdu</h1>
      <p className="mb-4">
        {!configuration ? 'Loading course configuration…' : isLocal
          ? 'Search your course materials by keyword. Results quote matching passages; no model explanation is generated.'
          : 'Local Q&A demo. Answers and sample sources are simulated; no course documents are used.'}
      </p>
      <nav className="mb-4" aria-label="Study pages">
        <a href="/auth">Mock sign-in</a> · <a href="/quiz">Quiz demo</a> · <a href="/quest-map">Quest map demo</a>
      </nav>
      {isLocal && (
        <div className="mb-4">
          <label htmlFor="course">Course</label>
          <select id="course" value={course} disabled={loading || noCourses} onChange={event => {
            setCourse(event.target.value);
            setResult(null);
            setError(null);
          }}>
            {configuration.courses.map(item => (
              <option key={item.course_id} value={item.course_id}>{item.course_id} ({item.documents} documents)</option>
            ))}
          </select>
          {noCourses && <p>No course materials yet. Add a PDF locally, then reload this page.</p>}
        </div>
      )}
      <label htmlFor="question">Your question</label>
      <textarea id="question" className="w-full border p-3 rounded mb-2" rows={4}
        value={question} maxLength={1000} onChange={event => setQuestion(event.target.value)} />
      <div className="flex gap-2 items-center">
        <button className="border px-4 py-2 rounded" onClick={ask}
          disabled={loading || !configuration || noCourses}>
          {loading ? 'Searching…' : 'Ask'}
        </button>
        <small className="text-gray-600">No external model calls</small>
      </div>
      {error && <div role="alert" className="mt-4 text-red-600">{error}</div>}
      {result && (
        <section aria-live="polite" className="mt-6 border rounded p-4 whitespace-pre-wrap">
          <h2 className="font-semibold mb-2">{result.metadata.status === 'insufficient_evidence'
            ? 'More evidence needed' : result.metadata.mode === 'local' ? 'Course excerpts' : 'Demo answer'}</h2>
          <p>{result.answer}</p>
          <h3 className="font-semibold">Citations</h3>
          {result.citations.length === 0 ? <p>No matching source passages.</p> : (
            <ul className="list-disc ml-5 mt-2">
              {result.citations.map((citation, i) => (
                <li key={i} className="mb-2">
                  <div className="font-semibold">{citation.title}</div>
                  {citation.source && <div>Source: {citation.source}</div>}
                  <div>Page: {citation.page ?? '?'}</div>
                  <blockquote>{citation.snippet}</blockquote>
                </li>
              ))}
            </ul>
          )}
        </section>
      )}
    </main>
  );
}
