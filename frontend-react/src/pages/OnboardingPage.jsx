/**
 * Therapity — OnboardingPage
 * Design System: glassmorphism, celestial SVG, Framer Motion
 * Fonts: Playfair Display (headings) / DM Sans (body)
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import useAuthStore from '../store/authStore';
import useThemeStore from '../store/themeStore';
import { profileAPI } from '../services/api';

const STEPS = [
  {
    key: 'dob',
    emoji: '🌙',
    titleVi: 'Ngày sinh của bạn?',
    titleEn: 'What is your date of birth?',
    subtitleVi: 'Giúp chúng tôi cá nhân hóa trải nghiệm cho bạn',
    subtitleEn: 'This helps us personalize your experience',
    type: 'date',
  },
  {
    key: 'gender',
    emoji: '✦',
    titleVi: 'Giới tính của bạn?',
    titleEn: 'What is your gender?',
    subtitleVi: 'Mọi lựa chọn đều được tôn trọng',
    subtitleEn: 'All choices are respected',
    options: ['Nam', 'Nữ', 'Khác', 'Không muốn tiết lộ'],
  },
  {
    key: 'interests',
    emoji: '◈',
    titleVi: 'Sở thích của bạn?',
    titleEn: 'What are your interests?',
    subtitleVi: 'Chọn một hoặc nhiều mục',
    subtitleEn: 'Select one or more',
    multi: true,
    options: ['Đọc sách', 'Thể thao', 'Âm nhạc', 'Du lịch', 'Công nghệ', 'Nghệ thuật', 'Nấu ăn', 'Thiền & Yoga', 'Viết lách', 'Phim ảnh'],
  },
  {
    key: 'problems',
    emoji: '◇',
    titleVi: 'Bạn đang gặp khó khăn gì?',
    titleEn: 'What challenges are you facing?',
    subtitleVi: 'Chúng tôi sẽ đồng hành cùng bạn',
    subtitleEn: 'We will be by your side',
    multi: true,
    options: ['Căng thẳng / Stress', 'Mất tập trung', 'Thiếu động lực', 'Lo âu', 'Khó kiểm soát cảm xúc', 'Thiếu mục tiêu sống', 'Trì hoãn', 'Tự ti'],
  },
  {
    key: 'goals',
    emoji: '🌟',
    titleVi: 'Mục tiêu của bạn với Therapity?',
    titleEn: 'Your goals for using Therapity?',
    subtitleVi: 'Hành trình của bạn bắt đầu từ đây',
    subtitleEn: 'Your journey starts here',
    multi: true,
    options: ['Quản lý cảm xúc', 'Phát triển bản thân', 'Tăng năng suất', 'Xây dựng thói quen tốt', 'Tìm hiểu bản thân', 'Kết nối cộng đồng'],
  },
];

export default function OnboardingPage() {
  const [step, setStep]     = useState(0);
  const [data, setData]     = useState({});
  const [loading, setLoading] = useState(false);
  const [dir, setDir]       = useState(1); // 1=forward, -1=back
  const { user, updateUser } = useAuthStore();
  const { theme }            = useThemeStore();
  const isDark               = theme === 'dark';
  const navigate             = useNavigate();

  const current  = STEPS[step];
  const progress = ((step + 1) / STEPS.length) * 100;

  const handleSelect = (option) => {
    if (current.multi) {
      const arr    = data[current.key] || [];
      const newArr = arr.includes(option) ? arr.filter(o => o !== option) : [...arr, option];
      setData({ ...data, [current.key]: newArr });
    } else {
      setData({ ...data, [current.key]: option });
    }
  };

  const goNext = () => {
    setDir(1);
    if (step < STEPS.length - 1) setStep(s => s + 1);
    else handleFinish();
  };

  const goBack = () => {
    if (step === 0) return;
    setDir(-1);
    setStep(s => s - 1);
  };

  const handleFinish = async () => {
    setLoading(true);
    try {
      await profileAPI.saveOnboarding(user?.username, data);
      updateUser({ onboarded: true });
      navigate('/coach');
    } catch (err) {
      console.error('Onboarding save error:', err);
      navigate('/coach');
    } finally { setLoading(false); }
  };

  const slideVariants = {
    enter: (d) => ({ opacity: 0, x: d > 0 ? 40 : -40, scale: 0.97 }),
    center: { opacity: 1, x: 0, scale: 1 },
    exit:  (d) => ({ opacity: 0, x: d > 0 ? -40 : 40, scale: 0.97 }),
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative overflow-hidden"
      style={{ background: isDark ? 'var(--color-bg-primary)' : 'var(--color-bg-primary)' }}>

      {/* ── Celestial background SVG ── */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none select-none"
        viewBox="0 0 1200 800" fill="none" preserveAspectRatio="xMidYMid slice"
        style={{ opacity: isDark ? 0.07 : 0.1 }}>
        {/* Constellation lines */}
        <line x1="150" y1="120" x2="340" y2="200" stroke="var(--color-accent)" strokeWidth="0.8"/>
        <line x1="340" y1="200" x2="520" y2="150" stroke="var(--color-accent)" strokeWidth="0.8"/>
        <line x1="520" y1="150" x2="680" y2="280" stroke="var(--color-accent)" strokeWidth="0.8"/>
        <line x1="680" y1="280" x2="900" y2="200" stroke="var(--color-accent)" strokeWidth="0.8"/>
        <line x1="900" y1="200" x2="1050" y2="350" stroke="var(--color-accent)" strokeWidth="0.8"/>
        <line x1="340" y1="200" x2="280" y2="380" stroke="var(--color-accent)" strokeWidth="0.8"/>
        <line x1="680" y1="280" x2="620" y2="480" stroke="var(--color-accent)" strokeWidth="0.8"/>
        <line x1="620" y1="480" x2="820" y2="560" stroke="var(--color-accent)" strokeWidth="0.8"/>
        <line x1="200" y1="580" x2="280" y2="380" stroke="var(--color-accent)" strokeWidth="0.8"/>
        {/* Star nodes */}
        {[[150,120],[340,200],[520,150],[680,280],[900,200],[1050,350],[280,380],[620,480],[820,560],[200,580]].map(([cx,cy],i) => (
          <g key={i}>
            <circle cx={cx} cy={cy} r={[1,4].includes(i) ? 6 : 3.5} fill="var(--color-accent)"/>
            <circle cx={cx} cy={cy} r={[1,4].includes(i) ? 14 : 9} fill="var(--color-accent)" opacity="0.15"/>
          </g>
        ))}
        {/* Diamonds */}
        <path d="M100 400 L108 415 L100 430 L92 415 Z" fill="var(--color-accent)" opacity="0.5"/>
        <path d="M1100 120 L1108 135 L1100 150 L1092 135 Z" fill="var(--color-accent)" opacity="0.45"/>
        <path d="M950 650 L957 663 L950 676 L943 663 Z" fill="var(--color-accent)" opacity="0.4"/>
        {/* Scattered dots */}
        {[[50,200],[400,50],[750,700],[1150,500],[300,700],[850,80],[60,600],[1000,420]].map(([cx,cy],i)=>(
          <circle key={i} cx={cx} cy={cy} r="1.5" fill="var(--color-accent)"/>
        ))}
      </svg>

      {/* Gradient overlay */}
      <div className="absolute inset-0 pointer-events-none" style={{
        background: isDark
          ? 'radial-gradient(ellipse at 50% 40%, rgba(124,58,237,0.08) 0%, transparent 70%)'
          : 'radial-gradient(ellipse at 50% 40%, rgba(201,164,245,0.15) 0%, transparent 70%)',
      }}/>

      <div className="relative w-full max-w-lg z-10">

        {/* ── Header: logo + step counter ── */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M10 1 L12.5 7.5 L19 10 L12.5 12.5 L10 19 L7.5 12.5 L1 10 L7.5 7.5 Z"
                fill="var(--color-accent)" opacity="0.9"/>
            </svg>
            <span className="font-display text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>
              Therapity
            </span>
          </div>
          <span className="text-xs font-medium px-2 py-1 rounded-full"
            style={{ background: 'var(--color-accent-subtle)', color: 'var(--color-text-muted)', border: '1px solid var(--color-border-subtle)', fontFamily: 'var(--font-sans)' }}>
            {step + 1} / {STEPS.length}
          </span>
        </div>

        {/* ── Progress bar ── */}
        <div className="mb-6">
          <div className="h-1 rounded-full overflow-hidden" style={{ background: 'var(--color-border-subtle)' }}>
            <motion.div
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5, ease: 'easeOut' }}
              style={{ height: '100%', background: 'linear-gradient(90deg, var(--color-accent), #FFBFA3)', borderRadius: 99 }}
            />
          </div>
          {/* Step dots */}
          <div className="flex justify-between mt-2">
            {STEPS.map((_, i) => (
              <motion.div key={i}
                animate={{ scale: i === step ? 1.3 : 1 }}
                style={{
                  width: 6, height: 6, borderRadius: '50%',
                  background: i <= step ? 'var(--color-accent)' : 'var(--color-border)',
                  transition: 'background 0.3s',
                }}
              />
            ))}
          </div>
        </div>

        {/* ── Card ── */}
        <div style={{
          background: isDark ? 'rgba(14,10,28,0.88)' : 'rgba(255,250,254,0.9)',
          border: '1px solid var(--color-border)',
          borderRadius: '1.5rem',
          backdropFilter: 'blur(28px)',
          boxShadow: isDark
            ? '0 24px 64px rgba(0,0,0,0.5), 0 0 0 1px rgba(124,58,237,0.2)'
            : '0 24px 64px rgba(139,92,246,0.14), 0 0 0 1px rgba(201,164,245,0.3)',
          overflow: 'hidden',
        }}>

          <AnimatePresence mode="wait" custom={dir}>
            <motion.div key={step}
              custom={dir}
              variants={slideVariants}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.28, ease: 'easeInOut' }}
              style={{ padding: '2rem' }}
            >
              {/* Step emoji + title */}
              <div className="mb-6">
                <motion.div
                  initial={{ scale: 0.5, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: 0.1, type: 'spring', stiffness: 260, damping: 20 }}
                  className="text-3xl mb-3">{current.emoji}
                </motion.div>
                <h2 className="font-display text-xl font-semibold mb-1.5"
                  style={{ color: 'var(--color-text-primary)', lineHeight: 1.3 }}>
                  {current.titleVi}
                </h2>
                <p className="text-sm" style={{ color: 'var(--color-text-muted)', fontFamily: 'var(--font-sans)' }}>
                  {current.subtitleVi}
                </p>
              </div>

              {/* Date input */}
              {current.type === 'date' && (
                <input
                  type="date"
                  value={data[current.key] || ''}
                  onChange={e => setData({ ...data, [current.key]: e.target.value })}
                  style={{
                    width: '100%', padding: '10px 14px',
                    background: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(139,92,246,0.06)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 12, color: 'var(--color-text-primary)',
                    fontFamily: 'var(--font-sans)', fontSize: '0.9rem', outline: 'none',
                    colorScheme: isDark ? 'dark' : 'light',
                  }}
                  onFocus={e => e.currentTarget.style.borderColor = 'var(--color-accent)'}
                  onBlur={e => e.currentTarget.style.borderColor = 'var(--color-border)'}
                />
              )}

              {/* Choice options */}
              {current.options && (
                <div className="flex flex-wrap gap-2">
                  {current.options.map((opt, i) => {
                    const isSelected = current.multi
                      ? (data[current.key] || []).includes(opt)
                      : data[current.key] === opt;
                    return (
                      <motion.button key={opt}
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.04 }}
                        whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.96 }}
                        onClick={() => handleSelect(opt)}
                        style={{
                          padding: '7px 14px',
                          borderRadius: 20,
                          fontSize: '0.84rem',
                          fontFamily: 'var(--font-sans)',
                          fontWeight: 500,
                          cursor: 'pointer',
                          transition: 'all 0.15s',
                          background: isSelected
                            ? 'var(--color-accent)'
                            : (isDark ? 'rgba(255,255,255,0.05)' : 'rgba(139,92,246,0.06)'),
                          color: isSelected ? 'white' : 'var(--color-text-primary)',
                          border: `1.5px solid ${isSelected ? 'var(--color-accent)' : 'var(--color-border)'}`,
                          boxShadow: isSelected ? '0 4px 16px rgba(124,58,237,0.3)' : 'none',
                        }}
                      >
                        {opt}
                      </motion.button>
                    );
                  })}
                </div>
              )}
            </motion.div>
          </AnimatePresence>

          {/* ── Footer: navigation buttons ── */}
          <div className="flex items-center justify-between px-8 py-4"
            style={{ borderTop: '1px solid var(--color-border-subtle)' }}>
            <motion.button
              whileHover={{ scale: step > 0 ? 1.04 : 1 }}
              whileTap={{ scale: step > 0 ? 0.96 : 1 }}
              onClick={goBack}
              disabled={step === 0}
              style={{
                padding: '8px 18px', borderRadius: 20,
                fontFamily: 'var(--font-sans)', fontSize: '0.85rem',
                color: step === 0 ? 'var(--color-text-muted)' : 'var(--color-text-secondary)',
                background: 'transparent',
                border: `1px solid ${step === 0 ? 'transparent' : 'var(--color-border)'}`,
                opacity: step === 0 ? 0.4 : 1,
                cursor: step === 0 ? 'default' : 'pointer',
                transition: 'all 0.15s',
              }}
            >
              ← Quay lại
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.04 }}
              whileTap={{ scale: 0.96 }}
              onClick={goNext}
              disabled={loading}
              style={{
                padding: '9px 22px', borderRadius: 20,
                background: loading ? 'var(--color-border)' : 'var(--color-accent)',
                color: 'white',
                fontFamily: 'var(--font-sans)', fontSize: '0.88rem', fontWeight: 600,
                border: 'none', cursor: loading ? 'wait' : 'pointer',
                boxShadow: loading ? 'none' : '0 6px 20px rgba(124,58,237,0.35)',
                transition: 'all 0.15s',
                display: 'flex', alignItems: 'center', gap: 6,
              }}
            >
              {loading ? (
                <>
                  <motion.span animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}>
                    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="white" strokeWidth="1.5" strokeLinecap="round">
                      <path d="M7 1.5 A5.5 5.5 0 1 1 1.5 7"/>
                    </svg>
                  </motion.span>
                  Đang lưu…
                </>
              ) : step === STEPS.length - 1 ? (
                'Bắt đầu hành trình ✦'
              ) : (
                'Tiếp theo →'
              )}
            </motion.button>
          </div>
        </div>

        {/* ── Skip link ── */}
        <motion.button
          whileHover={{ opacity: 1 }}
          onClick={() => navigate('/coach')}
          className="mt-5 w-full text-center text-sm"
          style={{ color: 'var(--color-text-muted)', fontFamily: 'var(--font-sans)', opacity: 0.6, transition: 'opacity 0.15s' }}
        >
          Bỏ qua, tôi sẽ khám phá sau →
        </motion.button>
      </div>
    </div>
  );
}
