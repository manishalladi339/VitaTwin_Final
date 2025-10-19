import React, { useState } from "react";
import { api } from "../utils/api";

export default function SummaryPage() {
  const [text, setText] = useState("");
  const [summary, setSummary] = useState("");
  const [error, setError] = useState("");

  const summarize = async () => {
    setError(""); setSummary("");
    try {
      const res = await api.post("/api/summary", { text });
      setSummary(res.data.summary);
    } catch (e) {
      setError(e?.response?.data?.detail || "Error generating summary");
    }
  };

  return (
    <div className="max-w-2xl mx-auto bg-white p-6 rounded shadow">
      <h2 className="text-xl font-bold mb-4">Text Summarizer</h2>
      <textarea className="border p-2 w-full mb-3" rows="6" value={text} onChange={(e)=>setText(e.target.value)} placeholder="Paste your notes here..."></textarea>
      <button onClick={summarize} className="bg-blue-600 text-white px-4 py-2 rounded">Summarize</button>
      {error && <div className="mt-3 text-red-600">{error}</div>}
      {summary && <pre className="mt-4 whitespace-pre-wrap">{summary}</pre>}
    </div>
  );
}
