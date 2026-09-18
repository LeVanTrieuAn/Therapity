import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import useAuthStore from '../store/authStore';
import useThemeStore from '../store/themeStore';
import { authAPI } from '../services/api';
import { useNavigate } from 'react-router-dom';

/* ── Floating celestial particle (CSS-only) ─────────────── */
function Particle({ style }) {
  return <div className="absolute rounded-full pointer-events-none" style={style} />;
}

/* ── Tarot card flat art (left panel decoration) ────────── */
function TarotArt({ theme }) {
  const c = theme === 'dark'
    ? { outer: '#7C3AED', inner: '#A78BFA', star: '#E2D9F3', glow: 'rgba(124,58,237,0.35)', text: '#B8A9D9' }
    : { outer: '#C9A4F5', inner: '#F4A8C6', star: 'white', glow: 'rgba(255,191,163,0.5)', text: '#6B4E7D' };

  return (
    <svg viewBox="0 0 320 480" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full max-w-xs mx-auto">
      {/* Card background */}
      <rect x="20" y="20" width="280" height="440" rx="24" fill={theme === 'dark' ? '#1A1035' : '#FFF7FB'} stroke={c.outer} strokeWidth="1.5"/>
      {/* Corner ornaments */}
      {[[32,32],[288,32],[32,448],[288,448]].map(([x,y],i) => (
        <g key={i} transform={`translate(${x},${y})`}>
          <circle r="5" fill={c.inner} opacity="0.6"/>
          <circle r="2" fill={c.star}/>
        </g>
      ))}
      {/* Border inner */}
      <rect x="30" y="30" width="260" height="420" rx="18" stroke={c.outer} strokeWidth="0.6" opacity="0.4"/>

      {/* Central sun/moon symbol */}
      <g transform="translate(160, 180)">
        {/* Outer ring of rays */}
        {Array.from({length:12},(_,i) => {
          const a = (i * 30 * Math.PI) / 180;
          const x1 = Math.sin(a)*62, y1 = -Math.cos(a)*62;
          const x2 = Math.sin(a)*74, y2 = -Math.cos(a)*74;
          return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke={c.inner} strokeWidth="1.5" opacity="0.7"/>;
        })}
        {/* Glow */}
        <circle r="56" fill={c.glow}/>
        {/* Main circle */}
        <circle r="48" stroke={c.outer} strokeWidth="1.5" fill={theme === 'dark' ? '#120B2E' : '#FEF3F8'}/>
        {/* Crescent moon */}
        <path d={`M -16 -20 A 28 28 0 0 1 -16 20 A 20 20 0 0 0 -16 -20 Z`} fill={c.outer} opacity="0.9"/>
        {/* Eye / center orb */}
        <ellipse cx="6" cy="0" rx="16" ry="22" stroke={c.inner} strokeWidth="1.2" fill="none"/>
        <ellipse cx="6" cy="0" rx="6" ry="9" fill={c.inner}/>
        <circle cx="4" cy="-2" r="2" fill={c.star}/>
        {/* Star dots around */}
        {[[-35,-10],[35,-10],[0,-40],[0,40]].map(([x,y],i) => (
          <circle key={i} cx={x} cy={y} r="2.5" fill={c.inner} opacity="0.8"/>
        ))}
      </g>

      {/* Wave bottom decoration */}
      <path d="M20 360 Q80 345 160 360 Q240 375 300 360 L300 440 Q240 425 160 440 Q80 455 20 440Z" fill={c.outer} opacity="0.08"/>

      {/* Text labels */}
      <text x="160" y="295" textAnchor="middle" fill={c.text} fontSize="11" letterSpacing="5" opacity="0.8">THE MIRROR</text>
      <text x="160" y="315" textAnchor="middle" fill={c.text} fontSize="9" letterSpacing="2" opacity="0.5">∞  THERAPITY  ∞</text>

      {/* Small constellation dots */}
      {[[60,100],[80,90],[95,108],[250,100],[240,85],[260,115]].map(([x,y],i) => (
        <circle key={i} cx={x} cy={y} r="1.5" fill={c.inner} opacity="0.5"/>
      ))}
      <line x1="60" y1="100" x2="80" y2="90" stroke={c.inner} strokeWidth="0.6" opacity="0.3"/>
      <line x1="80" y1="90" x2="95" y2="108" stroke={c.inner} strokeWidth="0.6" opacity="0.3"/>
      <line x1="250" y1="100" x2="240" y2="85" stroke={c.inner} strokeWidth="0.6" opacity="0.3"/>
      <line x1="240" y1="85" x2="260" y2="115" stroke={c.inner} strokeWidth="0.6" opacity="0.3"/>
    </svg>
  );
}

