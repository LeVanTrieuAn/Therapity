import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import useAuthStore from '../store/authStore';
import useThemeStore from '../store/themeStore';
import { tasksAPI } from '../services/api';

/* ── Flat vector SVG: Ocean sunset scene (light) ─────────── */
function SunsetScene() {
  return (
    <svg viewBox="0 0 800 320" fill="none" xmlns="http://www.w3.org/2000/svg"
      style={{ width: '100%', height: '100%', display: 'block' }}>
      {/* Sky gradient layers */}
      <defs>
        <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#C9A4F5" stopOpacity="0.5"/>
          <stop offset="40%" stopColor="#F4A8C6" stopOpacity="0.6"/>
          <stop offset="80%" stopColor="#FFBFA3" stopOpacity="0.7"/>
          <stop offset="100%" stopColor="#FFD5B8" stopOpacity="0.4"/>
        </linearGradient>
        <linearGradient id="ocean" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#C9A4F5" stopOpacity="0.25"/>
          <stop offset="100%" stopColor="#B07FD4" stopOpacity="0.1"/>
        </linearGradient>
        <radialGradient id="sun" cx="50%" cy="60%" r="30%">
          <stop offset="0%" stopColor="#FFD5B8" stopOpacity="0.9"/>
          <stop offset="50%" stopColor="#FFBFA3" stopOpacity="0.5"/>
          <stop offset="100%" stopColor="transparent"/>
        </radialGradient>
      </defs>

      {/* Sky */}
      <rect width="800" height="320" fill="url(#sky)"/>
      {/* Sun glow */}
      <ellipse cx="400" cy="195" rx="140" ry="90" fill="url(#sun)"/>
      {/* Sun circle */}
      <circle cx="400" cy="190" r="32" fill="#FFBFA3" opacity="0.85"/>
      <circle cx="400" cy="190" r="24" fill="#FFD5B8" opacity="0.9"/>
      <circle cx="400" cy="190" r="16" fill="white" opacity="0.6"/>

      {/* Sun rays */}
      {Array.from({length: 12}, (_, i) => {
        const a = (i * 30 * Math.PI) / 180;
        const r1 = 38, r2 = 56 + (i % 2 === 0 ? 8 : 0);
        return (
          <line key={i}
            x1={400 + r1 * Math.sin(a)} y1={190 - r1 * Math.cos(a)}
            x2={400 + r2 * Math.sin(a)} y2={190 - r2 * Math.cos(a)}
            stroke="#FFBFA3" strokeWidth="1.5" opacity="0.6"
          />
        );
      })}

      {/* Horizon line */}
      <rect x="0" y="205" width="800" height="2" fill="#F4A8C6" opacity="0.4"/>

      {/* Ocean surface */}
      <rect x="0" y="207" width="800" height="113" fill="url(#ocean)"/>

      {/* Ocean reflection ripples */}
      {[220, 240, 258, 274, 290].map((y, i) => (
        <ellipse key={i} cx="400" cy={y} rx={60 + i * 25} ry="2"
          fill="#F4A8C6" opacity={0.15 - i * 0.02}/>
      ))}

      {/* Flat birds (3 simple v-shapes) */}
      {[[180, 80], [220, 65], [560, 75]].map(([x, y], i) => (
        <path key={i} d={`M${x} ${y} Q${x+10} ${y-6} ${x+20} ${y}`}
          stroke="#C9A4F5" strokeWidth="1.5" fill="none" opacity="0.5"/>
      ))}

      {/* Distant flat ship silhouette */}
      <rect x="580" y="198" width="40" height="6" rx="2" fill="#B07FD4" opacity="0.25"/>
      <polygon points="590,198 600,185 608,198" fill="#B07FD4" opacity="0.2"/>

      {/* Tarot-star dots */}
      {[[100, 40], [680, 30], [150, 90], [650, 60], [300, 25]].map(([x, y], i) => (
        <circle key={i} cx={x} cy={y} r="2" fill="#C9A4F5" opacity="0.4"/>
      ))}
    </svg>
  );
}

