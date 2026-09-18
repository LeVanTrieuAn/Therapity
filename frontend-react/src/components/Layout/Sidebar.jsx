import { NavLink, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import useAuthStore from '../../store/authStore';
import useThemeStore from '../../store/themeStore';

/*
 * TASTE-SKILL ICON SYSTEM
 * ─────────────────────────────────────────────
 * No standard UI icons. All symbols are flat
 * geometric / celestial shapes — diamond (✦),
 * crescent, orb, eye, cross, constellation dot.
 * Each is a tiny standalone SVG with clip-path
 * or geometric primitives only.
 */

const TsIcon = {
  /* ✦ 4-pointed diamond star — Dashboard */
  dashboard: (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
      <path d="M10 1 L11.8 8.2 L19 10 L11.8 11.8 L10 19 L8.2 11.8 L1 10 L8.2 8.2 Z"/>
    </svg>
  ),

  /* ◎ Double circle / eye — Coach / mirror */
  coach: (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
      <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="1.4"/>
      <ellipse cx="10" cy="10" rx="3.5" ry="5" stroke="currentColor" strokeWidth="1.2"/>
      <circle cx="10" cy="10" r="1.5" fill="currentColor"/>
    </svg>
  ),

  /* ☽ Crescent + dot — Diary / reflection */
  diary: (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
      <path d="M10 3 A7 7 0 0 1 10 17 A5 5 0 0 0 10 3 Z" opacity="0.9"/>
      <circle cx="14" cy="6" r="1.2"/>
      <circle cx="15.5" cy="10" r="0.8" opacity="0.6"/>
    </svg>
  ),

  /* ✤ Compass rose — AOA / global */
  aoa: (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
      <path d="M10 2 L11.2 8.8 L18 10 L11.2 11.2 L10 18 L8.8 11.2 L2 10 L8.8 8.8 Z" opacity="0.85"/>
      <circle cx="10" cy="10" r="2" fill="none" stroke="currentColor" strokeWidth="1"/>
    </svg>
  ),

  /* ○ Minimal ring with tick — Tasks / checkmark */
  tasks: (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
      <circle cx="10" cy="10" r="7.5" stroke="currentColor" strokeWidth="1.4"/>
      <path d="M7 10.5 L9 12.5 L13.5 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    </svg>
  ),

  /* △▽ Upward triangle — Cohort / path */
  cohort: (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
      <polygon points="10,3 18,16 2,16" opacity="0.85"/>
      <polygon points="10,9 15,17 5,17" fill="var(--color-bg-primary)" opacity="0.5"/>
    </svg>
  ),

  /* ☀ Minimal sun rays — Light mode */
  sun: (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
      <circle cx="8" cy="8" r="3"/>
      {[0,45,90,135,180,225,270,315].map((deg, i) => {
        const r = deg * Math.PI / 180;
        const x1 = 8 + 4.5 * Math.sin(r), y1 = 8 - 4.5 * Math.cos(r);
        const x2 = 8 + 6 * Math.sin(r), y2 = 8 - 6 * Math.cos(r);
        return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>;
      })}
    </svg>
  ),

  /* ☽ Small crescent — Dark mode */
  moon: (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
      <path d="M8 2 A6 6 0 0 1 8 14 A4.5 4.5 0 0 0 8 2 Z"/>
    </svg>
  ),

  /* ← Arrow left — Logout */
  logout: (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round">
      <path d="M9 7H2M5 4L2 7L5 10"/>
      <path d="M6 3H11V11H6" strokeLinejoin="round"/>
    </svg>
  ),
};

/* ── Tarot logo mark ───────────────────────────────────── */
const TarotLogo = ({ theme }) => {
  const c = theme === 'dark' ? '#7C3AED' : '#B07FD4';
  const dot = theme === 'dark' ? '#A78BFA' : '#F4A8C6';
  return (
    <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
      <circle cx="18" cy="18" r="16" stroke={c} strokeWidth="1.2" fill={theme === 'dark' ? 'rgba(124,58,237,0.1)' : 'rgba(176,127,212,0.1)'}/>
      {/* 4-pointed star */}
      <path d="M18 6 L19.5 14.5 L28 18 L19.5 21.5 L18 30 L16.5 21.5 L8 18 L16.5 14.5 Z" fill={c} opacity="0.85"/>
      <circle cx="18" cy="18" r="2.5" fill="white" opacity="0.9"/>
      {[0,90,180,270].map((deg, i) => {
        const r = deg * Math.PI / 180;
        return <circle key={i} cx={18 + 13 * Math.sin(r)} cy={18 - 13 * Math.cos(r)} r="1.2" fill={dot} opacity="0.5"/>;
      })}
    </svg>
  );
};

const navItems = [
  { path: '/dashboard', icon: TsIcon.dashboard, labelVi: 'Tổng quan',  labelEn: 'Dashboard' },
  { path: '/coach',     icon: TsIcon.coach,     labelVi: 'Tham vấn',  labelEn: 'Dialogue'  },
  { path: '/diary',     icon: TsIcon.diary,     labelVi: 'Nhật ký',   labelEn: 'Diary'     },
  { path: '/aoa',       icon: TsIcon.aoa,       labelVi: 'Bản tin',   labelEn: 'AOA Feed'  },
  { path: '/tasks',     icon: TsIcon.tasks,     labelVi: 'Nhiệm vụ',  labelEn: 'Tasks'     },
  { path: '/cohort',    icon: TsIcon.cohort,    labelVi: 'Lộ trình',  labelEn: 'Roadmap'   },
];

const sidebarVariants = {
  hidden: {},
  show: { transition: { staggerChildren: 0.07, delayChildren: 0.1 } },
};
const itemVariants = {
  hidden: { x: -14, opacity: 0 },
  show: { x: 0, opacity: 1, transition: { type: 'spring', stiffness: 260, damping: 24 } },
};

export default function Sidebar() {
  const { user, logout } = useAuthStore();
  const { theme, toggleTheme, lang, toggleLang } = useThemeStore();
  const navigate = useNavigate();

  const handleLogout = () => { logout(); navigate('/'); };
  const displayName = user?.displayName || user?.username || 'User';
  const initials = displayName.charAt(0).toUpperCase();
  const isDark = theme === 'dark';

  return (
    <motion.aside
      className="sidebar"
      initial={{ x: -260 }}
      animate={{ x: 0 }}
      transition={{ type: 'spring', stiffness: 220, damping: 26 }}
    >
      {/* ── Logo ─────────────────────────────────── */}
      <div className="mb-8 px-1">
        <div className="flex items-center gap-3">
          <motion.div whileHover={{ rotate: 45, scale: 1.08 }} transition={{ type: 'spring', stiffness: 280 }}>
            <TarotLogo theme={theme} />
          </motion.div>
          <div>
            <h1 className="font-display text-xl font-semibold" style={{ color: 'var(--color-text-primary)', letterSpacing: '0.03em' }}>
              Therapity
            </h1>
            <span className="text-xs font-body" style={{ color: 'var(--color-text-muted)' }}>
              {lang === 'en' ? 'AI Psychology' : 'Tâm lý AI'}
            </span>
          </div>
        </div>
      </div>

      {/* ── Navigation ───────────────────────────── */}
      <motion.nav className="flex-1 flex flex-col gap-0.5" variants={sidebarVariants} initial="hidden" animate="show">
        {navItems.map((item) => (
          <motion.div key={item.path} variants={itemVariants}>
            <NavLink to={item.path} className={({ isActive }) => `sidebar-link ${isActive ? 'active' : ''}`}>
              <span style={{ color: 'var(--color-accent)', flexShrink: 0, display: 'flex', alignItems: 'center' }}>
                {item.icon}
              </span>
              <span>{lang === 'en' ? item.labelEn : item.labelVi}</span>
            </NavLink>
          </motion.div>
        ))}
      </motion.nav>

      {/* ── Footer ───────────────────────────────── */}
      <div className="mt-auto space-y-3">
        {/* Theme + Language */}
        <div className="flex items-center gap-1 px-1">
          <button onClick={toggleTheme} className="btn-ghost flex-1 text-sm gap-2"
            title="Toggle theme" style={{ justifyContent: 'flex-start', paddingLeft: '0.625rem' }}>
            <span style={{ color: 'var(--color-accent)', display: 'flex' }}>
              {isDark ? TsIcon.sun : TsIcon.moon}
            </span>
            <span style={{ fontSize: '0.78rem', color: 'var(--color-text-muted)' }}>
              {isDark ? (lang === 'en' ? 'Light' : 'Sáng') : (lang === 'en' ? 'Dark' : 'Tối')}
            </span>
          </button>
          <button onClick={toggleLang} className="btn-ghost text-xs font-bold px-3"
            style={{ color: 'var(--color-accent)' }} title="Toggle language">
            {lang === 'vi' ? 'EN' : 'VI'}
          </button>
        </div>

        {/* User card */}
        <div className="flex items-center gap-3 px-3 py-2.5 rounded-xl"
          style={{ background: 'var(--color-bg-hover)', border: '1px solid var(--color-border-subtle)' }}>
          <div className="avatar">{initials}</div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-semibold truncate" style={{ color: 'var(--color-text-primary)' }}>
              {displayName}
            </p>
            <button onClick={handleLogout}
              className="flex items-center gap-1.5 text-xs transition-opacity hover:opacity-70"
              style={{ color: 'var(--color-text-muted)' }}>
              <span style={{ display: 'flex' }}>{TsIcon.logout}</span>
              {lang === 'en' ? 'Sign out' : 'Đăng xuất'}
            </button>
          </div>
        </div>

        {/* Diamond star divider */}
        <p className="flex items-center justify-center gap-2" style={{ fontSize: '0.65rem', color: 'var(--color-text-muted)', letterSpacing: '0.08em' }}>
          <span className="ts-diamond-sm" style={{ color: 'var(--color-accent)', width: '0.4rem', height: '0.4rem' }}/>
          THERAPITY v4.0
          <span className="ts-diamond-sm" style={{ color: 'var(--color-accent)', width: '0.4rem', height: '0.4rem' }}/>
        </p>
      </div>
    </motion.aside>
  );
}
