import React, { useState } from 'react'

// MVP Quest Map page: static demo data and local-progress UI.
// This is intentionally self-contained so the frontend shows a minimal view
// even when the backend is not running.

type Quest = {
  id: string
  type: string
  title: string
  description: string
  estimated_minutes: number
  week: number
  topic: string
}

const sample = {
  course_id: 'demo-course',
  weeks: [
    {
      week: 1,
      quests: [
        { id: 'r1', type: 'read', title: 'Read: Intro', description: 'Read the intro', estimated_minutes: 20, week: 1, topic: 'Intro' },
        { id: 'q1', type: 'quiz', title: 'Quick Quiz: Intro', description: 'Quiz yourself', estimated_minutes: 10, week: 1, topic: 'Intro' },
        { id: 'a1', type: 'apply', title: 'Apply: Intro', description: 'Do small exercise', estimated_minutes: 30, week: 1, topic: 'Intro' },
      ]
    },
    {
      week: 2,
      quests: [
        { id: 'r2', type: 'read', title: 'Read: Graphs', description: 'Read about graphs', estimated_minutes: 20, week: 2, topic: 'Graphs' },
        { id: 'q2', type: 'quiz', title: 'Quick Quiz: Graphs', description: 'Short quiz', estimated_minutes: 10, week: 2, topic: 'Graphs' },
        { id: 'a2', type: 'apply', title: 'Apply: Graphs', description: 'Implement DFS', estimated_minutes: 45, week: 2, topic: 'Graphs' },
      ]
    }
  ]
}

export default function QuestMapPage() {
  const [data] = useState(sample)
  // progress state: map questId -> completed boolean
  const [completed, setCompleted] = useState<Record<string, boolean>>({})

  const toggle = (id: string) => {
    setCompleted((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  const progressForWeek = (quests: Quest[]) => {
    if (!quests || quests.length === 0) return 0
    const done = quests.filter((q) => completed[q.id]).length
    return Math.round((done / quests.length) * 100)
  }

  return (
    <div style={{ padding: 24, fontFamily: 'Arial, sans-serif' }}>
      <h1>Quest Map — {data.course_id}</h1>
      {data.weeks.map((w) => (
        <section key={w.week} style={{ marginBottom: 20, border: '1px solid #eee', padding: 12 }}>
          <h2>Week {w.week} — Progress: {progressForWeek(w.quests)}%</h2>
          <div style={{ display: 'flex', gap: 12 }}>
            {w.quests.map((q: Quest) => (
              <div key={q.id} style={{ flex: '1 1 0', padding: 8, border: '1px solid #ddd', borderRadius: 6 }}>
                <h3 style={{ marginTop: 0 }}>{q.title}</h3>
                <p style={{ margin: '6px 0', color: '#444' }}>{q.description}</p>
                <p style={{ margin: '6px 0', fontSize: 12, color: '#666' }}>Est: {q.estimated_minutes} min</p>
                <button onClick={() => toggle(q.id)} style={{ padding: '6px 10px' }}>
                  {completed[q.id] ? 'Mark Incomplete' : 'Mark Complete'}
                </button>
              </div>
            ))}
          </div>
        </section>
      ))}
      <footer style={{ marginTop: 24, color: '#888' }}>This is an MVP view — progress is local only in this demo.</footer>
    </div>
  )
}
