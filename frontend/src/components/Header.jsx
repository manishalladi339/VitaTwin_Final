import React from "react";
import { clearToken } from "../utils/auth";
import { Link } from "react-router-dom";

export default function Header({ onLogout }) {
  const logout = () => {
    clearToken();
    onLogout?.();
    window.location.href = "/";
  };
  return (
    <div className="bg-white shadow p-4 flex justify-between items-center">
      <div className="font-bold"><Link to="/">VitaTwin</Link></div>
      <nav className="space-x-3">
        <Link to="/mood" className="underline">Mood</Link>
        <Link to="/summary" className="underline">Summary</Link>
        <Link to="/profile" className="underline">Profile</Link>
      </nav>
      <button onClick={logout} className="bg-gray-200 px-3 py-1 rounded">Logout</button>
    </div>
  );
}