/* ── Star background (dark mode) ────────────────────────── */
const STARS = Array.from({ length: 28 }, (_, i) => ({
  left: `${Math.random() * 100}%`,
  top: `${Math.random() * 100}%`,
  size: Math.random() * 2.5 + 1,
  delay: Math.random() * 4,
  dur: 2 + Math.random() * 3,
}));

export default function LoginPage() {
  const [tab, setTab] = useState('login');
  const [form, setForm] = useState({ email: '', password: '', fullName: '', confirmPassword: '', newPassword: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');

  const { login } = useAuthStore();
  const { theme, toggleTheme } = useThemeStore();
  const navigate = useNavigate();

  const set = (key, val) => setForm(prev => ({ ...prev, [key]: val }));
  const switchTab = (t) => { setTab(t); setError(''); setInfo(''); };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(''); setLoading(true);
    try {
      const res = await authAPI.login({ username: form.email, password: form.password });
      const d = res.data;
      login({ username: d.username, displayName: d.displayName, avatar: d.avatar, bio: d.bio, onboarded: d.onboarded, following_list: d.following_list }, d.access_token, d.refresh_token);
      navigate(d.onboarded ? '/dashboard' : '/onboarding');
    } catch (err) { setError(err.response?.data?.detail || 'Lỗi hệ thống'); }
    finally { setLoading(false); }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    if (form.password !== form.confirmPassword) { setError('Mật khẩu xác nhận không khớp!'); return; }
    setLoading(true);
    try {
      const res = await authAPI.register({ username: form.email, password: form.password, email: form.email, full_name: form.fullName });
      const d = res.data;
      login({ username: d.username, displayName: d.displayName, avatar: '', bio: d.bio, onboarded: false, following_list: [] }, d.access_token, d.refresh_token);
      navigate('/onboarding');
    } catch (err) { setError(err.response?.data?.detail || 'Lỗi hệ thống'); }
    finally { setLoading(false); }
  };

  const handleReset = async (e) => {
    e.preventDefault();
    setError(''); setLoading(true);
    try {
      await authAPI.resetPassword({ email: form.email, new_password: form.newPassword });
      setInfo('Đổi mật khẩu thành công!');
      switchTab('login');
    } catch (err) { setError(err.response?.data?.detail || 'Lỗi hệ thống'); }
    finally { setLoading(false); }
  };

  const isLight = theme === 'light';

  return (
    <div className="min-h-screen flex relative overflow-hidden" style={{ background: 'var(--color-bg-primary)' }}>

      {/* ── Star field (dark mode) ───────────────────── */}
      {!isLight && (
        <div className="star-field">
          {STARS.map((s, i) => (
            <div key={i} className="star" style={{
              left: s.left, top: s.top,
              width: s.size, height: s.size,
              '--duration': `${s.dur}s`,
              '--delay': `${s.delay}s`,
            }}/>
          ))}
        </div>
      )}

      {/* ── Ambient gradient orbs ────────────────────── */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-32 -left-32 w-96 h-96 rounded-full blur-3xl opacity-30 animate-breathe"
          style={{ background: isLight ? 'radial-gradient(circle, #FFBFA3, #F4A8C6)' : 'radial-gradient(circle, #7C3AED, #3B1D6E)' }}/>
        <div className="absolute -bottom-32 -right-32 w-80 h-80 rounded-full blur-3xl opacity-20 animate-breathe"
          style={{ background: isLight ? 'radial-gradient(circle, #C9A4F5, #F4A8C6)' : 'radial-gradient(circle, #1E3A6E, #120B2E)', animationDelay: '1.5s' }}/>
      </div>

      {/* ── Left panel: Tarot art ───────────────────── */}
      <motion.div
        className="hidden lg:flex flex-col items-center justify-center flex-1 px-12 relative z-10"
        initial={{ opacity: 0, x: -40 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.7, ease: [0.25, 0.46, 0.45, 0.94] }}
      >
        <motion.div animate={{ y: [0, -10, 0] }} transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}>
          <TarotArt theme={theme} />
        </motion.div>
        <div className="mt-8 text-center space-y-2">
          <h2 className="font-display text-3xl font-medium" style={{ color: 'var(--color-text-primary)' }}>
            Gương Soi Tâm Trí
          </h2>
          <p className="text-sm max-w-xs mx-auto leading-relaxed" style={{ color: 'var(--color-text-muted)' }}>
            Hành trình khám phá bản thân qua những câu hỏi Socratic sâu sắc
          </p>
        </div>
      </motion.div>

      {/* ── Right panel: Auth form ──────────────────── */}
      <div className="flex flex-1 items-center justify-center px-6 py-12 relative z-10">
        <motion.div
          className="w-full max-w-md"
          initial={{ opacity: 0, y: 32 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.15, ease: [0.25, 0.46, 0.45, 0.94] }}
        >
          {/* Logo mobile */}
          <div className="lg:hidden text-center mb-8">
            <h1 className="font-display text-4xl font-medium gradient-text">Therapity</h1>
            <p className="text-sm mt-1" style={{ color: 'var(--color-text-muted)' }}>Tâm lý AI · Gương soi tâm trí</p>
          </div>

          {/* Theme toggle */}
          <div className="flex justify-end mb-4">
            <button onClick={toggleTheme} className="btn-ghost text-sm gap-2" style={{ color: 'var(--color-text-muted)' }}>
              {theme === 'dark'
                ? <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>
                : <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
              }
              {theme === 'dark' ? 'Sáng' : 'Tối'}
            </button>
          </div>

          {/* Card */}
          <div className="glass-card">
            {/* Header */}
            <div className="text-center mb-6">
              <h1 className="font-display text-4xl font-semibold hidden lg:block" style={{ color: 'var(--color-text-primary)' }}>
                Therapity
              </h1>
              <p className="text-sm mt-1" style={{ color: 'var(--color-text-muted)' }}>
                {tab === 'login' ? 'Chào mừng trở lại' : tab === 'register' ? 'Bắt đầu hành trình' : 'Đặt lại mật khẩu'}
              </p>
            </div>

            {/* Tabs */}
            {tab !== 'forgot' && (
              <div className="flex mb-6 p-1 rounded-xl gap-1" style={{ background: 'var(--color-bg-secondary)' }}>
                {[['login','Đăng nhập'],['register','Đăng ký']].map(([t, label]) => (
                  <button key={t} onClick={() => switchTab(t)}
                    className="flex-1 py-2 text-sm font-semibold rounded-lg transition-all"
                    style={{
                      background: tab === t ? 'var(--color-accent)' : 'transparent',
                      color: tab === t ? 'white' : 'var(--color-text-muted)',
                      boxShadow: tab === t ? '0 2px 8px var(--color-shadow-strong)' : 'none',
                    }}>
                    {label}
                  </button>
                ))}
              </div>
            )}

            {/* Messages */}
            <AnimatePresence>
              {error && (
                <motion.div key="err" initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}
                  className="mb-4 p-3 rounded-lg text-sm overflow-hidden"
                  style={{ background: 'rgba(224,107,138,0.1)', color: 'var(--color-danger)', border: '1px solid rgba(224,107,138,0.2)' }}>
                  {error}
                </motion.div>
              )}
              {info && (
                <motion.div key="info" initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }}
                  className="mb-4 p-3 rounded-lg text-sm overflow-hidden"
                  style={{ background: 'rgba(109,185,123,0.1)', color: 'var(--color-success)', border: '1px solid rgba(109,185,123,0.2)' }}>
                  {info}
                </motion.div>
              )}
            </AnimatePresence>

            {/* ── Login ── */}
            <AnimatePresence mode="wait">
              {tab === 'login' && (
                <motion.form key="login" onSubmit={handleLogin} className="space-y-4"
                  initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 16 }}
                  transition={{ duration: 0.22 }}>
                  <div>
                    <label className="block text-xs font-semibold mb-1.5 uppercase tracking-wider" style={{ color: 'var(--color-text-muted)' }}>Email</label>
                    <input className="input" type="email" placeholder="you@example.com" value={form.email} onChange={e => set('email', e.target.value)} required/>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold mb-1.5 uppercase tracking-wider" style={{ color: 'var(--color-text-muted)' }}>Mật khẩu</label>
                    <input className="input" type="password" placeholder="••••••••" value={form.password} onChange={e => set('password', e.target.value)} required/>
                  </div>
                  <div className="flex justify-end">
                    <button type="button" onClick={() => switchTab('forgot')} className="text-xs hover:underline transition-opacity" style={{ color: 'var(--color-accent)' }}>
                      Quên mật khẩu?
                    </button>
                  </div>
                  <button type="submit" className="btn-primary w-full mt-2 py-3 text-base" disabled={loading}>
                    {loading ? <span className="animate-breathe">Đang xử lý…</span> : 'Đăng nhập'}
                  </button>
                </motion.form>
              )}

              {/* ── Register ── */}
              {tab === 'register' && (
                <motion.form key="register" onSubmit={handleRegister} className="space-y-4"
                  initial={{ opacity: 0, x: 16 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -16 }}
                  transition={{ duration: 0.22 }}>
                  <div>
                    <label className="block text-xs font-semibold mb-1.5 uppercase tracking-wider" style={{ color: 'var(--color-text-muted)' }}>Họ và tên</label>
                    <input className="input" placeholder="Tên của bạn…" value={form.fullName} onChange={e => set('fullName', e.target.value)} required/>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold mb-1.5 uppercase tracking-wider" style={{ color: 'var(--color-text-muted)' }}>Email</label>
                    <input className="input" type="email" placeholder="you@example.com" value={form.email} onChange={e => set('email', e.target.value)} required/>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold mb-1.5 uppercase tracking-wider" style={{ color: 'var(--color-text-muted)' }}>Mật khẩu</label>
                    <input className="input" type="password" placeholder="••••••••" value={form.password} onChange={e => set('password', e.target.value)} required/>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold mb-1.5 uppercase tracking-wider" style={{ color: 'var(--color-text-muted)' }}>Xác nhận mật khẩu</label>
                    <input className="input" type="password" placeholder="••••••••" value={form.confirmPassword} onChange={e => set('confirmPassword', e.target.value)} required/>
                  </div>
                  <button type="submit" className="btn-primary w-full mt-2 py-3 text-base" disabled={loading}>
                    {loading ? <span className="animate-breathe">Đang tạo…</span> : 'Tạo tài khoản'}
                  </button>
                </motion.form>
              )}

              {/* ── Forgot ── */}
              {tab === 'forgot' && (
                <motion.form key="forgot" onSubmit={handleReset} className="space-y-4"
                  initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -12 }}
                  transition={{ duration: 0.22 }}>
                  <div>
                    <label className="block text-xs font-semibold mb-1.5 uppercase tracking-wider" style={{ color: 'var(--color-text-muted)' }}>Email đã đăng ký</label>
                    <input className="input" type="email" placeholder="you@example.com" value={form.email} onChange={e => set('email', e.target.value)} required/>
                  </div>
                  <div>
                    <label className="block text-xs font-semibold mb-1.5 uppercase tracking-wider" style={{ color: 'var(--color-text-muted)' }}>Mật khẩu mới</label>
                    <input className="input" type="password" placeholder="••••••••" value={form.newPassword} onChange={e => set('newPassword', e.target.value)} required/>
                  </div>
                  <button type="submit" className="btn-primary w-full py-3 text-base" disabled={loading}>
                    {loading ? <span className="animate-breathe">Đang đổi…</span> : 'Đặt lại mật khẩu'}
                  </button>
                  <button type="button" onClick={() => switchTab('login')} className="btn-ghost w-full" style={{ color: 'var(--color-text-muted)' }}>
                    ← Quay lại đăng nhập
                  </button>
                </motion.form>
              )}
            </AnimatePresence>
          </div>

          {/* Bottom tagline */}
          <p className="text-center mt-6 text-xs" style={{ color: 'var(--color-text-muted)' }}>
            Mọi cuộc trò chuyện đều được bảo mật · Therapity 2026
          </p>
        </motion.div>
      </div>
    </div>
  );
}
