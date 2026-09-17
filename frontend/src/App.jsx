import { useCallback, useEffect, useMemo, useState } from 'react';
import { Activity, BarChart3, Bot, CalendarCheck, ChevronRight, FlaskConical, HeartPulse, LogOut, Menu, ShieldCheck, Sparkles, UserRound, X } from 'lucide-react';

import { api, messageOf } from './utils/api';
import { clearToken, getToken, saveToken } from './utils/auth';

const NAV = [
  ['dashboard', 'Overview', BarChart3],
  ['checkin', 'Daily check-in', CalendarCheck],
  ['simulator', 'What-if lab', FlaskConical],
  ['coach', 'AI coach', Bot],
  ['profile', 'Health profile', UserRound],
];

export default function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(getToken()));
  const [page, setPage] = useState('dashboard');
  const [mobileNav, setMobileNav] = useState(false);

  useEffect(() => {
    if (!getToken()) return;
    api.get('/api/v1/auth/me').then(({ data }) => setUser(data)).catch(() => clearToken()).finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingScreen />;
  if (!user) return <Auth onAuthenticated={setUser} />;
  if (!user.profile_complete) return <ProfileSetup user={user} onComplete={() => setUser({ ...user, profile_complete: true })} />;

  return (
    <div className="app-shell">
      <aside className={mobileNav ? 'sidebar sidebar-open' : 'sidebar'}>
        <div className="brand"><div className="brand-mark"><HeartPulse size={22} /></div><div><strong>VitaTwin</strong><span>Know your pattern</span></div></div>
        <nav>{NAV.map(([id, label, Icon]) => <button className={page === id ? 'nav-item active' : 'nav-item'} key={id} onClick={() => { setPage(id); setMobileNav(false); }}><Icon size={18} />{label}</button>)}</nav>
        <div className="sidebar-note"><ShieldCheck size={18} /><p>Your score explains its inputs. VitaTwin does not diagnose conditions.</p></div>
        <button className="nav-item signout" onClick={() => { clearToken(); setUser(null); }}><LogOut size={18} />Sign out</button>
      </aside>
      <main>
        <header className="topbar">
          <button className="icon-button menu-button" onClick={() => setMobileNav(!mobileNav)}>{mobileNav ? <X /> : <Menu />}</button>
          <div><p className="eyebrow">PERSONAL WELLNESS TWIN</p><h1>{NAV.find(([id]) => id === page)?.[1]}</h1></div>
          <div className="user-chip"><span>{user.name.charAt(0).toUpperCase()}</span><div><strong>{user.name}</strong><small>Private workspace</small></div></div>
        </header>
        <section className="content">
          {page === 'dashboard' && <Dashboard onNavigate={setPage} />}
          {page === 'checkin' && <CheckIn onSaved={() => setPage('dashboard')} />}
          {page === 'simulator' && <Simulator />}
          {page === 'coach' && <Coach />}
          {page === 'profile' && <ProfileEditor />}
        </section>
      </main>
    </div>
  );
}

function Auth({ onAuthenticated }) {
  const [mode, setMode] = useState('login');
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  async function submit(event) {
    event.preventDefault(); setError(''); setBusy(true);
    try {
      const { data } = await api.post(`/api/v1/auth/${mode}`, form);
      saveToken(data.access_token); onAuthenticated(data.user);
    } catch (err) { setError(messageOf(err)); } finally { setBusy(false); }
  }
  return <div className="auth-layout">
    <section className="auth-story"><div className="brand light"><div className="brand-mark"><HeartPulse size={22} /></div><strong>VitaTwin</strong></div><div><p className="eyebrow">YOUR HEALTH, MADE LEGIBLE</p><h1>A digital twin built from the days you actually live.</h1><p>Track daily signals, understand your trends, and explore small changes through an explainable wellness model.</p></div><div className="privacy-line"><ShieldCheck />Private by design · Transparent scoring · No diagnostic claims</div></section>
    <section className="auth-panel"><form className="form-card auth-card" onSubmit={submit}><p className="eyebrow">{mode === 'login' ? 'WELCOME BACK' : 'CREATE YOUR TWIN'}</p><h2>{mode === 'login' ? 'Sign in to continue' : 'Start building your baseline'}</h2>{mode === 'register' && <Field label="Name" value={form.name} onChange={(value) => setForm({ ...form, name: value })} required />}<Field label="Email" type="email" value={form.email} onChange={(value) => setForm({ ...form, email: value })} required /><Field label="Password" type="password" value={form.password} onChange={(value) => setForm({ ...form, password: value })} hint={mode === 'register' ? 'At least 8 characters' : ''} required />{error && <ErrorBox>{error}</ErrorBox>}<button className="primary-button" disabled={busy}>{busy ? 'Please wait…' : mode === 'login' ? 'Sign in' : 'Create account'}<ChevronRight size={18} /></button><button type="button" className="text-button" onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError(''); }}>{mode === 'login' ? 'New to VitaTwin? Create an account' : 'Already have an account? Sign in'}</button></form></section>
  </div>;
}

