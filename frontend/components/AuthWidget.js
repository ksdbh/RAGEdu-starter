import React, { useState } from "react";

export default function AuthWidget({ onChange }) {
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);

  function setTokenAndNotify(token) {
    if (typeof window !== "undefined") {
      localStorage.setItem("ragedu_token", token);
    }
    fetchWhoami(token);
  }

  async function fetchWhoami(token) {
    setLoading(true);
    try {
      const res = await fetch("/whoami", { headers: { Authorization: `Bearer ${token}` } });
      if (!res.ok) {
        setUser(null);
        onChange && onChange(null);
        setLoading(false);
        return;
      }
      const j = await res.json();
      setUser(j);
      onChange && onChange(j);
    } catch (err) {
      console.error("whoami failed", err);
      setUser(null);
      onChange && onChange(null);
    }
    setLoading(false);
  }

  function loginAsStudent() {
    // In a real app you'd open a Cognito hosted UI / redirect and obtain tokens.
    // For the scaffold we accept a local mock token value.
    setTokenAndNotify("student_token");
  }

  function loginAsProfessor() {
    setTokenAndNotify("prof_token");
  }

  function logout() {
    if (typeof window !== "undefined") {
      localStorage.removeItem("ragedu_token");
    }
    setUser(null);
    onChange && onChange(null);
  }

  return (
    <div style={{ border: "1px solid #ddd", padding: 12, display: "inline-block" }}>
      <div>
        <strong>Auth widget (local mock)</strong>
      </div>
      <div style={{ marginTop: 8 }}>
        <button onClick={loginAsStudent} disabled={loading} style={{ marginRight: 8 }}>
          Login as Student
        </button>
        <button onClick={loginAsProfessor} disabled={loading} style={{ marginRight: 8 }}>
          Login as Professor
        </button>
        <button onClick={logout} disabled={loading}>
          Logout
        </button>
      </div>
      <div style={{ marginTop: 8 }}>
        {loading && <em>Loading user...</em>}
        {!loading && user && (
          <div>
            <div><strong>{user.username}</strong> ({user.role})</div>
            <div style={{ fontSize: 12 }}>{user.email}</div>
          </div>
        )}
        {!loading && !user && <div style={{ fontSize: 12 }}>Not signed in</div>}
      </div>
    </div>
  );
}
