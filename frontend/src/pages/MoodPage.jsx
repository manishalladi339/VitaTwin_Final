import React, { useState } from "react";
import { api } from "../utils/api";

export default function MoodPage() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const analyze = async () => {
    setError(""); setResult(null);
    try {
      const res = await api.post("/api/mood/analyze", { text });
      setResult(res.data);
    } catch (e) {
      setError(e?.response?.data?.detail || "Error analyzing mood");
    }
  };

  return (
    <div className="max-w-2xl mx-auto bg-white p-6 rounded shadow">
      <h2 className="text-xl font-bold mb-4">Mood Check</h2>
      <textarea className="border p-2 w-full mb-3" rows="4" value={text} onChange={(e)=>setText(e.target.value)} placeholder="How are you feeling today?"></textarea>
      <button onClick={analyze} className="bg-blue-600 text-white px-4 py-2 rounded">Analyze</button>
      {error && <div className="mt-3 text-red-600">{error}</div>}
      {result && (
        <div className="mt-4">
          <div><b>Mood:</b> {result.mood}</div>
          <div><b>Confidence:</b> {result.confidence}</div>
          <div><b>Reasoning:</b> {result.reasoning}</div>
        </div>
      )}
    </div>
  );
}