function ProfileSetup({ user, onComplete }) {
  return <div className="setup-layout"><div className="setup-copy"><div className="brand"><div className="brand-mark"><HeartPulse size={22} /></div><strong>VitaTwin</strong></div><p className="eyebrow">WELCOME, {user.name.toUpperCase()}</p><h1>Give your twin a starting point.</h1><p>These details establish a baseline. You can update them whenever your circumstances change.</p><div className="sidebar-note"><ShieldCheck /><p>VitaTwin provides general wellness information. It is not a medical device and does not replace professional care.</p></div></div><ProfileForm submitLabel="Build my twin" onSaved={onComplete} /></div>;
}

function Dashboard({ onNavigate }) {
  const [data, setData] = useState(null); const [error, setError] = useState('');
  const load = useCallback(() => api.get('/api/v1/twin/dashboard').then(({ data }) => setData(data)).catch((err) => setError(messageOf(err))), []);
  useEffect(() => { load(); }, [load]);
  if (error) return <ErrorBox>{error}</ErrorBox>;
  if (!data) return <PanelLoader />;
  return <div className="dashboard-grid">
    <article className="score-card card"><div><p className="eyebrow">TODAY'S VITALITY</p><h2>Your twin is <span>{data.status}</span></h2><p className="muted">Based on {data.checkin_count} check-in{data.checkin_count === 1 ? '' : 's'} · {data.streak} day streak</p></div><ScoreRing score={data.score} /></article>
    <article className="card action-card"><div className="icon-tile"><Activity /></div><div><p className="eyebrow">KEEP THE MODEL CURRENT</p><h3>How are you feeling today?</h3><p className="muted">A check-in takes about 30 seconds.</p></div><button className="primary-button compact" onClick={() => onNavigate('checkin')}>Check in <ChevronRight size={17} /></button></article>
    <article className="card dimensions"><div className="section-heading"><div><p className="eyebrow">SIGNAL BREAKDOWN</p><h3>What shapes your score</h3></div><span className="confidence">Explainable</span></div>{Object.entries(data.dimensions).map(([name, value]) => <Metric key={name} name={name} value={value} />)}</article>
    <article className="card"><div className="section-heading"><div><p className="eyebrow">RECENT PATTERN</p><h3>Fourteen-day signals</h3></div><span className="stat">BMI {data.bmi}</span></div><Trend data={data.trend} /></article>
    <article className="card"><p className="eyebrow">NEXT BEST STEPS</p><h3>Focus on what can move</h3><div className="recommendation-list">{data.recommendations.map((item, index) => <div key={item}><span>{index + 1}</span><p>{item}</p></div>)}</div></article>
    <article className="card"><p className="eyebrow">ATTENTION FLAGS</p><h3>{data.flags.length ? `${data.flags.length} signal${data.flags.length > 1 ? 's' : ''} to watch` : 'No major flags today'}</h3>{data.flags.length ? <div className="flag-list">{data.flags.map((flag) => <div key={flag.title} className={`flag ${flag.level}`}><strong>{flag.title}</strong><p>{flag.detail}</p></div>)}</div> : <p className="muted roomy">Keep checking in. Trends become more useful as your baseline grows.</p>}</article>
  </div>;
}

