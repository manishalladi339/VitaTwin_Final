import React, { useEffect, useState } from "react";
import { api } from "../utils/api";

export default function ProfilePage() {
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const res = await api.get("/api/auth/me");
        setProfile(res.data);
      } catch (e) {
        setError(e?.response?.data?.detail || "Error fetching profile");
      }
    })();
  }, []);

  return (
    <div className="max-w-2xl mx-auto bg-white p-6 rounded shadow">
      <h2 className="text-xl font-bold mb-4">Profile</h2>
      {error && <div className="text-red-600">{error}</div>}
      {profile && (
        <div>
          <div><b>User ID:</b> {profile.user_id}</div>
          <div><b>Status:</b> {profile.message || "Authenticated"}</div>
        </div>
      )}
    </div>
  );
}
