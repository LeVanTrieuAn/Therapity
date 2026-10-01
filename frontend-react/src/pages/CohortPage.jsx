/**
 * Therapity — CohortPage (Roadmap)
 *
 * 12-week personalized learning roadmap with:
 *  - Context verification (pre-enrollment)
 *  - Overview tab: progress chart + donut
 *  - Roadmap tab: timeline + personal tasks + quiz
 *
 * Design: DESIGN_SYSTEM.md — Cormorant Garamond / DM Sans
 * Colors: var(--color-*) tokens, accent lavender, geometric SVG icons
 * Animations: Framer Motion
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import useAuthStore from '../store/authStore';
import useThemeStore from '../store/themeStore';
import { cohortAPI, chatAPI } from '../services/api';

/* ══════════════════════════════════════════════════════════════
   SVG ICONS — geometric, Design-System-aligned
   ══════════════════════════════════════════════════════════════ */
const Icon = {
  compass: (
    <svg width="18" height="18" viewBox="0 0 20 20" fill="none">
      <circle cx="10" cy="10" r="8.5" stroke="currentColor" strokeWidth="1.2"/>
      <polygon points="10,3 12,10 10,17 8,10" fill="currentColor" opacity="0.7"/>
      <circle cx="10" cy="10" r="1.5" fill="currentColor"/>
    </svg>
  ),
  lock: (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.2">
      <rect x="3" y="6" width="8" height="6" rx="1.5"/>
      <path d="M5 6V4.5a2 2 0 0 1 4 0V6"/>
    </svg>
  ),
  check: (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round">
      <path d="M3.5 7.5 L6 10 L10.5 4.5"/>
    </svg>
  ),
  play: (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="currentColor">
      <polygon points="4,2 12,7 4,12"/>
    </svg>
  ),
  star: (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
      <path d="M8 1 L9.2 6.8 L15 8 L9.2 9.2 L8 15 L6.8 9.2 L1 8 L6.8 6.8 Z" opacity="0.8"/>
    </svg>
  ),
  quiz: (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.2">
      <circle cx="7" cy="7" r="5.5"/>
      <path d="M5.5 5.5a1.5 1.5 0 0 1 3 0c0 .8-.7 1-1.5 1.5V9" strokeLinecap="round"/>
      <circle cx="7" cy="10.5" r="0.5" fill="currentColor"/>
    </svg>
  ),
  expand: (
    <svg width="10" height="10" viewBox="0 0 10 10" fill="currentColor">
      <path d="M3 4L5 6.5L7 4"/>
    </svg>
  ),
};

/* ── Background SVG — hidden constellation ──────────────────── */
function SceneBg() {
  return (
    <svg className="scene-bg-element" viewBox="0 0 600 400" fill="none" style={{
      position: 'absolute', top: 0, left: 0, width: '100%', height: '100%',
      opacity: 0.04, pointerEvents: 'none', zIndex: 0,
    }}>
      {/* Upward triangle — roadmap symbol */}
      <polygon points="300,50 450,300 150,300" stroke="currentColor" strokeWidth="1" fill="none" opacity="0.6"/>
      <polygon points="300,120 380,280 220,280" stroke="currentColor" strokeWidth="0.6" fill="none" opacity="0.4"/>
      {/* Constellation dots */}
      {[[100,80],[200,60],[350,90],[480,70],[150,350],[400,320],[250,380],[500,350]].map(([x,y],i)=>(
        <circle key={i} cx={x} cy={y} r="2" fill="currentColor" opacity="0.5"/>
      ))}
      {/* Connecting lines */}
      <line x1="100" y1="80" x2="200" y2="60" stroke="currentColor" strokeWidth="0.4" opacity="0.3"/>
      <line x1="200" y1="60" x2="350" y2="90" stroke="currentColor" strokeWidth="0.4" opacity="0.3"/>
      <line x1="350" y1="90" x2="480" y2="70" stroke="currentColor" strokeWidth="0.4" opacity="0.3"/>
      {/* Circular orbit */}
      <circle cx="300" cy="200" r="120" stroke="currentColor" strokeWidth="0.5" fill="none" opacity="0.2" strokeDasharray="4 6"/>
    </svg>
  );
}

/* ── Progress Donut ─────────────────────────────────────────── */
function ProgressDonut({ progress, week, lang }) {
  const r = 40, C = 2 * Math.PI * r;
  const offset = C * (1 - progress / 100);
  return (
    <div className="relative" style={{ width: 140, height: 140 }}>
      <svg className="w-full h-full" viewBox="0 0 100 100" style={{ transform: 'rotate(-90deg)' }}>
        <circle cx="50" cy="50" r={r} stroke="var(--color-border)" strokeWidth="7" fill="transparent"/>
        <circle cx="50" cy="50" r={r} stroke="var(--color-accent)" strokeWidth="7" fill="transparent"
          strokeDasharray={C} strokeDashoffset={offset} strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.7s ease' }}/>
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-display text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>{progress}%</span>
        <span className="text-[10px] font-bold tracking-widest uppercase" style={{ color: 'var(--color-accent)' }}>
          {lang === 'en' ? `Week ${week}` : `Tuần ${week}`}
        </span>
      </div>
    </div>
  );
}

