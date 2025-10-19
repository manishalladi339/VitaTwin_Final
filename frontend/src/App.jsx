import React, { useState, useEffect } from "react";
import Onboarding from "./components/Onboarding";
import Dashboard from "./components/Dashboard";
import Auth from "./components/Auth";
import Header from "./components/Header";
import { getToken } from "./utils/auth";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import MoodPage from './pages/MoodPage';
import SummaryPage from './pages/SummaryPage';
import ProfilePage from './pages/ProfilePage';
import NotFound from './pages/NotFound';

function App() {
  const [authed, setAuthed] = useState(false);
  const [userData, setUserData] = useState(null);

  useEffect(() => { setAuthed(!!getToken()); }, []);

  if (!authed) return <Auth onAuthed={() => setAuthed(true)} />;

  return (
    <BrowserRouter>
      <Header onLogout={() => setAuthed(false)} />
      <Routes>
        <Route path="/" element={
          <div className="min-h-screen bg-gray-100 p-4">
            {!userData ? (<Onboarding onSubmit={setUserData} />) : (<Dashboard userData={userData} />)}
          </div>
        } />
        <Route path="/mood" element={<MoodPage />} />
        <Route path="/summary" element={<SummaryPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}
export default App;
