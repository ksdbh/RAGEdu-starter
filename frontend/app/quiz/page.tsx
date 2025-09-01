"use client"

import React, { useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function QuizPage() {
  const [query, setQuery] = useState("graph algorithms");
  const [quiz, setQuiz] = useState<any | null>(null);
  const [answers, setAnswers] = useState<{ [k: string]: any }>({});
  const [score, setScore] = useState<number | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function generate() {
    setQuiz(null);
    setScore(null);
    const resp = await fetch(`${API_URL}/quiz/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    if (resp.ok) {
      const data = await resp.json();
      setQuiz(data);
      setAnswers({});
    } else {
      alert("Failed to generate quiz");
    }
  }

  function setAnswer(qid: string, val: any) {
    setAnswers((s) => ({ ...s, [qid]: val }));
  }

  async function submit() {
    if (!quiz) return;
    setSubmitting(true);
    const results = quiz.questions.map((q: any) => {
      const resp = answers[q.id] ?? null;
      const correct = resp !== null && String(resp).trim() === String(q.answer).trim();
      return { question_id: q.id, correct, response: resp };
    });

    // local grading
    const correctCount = results.filter((r: any) => r.correct).length;
    setScore(correctCount);

    // send to backend
    try {
      await fetch(`${API_URL}/quiz/submit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quiz_id: quiz.quiz_id, user_id: null, results }),
      });
    } catch (err) {
      console.error("Failed to record results", err);
    }
    setSubmitting(false);
  }

  return (
    <main className="p-8 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">RAGEdu — Quiz</h1>
      <div className="mb-4">
        <label className="mb-2 block">Quiz topic / seed query</label>
        <div className="flex gap-2 items-center">
          <input value={query} onChange={(e) => setQuery(e.target.value)} className="p-3 border rounded flex-1" />
          <button onClick={generate} className="p-3 bg-blue-600 text-white rounded">Generate</button>
        </div>
      </div>

      {quiz && (
        <div>
          <h2 className="font-semibold mb-2">Quiz (x{quiz.questions.length})</h2>
          <ol className="list-decimal ml-5">
            {quiz.questions.map((q: any, idx: number) => (
              <li key={q.id} className="mb-4">
                <div className="font-semibold mb-1">{q.prompt}</div>
                {q.type === "mcq" ? (
                  <div>
                    {q.choices.map((c: string) => (
                      <label key={c} className="block">
                        <input
                          type="radio"
                          name={q.id}
                          checked={answers[q.id] === c}
                          onChange={() => setAnswer(q.id, c)}
                        />
                        <span className="ml-2">{c}</span>
                      </label>
                    ))}
                  </div>
                ) : (
                  <div>
                    <input
                      type="text"
                      value={answers[q.id] ?? ""}
                      onChange={(e) => setAnswer(q.id, e.target.value)}
                      className="p-3 border rounded w-full"
                    />
                  </div>
                )}
              </li>
            ))}
          </ol>

          <div className="mt-4 flex gap-2">
            <button onClick={submit} disabled={submitting} className="p-3 bg-blue-600 text-white rounded">
              Submit
            </button>
            {score !== null && <div className="p-3">Score: {score} / {quiz.questions.length}</div>}
          </div>
        </div>
      )}
    </main>
  );
}
