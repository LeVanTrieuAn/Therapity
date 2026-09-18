import { NavLink, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import useAuthStore from '../../store/authStore';
import useThemeStore from '../../store/themeStore';

/* ── Tarot-inspired flat SVG icons ─────────────────────── */
const Icons = {
  coach: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2a5 5 0 0 1 5 5c0 1.8-.95 3.37-2.37 4.26L12 22l-2.63-10.74A5 5 0 0 1 12 2z"/>
      <circle cx="12" cy="7" r="1.5" fill="currentColor" stroke="none"/>
    </svg>
  ),
  diary: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <rect x="4" y="2" width="13" height="20" rx="2"/>
      <path d="M8 6h6M8 10h6M8 14h4"/>
      <path d="M17 2l3 3-3 3" strokeWidth="1.2"/>
    </svg>
  ),
  aoa: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="9"/>
      <path d="M12 3a9 9 0 0 1 0 18M3 12h18"/>
      <path d="M12 3c-2.5 3-4 5.7-4 9s1.5 6 4 9M12 3c2.5 3 4 5.7 4 9s-1.5 6-4 9"/>
    </svg>
  ),
  tasks: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 11l3 3L22 4"/>
      <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
    </svg>
  ),
  cohort: (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
    </svg>
  ),
  sun: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
      <circle cx="12" cy="12" r="5"/>
      <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
    </svg>
  ),
  moon: (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
    </svg>
  ),
  logout: (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
      <polyline points="16 17 21 12 16 7"/>
      <line x1="21" y1="12" x2="9" y2="12"/>
    </svg>
  ),
};

/* ── Tarot logo mark (flat vector) ─────────────────────── */
const TarotLogo = ({ theme }) => (
  <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
    {/* Outer ring */}
    <circle cx="18" cy="18" r="16" stroke={theme === 'dark' ? '#7C3AED' : '#C9A4F5'} strokeWidth="1.2" fill={theme === 'dark' ? 'rgba(124,58,237,0.12)' : 'rgba(201,164,245,0.12)'}/>
    {/* Inner crescent */}
    <path d="M18 9 A9 9 0 0 1 18 27 A6 6 0 0 0 18 9Z" fill={theme === 'dark' ? '#7C3AED' : '#C9A4F5'}/>
    {/* Sun ray dots */}
    {[0,60,120,180,240,300].map((deg, i) => {
      const r = 13;
      const rad = (deg * Math.PI) / 180;
      const x = 18 + r * Math.sin(rad);
      const y = 18 - r * Math.cos(rad);
      return <circle key={i} cx={x} cy={y} r="1.2" fill={theme === 'dark' ? '#A78BFA' : '#F4A8C6'}/>;
    })}
    {/* Center star */}
    <circle cx="18" cy="18" r="2" fill={theme === 'dark' ? '#E2D9F3' : 'white'}/>
  </svg>
);

const navItems = [
  { path: '/coach',  icon: Icons.coach,  labelVi: 'Tham vấn',   labelEn: 'Dialogue' },
  { path: '/diary',  icon: Icons.diary,  labelVi: 'Nhật ký',    labelEn: 'Diary' },
  { path: '/aoa',    icon: Icons.aoa,    labelVi: 'Bản tin',    labelEn: 'AOA Feed' },
  { path: '/tasks',  icon: Icons.tasks,  labelVi: 'Nhiệm vụ',   labelEn: 'Tasks' },
  { path: '/cohort', icon: Icons.cohort, labelVi: 'Lộ trình',   labelEn: 'Roadmap' },
];

const sidebarVariants = {
  hidden: { x: -20, opacity: 0 },
  show: { x: 0, opacity: 1, transition: { staggerChildren: 0.06, delayChildren: 0.1 } }
};
const itemVariants = {
  hidden: { x: -12, opacity: 0 },
  show: { x: 0, opacity: 1, transition: { type: 'spring', stiffness: 260, damping: 24 } }
};

