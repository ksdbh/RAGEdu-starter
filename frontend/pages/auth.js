import React, { useEffect, useState } from "react";
import AuthWidget from "../components/AuthWidget";

export default function Home() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    async function loadUser() {
      const token = typeof window !== "undefined" ? localStorage.getItem("ragedu_token") : null;
      if (!token) {
        setUser(null);
        return;
      }
      try {
        const res = await fetch("/whoami", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) {
          setUser(null);
          return;
        }
        const j = await res.json();
        setUser(j);
      } catch (err) {
        console.error("Failed to fetch whoami", err);
        setUser(null);
      }
    }
    loadUser();
  }, []);

  return (
    <div style={{ padding: 24 }}>
      <h1>RAGEdu (scaffold) — Auth demo</h1>
      <AuthWidget onChange={(u) => setUser(u)} />

      <section style={{ marginTop: 24 }}>
        <h2>Role-based content</h2>
        {!user && <p>You are viewing this as an anonymous user. Please log in.</p>}
        {user && user.role === "student" && (
          <div>
            <h3>Student Dashboard</h3>
            <p>Welcome {user.username}. Here are your assignments and quizzes.</p>
          </div>
        )}
        {user && user.role === "professor" && (
          <div>
            <h3>Professor Dashboard</h3>
            <p>Welcome {user.username}. Manage course materials and quizzes here.</p>
          </div>
        )}
      </section>
    </div>
  );
}
