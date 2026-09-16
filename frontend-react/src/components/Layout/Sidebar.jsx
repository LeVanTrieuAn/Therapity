import { NavLink, useNavigate } from 'react-router-dom';
import useAuthStore from '../../store/authStore';
import useThemeStore from '../../store/themeStore';

const navItems = [
  { path: '/coach', icon: '🧠', labelVi: 'Tham vấn', labelEn: 'Coach' },
  { path: '/diary', icon: '📓', labelVi: 'Nhật ký', labelEn: 'Diary' },
  { path: '/aoa', icon: '🌐', labelVi: 'Bản tin AOA', labelEn: 'AOA Feed' },
  { path: '/tasks', icon: '✅', labelVi: 'Nhiệm vụ', labelEn: 'Tasks' },
  { path: '/cohort', icon: '🎓', labelVi: 'Lộ trình', labelEn: 'Roadmap' },
];

export default function Sidebar() {
  const { user, logout } = useAuthStore();
  const { theme, toggleTheme, lang, toggleLang } = useThemeStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const displayName = user?.displayName || user?.username || 'User';
  const initials = displayName.charAt(0).toUpperCase();

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="mb-8">
        <div className="flex items-center gap-3 px-2">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center font-black text-lg"
               style={{ background: 'var(--color-accent)', color: 'var(--color-text-inverse)' }}>
            T
          </div>
          <div>
            <h1 className="text-lg font-bold" style={{ color: 'var(--color-text-primary)' }}>Therapity</h1>
            <span className="text-xs" style={{ color: 'var(--color-text-muted)' }}>Mindset OS</span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 flex flex-col gap-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
          >
            <span className="text-lg">{item.icon}</span>
            <span>{lang === 'en' ? item.labelEn : item.labelVi}</span>
          </NavLink>
        ))}
      </nav>

      {/* Controls */}
      <div className="mt-auto space-y-3">
        {/* Theme & Language Toggles */}
        <div className="flex items-center gap-2 px-2">
          <button onClick={toggleTheme} className="btn-ghost text-lg" title="Toggle theme">
            {theme === 'dark' ? '☀️' : '🌙'}
          </button>
          <button onClick={toggleLang} className="btn-ghost text-xs font-bold" title="Toggle language"
                  style={{ color: 'var(--color-accent)' }}>
            {lang === 'vi' ? 'EN' : 'VI'}
          </button>
        </div>

        {/* User */}
        <div className="flex items-center gap-3 px-2 py-2 rounded-xl" style={{ background: 'var(--color-bg-hover)' }}>
          <div className="avatar">{initials}</div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold truncate" style={{ color: 'var(--color-text-primary)' }}>{displayName}</p>
            <button onClick={handleLogout} className="text-xs hover:underline" style={{ color: 'var(--color-text-muted)' }}>
              {lang === 'en' ? 'Log Out' : 'Đăng xuất'}
            </button>
          </div>
        </div>

        {/* Version */}
        <p className="text-center text-xs" style={{ color: 'var(--color-text-muted)' }}>Therapity v4.0</p>
      </div>
    </aside>
  );
}
