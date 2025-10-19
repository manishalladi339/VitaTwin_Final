import React, { useState } from "react";
import { analyzeHealth } from "../utils/api";

export default function Onboarding({ onSubmit }) {
  const [form, setForm] = useState({
    name: "", age: "", weight: "", height: "", smoker: false, drinker: false,
    mood: "", stress_level: "", sleep_hours: "", activity_level: "", diet_quality: "",
  });

  const handleChange = (e) => {
    const { name, type, checked, value } = e.target;
    setForm({ ...form, [name]: type === "checkbox" ? checked : value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await analyzeHealth(form);
    onSubmit(res);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded shadow max-w-md mx-auto">
      <h2 className="text-2xl font-bold mb-4">🧠 VitaTwin Onboarding</h2>
      <input className="border p-2 w-full mb-2" name="name" placeholder="Name" onChange={handleChange} />
      <input className="border p-2 w-full mb-2" name="age" type="number" placeholder="Age" onChange={handleChange} />
      <input className="border p-2 w-full mb-2" name="weight" type="number" placeholder="Weight (kg)" onChange={handleChange} />
      <input className="border p-2 w-full mb-2" name="height" type="number" placeholder="Height (cm)" onChange={handleChange} />
      <label className="block mb-2"><input type="checkbox" name="smoker" onChange={handleChange} /> Smoker</label>
      <label className="block mb-4"><input type="checkbox" name="drinker" onChange={handleChange} /> Drinker</label>
      <textarea className="border p-2 w-full mb-2" name="mood" placeholder="Mood today" onChange={handleChange}></textarea>
      <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded">Submit</button>
    </form>
  );
}