/* ── Progress Chart (12 weeks) ──────────────────────────────── */
function ProgressChart({ data, currentWeek, lang }) {
  const w = 500, h = 180, padX = 40, padY = 20;
  const chartW = w - padX * 2, chartH = h - padY * 2;
  const step = chartW / 11;

  const points = data.map((v, i) => {
    const x = padX + i * step;
    const y = h - padY - (v / 100) * chartH;
    return { x, y, v };
  });

  const lineStr = points.map(p => `${p.x},${p.y}`).join(' ');
  const areaStr = `${padX},${h-padY} ${lineStr} ${padX + 11*step},${h-padY}`;

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full" style={{ maxHeight: 200 }}>
      <defs>
        <linearGradient id="chart-grad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="var(--color-accent)" stopOpacity="0.25"/>
          <stop offset="100%" stopColor="var(--color-accent)" stopOpacity="0"/>
        </linearGradient>
      </defs>
      {/* Grid */}
      {[0,25,50,75,100].map((v,i)=>{
        const y = h - padY - (v/100)*chartH;
        return <g key={i}>
          <line x1={padX} y1={y} x2={w-padX} y2={y} stroke="var(--color-border)" strokeWidth="0.5" strokeDasharray="3 3"/>
          <text x={padX-6} y={y+3} fontSize="7" textAnchor="end" fill="var(--color-text-muted)" fontFamily="DM Sans">{v}%</text>
        </g>;
      })}
      {/* X labels */}
      {points.map((p,i) => (
        <text key={i} x={p.x} y={h-4} fontSize="7" textAnchor="middle" fill="var(--color-text-muted)" fontFamily="DM Sans">
          {lang === 'en' ? `W${i+1}` : `T${i+1}`}
        </text>
      ))}
      {/* Area + Line */}
      <polygon points={areaStr} fill="url(#chart-grad)"/>
      <polyline points={lineStr} fill="none" stroke="var(--color-accent)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
      {/* Dots */}
      {points.map((p,i) => (
        <g key={i}>
          {i+1 === currentWeek && <circle cx={p.x} cy={p.y} r="7" fill="var(--color-accent)" opacity="0.25" className="animate-breathe"/>}
          <circle cx={p.x} cy={p.y} r="4"
            fill={i+1 === currentWeek ? 'var(--color-accent)' : i+1 < currentWeek ? 'var(--color-success)' : 'var(--color-border)'}
            stroke={i+1 === currentWeek ? 'var(--color-bg-primary)' : 'none'} strokeWidth="1.5"/>
        </g>
      ))}
    </svg>
  );
}

/* ══════════════════════════════════════════════════════════════
   MAIN — CohortPage
   ══════════════════════════════════════════════════════════════ */