/* ── Flat vector SVG: Ocean abyss & stars (dark) ─────────── */
function AbyssScene() {
  const stars = Array.from({ length: 40 }, (_, i) => ({
    x: (i * 127 + 30) % 800,
    y: (i * 73 + 15) % 160,
    r: [1, 1.5, 2][i % 3],
    op: 0.3 + (i % 5) * 0.1,
  }));

  return (
    <svg viewBox="0 0 800 320" fill="none" xmlns="http://www.w3.org/2000/svg"
      style={{ width: '100%', height: '100%', display: 'block' }}>
      <defs>
        <linearGradient id="abyssSky" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#0D0B1A" stopOpacity="0.9"/>
          <stop offset="60%" stopColor="#120B2E" stopOpacity="0.8"/>
          <stop offset="100%" stopColor="#1A1035" stopOpacity="0.6"/>
        </linearGradient>
        <linearGradient id="abyssOcean" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#1E3A6E" stopOpacity="0.4"/>
          <stop offset="100%" stopColor="#0D0B1A" stopOpacity="0.2"/>
        </linearGradient>
        <radialGradient id="moonGlow" cx="72%" cy="25%" r="15%">
          <stop offset="0%" stopColor="#A78BFA" stopOpacity="0.5"/>
          <stop offset="100%" stopColor="transparent"/>
        </radialGradient>
      </defs>

      <rect width="800" height="320" fill="url(#abyssSky)"/>
      <ellipse cx="576" cy="80" rx="80" ry="60" fill="url(#moonGlow)"/>

      {/* Crescent moon */}
      <circle cx="576" cy="65" r="22" fill="#1E1545" opacity="0.95"/>
      <circle cx="584" cy="60" r="22" fill="#0D0B1A" opacity="0.95"/>
      <circle cx="576" cy="65" r="18" fill="#E2D9F3" opacity="0.08"/>

      {/* Stars */}
      {stars.map((s, i) => (
        <circle key={i} cx={s.x} cy={s.y} r={s.r} fill="#E2D9F3" opacity={s.op}/>
      ))}

      {/* Constellation lines */}
      {[[80,30],[120,50],[100,70],[140,45]].reduce((acc, [x,y], i, arr) => {
        if (i === 0) return acc;
        const [px, py] = arr[i-1];
        return [...acc, <line key={i} x1={px} y1={py} x2={x} y2={y} stroke="#A78BFA" strokeWidth="0.5" opacity="0.25"/>];
      }, [])}

      {/* Horizon */}
      <rect x="0" y="200" width="800" height="1" fill="#7C3AED" opacity="0.3"/>

      {/* Ocean */}
      <rect x="0" y="201" width="800" height="119" fill="url(#abyssOcean)"/>

      {/* Moon reflection ripples */}
      {[220, 238, 255, 272].map((y, i) => (
        <ellipse key={i} cx="400" cy={y} rx={50 + i * 30} ry="1.5"
          fill="#7C3AED" opacity={0.12 - i * 0.02}/>
      ))}

      {/* Bioluminescent dots on ocean */}
      {[[200,260],[350,275],[500,265],[650,270]].map(([x,y], i) => (
        <circle key={i} cx={x} cy={y} r="2" fill="#60A5FA" opacity="0.2"/>
      ))}
    </svg>
  );
}

/* ── Stat Card ────────────────────────────────────────────── */
function StatCard({ symbol, value, label, delay = 0 }) {
  return (
    <motion.div
      className="tarot-card flex flex-col items-center gap-1 py-5 px-4"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, type: 'spring', stiffness: 220, damping: 22 }}
      whileHover={{ y: -3, transition: { type: 'spring', stiffness: 300 } }}
    >
      <div style={{ color: 'var(--color-accent)', display: 'flex', alignItems: 'center', justifyContent: 'center', width: 32, height: 32 }}>
        {symbol}
      </div>
      <span className="font-display text-3xl font-semibold" style={{ color: 'var(--color-accent)' }}>{value}</span>
      <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textAlign: 'center' }}>{label}</span>
    </motion.div>
  );
}

/* ── Quick-action Card ───────────────────────────────────── */
function ActionCard({ to, icon, title, subtitle, gradient, delay = 0 }) {
  const navigate = useNavigate();
  return (
    <motion.button
      onClick={() => navigate(to)}
      className="glass-card text-left w-full flex items-start gap-4 cursor-pointer"
      style={{ padding: '1.25rem' }}
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, type: 'spring', stiffness: 220, damping: 22 }}
      whileHover={{ y: -4, boxShadow: '0 16px 40px var(--color-shadow-strong)' }}
      whileTap={{ scale: 0.98 }}
    >
      <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
        style={{ background: gradient }}>
        <span style={{ fontSize: '1.2rem' }}>{icon}</span>
      </div>
      <div>
        <p className="font-semibold text-sm" style={{ color: 'var(--color-text-primary)' }}>{title}</p>
        <p className="text-xs mt-0.5" style={{ color: 'var(--color-text-muted)' }}>{subtitle}</p>
      </div>
    </motion.button>
  );
}