function CheckIn({ onSaved }) {
  const [form, setForm] = useState({ recorded_on: new Date().toISOString().slice(0, 10), mood: 3, stress: 5, sleep_hours: 7.5, active_minutes: 30, steps: 5000, water_liters: 2, resting_heart_rate: '', note: '' });
  const [error, setError] = useState(''); const [busy, setBusy] = useState(false);
  async function save(event) { event.preventDefault(); setBusy(true); setError(''); try { await api.post('/api/v1/checkins', { ...form, resting_heart_rate: form.resting_heart_rate || null }); onSaved(); } catch (err) { setError(messageOf(err)); } finally { setBusy(false); } }
  return <form className="form-card wide" onSubmit={save}><div className="section-heading"><div><p className="eyebrow">DAILY SIGNALS</p><h2>Record today without judging it.</h2></div><span className="confidence">~30 sec</span></div><div className="form-grid"><Field label="Date" type="date" value={form.recorded_on} onChange={(value) => setForm({ ...form, recorded_on: value })} /><RangeField label="Mood" value={form.mood} min="1" max="5" low="Low" high="Great" onChange={(value) => setForm({ ...form, mood: Number(value) })} /><RangeField label="Stress" value={form.stress} min="1" max="10" low="Calm" high="High" onChange={(value) => setForm({ ...form, stress: Number(value) })} /><Field label="Sleep (hours)" type="number" step="0.1" value={form.sleep_hours} onChange={(value) => setForm({ ...form, sleep_hours: Number(value) })} /><Field label="Active minutes" type="number" value={form.active_minutes} onChange={(value) => setForm({ ...form, active_minutes: Number(value) })} /><Field label="Steps" type="number" value={form.steps} onChange={(value) => setForm({ ...form, steps: Number(value) })} /><Field label="Water (litres)" type="number" step="0.1" value={form.water_liters} onChange={(value) => setForm({ ...form, water_liters: Number(value) })} /><Field label="Resting heart rate (optional)" type="number" value={form.resting_heart_rate} onChange={(value) => setForm({ ...form, resting_heart_rate: value })} /></div><Field label="A note about today (optional)" textarea value={form.note} onChange={(value) => setForm({ ...form, note: value })} />{error && <ErrorBox>{error}</ErrorBox>}<button className="primary-button" disabled={busy}>{busy ? 'Saving…' : 'Save today’s check-in'}<ChevronRight size={18} /></button></form>;
}

function Simulator() {
  const [form, setForm] = useState({ sleep_hours: 8, active_minutes: 45, stress: 4, smoker: false }); const [result, setResult] = useState(null); const [error, setError] = useState('');
  async function run(event) { event.preventDefault(); setError(''); try { const { data } = await api.post('/api/v1/twin/simulate', form); setResult(data); } catch (err) { setError(messageOf(err)); } }
  return <div className="two-column"><form className="form-card" onSubmit={run}><p className="eyebrow">SAFE SCENARIO MODELLING</p><h2>What if I changed…</h2><p className="muted">Explore how transparent wellness rules respond. This is not a forecast of disease or lifespan.</p><Field label="Sleep each night" type="number" step="0.5" value={form.sleep_hours} onChange={(value) => setForm({ ...form, sleep_hours: Number(value) })} /><Field label="Active minutes per day" type="number" value={form.active_minutes} onChange={(value) => setForm({ ...form, active_minutes: Number(value) })} /><RangeField label="Stress level" value={form.stress} min="1" max="10" low="Calm" high="High" onChange={(value) => setForm({ ...form, stress: Number(value) })} /><label className="toggle-row"><input type="checkbox" checked={!form.smoker} onChange={(event) => setForm({ ...form, smoker: !event.target.checked })} /><span><strong>Model a smoke-free scenario</strong><small>Compare lifestyle signal impact</small></span></label>{error && <ErrorBox>{error}</ErrorBox>}<button className="primary-button">Run scenario <Sparkles size={18} /></button></form><article className="card simulation-result">{result ? <><p className="eyebrow">ESTIMATED SIGNAL CHANGE</p><div className="score-comparison"><ScoreRing score={result.before.score} small /><ChevronRight /><ScoreRing score={result.after.score} small /></div><div className={result.delta >= 0 ? 'delta positive' : 'delta'}>{result.delta >= 0 ? '+' : ''}{result.delta} points</div><p className="muted">{result.explanation}</p></> : <div className="empty-state"><FlaskConical size={44} /><h3>Run a scenario</h3><p>Adjust the inputs to see which dimensions respond and why.</p></div>}</article></div>;
}