export default function Sidebar() {
  const { user, logout } = useAuthStore();
  const { theme, toggleTheme, lang, toggleLang } = useThemeStore();
  const navigate = useNavigate();

  const handleLogout = () => { logout(); navigate('/'); };
  const displayName = user?.displayName || user?.username || 'User';
  const initials = displayName.charAt(0).toUpperCase();

  return (
    <motion.aside
      className="sidebar"
      initial={{ x: -260 }}
      animate={{ x: 0 }}
      transition={{ type: 'spring', stiffness: 220, damping: 26 }}
    >
      {/* ── Logo ──────────────────────────────────── */}
      <div className="mb-8 px-1">
        <div className="flex items-center gap-3">
          <motion.div whileHover={{ rotate: 30, scale: 1.1 }} transition={{ type: 'spring', stiffness: 300 }}>
            <TarotLogo theme={theme} />
          </motion.div>
          <div>
            <h1 className="font-display text-xl font-semibold" style={{ color: 'var(--color-text-primary)', letterSpacing: '0.02em' }}>
              Therapity
            </h1>
            <span className="text-xs font-body" style={{ color: 'var(--color-text-muted)' }}>
              {lang === 'en' ? 'AI Psychology' : 'Tâm lý AI'}
            </span>
          </div>
        </div>
      </div>

      {/* ── Navigation ────────────────────────────── */}
      <motion.nav
        className="flex-1 flex flex-col gap-0.5"
        variants={sidebarVariants}
        initial="hidden"
        animate="show"
      >
        {navItems.map((item) => (
          <motion.div key={item.path} variants={itemVariants}>
            <NavLink
              to={item.path}
              className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}
            >
              <span style={{ color: 'var(--color-accent)', opacity: 0.9 }}>{item.icon}</span>
              <span style={{ color: 'inherit' }}>{lang === 'en' ? item.labelEn : item.labelVi}</span>
            </NavLink>
          </motion.div>
        ))}
      </motion.nav>

      {/* ── Footer Controls ───────────────────────── */}
      <div className="mt-auto space-y-3">
        {/* Theme + Lang */}
        <div className="flex items-center gap-1 px-1">
          <button
            onClick={toggleTheme}
            className="btn-ghost flex-1 text-sm gap-2"
            title="Toggle theme"
            style={{ justifyContent: 'flex-start', paddingLeft: '0.625rem' }}
          >
            <span style={{ color: 'var(--color-accent)' }}>
              {theme === 'dark' ? Icons.sun : Icons.moon}
            </span>
            <span style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>
              {theme === 'dark' ? (lang === 'en' ? 'Light' : 'Sáng') : (lang === 'en' ? 'Dark' : 'Tối')}
            </span>
          </button>
          <button
            onClick={toggleLang}
            className="btn-ghost text-xs font-bold px-3"
            style={{ color: 'var(--color-accent)' }}
            title="Toggle language"
          >
            {lang === 'vi' ? 'EN' : 'VI'}
          </button>
        </div>

        {/* User Card */}
        <div
          className="flex items-center gap-3 px-3 py-2.5 rounded-xl"
          style={{
            background: 'var(--color-bg-hover)',
            border: '1px solid var(--color-border-subtle)',
          }}
        >
          <div className="avatar">{initials}</div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold truncate" style={{ color: 'var(--color-text-primary)' }}>
              {displayName}
            </p>
            <button
              onClick={handleLogout}
              className="flex items-center gap-1 text-xs transition-colors hover:opacity-80"
              style={{ color: 'var(--color-text-muted)' }}
            >
              {Icons.logout}
              <span>{lang === 'en' ? 'Sign out' : 'Đăng xuất'}</span>
            </button>
          </div>
        </div>

        {/* Version */}
        <p className="text-center" style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)', letterSpacing: '0.05em' }}>
          THERAPITY v4.0
        </p>
      </div>
    </motion.aside>
  );
}
