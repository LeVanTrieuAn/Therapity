import { useState } from 'react';
import useAuthStore from '../store/authStore';
import useThemeStore from '../store/themeStore';
import { authAPI } from '../services/api';
import { useNavigate } from 'react-router-dom';

export default function LoginPage() {
  const [tab, setTab] = useState('login'); // login | register | forgot
  const [form, setForm] = useState({ email: '', password: '', fullName: '', confirmPassword: '', newPassword: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');

  const { login } = useAuthStore();
  const { theme, toggleTheme } = useThemeStore();
  const navigate = useNavigate();

  const set = (key, val) => setForm(prev => ({ ...prev, [key]: val }));

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(''); setLoading(true);
    try {
      const res = await authAPI.login({ username: form.email, password: form.password });
      const d = res.data;
      login(
        { username: d.username, displayName: d.displayName, avatar: d.avatar, bio: d.bio, onboarded: d.onboarded, following_list: d.following_list },
        d.access_token,
        d.refresh_token,
      );
      navigate(d.onboarded ? '/coach' : '/onboarding');
    } catch (err) {
      setError(err.response?.data?.detail || 'Lỗi hệ thống');
    } finally { setLoading(false); }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    if (form.password !== form.confirmPassword) { setError('Mật khẩu xác nhận không khớp!'); return; }
    setLoading(true);
    try {
      const res = await authAPI.register({
        username: form.email, password: form.password, email: form.email,
        full_name: form.fullName,
      });
      const d = res.data;
      login(
        { username: d.username, displayName: d.displayName, avatar: '', bio: d.bio, onboarded: false, following_list: [] },
        d.access_token, d.refresh_token,
      );
      navigate('/onboarding');
    } catch (err) {
      setError(err.response?.data?.detail || 'Lỗi hệ thống');
    } finally { setLoading(false); }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setError(''); setLoading(true);
    try {
      await authAPI.resetPassword({ email: form.email, new_password: form.newPassword });
      setInfo('Đổi mật khẩu thành công! Mời bạn đăng nhập.');
      setTab('login');
    } catch (err) {
      setError(err.response?.data?.detail || 'Lỗi hệ thống');
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ background: 'var(--color-bg-primary)' }}>
      {/* Theme toggle */}
      <button onClick={toggleTheme} className="fixed top-4 right-4 btn-ghost text-xl" title="Toggle theme">
        {theme === 'dark' ? '☀️' : '🌙'}
      </button>

      <div className="w-full max-w-md animate-fade-in">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4 text-2xl font-black"
               style={{ background: 'var(--color-accent)', color: 'var(--color-text-inverse)' }}>T</div>
          <h1 className="text-3xl font-bold" style={{ color: 'var(--color-text-primary)' }}>Therapity</h1>
          <p className="text-sm mt-1" style={{ color: 'var(--color-text-muted)' }}>Mindset OS — Kiến tạo bản đồ tư duy</p>
        </div>

        {/* Card */}
        <div className="glass-card">
          {/* Tabs */}
          {(tab === 'login' || tab === 'register') && (
            <div className="flex mb-6 rounded-xl p-1" style={{ background: 'var(--color-bg-secondary)' }}>
              {['login', 'register'].map((t) => (
                <button key={t} onClick={() => { setTab(t); setError(''); setInfo(''); }}
                  className="flex-1 py-2 text-sm font-semibold rounded-lg transition-all"
                  style={{
                    background: tab === t ? 'var(--color-accent)' : 'transparent',
                    color: tab === t ? 'var(--color-text-inverse)' : 'var(--color-text-muted)',
                  }}>
                  {t === 'login' ? 'Đăng nhập' : 'Đăng ký'}
                </button>
              ))}
            </div>
          )}

          {/* Messages */}
          {error && <div className="mb-4 p-3 rounded-lg text-sm" style={{ background: 'rgba(239,68,68,0.1)', color: '#EF4444' }}>{error}</div>}
          {info && <div className="mb-4 p-3 rounded-lg text-sm" style={{ background: 'rgba(22,163,74,0.1)', color: '#16A34A' }}>{info}</div>}

          {/* Login Form */}
          {tab === 'login' && (
            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--color-text-secondary)' }}>Email</label>
                <input className="input" type="email" placeholder="example@email.com" value={form.email} onChange={e => set('email', e.target.value)} required />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--color-text-secondary)' }}>Mật khẩu</label>
                <input className="input" type="password" placeholder="••••••••" value={form.password} onChange={e => set('password', e.target.value)} required />
              </div>
              <div className="flex justify-end">
                <button type="button" onClick={() => setTab('forgot')} className="text-xs hover:underline" style={{ color: 'var(--color-accent)' }}>Quên mật khẩu?</button>
              </div>
              <button type="submit" className="btn-primary w-full" disabled={loading}>
                {loading ? '⏳ Đang xử lý...' : 'Đăng nhập'}
              </button>
            </form>
          )}

          {/* Register Form — Direct (no OTP) */}
          {tab === 'register' && (
            <form onSubmit={handleRegister} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--color-text-secondary)' }}>Họ và tên</label>
                <input className="input" placeholder="Nhập họ và tên..." value={form.fullName} onChange={e => set('fullName', e.target.value)} required />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--color-text-secondary)' }}>Email</label>
                <input className="input" type="email" placeholder="example@email.com" value={form.email} onChange={e => set('email', e.target.value)} required />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--color-text-secondary)' }}>Mật khẩu</label>
                <input className="input" type="password" placeholder="••••••••" value={form.password} onChange={e => set('password', e.target.value)} required />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--color-text-secondary)' }}>Xác nhận mật khẩu</label>
                <input className="input" type="password" placeholder="••••••••" value={form.confirmPassword} onChange={e => set('confirmPassword', e.target.value)} required />
              </div>
              <button type="submit" className="btn-primary w-full" disabled={loading}>
                {loading ? '⏳ Đang tạo...' : 'Tạo tài khoản'}
              </button>
            </form>
          )}

          {/* Forgot Password — Direct reset (no OTP) */}
          {tab === 'forgot' && (
            <form onSubmit={handleResetPassword} className="space-y-4">
              <h3 className="text-lg font-semibold" style={{ color: 'var(--color-text-primary)' }}>Đặt lại mật khẩu</h3>
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--color-text-secondary)' }}>Email đã đăng ký</label>
                <input className="input" type="email" placeholder="example@email.com" value={form.email} onChange={e => set('email', e.target.value)} required />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1" style={{ color: 'var(--color-text-secondary)' }}>Mật khẩu mới</label>
                <input className="input" type="password" placeholder="Mật khẩu mới" value={form.newPassword} onChange={e => set('newPassword', e.target.value)} required />
              </div>
              <button type="submit" className="btn-primary w-full" disabled={loading}>{loading ? '⏳ Đang đổi...' : 'Đổi mật khẩu'}</button>
              <button type="button" onClick={() => setTab('login')} className="btn-ghost w-full">← Quay lại</button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