function Coach() {
  const [question, setQuestion] = useState(''); const [messages, setMessages] = useState([]); const [busy, setBusy] = useState(false); const [error, setError] = useState('');
  async function ask(event) { event.preventDefault(); if (!question.trim()) return; const prompt = question.trim(); setMessages([...messages, { role: 'you', text: prompt }]); setQuestion(''); setBusy(true); setError(''); try { const { data } = await api.post('/api/v1/twin/coach', { question: prompt }); setMessages((current) => [...current, { role: 'coach', text: data.answer, note: data.disclaimer }]); } catch (err) { setError(messageOf(err)); } finally { setBusy(false); } }
  return <div className="coach-layout"><article className="card coach-intro"><div className="icon-tile"><Bot /></div><p className="eyebrow">CONTEXT-AWARE WELLNESS</p><h2>Ask about your patterns.</h2><p className="muted">VitaTwin uses your recorded signals to explain possible next steps. It will not diagnose symptoms or replace medical care.</p><div className="prompt-list">{['What should I focus on this week?', 'Why is my recovery score low?', 'How can I build a better sleep routine?'].map((prompt) => <button key={prompt} onClick={() => setQuestion(prompt)}>{prompt}<ChevronRight size={16} /></button>)}</div></article><article className="card chat-card"><div className="messages">{messages.length === 0 && <div className="empty-state"><Sparkles /><p>Your conversation will appear here.</p></div>}{messages.map((message, index) => <div key={index} className={`message ${message.role}`}><strong>{message.role === 'you' ? 'You' : 'VitaTwin'}</strong><p>{message.text}</p>{message.note && <small>{message.note}</small>}</div>)}{busy && <div className="message coach"><p>Reviewing your recent signals…</p></div>}</div>{error && <ErrorBox>{error}</ErrorBox>}<form className="chat-input" onSubmit={ask}><input value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask about your wellness pattern…" /><button disabled={busy || !question.trim()}><ChevronRight /></button></form></article></div>;
}

function ProfileEditor() { const [saved, setSaved] = useState(false); return <ProfileForm submitLabel="Save profile" onSaved={() => setSaved(true)} loadExisting success={saved ? 'Profile updated.' : ''} />; }