/* ── Main Dashboard ──────────────────────────────────────── */
export default function DashboardPage() {
  const { user } = useAuthStore();
  const { lang, theme } = useThemeStore();
  const navigate = useNavigate();
  const isDark = theme === 'dark';

  const [tasks, setTasks] = useState([]);
  const [loadingTasks, setLoadingTasks] = useState(true);

  const displayName = user?.displayName || user?.username || 'bạn';

  useEffect(() => {
    if (user?.username) {
      tasksAPI.getTasks(user.username)
        .then(r => setTasks(Object.values(r.data || {})))
        .catch(() => {})
        .finally(() => setLoadingTasks(false));
    }
  }, [user]);

  const pendingTasks = tasks.filter(t => !t.completed);
  const completedTasks = tasks.filter(t => t.completed);

  const stagger = { hidden: {}, show: { transition: { staggerChildren: 0.08 } } };
  const itemFade = { hidden: { opacity: 0, y: 12 }, show: { opacity: 1, y: 0 } };

  return (
    <div className="relative min-h-full pb-8">

      {/* ── Full-page background image ────────────── */}
      <div
        className={`fixed inset-0 pointer-events-none z-0 ${isDark ? 'scene-bg-abyss' : 'scene-bg-sunset'}`}
        style={{ opacity: isDark ? 0.55 : 0.7 }}
      />
      {/* Fade to page bg at bottom */}
      <div className="fixed inset-0 pointer-events-none z-0" style={{
        background: isDark
          ? 'linear-gradient(to bottom, transparent 45%, var(--color-bg-primary) 85%)'
          : 'linear-gradient(to bottom, transparent 40%, var(--color-bg-primary) 80%)',
      }}/>

      {/* ── Content ────────────────────────────────────── */}
      <div className="relative z-10 pt-6">

        {/* Greeting */}
        <motion.div className="mb-8"
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}>
          <p className="text-sm mb-1" style={{ color: isDark ? '#A78BFA' : '#C9A4F5', fontStyle: 'italic' }}>
            {lang === 'en' ? 'Welcome back' : 'Chào mừng trở lại'}
          </p>
          <h1 className="font-display text-4xl font-semibold" style={{ color: 'var(--color-text-primary)' }}>
            {displayName}
          </h1>
          <p className="text-sm mt-2 max-w-lg" style={{ color: 'var(--color-text-muted)' }}>
            {lang === 'en'
              ? 'Your mind is a mirror — every question reflects the truth deeper.'
              : 'Tâm trí của bạn là một tấm gương — mỗi câu hỏi phản chiếu sự thật sâu hơn.'}
          </p>
        </motion.div>

        {/* Stat row */}
        <div className="grid grid-cols-3 gap-3 mb-6">
          <StatCard
            symbol={
              <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
                <path d="M12 2L14 9.5L22 12L14 14.5L12 22L10 14.5L2 12L10 9.5Z"/>
              </svg>
            }
            value={pendingTasks.length} label={lang === 'en' ? 'Pending tasks' : 'Nhiệm vụ chờ'} delay={0.1}/>
          <StatCard
            symbol={
              <svg viewBox="0 0 24 24" fill="none" width="24" height="24">
                <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.5"/>
                <ellipse cx="12" cy="12" rx="4" ry="6" stroke="currentColor" strokeWidth="1.2"/>
                <circle cx="12" cy="12" r="2" fill="currentColor"/>
              </svg>
            }
            value={completedTasks.length} label={lang === 'en' ? 'Completed' : 'Đã hoàn thành'} delay={0.18}/>
          <StatCard
            symbol={
              <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
                <path d="M12 2 A8 8 0 0 1 12 18 A6 6 0 0 0 12 2 Z" opacity="0.85"/>
                <circle cx="17" cy="7" r="1.5"/>
              </svg>
            }
            value={loadingTasks ? '…' : tasks.length} label={lang === 'en' ? 'Total tasks' : 'Tổng cộng'} delay={0.26}/>
        </div>

        {/* CTA banner: start dialogue */}
        <motion.div
          className="rounded-2xl mb-6 overflow-hidden relative cursor-pointer"
          style={{
            background: isDark
              ? 'linear-gradient(135deg, rgba(124,58,237,0.25), rgba(30,58,110,0.3))'
              : 'linear-gradient(135deg, rgba(255,191,163,0.3), rgba(201,164,245,0.3))',
            border: '1px solid var(--color-border)',
            padding: '1.5rem',
          }}
          initial={{ opacity: 0, scale: 0.97 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          whileHover={{ scale: 1.01 }}
          onClick={() => navigate('/coach')}
        >
          {/* Abstract tarot card motif */}
          <div className="absolute right-6 top-0 bottom-0 flex items-center opacity-20 pointer-events-none">
            <svg width="80" height="120" viewBox="0 0 80 120" fill="none">
              <rect x="4" y="4" width="72" height="112" rx="8" stroke="var(--color-accent)" strokeWidth="1.2"/>
              <circle cx="40" cy="50" r="22" stroke="var(--color-accent)" strokeWidth="1"/>
              <circle cx="40" cy="50" r="10" fill="var(--color-accent)" opacity="0.5"/>
              {[0,60,120,180,240,300].map((deg,i) => {
                const r=19, rad=deg*Math.PI/180;
                return <circle key={i} cx={40+r*Math.sin(rad)} cy={50-r*Math.cos(rad)} r="2" fill="var(--color-accent)"/>;
              })}
              <text x="40" y="92" textAnchor="middle" fill="var(--color-accent)" fontSize="8" letterSpacing="3">MIRROR</text>
            </svg>
          </div>

          <div className="relative z-10">
            <div className="badge mb-2">
              {lang === 'en' ? 'Daily session' : 'Phiên hằng ngày'}
            </div>
            <h2 className="font-display text-2xl font-semibold mb-1" style={{ color: 'var(--color-text-primary)' }}>
              {lang === 'en' ? 'Begin your Dialogue' : 'Bắt đầu Đối thoại'}
            </h2>
            <p className="text-sm mb-4" style={{ color: 'var(--color-text-muted)' }}>
              {lang === 'en'
                ? 'Your AI Socratic coach is ready to reflect your thoughts back.'
                : 'Coach Socratic AI đã sẵn sàng phản chiếu suy nghĩ của bạn.'}
            </p>
            <button className="btn-primary">
              {lang === 'en' ? 'Open Dialogue →' : 'Mở Đối thoại →'}
            </button>
          </div>
        </motion.div>

        {/* Quick-action grid */}
        <p className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: 'var(--color-text-muted)' }}>
          {lang === 'en' ? 'Navigate' : 'Điều hướng'}
        </p>
        <div className="grid grid-cols-2 gap-3 mb-6">
          <ActionCard to="/diary"
            icon="📓" title={lang === 'en' ? 'Diary' : 'Nhật ký'}
            subtitle={lang === 'en' ? 'Record reflections' : 'Ghi lại cảm xúc'}
            gradient="linear-gradient(135deg, #F4A8C6, #C9A4F5)"
            delay={0.35}/>
          <ActionCard to="/tasks"
            icon="✅" title={lang === 'en' ? 'Tasks' : 'Nhiệm vụ'}
            subtitle={lang === 'en' ? 'Track growth actions' : 'Theo dõi hành động'}
            gradient="linear-gradient(135deg, #FFBFA3, #F4A8C6)"
            delay={0.42}/>
          <ActionCard to="/aoa"
            icon="🌐" title={lang === 'en' ? 'AOA Feed' : 'Bản tin AOA'}
            subtitle={lang === 'en' ? 'Community insights' : 'Góc nhìn cộng đồng'}
            gradient="linear-gradient(135deg, #C9A4F5, #7C3AED)"
            delay={0.49}/>
          <ActionCard to="/cohort"
            icon="✦" title={lang === 'en' ? 'Roadmap' : 'Lộ trình'}
            subtitle={lang === 'en' ? 'Learning path' : 'Hành trình học'}
            gradient="linear-gradient(135deg, #A78BFA, #60A5FA)"
            delay={0.56}/>
        </div>

        {/* Recent tasks */}
        {pendingTasks.length > 0 && (
          <motion.div variants={stagger} initial="hidden" animate="show">
            <p className="text-xs font-semibold uppercase tracking-widest mb-3" style={{ color: 'var(--color-text-muted)' }}>
              {lang === 'en' ? 'Pending tasks' : 'Nhiệm vụ chờ xử lý'}
            </p>
            <div className="space-y-2">
              {pendingTasks.slice(0, 3).map((task, i) => (
                <motion.div key={task.id || i} variants={itemFade}
                  className="glass-card flex items-center gap-3"
                  style={{ padding: '0.875rem 1rem' }}>
                  <div className="w-2 h-2 rounded-full flex-shrink-0" style={{ background: 'var(--color-accent)' }}/>
                  <p className="text-sm flex-1" style={{ color: 'var(--color-text-primary)' }}>
                    {lang === 'en' ? (task.content_en || task.content_vi) : (task.content_vi || task.content_en)}
                  </p>
                  {task.deadline && (
                    <span className="text-xs flex-shrink-0" style={{ color: 'var(--color-text-muted)' }}>
                      {task.deadline}
                    </span>
                  )}
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
