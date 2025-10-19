import React from "react";
export default function Dashboard({ userData }) {
  return (
    <div className="max-w-2xl mx-auto bg-white p-6 mt-10 rounded shadow">
      <h2 className="text-2xl font-bold mb-4">VitaTwin AI Health Report</h2>
      <pre className="whitespace-pre-wrap">{JSON.stringify(userData, null, 2)}</pre>
    </div>
  );
}