export default function CohortPage() {
  const { user } = useAuthStore();
  const { theme, lang } = useThemeStore();
  const username = user?.username || 'user';

  // State
  const [pageLoading, setPageLoading] = useState(true);
  const [isEnrolled, setIsEnrolled] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');
  const [contextCheck, setContextCheck] = useState({ loaded: false, count: 0, isSufficient: false });
  const [joiningLoading, setJoiningLoading] = useState(false);
  const [matchingProgress, setMatchingProgress] = useState(0);
  const [matchingStatus, setMatchingStatus] = useState('');

  // Data
  const [syllabus, setSyllabus] = useState([]);
  const [cohortInfo, setCohortInfo] = useState({});
  const [members, setMembers] = useState([]);
  const [cohortTasks, setCohortTasks] = useState([]);
  const [selectedWeek, setSelectedWeek] = useState(1);
  const [expandedTaskId, setExpandedTaskId] = useState(null);
  const [weeklyProgress, setWeeklyProgress] = useState(Array(12).fill(0));

  // Quiz
  const [quizData, setQuizData] = useState(null);
  const [quizResult, setQuizResult] = useState(null);
  const [userAnswers, setUserAnswers] = useState(Array(8).fill(null));
  const [quizLoading, setQuizLoading] = useState(false);
  const [quizSubmitting, setQuizSubmitting] = useState(false);

  // Personalizing
  const [personalizingLoading, setPersonalizingLoading] = useState(false);

  const isEn = lang === 'en';

  /* ── helper: clean markdown cruft ────────────────────────── */
  const clean = (s) => (s || '').replace(/^\*+\s*/gm, '').replace(/\*+/g, '').trim();

  /* ── Load all data ──────────────────────────────────────── */
  const loadAll = useCallback(async (week) => {
    try {
      const w = week || selectedWeek || 1;
      const [syllRes, tasksRes] = await Promise.all([
        cohortAPI.getSyllabus(username, w),
        cohortAPI.getTasks(username),
      ]);
      const syll = syllRes.data;
      setSyllabus(syll.syllabus || []);
      setCohortInfo(syll.cohort_info || {});
      setCohortTasks(tasksRes.data || []);

      // Members — declared outside inner try so hasSelf check can access it
      let rawMembers = [];
      try {
        const membRes = await cohortAPI.getMembers();
        rawMembers = membRes.data.members || [];
        rawMembers.forEach(mem => {
          const memUser = (mem.username || '').toLowerCase();
          if (mem.is_self || memUser === username.toLowerCase()) {
            mem.is_self = true;
            mem.display_name = user?.displayName || username;
          }
        });
        setMembers(rawMembers);
      } catch { setMembers([]); }

      // Build weekly progress from localStorage + server
      const history = JSON.parse(localStorage.getItem(`therapity_cohort_progress_${username}`) || '{}');
      if (syll.cohort_info?.weekly_progress_history) {
        Object.entries(syll.cohort_info.weekly_progress_history).forEach(([wk, val]) => {
          history[wk] = Math.max(Number(val || 0), Number(history[wk] || 0));
        });
        localStorage.setItem(`therapity_cohort_progress_${username}`, JSON.stringify(history));
      }
      const currentW = syll.cohort_info?.current_week || 1;
      const list = [];
      for (let i = 1; i <= 12; i++) {
        if (i < currentW) list.push(Number(history[i] || history[String(i)] || 100));
        else if (i === currentW) list.push(Number(history[i] || history[String(i)] || 0));
        else list.push(0);
      }
      setWeeklyProgress(list);

      // Extract quiz from core task
      const weekTasks = (tasksRes.data || []).filter(t => t.week === w);
      const coreTask = weekTasks.find(t => t.type === 'core');
      if (coreTask?.quiz?.questions) {
        setQuizData(coreTask.quiz);
        const attempt = coreTask.quiz.attempts?.length > 0
          ? coreTask.quiz.attempts[coreTask.quiz.attempts.length - 1] : null;
        if (attempt) {
          setQuizResult(attempt);
          setUserAnswers(attempt.answers ? [...attempt.answers] : Array(8).fill(null));
        }
      } else {
        setQuizData(null);
      }

      // Determine enrollment
      const hasSelf = rawMembers.some(mem =>
        mem.is_self || (mem.username || '').toLowerCase() === username.toLowerCase()
      );
      if (hasSelf || localStorage.getItem(`therapity_cohort_activated_${username}`) === 'true') {
        setIsEnrolled(true);
      } else {
        setIsEnrolled(false);
        // Check dialogue context
        try {
          const checkRes = await cohortAPI.checkContext(username);
          setContextCheck({ loaded: true, count: checkRes.data.prompt_count || 0, isSufficient: checkRes.data.is_sufficient || false });
        } catch { setContextCheck({ loaded: true, count: 0, isSufficient: false }); }
      }
    } catch (e) {
      console.error('loadAll error', e);
    }
  }, [username, selectedWeek, user]);

  /* ── Init ───────────────────────────────────────────────── */
  useEffect(() => {
    (async () => {
      setPageLoading(true);
      await loadAll(1);
      const cw = cohortInfo.current_week || 1;
      setSelectedWeek(cw);
      await loadAll(cw);
      setTimeout(() => setPageLoading(false), 400);
    })();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  /* ── On week change ─────────────────────────────────────── */
  useEffect(() => {
    if (!pageLoading) {
      (async () => {
        setPageLoading(true);
        setQuizData(null); setQuizResult(null); setUserAnswers(Array(8).fill(null));
        await loadAll(selectedWeek);
        setTimeout(() => setPageLoading(false), 300);
      })();
    }
  }, [selectedWeek]); // eslint-disable-line react-hooks/exhaustive-deps

  const currentWeek = cohortInfo.current_week || 1;
  const selfMember = members.find(m => m.is_self);
  const selfProgress = selfMember?.week_progress || 0;

  /* ── Join / AI Allocation ────────────────────────────────── */
  const handleJoin = async () => {
    setJoiningLoading(true);
    setMatchingProgress(5);
    const statuses = isEn
      ? ["Ingesting Socratic dialogue history...", "Mapping cognitive ruptures...", "Analyzing personal goals...", "Synthesizing cognitive patterns...", "Populating personalized tasks...", "Welcome to your Personal Roadmap!"]
      : ["Đọc hiểu lịch sử hội thoại...", "Lập bản đồ đứt gãy nhận thức...", "Phân tích mục tiêu cá nhân...", "Kiến tạo mô thức phát triển...", "Đồng bộ hóa nhiệm vụ...", "Lộ trình cá nhân đã sẵn sàng!"];
    let progress = 5;
    const iv = setInterval(() => {
      if (progress < 95) {
        progress += Math.floor(Math.random() * 15) + 5;
        if (progress > 95) progress = 95;
        setMatchingProgress(progress);
        const idx = Math.floor((progress / 100) * statuses.length);
        setMatchingStatus(statuses[idx] || statuses[statuses.length - 1]);
      }
    }, 600);
    try {
      const res = await cohortAPI.join({
        username, display_name: user?.displayName || username, current_tasks: cohortTasks,
      });
      if (res.data.status === 'insufficient_info') {
        clearInterval(iv); setJoiningLoading(false);
        return;
      }
      localStorage.setItem(`therapity_cohort_activated_${username}`, 'true');
      setTimeout(async () => {
        clearInterval(iv); setMatchingProgress(100);
        setMatchingStatus(statuses[statuses.length - 1]);
        setTimeout(async () => {
          await loadAll(); setIsEnrolled(true); setJoiningLoading(false);
        }, 800);
      }, 3500);
    } catch (e) {
      clearInterval(iv); setJoiningLoading(false);
    }
  };

  /* ── Start learning a week ──────────────────────────────── */
  const startLearningWeek = async (weekNum) => {
    const weekTasks = cohortTasks.filter(t => t.week === weekNum);
    if (weekTasks.length > 0) {
      setSelectedWeek(weekNum); return;
    }
    setPersonalizingLoading(true);
    try {
      await cohortAPI.personalizeWeek({ username, week: weekNum, lang });
      await loadAll(weekNum);
      setSelectedWeek(weekNum);
    } catch (e) { console.error('Personalize error', e); }
    finally { setPersonalizingLoading(false); }
  };

  /* ── Toggle task done ───────────────────────────────────── */
  const toggleTask = async (task) => {
    const newStatus = task.status === 'done' ? 'backlog' : 'done';
    task.status = newStatus;
    setCohortTasks([...cohortTasks]);
    try {
      await cohortAPI.patchTask(task.id, { status: newStatus, subtasks: task.subtasks });
    } catch (e) { console.error(e); }
  };

  /* ── Save essay ─────────────────────────────────────────── */
  const saveEssay = async (task) => {
    try {
      await cohortAPI.patchTask(task.id, { status: task.status, subtasks: task.subtasks, essay: task.essay });
    } catch (e) { console.error(e); }
  };

  /* ── Quiz ───────────────────────────────────────────────── */
  const generateQuiz = async () => {
    setQuizLoading(true);
    try {
      const res = await cohortAPI.generateQuiz({ username, week: selectedWeek, lang });
      setQuizData(res.data); setUserAnswers(Array(8).fill(null)); setQuizResult(null);
    } catch (e) { console.error(e); }
    finally { setQuizLoading(false); }
  };

  const submitQuiz = async () => {
    if (userAnswers.includes(null)) return;
    setQuizSubmitting(true);
    try {
      const res = await cohortAPI.submitQuiz({ username, week: selectedWeek, answers: userAnswers, lang });
      setQuizResult(res.data.attempt || res.data);
      await loadAll(selectedWeek);
    } catch (e) { console.error(e); }
    finally { setQuizSubmitting(false); }
  };

  /* ── Filtered tasks for selected week ───────────────────── */
  const weekTasks = cohortTasks.filter(t => t.week === selectedWeek);

  /* ══════════════════════════════════════════════════════════════
     RENDER
     ══════════════════════════════════════════════════════════════ */
  return (
    <div className="relative min-h-full" style={{ color: 'var(--color-text-primary)' }}>
      <SceneBg/>

      {/* Page loading overlay */}
      <AnimatePresence>
        {pageLoading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center"
            style={{ background: 'var(--color-bg-primary)', opacity: 0.85 }}>
            <div className="glass-card p-8 flex flex-col items-center gap-4 text-center max-w-xs">
              <motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}>
                {Icon.compass}
              </motion.div>
              <p className="text-xs font-bold uppercase tracking-widest" style={{ color: 'var(--color-accent)' }}>
                {isEn ? 'SYNCING ROADMAP...' : 'ĐỒNG BỘ LỘ TRÌNH...'}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }} className="relative z-10 mb-6">
        <h1 className="font-display text-3xl font-semibold" style={{ color: 'var(--color-text-primary)' }}>
          {isEn ? 'Learning Roadmap' : 'Lộ Trình Học Tập'}
        </h1>
        <p className="text-sm mt-1" style={{ color: 'var(--color-text-muted)' }}>
          {isEn ? 'Unlearn → Relearn → Execute — 12-week personalized program' : 'Phá bỏ → Tái thiết → Vận hành — Chương trình 12 tuần cá nhân hóa'}
        </p>
      </motion.div>

      {/* ══════════════════════════════════════════════════════════
         UNENROLLED — Context Verification
         ══════════════════════════════════════════════════════════ */}
      {!isEnrolled && !pageLoading && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="relative z-10">

          {/* Joining loading overlay */}
          <AnimatePresence>
            {joiningLoading && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="fixed inset-0 z-50 flex items-center justify-center" style={{ background: 'rgba(0,0,0,0.6)' }}>
                <div className="glass-card p-8 max-w-sm text-center flex flex-col items-center gap-4">
                  <motion.div animate={{ rotate: 360 }} transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}>
                    {Icon.compass}
                  </motion.div>
                  {/* Progress bar */}
                  <div className="w-full h-2 rounded-full" style={{ background: 'var(--color-bg-secondary)' }}>
                    <motion.div className="h-full rounded-full" style={{ background: 'var(--color-accent)', width: `${matchingProgress}%` }}
                      transition={{ duration: 0.3 }}/>
                  </div>
                  <p className="text-xs font-medium" style={{ color: 'var(--color-text-muted)' }}>{matchingStatus}</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="glass-card p-8 max-w-2xl mx-auto text-center relative overflow-hidden">
            {/* Decorative orbs */}
            <div className="absolute -top-16 -right-16 w-40 h-40 rounded-full pointer-events-none" style={{ background: 'var(--color-accent)', opacity: 0.04 }}/>
            <div className="absolute -bottom-16 -left-16 w-32 h-32 rounded-full pointer-events-none" style={{ background: 'var(--color-accent)', opacity: 0.03 }}/>

            <div className="relative z-10">
              {/* Icon */}
              <div className="w-14 h-14 mx-auto rounded-full flex items-center justify-center mb-4"
                style={{ background: 'var(--color-accent-subtle)', border: '1px solid var(--color-border)' }}>
                <span style={{ color: 'var(--color-accent)' }}>{Icon.compass}</span>
              </div>

              <h2 className="font-display text-2xl font-semibold mb-2">
                {isEn ? 'Verify Socratic Dialogue Context' : 'Xác thực Bối cảnh Đối thoại Socratic'}
              </h2>
              <p className="text-sm mb-6 max-w-lg mx-auto" style={{ color: 'var(--color-text-muted)' }}>
                {isEn ? 'Complete 10 conversational turns with the Coach so we can discover the cognitive barriers holding you back.'
                       : 'Hoàn thành 10 lượt trò chuyện với AI Coach để khám phá những rào cản nhận thức đang giữ chân bạn.'}
              </p>

              {/* Context progress widget */}
              <div className="p-4 rounded-xl mb-6 text-left max-w-md mx-auto"
                style={{ background: 'var(--color-bg-secondary)', border: '1px solid var(--color-border)' }}>
                {!contextCheck.loaded ? (
                  <div className="animate-pulse flex flex-col gap-2">
                    <div className="h-3 rounded w-2/3" style={{ background: 'var(--color-border)' }}/>
                    <div className="h-2 rounded w-full" style={{ background: 'var(--color-border)' }}/>
                  </div>
                ) : (
                  <>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] font-bold uppercase tracking-widest" style={{ color: 'var(--color-text-muted)' }}>
                        {isEn ? 'DIALOGUE ELIGIBILITY' : 'TRẠNG THÁI'}
                      </span>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded" style={{
                        background: contextCheck.isSufficient ? 'rgba(109,185,123,0.15)' : 'rgba(245,158,11,0.15)',
                        color: contextCheck.isSufficient ? 'var(--color-success)' : '#f59e0b',
                      }}>
                        {contextCheck.isSufficient ? (isEn ? 'READY' : 'ĐỦ') : (isEn ? 'PENDING' : 'CHƯA ĐỦ')}
                      </span>
                    </div>
                    <p className="text-xs mb-3" style={{ color: 'var(--color-text-secondary)' }}>
                      {contextCheck.isSufficient
                        ? (isEn ? 'Perfect! AI is ready to allocate your roadmap.' : 'Tuyệt vời! AI đã sẵn sàng phân bổ lộ trình.')
                        : (isEn ? `${contextCheck.count}/10 exchanges completed. Chat more to unlock.` : `${contextCheck.count}/10 lượt. Trò chuyện thêm để mở khóa.`)}
                    </p>
                    <div className="h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--color-border)' }}>
                      <div className="h-full rounded-full transition-all duration-700" style={{
                        width: `${Math.min((contextCheck.count / 10) * 100, 100)}%`,
                        background: contextCheck.isSufficient ? 'var(--color-success)' : '#f59e0b',
                      }}/>
                    </div>
                  </>
                )}
              </div>

              {/* What's included */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6 max-w-lg mx-auto text-left">
                {[
                  { icon: Icon.compass, title: isEn ? 'Personalized 12-Week Roadmap' : 'Lộ trình 12 tuần cá nhân hóa', sub: isEn ? 'Tailored by AI based on your data' : 'AI thiết kế riêng cho bạn' },
                  { icon: Icon.check, title: isEn ? 'Weekly Tasks' : 'Nhiệm vụ hàng tuần', sub: isEn ? 'Practical exercises for self-understanding' : 'Bài tập hiểu bản thân' },
                  { icon: Icon.quiz, title: isEn ? 'Visual Quizzes' : 'Trắc nghiệm trực quan', sub: isEn ? 'Test your self-understanding' : 'Kiểm tra mức thấu hiểu' },
                  { icon: Icon.star, title: isEn ? 'Learning Progress' : 'Tiến độ học tập', sub: isEn ? 'Track your growth' : 'Theo dõi sự phát triển' },
                ].map((item, i) => (
                  <motion.div key={i} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 * i }}
                    className="p-3 rounded-xl flex items-start gap-3"
                    style={{ background: 'var(--color-bg-primary)', border: '1px solid var(--color-border)' }}>
                    <span style={{ color: 'var(--color-accent)' }}>{item.icon}</span>
                    <div>
                      <p className="text-xs font-bold" style={{ color: 'var(--color-text-primary)' }}>{item.title}</p>
                      <p className="text-[11px]" style={{ color: 'var(--color-text-muted)' }}>{item.sub}</p>
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* Join button */}
              <button onClick={handleJoin}
                disabled={!contextCheck.isSufficient || joiningLoading}
                className="btn-primary px-8 py-3 text-sm font-bold"
                style={{ opacity: contextCheck.isSufficient ? 1 : 0.5 }}>
                {isEn ? 'Activate AI Roadmap' : 'Kích hoạt Lộ trình AI'}
              </button>
            </div>
          </div>
        </motion.div>
      )}

      {/* ══════════════════════════════════════════════════════════
         ENROLLED — Main Dashboard
         ══════════════════════════════════════════════════════════ */}
      {isEnrolled && !pageLoading && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="relative z-10 flex flex-col gap-6">

          {/* Tab bar */}
          <div className="flex gap-1 p-1 rounded-xl w-fit" style={{ background: 'var(--color-bg-secondary)' }}>
            {[['overview', isEn ? 'Overview' : 'Tổng quan'], ['roadmap', isEn ? 'Roadmap' : 'Lộ trình']].map(([key, label]) => (
              <button key={key} onClick={() => setActiveTab(key)}
                className="px-5 py-2 text-xs font-bold rounded-lg transition-all"
                style={{
                  background: activeTab === key ? 'var(--color-accent)' : 'transparent',
                  color: activeTab === key ? 'white' : 'var(--color-text-muted)',
                  boxShadow: activeTab === key ? '0 2px 8px var(--color-shadow-strong)' : 'none',
                }}>
                {label}
              </button>
            ))}
          </div>

          {/* ── TAB: OVERVIEW ───────────────────────────────── */}
          {activeTab === 'overview' && (
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Chart */}
              <div className="lg:col-span-2 glass-card p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="font-display text-lg font-semibold">{isEn ? 'Weekly Progress' : 'Tiến độ hàng tuần'}</h3>
                    <p className="text-xs" style={{ color: 'var(--color-text-muted)' }}>
                      {isEn ? '12-week learning journey' : 'Hành trình 12 tuần'}
                    </p>
                  </div>
                  <div className="flex items-center gap-4 text-[10px]" style={{ color: 'var(--color-text-muted)' }}>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{ background: 'var(--color-success)' }}/> {isEn ? 'Completed' : 'Đã xong'}</span>
                    <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full animate-breathe" style={{ background: 'var(--color-accent)' }}/> {isEn ? 'Current' : 'Hiện tại'}</span>
                  </div>
                </div>
                <ProgressChart data={weeklyProgress} currentWeek={currentWeek} lang={lang}/>
              </div>
              {/* Donut */}
              <div className="glass-card p-6 flex flex-col items-center justify-center">
                <h3 className="text-xs font-bold uppercase tracking-widest mb-4" style={{ color: 'var(--color-text-muted)' }}>
                  {isEn ? 'Your Progress' : 'Tiến độ của bạn'}
                </h3>
                <ProgressDonut progress={selfProgress} week={currentWeek} lang={lang}/>
                <p className="text-[11px] mt-4 text-center px-4" style={{ color: 'var(--color-text-muted)' }}>
                  {isEn ? 'Based on quiz scores and reflection.' : 'Dựa trên điểm trắc nghiệm và chiêm nghiệm.'}
                </p>
              </div>
            </motion.div>
          )}

          {/* ── TAB: ROADMAP ───────────────────────────────── */}
          {activeTab === 'roadmap' && (
            <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
              className="grid grid-cols-1 lg:grid-cols-2 gap-6">

              {/* Left: 12-Week Timeline */}
              <div className="glass-card p-6 flex flex-col">
                <h3 className="font-display text-lg font-semibold mb-1">{isEn ? '12-Week Timeline' : 'Lộ trình 12 Tuần'}</h3>
                <p className="text-xs mb-4" style={{ color: 'var(--color-text-muted)' }}>
                  {isEn ? 'Unlock weekly Socratic challenges' : 'Mở khóa thử thách hàng tuần'}
                </p>
                <div className="flex flex-col gap-3 overflow-y-auto pr-1" style={{ maxHeight: 520 }}>
                  {syllabus.map(weekObj => {
                    const isCurrent = weekObj.week === currentWeek;
                    const isPast = weekObj.week < currentWeek;
                    const isFuture = weekObj.week > currentWeek;
                    return (
                      <motion.div key={weekObj.week} whileHover={{ scale: 1.005 }}
                        className="p-4 rounded-xl transition-all flex items-start gap-3"
                        style={{
                          border: `1px solid ${isCurrent ? 'var(--color-accent)' : 'var(--color-border)'}`,
                          background: isCurrent ? 'var(--color-accent-subtle)' : 'var(--color-bg-secondary)',
                          opacity: isFuture ? 0.5 : 1,
                        }}>
                        {/* Status icon */}
                        <div className="w-9 h-9 rounded-full flex items-center justify-center shrink-0" style={{
                          background: isCurrent ? 'var(--color-accent-subtle)' : isPast ? 'rgba(109,185,123,0.15)' : 'var(--color-bg-primary)',
                          color: isCurrent ? 'var(--color-accent)' : isPast ? 'var(--color-success)' : 'var(--color-text-muted)',
                        }}>
                          {isPast ? Icon.check : isFuture ? Icon.lock : (
                            <motion.span animate={{ rotate: 360 }} transition={{ duration: 4, repeat: Infinity, ease: 'linear' }}>
                              {Icon.compass}
                            </motion.span>
                          )}
                        </div>
                        {/* Content */}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-0.5">
                            <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color: 'var(--color-accent)' }}>
                              {isEn ? `Week ${weekObj.week}` : `Tuần ${weekObj.week}`}
                            </span>
                            {isCurrent && (
                              <span className="px-1.5 py-0.5 rounded text-[9px] font-bold"
                                style={{ background: 'var(--color-accent)', color: 'white' }}>
                                {isEn ? 'ACTIVE' : 'HIỆN TẠI'}
                              </span>
                            )}
                            {isPast && <span className="text-[10px]" style={{ color: 'var(--color-success)' }}>{isEn ? 'Done' : 'Xong'}</span>}
                          </div>
                          <h4 className="text-sm font-bold truncate">{clean(weekObj.title)}</h4>
                          <p className="text-xs truncate" style={{ color: 'var(--color-text-muted)' }}>{clean(weekObj.description)}</p>
                        </div>
                        {/* Action */}
                        <div className="shrink-0">
                          {isCurrent && (
                            <button onClick={() => startLearningWeek(weekObj.week)} disabled={personalizingLoading}
                              className="btn-primary text-[11px] px-3 py-1.5 flex items-center gap-1">
                              {Icon.play} {isEn ? 'Learn' : 'Học'}
                            </button>
                          )}
                          {isFuture && (
                            <span className="flex items-center gap-1 text-[10px] px-3 py-1.5 rounded-lg"
                              style={{ background: 'var(--color-bg-primary)', color: 'var(--color-text-muted)', border: '1px solid var(--color-border)' }}>
                              {Icon.lock} {isEn ? 'Locked' : 'Khóa'}
                            </span>
                          )}
                          {isPast && (
                            <button onClick={() => setSelectedWeek(weekObj.week)}
                              className="btn-ghost text-[11px] px-3 py-1.5 flex items-center gap-1"
                              style={{ color: 'var(--color-text-muted)', border: '1px solid var(--color-border)' }}>
                              {Icon.check} {isEn ? 'Review' : 'Xem lại'}
                            </button>
                          )}
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              </div>

              {/* Right: Personal Tasks + Quiz */}
              <div className="flex flex-col gap-6">
                {/* Tasks */}
                <div className="glass-card p-6">
                  <h3 className="font-display text-lg font-semibold mb-1">{isEn ? 'Personal Tasks' : 'Nhiệm vụ cá nhân'}</h3>
                  <p className="text-xs mb-4" style={{ color: 'var(--color-text-muted)' }}>
                    {isEn ? `Week ${selectedWeek} Socratic actions` : `Nhiệm vụ Tuần ${selectedWeek}`}
                  </p>
                  {weekTasks.length === 0 ? (
                    <div className="text-center py-8">
                      <p className="text-sm" style={{ color: 'var(--color-text-muted)' }}>
                        {isEn ? 'No tasks yet. Click "Learn" to generate.' : 'Chưa có nhiệm vụ. Bấm "Học" để tạo.'}
                      </p>
                    </div>
                  ) : (
                    <div className="flex flex-col gap-3 overflow-y-auto pr-1" style={{ maxHeight: 400 }}>
                      {weekTasks.map(task => (
                        <div key={task.id}>
                          <motion.div whileHover={{ scale: 1.005 }}
                            className="p-3 rounded-xl cursor-pointer flex items-center gap-3 transition-all"
                            style={{
                              background: 'var(--color-bg-secondary)',
                              border: `1px solid var(--color-border)`,
                              borderLeft: `3px solid ${task.type === 'core' ? 'var(--color-accent)' : 'var(--color-border)'}`,
                              opacity: task.status === 'done' ? 0.65 : 1,
                            }}
                            onClick={() => setExpandedTaskId(expandedTaskId === task.id ? null : task.id)}>
                            {/* Checkbox */}
                            <button onClick={(e) => { e.stopPropagation(); toggleTask(task); }}
                              className="w-5 h-5 rounded-md flex items-center justify-center shrink-0 transition-colors"
                              style={{
                                border: `1.5px solid ${task.status === 'done' ? 'var(--color-success)' : 'var(--color-border)'}`,
                                background: task.status === 'done' ? 'rgba(109,185,123,0.15)' : 'transparent',
                                color: task.status === 'done' ? 'var(--color-success)' : 'transparent',
                              }}>
                              {Icon.check}
                            </button>
                            <div className="flex-1 min-w-0">
                              <span className="text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded"
                                style={{
                                  background: task.type === 'core' ? 'var(--color-accent-subtle)' : 'var(--color-bg-primary)',
                                  color: task.type === 'core' ? 'var(--color-accent)' : 'var(--color-text-muted)',
                                }}>
                                {task.type === 'core' ? (isEn ? 'CORE' : 'CỐT LÕI') : (isEn ? 'SUPPLEMENTARY' : 'BỔ TRỢ')}
                              </span>
                              <h4 className="text-sm font-bold mt-1 truncate" style={{ textDecoration: task.status === 'done' ? 'line-through' : 'none' }}>
                                {clean(task.title)}
                              </h4>
                              <p className="text-xs truncate" style={{ color: 'var(--color-text-muted)' }}>{clean(task.goal)}</p>
                            </div>
                            <span className="transition-transform" style={{
                              transform: expandedTaskId === task.id ? 'rotate(180deg)' : 'rotate(0)',
                              color: expandedTaskId === task.id ? 'var(--color-accent)' : 'var(--color-text-muted)',
                            }}>{Icon.expand}</span>
                          </motion.div>

                          {/* Expanded details */}
                          <AnimatePresence>
                            {expandedTaskId === task.id && (
                              <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
                                <div className="p-4 rounded-xl mt-1" style={{ background: 'var(--color-bg-secondary)', border: '1px solid var(--color-border)' }}>
                                  <table className="w-full text-left text-xs">
                                    <tbody style={{ color: 'var(--color-text-secondary)' }}>
                                      <tr className="border-b" style={{ borderColor: 'var(--color-border)' }}>
                                        <td className="py-2 font-bold w-1/3">{isEn ? 'Description' : 'Mô tả'}</td>
                                        <td className="py-2 whitespace-pre-line">{clean(task.goal)}</td>
                                      </tr>
                                      <tr className="border-b" style={{ borderColor: 'var(--color-border)' }}>
                                        <td className="py-2 font-bold">{isEn ? 'Effort' : 'Thời gian'}</td>
                                        <td className="py-2">{task.effort} {isEn ? 'hours' : 'giờ'}</td>
                                      </tr>
                                    </tbody>
                                  </table>
                                  {/* Essay */}
                                  <div className="mt-3 pt-3" style={{ borderTop: '1px solid var(--color-border)' }}>
                                    <label className="text-[10px] font-bold uppercase tracking-wider flex items-center gap-1 mb-2"
                                      style={{ color: 'var(--color-accent)' }}>
                                      {Icon.star} {isEn ? 'Socratic Reflection Essay' : 'Bài luận Chiêm nghiệm'}
                                    </label>
                                    <textarea value={task.essay || ''} onChange={e => {
                                      task.essay = e.target.value;
                                      setCohortTasks([...cohortTasks]);
                                    }}
                                      className="input w-full h-20 resize-none text-xs"
                                      placeholder={isEn ? 'Write your reflection...' : 'Ghi lại chiêm nghiệm của bạn...'}/>
                                    <div className="flex justify-end mt-2">
                                      <button onClick={() => saveEssay(task)} className="btn-ghost text-[10px] px-3 py-1 flex items-center gap-1"
                                        style={{ color: 'var(--color-accent)', border: '1px solid var(--color-border)' }}>
                                        {isEn ? 'Save' : 'Lưu'}
                                      </button>
                                    </div>
                                  </div>
                                </div>
                              </motion.div>
                            )}
                          </AnimatePresence>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Quiz Section */}
                {quizData && quizData.questions && (
                  <div className="glass-card p-6">
                    <div className="flex items-center gap-2 mb-4">
                      <span style={{ color: 'var(--color-accent)' }}>{Icon.quiz}</span>
                      <h3 className="font-display text-base font-semibold">{isEn ? 'Socratic Quiz' : 'Trắc nghiệm Socratic'}</h3>
                    </div>

                    {quizResult ? (
                      /* Quiz result */
                      <div className="text-center py-4">
                        <div className="text-3xl font-display font-bold mb-2" style={{ color: 'var(--color-accent)' }}>
                          {Math.round(quizResult.total_score || 0)}%
                        </div>
                        <p className="text-xs mb-4" style={{ color: 'var(--color-text-muted)' }}>
                          {isEn ? 'Socratic reflection score' : 'Điểm chiêm nghiệm Socratic'}
                        </p>
                        <button onClick={() => { setQuizResult(null); setUserAnswers(Array(8).fill(null)); }}
                          className="btn-ghost text-xs px-4 py-1.5" style={{ color: 'var(--color-accent)', border: '1px solid var(--color-border)' }}>
                          {isEn ? 'Retry' : 'Thử lại'}
                        </button>
                      </div>
                    ) : (
                      /* Quiz questions */
                      <div className="flex flex-col gap-4">
                        {(quizData.questions || []).map((q, qi) => (
                          <div key={qi} className="p-3 rounded-lg" style={{ background: 'var(--color-bg-secondary)', border: '1px solid var(--color-border)' }}>
                            <p className="text-xs font-bold mb-2">
                              <span style={{ color: 'var(--color-accent)' }}>Q{qi+1}.</span> {clean(q.question)}
                            </p>
                            <div className="flex flex-col gap-1.5">
                              {(q.options || []).map((opt, oi) => (
                                <button key={oi} onClick={() => {
                                  const a = [...userAnswers]; a[qi] = oi; setUserAnswers(a);
                                }}
                                  className="text-left text-xs p-2 rounded-lg transition-all"
                                  style={{
                                    background: userAnswers[qi] === oi ? 'var(--color-accent-subtle)' : 'transparent',
                                    border: `1px solid ${userAnswers[qi] === oi ? 'var(--color-accent)' : 'var(--color-border)'}`,
                                    color: userAnswers[qi] === oi ? 'var(--color-accent)' : 'var(--color-text-secondary)',
                                    fontWeight: userAnswers[qi] === oi ? 600 : 400,
                                  }}>
                                  {clean(opt)}
                                </button>
                              ))}
                            </div>
                          </div>
                        ))}
                        <button onClick={submitQuiz} disabled={userAnswers.includes(null) || quizSubmitting}
                          className="btn-primary w-full py-2.5 text-sm font-bold mt-2"
                          style={{ opacity: userAnswers.includes(null) ? 0.5 : 1 }}>
                          {quizSubmitting ? (isEn ? 'Grading...' : 'Đang chấm...') : (isEn ? 'Submit Quiz' : 'Nộp bài')}
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {/* Generate quiz button if no quiz */}
                {!quizData && weekTasks.length > 0 && (
                  <div className="glass-card p-6 text-center">
                    <p className="text-xs mb-3" style={{ color: 'var(--color-text-muted)' }}>
                      {isEn ? 'Complete tasks and reflections to unlock the Socratic quiz.' : 'Hoàn thành nhiệm vụ và bài luận để mở khóa trắc nghiệm.'}
                    </p>
                    <button onClick={generateQuiz} disabled={quizLoading}
                      className="btn-primary text-xs px-5 py-2 flex items-center gap-2 mx-auto">
                      {Icon.quiz} {quizLoading ? (isEn ? 'Generating...' : 'Đang tạo...') : (isEn ? 'Generate Quiz' : 'Tạo trắc nghiệm')}
                    </button>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </motion.div>
      )}
    </div>
  );
}