function ProfileForm({ submitLabel, onSaved, loadExisting = false, success = '' }) {
  const initial = { age: 25, height_cm: 175, weight_kg: 75, smoker: false, alcohol_per_week: 0, activity_goal_minutes: 150, sleep_goal_hours: 8, conditions: [] };
  const [form, setForm] = useState(initial); const [conditions, setConditions] = useState(''); const [error, setError] = useState(''); const [busy, setBusy] = useState(false);
  useEffect(() => { if (loadExisting) api.get('/api/v1/profile').then(({ data }) => { setForm(data); setConditions(data.conditions.join(', ')); }).catch((err) => setError(messageOf(err))); }, [loadExisting]);
  async function save(event) { event.preventDefault(); setBusy(true); setError(''); try { await api.put('/api/v1/profile', { ...form, conditions: conditions.split(',').map((item) => item.trim()).filter(Boolean) }); onSaved(); } catch (err) { setError(messageOf(err)); } finally { setBusy(false); } }
  return <form className="form-card profile-form" onSubmit={save}><p className="eyebrow">BASELINE PROFILE</p><h2>Your starting context</h2><p className="muted">Only enter information you are comfortable storing in your local or deployed database.</p><div className="form-grid"><Field label="Age" type="number" value={form.age} onChange={(value) => setForm({ ...form, age: Number(value) })} /><Field label="Height (cm)" type="number" step="0.1" value={form.height_cm} onChange={(value) => setForm({ ...form, height_cm: Number(value) })} /><Field label="Weight (kg)" type="number" step="0.1" value={form.weight_kg} onChange={(value) => setForm({ ...form, weight_kg: Number(value) })} /><Field label="Alcoholic drinks per week" type="number" value={form.alcohol_per_week} onChange={(value) => setForm({ ...form, alcohol_per_week: Number(value) })} /><Field label="Weekly activity goal (minutes)" type="number" value={form.activity_goal_minutes} onChange={(value) => setForm({ ...form, activity_goal_minutes: Number(value) })} /><Field label="Nightly sleep goal" type="number" step="0.5" value={form.sleep_goal_hours} onChange={(value) => setForm({ ...form, sleep_goal_hours: Number(value) })} /></div><label className="toggle-row"><input type="checkbox" checked={form.smoker} onChange={(event) => setForm({ ...form, smoker: event.target.checked })} /><span><strong>I currently smoke</strong><small>Used only as a transparent lifestyle factor</small></span></label><Field label="Known conditions (optional, comma-separated)" value={conditions} onChange={setConditions} />{error && <ErrorBox>{error}</ErrorBox>}{success && <div className="success-box">{success}</div>}<button className="primary-button" disabled={busy}>{busy ? 'Saving…' : submitLabel}<ChevronRight size={18} /></button></form>;
}

function ScoreRing({ score, small = false }) { return <div className={small ? 'score-ring small' : 'score-ring'} style={{ '--score': `${score * 3.6}deg` }}><div><strong>{score}</strong><span>/100</span></div></div>; }
function Metric({ name, value }) { return <div className="metric"><div><span>{name}</span><strong>{value}</strong></div><div className="metric-track"><span style={{ width: `${value}%` }} /></div></div>; }
function Trend({ data }) { const points = useMemo(() => data.map((item, index) => `${data.length === 1 ? 50 : (index / (data.length - 1)) * 100},${100 - item.mood * 18}`).join(' '), [data]); if (!data.length) return <div className="empty-state short"><Activity /><p>Add a daily check-in to start your trend.</p></div>; return <div className="trend"><svg viewBox="0 0 100 100" preserveAspectRatio="none"><defs><linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#6ee7b7" stopOpacity=".35"/><stop offset="1" stopColor="#6ee7b7" stopOpacity="0"/></linearGradient></defs><polygon points={`0,100 ${points} 100,100`} fill="url(#trendFill)"/><polyline points={points} fill="none" stroke="#34d399" strokeWidth="3" vectorEffect="non-scaling-stroke"/></svg><div className="trend-legend"><span>{data[0].date}</span><span>Mood trend</span><span>{data[data.length - 1].date}</span></div></div>; }
function Field({ label, hint, textarea, onChange, ...props }) { const Tag = textarea ? 'textarea' : 'input'; return <label className="field"><span>{label}</span><Tag {...props} onChange={(event) => onChange(event.target.value)} />{hint && <small>{hint}</small>}</label>; }
function RangeField({ label, low, high, onChange, ...props }) { return <label className="field range-field"><span>{label}<strong>{props.value}</strong></span><input type="range" {...props} onChange={(event) => onChange(event.target.value)} /><small><i>{low}</i><i>{high}</i></small></label>; }
function ErrorBox({ children }) { return <div className="error-box">{children}</div>; }
function PanelLoader() { return <div className="panel-loader"><div /><p>Building your twin…</p></div>; }
function LoadingScreen() { return <div className="loading-screen"><div className="brand-mark"><HeartPulse /></div><p>Loading VitaTwin…</p></div>; }
