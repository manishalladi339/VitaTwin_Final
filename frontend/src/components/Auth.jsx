import React, { useState } from "react";
import { api } from "../utils/api";
import { saveToken } from "../utils/auth";

export default function Auth({ onAuthed }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ email: "", password: "", name: "" });
  const [error, setError] = useState("");

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      if (mode === "register") await api.post("/api/auth/register", form);
      const res = await api.post("/api/auth/login", { email: form.email, password: form.password });
      saveToken(res.data.access_token);
      onAuthed();
    } catch (err) {
      setError(err?.response?.data?.detail || "Something went wrong");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="bg-white shadow rounded p-6 w-full max-w-md">
        <h1 className="text-2xl font-bold mb-4">VitaTwin — {mode === "login" ? "Login" : "Register"}</h1>
        {error && <div className="bg-red-100 text-red-700 p-2 mb-3 rounded">{error}</div>}
        {mode === "register" && <input className="border p-2 w-full mb-2" name="name" placeholder="Name" onChange={handleChange} />}
        <input className="border p-2 w-full mb-2" name="email" placeholder="Email" onChange={handleChange} />
        <input className="border p-2 w-full mb-4" name="password" type="password" placeholder="Password" onChange={handleChange} />
        <button onClick={submit} className="bg-blue-600 text-white px-4 py-2 rounded w-full">
          {mode === "login" ? "Login" : "Create account"}
        </button>
        <button className="mt-3 text-sm text-gray-600 underline" onClick={() => setMode(mode === "login" ? "register" : "login")}>
          {mode === "login" ? "No account? Register" : "Have an account? Login"}
        </button>
      </div>
    </div>
  );
}
