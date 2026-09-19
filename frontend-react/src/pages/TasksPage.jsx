/**
 * Therapity — TasksPage
 * Layout: Kanban (3 cols, full-width) + Centered horizontal modal for Task Detail
 * Design System: DESIGN_SYSTEM.md
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import useAuthStore from '../store/authStore';
import useThemeStore from '../store/themeStore';
import { tasksAPI } from '../services/api';

/* ═══════════════════════════════════════════ ICONS ══ */
const Icon = {
  add:     <svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round"><line x1="6.5" y1="1.5" x2="6.5" y2="11.5"/><line x1="1.5" y1="6.5" x2="11.5" y2="6.5"/></svg>,
  trash:   <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"><line x1="3" y1="3" x2="9" y2="9"/><line x1="9" y1="3" x2="3" y2="9"/></svg>,
  ai:      <svg width="13" height="13" viewBox="0 0 13 13" fill="currentColor"><path d="M6.5 1 A5.5 5.5 0 0 1 6.5 12 A4 4 0 0 0 6.5 1 Z"/><circle cx="9.5" cy="3.5" r="0.9"/></svg>,
  star:    <svg width="14" height="14" viewBox="0 0 14 14" fill="currentColor"><path d="M7 0.5 L8.5 5 L13.5 5 L9.5 8 L11 12.5 L7 9.5 L3 12.5 L4.5 8 L0.5 5 L5.5 5 Z" opacity="0.9"/></svg>,
  clock:   <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"><circle cx="6" cy="6" r="4.5"/><line x1="6" y1="3.5" x2="6" y2="6"/><line x1="6" y1="6" x2="8" y2="7.5"/></svg>,
  diamond: <svg width="9" height="9" viewBox="0 0 9 9" fill="currentColor"><path d="M4.5 0.5 L5.5 3.5 L8.5 4.5 L5.5 5.5 L4.5 8.5 L3.5 5.5 L0.5 4.5 L3.5 3.5 Z"/></svg>,
  chevR:   <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"><path d="M5 3 L9 7 L5 11"/></svg>,
  chevL:   <svg width="14" height="14" viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"><path d="M9 3 L5 7 L9 11"/></svg>,
  close:   <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"><line x1="2" y1="2" x2="10" y2="10"/><line x1="10" y1="2" x2="2" y2="10"/></svg>,
  link:    <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"><path d="M5 7 A3 3 0 0 0 7 9 L9 9 A2.5 2.5 0 0 0 9 4 L7.5 4"/><path d="M7 5 A3 3 0 0 0 5 3 L3 3 A2.5 2.5 0 0 0 3 8 L4.5 8"/></svg>,
};

/* ══════════════════════════════════════ CONSTANTS ══ */
const COLUMNS = [
  { id: 'backlog',      label: 'Hàng chờ',   labelEn: 'Backlog',     dot: '#A78BFA' },
  { id: 'in_progress',  label: 'Đang làm',   labelEn: 'In Progress', dot: '#FFBFA3' },
  { id: 'done',         label: 'Hoàn thành', labelEn: 'Done',        dot: '#86EFAC' },
];

const EFFORT_COLOR = (n, dark) => {
  const c = dark
    ? ['#A78BFA','#93C5FD','#FFBFA3','#FCA5A5','#F87171']
    : ['#C9A4F5','#93C5FD','#FFBFA3','#F87171','#F4607E'];
  return c[Math.max(0, n - 1)];
};

/* ══════════════════════════════════════ TASK CARD ══ */
function TaskCard({ task, isDark, lang, isSelected, onSelect, onUpdate, onDelete }) {
  const subtasks = task.subtasks || [];
  const done = subtasks.filter(s => s.done).length;
  const pct  = subtasks.length ? Math.round((done / subtasks.length) * 100) : -1;
  const colIdx = COLUMNS.findIndex(c => c.id === task.status);

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      whileHover={{ y: -1 }}
      onClick={() => onSelect(task)}
      className="rounded-xl p-3 cursor-pointer select-none"
      style={{
        background: isSelected
          ? (isDark ? 'rgba(124,58,237,0.18)' : 'rgba(201,164,245,0.22)')
          : (isDark ? 'rgba(20,13,46,0.72)' : 'rgba(255,247,251,0.88)'),
        border: `1px solid ${isSelected ? 'var(--color-accent)' : (isDark ? 'rgba(124,58,237,0.18)' : 'rgba(176,127,212,0.18)')}`,
        backdropFilter: 'blur(10px)',
        transition: 'background 0.18s, border-color 0.18s',
      }}
    >
      <div className="flex items-start gap-1.5 mb-1">
        <span style={{ color: 'var(--color-accent)', opacity: 0.6, flexShrink: 0, marginTop: 2 }}>{Icon.diamond}</span>
        <span className="flex-1 text-sm font-medium leading-snug" style={{ color: 'var(--color-text-primary)', fontFamily: 'var(--font-sans)' }}>
          {task.title}
        </span>
        <button
          onClick={e => { e.stopPropagation(); onDelete(task.id); }}
          style={{ color: 'var(--color-text-muted)', opacity: 0.3, flexShrink: 0, marginTop: 1, transition: 'opacity 0.15s' }}
          onMouseEnter={e => e.currentTarget.style.opacity = '1'}
          onMouseLeave={e => e.currentTarget.style.opacity = '0.3'}
        >{Icon.trash}</button>
      </div>

      {task.goal && (
        <p className="text-xs mb-1.5 leading-relaxed" style={{ color: 'var(--color-text-muted)', paddingLeft: '1.1rem' }}>
          {task.goal.length > 64 ? task.goal.slice(0, 62) + '…' : task.goal}
        </p>
      )}

      {pct >= 0 && (
        <div className="mb-1.5" style={{ height: 2, background: 'var(--color-border-subtle)', borderRadius: 99, overflow: 'hidden' }}>
          <motion.div animate={{ width: `${pct}%` }} transition={{ duration: 0.4 }}
            style={{ height: '100%', background: 'var(--color-accent)', borderRadius: 99 }}/>
        </div>
      )}

      <div className="flex items-center gap-1.5 flex-wrap" style={{ paddingLeft: '1.1rem' }}>
        {task.effort > 0 && (
          <div className="flex gap-0.5">
            {Array.from({ length: task.effort }).map((_, i) => (
              <span key={i} style={{ width: 5, height: 5, borderRadius: '50%', background: EFFORT_COLOR(task.effort, isDark), display: 'inline-block' }}/>
            ))}
          </div>
        )}
        {task.deadline && (
          <span className="flex items-center gap-0.5 text-xs" style={{ color: 'var(--color-text-muted)' }}>
            {Icon.clock}<span style={{ fontSize: '0.63rem' }}>{task.deadline}</span>
          </span>
        )}
        <div className="flex items-center gap-0.5 ml-auto">
          {colIdx > 0 && (
            <button onClick={e => { e.stopPropagation(); onUpdate(task.id, { status: COLUMNS[colIdx - 1].id }); }}
              style={{ color: 'var(--color-text-muted)', display: 'flex', opacity: 0.5 }}
              onMouseEnter={e => e.currentTarget.style.opacity = '1'}
              onMouseLeave={e => e.currentTarget.style.opacity = '0.5'}
            >{Icon.chevL}</button>
          )}
          {colIdx < COLUMNS.length - 1 && (
            <button onClick={e => { e.stopPropagation(); onUpdate(task.id, { status: COLUMNS[colIdx + 1].id }); }}
              style={{ color: 'var(--color-accent)', display: 'flex', opacity: 0.7 }}
              onMouseEnter={e => e.currentTarget.style.opacity = '1'}
              onMouseLeave={e => e.currentTarget.style.opacity = '0.7'}
            >{Icon.chevR}</button>
          )}
        </div>
      </div>
    </motion.div>
  );
}

/* ══════════════════════════════════════ ADD FORM ══ */
function AddForm({ isDark, lang, status, onSave, onCancel }) {
  const [title, setTitle] = useState('');
  const ref = useRef(null);
  useEffect(() => { ref.current?.focus(); }, []);

  const submit = () => {
    if (!title.trim()) { onCancel(); return; }
    onSave({ title: title.trim(), status, effort: 1 });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }}
      className="rounded-xl p-3 mb-2"
      style={{ background: isDark ? 'rgba(20,13,46,0.9)' : 'rgba(255,247,251,0.98)', border: '1px solid var(--color-accent)' }}
    >
      <input ref={ref} value={title}
        onChange={e => setTitle(e.target.value)}
        onKeyDown={e => { if (e.key === 'Enter') submit(); if (e.key === 'Escape') onCancel(); }}
        placeholder={lang === 'en' ? 'Task name… (Enter to save)' : 'Tên nhiệm vụ… (Enter để lưu)'}
        className="w-full text-sm bg-transparent outline-none"
        style={{ color: 'var(--color-text-primary)', fontFamily: 'var(--font-sans)' }}
      />
      <div className="flex gap-2 mt-2.5">
        <motion.button whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
          onClick={submit} className="btn-primary text-xs px-3 py-1.5">
          {lang === 'en' ? 'Add' : 'Thêm'}
        </motion.button>
        <button onClick={onCancel} className="text-xs px-3 py-1.5 rounded-lg"
          style={{ color: 'var(--color-text-muted)', background: 'var(--color-accent-subtle)' }}>
          {lang === 'en' ? 'Cancel' : 'Hủy'}
        </button>
      </div>
    </motion.div>
  );
}

/* ══════════════════════ CHI TIẾT NHIỆM VỤ — Horizontal modal ══ */
function DetailPanel({ task, isDark, lang, onClose, onUpdate, onDelete }) {
  const [title, setTitle]           = useState(task.title || '');
  const [goal, setGoal]             = useState(task.goal || '');
  const [deadline, setDeadline]     = useState(task.deadline || '');
  const [effort, setEffort]         = useState(task.effort || 1);
  const [status, setStatus]         = useState(task.status || 'backlog');
  const [contextLink, setContextLink] = useState(task.context_link || '');
  const [aiLoading, setAiLoading]   = useState(false);
  const subtasks = task.subtasks || [];

  useEffect(() => {
    setTitle(task.title || '');
    setGoal(task.goal || '');
    setDeadline(task.deadline || '');
    setEffort(task.effort || 1);
    setStatus(task.status || 'backlog');
    setContextLink(task.context_link || '');
  }, [task.id]);

  const save = (extra = {}) =>
    onUpdate(task.id, { title, goal, deadline, effort, status, context_link: contextLink, ...extra });

  const toggleSubtask = (idx) => {
    const updated = subtasks.map((s, i) => i === idx ? { ...s, done: !s.done } : s);
    onUpdate(task.id, { subtasks: updated });
  };

  const aiBreakdown = async () => {
    setAiLoading(true);
    try {
      const res = await tasksAPI.microsteps({ title, goal, effort, lang });
      if (res.data?.subtasks) onUpdate(task.id, { subtasks: res.data.subtasks });
    } catch { /**/ }
    finally { setAiLoading(false); }
  };

  const done = subtasks.filter(s => s.done).length;
  const pct  = subtasks.length ? Math.round((done / subtasks.length) * 100) : 0;
  const activeCol = COLUMNS.find(c => c.id === status);

  const inputStyle = {
    width: '100%',
    background: isDark ? 'rgba(255,255,255,0.04)' : 'rgba(139,92,246,0.05)',
    border: '1px solid var(--color-border)', borderRadius: 10,
    padding: '8px 12px', color: 'var(--color-text-primary)',
    fontFamily: 'var(--font-sans)', fontSize: '0.875rem', outline: 'none',
    transition: 'border-color 0.15s',
  };

  const FL = (text) => (
    <label className="block text-xs font-semibold mb-1.5" style={{
      color: 'var(--color-text-muted)', letterSpacing: '0.06em',
      fontFamily: 'var(--font-sans)', textTransform: 'uppercase',
    }}>{text}</label>
  );

  return (
    <motion.div
      key={task.id}
      initial={{ opacity: 0, scale: 0.94, y: 16 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.94, y: 16 }}
      transition={{ type: 'spring', stiffness: 280, damping: 26 }}
      className="flex overflow-hidden"
      style={{
        width: '90vw', maxWidth: 860, maxHeight: '82vh',
        borderRadius: '1.75rem',
        border: '1px solid var(--color-border)',
        background: isDark ? 'rgba(12,8,26,0.95)' : 'rgba(255,250,254,0.96)',
        backdropFilter: 'blur(32px)',
        boxShadow: isDark
          ? '0 32px 80px rgba(0,0,0,0.65), 0 0 0 1px rgba(124,58,237,0.25)'
          : '0 32px 80px rgba(139,92,246,0.18), 0 0 0 1px rgba(201,164,245,0.35)',
      }}
    >
      {/* ════ LEFT — Decorative panel ════ */}
      <div
        className="relative flex-shrink-0 flex flex-col justify-between overflow-hidden"
        style={{
          width: 256, padding: '2rem 1.75rem',
          background: isDark
            ? 'linear-gradient(160deg, rgba(124,58,237,0.18) 0%, rgba(13,11,26,0.6) 100%)'
            : 'linear-gradient(160deg, rgba(201,164,245,0.3) 0%, rgba(255,235,250,0.5) 100%)',
          borderRight: '1px solid var(--color-border-subtle)',
        }}
      >
        {/* Celestial SVG decoration */}
        <svg className="absolute inset-0 w-full h-full pointer-events-none select-none"
          viewBox="0 0 256 480" fill="none"
          style={{ opacity: isDark ? 0.12 : 0.17 }}>
          <line x1="38"  y1="78"  x2="128" y2="138" stroke="var(--color-accent)" strokeWidth="0.6"/>
          <line x1="128" y1="138" x2="198" y2="98"  stroke="var(--color-accent)" strokeWidth="0.6"/>
          <line x1="128" y1="138" x2="158" y2="218" stroke="var(--color-accent)" strokeWidth="0.6"/>
          <line x1="158" y1="218" x2="88"  y2="278" stroke="var(--color-accent)" strokeWidth="0.6"/>
          <line x1="88"  y1="278" x2="178" y2="328" stroke="var(--color-accent)" strokeWidth="0.6"/>
          <line x1="178" y1="328" x2="218" y2="398" stroke="var(--color-accent)" strokeWidth="0.6"/>
          <line x1="38"  y1="358" x2="88"  y2="278" stroke="var(--color-accent)" strokeWidth="0.6"/>
          {[[38,78],[128,138],[198,98],[158,218],[88,278],[178,328],[218,398],[38,358],[98,418]].map(([cx,cy],i) => (
            <g key={i}>
              <circle cx={cx} cy={cy} r={i===1||i===4?5:3} fill="var(--color-accent)"/>
              <circle cx={cx} cy={cy} r={i===1||i===4?10:7} fill="var(--color-accent)" opacity="0.15"/>
            </g>
          ))}
          <path d="M218 198 L224 208 L218 218 L212 208 Z" fill="var(--color-accent)" opacity="0.45"/>
          <path d="M48 178 L54 190 L48 202 L42 190 Z"     fill="var(--color-accent)" opacity="0.35"/>
          <path d="M198 368 L203 376 L198 384 L193 376 Z" fill="var(--color-accent)" opacity="0.4"/>
          {[[18,138],[238,168],[68,238],[238,298],[28,398],[198,458]].map(([cx,cy],i)=>(
            <circle key={i} cx={cx} cy={cy} r="1.3" fill="var(--color-accent)"/>
          ))}
        </svg>

        {/* Top: Status + Title */}
        <div className="relative z-10">
          <div className="flex items-center gap-2 mb-4">
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: activeCol?.dot || 'var(--color-accent)', display: 'inline-block' }}/>
            <span className="text-xs font-medium" style={{ color: activeCol?.dot || 'var(--color-accent)', fontFamily: 'var(--font-sans)' }}>
              {lang === 'en' ? (activeCol?.labelEn || '') : (activeCol?.label || '')}
            </span>
          </div>
          <textarea
            value={title}
            onChange={e => setTitle(e.target.value)}
            onBlur={() => save()}
            rows={4}
            className="w-full bg-transparent outline-none resize-none font-display"
            style={{ color: 'var(--color-text-primary)', fontSize: '1.1rem', fontWeight: 600, lineHeight: 1.45, border: 'none', padding: 0 }}
            placeholder={lang === 'en' ? 'Task title…' : 'Tên nhiệm vụ…'}
          />
        </div>

        {/* Middle: Effort + Deadline + Progress ring */}
        <div className="relative z-10 flex flex-col gap-4">
          <div>
            <div className="text-xs font-semibold mb-2 uppercase" style={{ color: 'var(--color-text-muted)', letterSpacing: '0.06em', fontFamily: 'var(--font-sans)' }}>
              {lang === 'en' ? 'Effort' : 'Nỗ lực'}
            </div>
            <div className="flex gap-1.5">
              {[1,2,3,4,5].map(n => (
                <motion.button key={n}
                  whileHover={{ scale: 1.2 }} whileTap={{ scale: 0.9 }}
                  onClick={() => { setEffort(n); save({ effort: n }); }}
                  style={{
                    width: 22, height: 22, borderRadius: 6,
                    background: n <= effort ? EFFORT_COLOR(n, isDark) : (isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'),
                    border: `1px solid ${n <= effort ? EFFORT_COLOR(n, isDark) : 'var(--color-border)'}`,
                    transition: 'all 0.15s',
                  }}
                />
              ))}
            </div>
          </div>

          {deadline && (
            <div className="flex items-center gap-2">
              <span style={{ color: 'var(--color-text-muted)' }}>{Icon.clock}</span>
              <span className="text-xs" style={{ color: 'var(--color-text-muted)', fontFamily: 'var(--font-sans)' }}>{deadline}</span>
            </div>
          )}

          {subtasks.length > 0 && (
            <div className="flex items-center gap-3">
              <svg width="38" height="38" viewBox="0 0 38 38">
                <circle cx="19" cy="19" r="15" fill="none"
                  stroke={isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.07)'} strokeWidth="3"/>
                <circle cx="19" cy="19" r="15" fill="none"
                  stroke="var(--color-accent)" strokeWidth="3"
                  strokeDasharray={`${pct * 0.942} 94.2`}
                  strokeDashoffset="23.5"
                  strokeLinecap="round"
                  style={{ transition: 'stroke-dasharray 0.5s ease' }}
                />
                <text x="19" y="23" textAnchor="middle" fontSize="8.5"
                  fill="var(--color-accent)" fontFamily="var(--font-sans)" fontWeight="700">
                  {pct}%
                </text>
              </svg>
              <div>
                <div className="text-xs font-semibold" style={{ color: 'var(--color-text-primary)', fontFamily: 'var(--font-sans)' }}>
                  {done}/{subtasks.length}
                </div>
                <div style={{ fontSize: '0.63rem', color: 'var(--color-text-muted)', fontFamily: 'var(--font-sans)' }}>
                  {lang === 'en' ? 'steps done' : 'bước xong'}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Bottom: Delete */}
        <div className="relative z-10">
          <motion.button
            whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
            onClick={() => { onDelete(task.id); onClose(); }}
            className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full w-full justify-center"
            style={{ color: '#F87171', border: '1px solid rgba(248,113,113,0.25)', background: 'rgba(248,113,113,0.07)', fontFamily: 'var(--font-sans)' }}
          >
            {Icon.trash}
            {lang === 'en' ? 'Delete task' : 'Xóa nhiệm vụ'}
          </motion.button>
        </div>
      </div>

      {/* ════ RIGHT — Form panel ════ */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-6 pt-5 pb-3 flex-shrink-0"
          style={{ borderBottom: '1px solid var(--color-border-subtle)' }}>
          <span className="font-display text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>
            {lang === 'en' ? 'Task Detail' : 'Chi tiết nhiệm vụ'}
          </span>
          <motion.button whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}
            onClick={onClose} style={{ color: 'var(--color-text-muted)', display: 'flex' }}>
            {Icon.close}
          </motion.button>
        </div>

        {/* Scrollable body */}
        <div className="flex-1 overflow-y-auto px-6 py-4 flex flex-col gap-4">

          {/* Status */}
          <div>
            {FL(lang === 'en' ? 'Status' : 'Trạng thái')}
            <div className="flex gap-2">
              {COLUMNS.map(col => (
                <motion.button key={col.id}
                  whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.96 }}
                  onClick={() => { setStatus(col.id); save({ status: col.id }); }}
                  className="flex-1 text-xs py-1.5 rounded-xl font-medium"
                  style={{
                    background: status === col.id ? col.dot + '25' : (isDark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.03)'),
                    border: `1.5px solid ${status === col.id ? col.dot : 'var(--color-border)'}`,
                    color: status === col.id ? col.dot : 'var(--color-text-muted)',
                    transition: 'all 0.15s', fontFamily: 'var(--font-sans)',
                  }}
                >
                  {lang === 'en' ? col.labelEn : col.label}
                </motion.button>
              ))}
            </div>
          </div>

          {/* Goal */}
          <div>
            {FL(lang === 'en' ? 'Goal / Context' : 'Mục tiêu / Bối cảnh')}
            <textarea value={goal}
              onChange={e => setGoal(e.target.value)}
              onBlur={() => save()}
              rows={3}
              style={{ ...inputStyle, resize: 'none', lineHeight: 1.7 }}
              onFocus={e => e.currentTarget.style.borderColor = 'var(--color-accent)'}
              onBlurCapture={e => e.currentTarget.style.borderColor = 'var(--color-border)'}
              placeholder={lang === 'en' ? 'What is this task about?' : 'Nhiệm vụ này nhằm mục đích gì?'}
            />
          </div>

          {/* Deadline */}
          <div>
            {FL(lang === 'en' ? 'Deadline' : 'Hạn chót')}
            <input type="date" value={deadline}
              onChange={e => setDeadline(e.target.value)}
              onBlur={() => save()}
              style={inputStyle}
            />
          </div>

          {/* Link */}
          <div>
            {FL(lang === 'en' ? 'Link / Reference' : 'Liên kết tham chiếu')}
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--color-text-muted)' }}>{Icon.link}</span>
              <input value={contextLink}
                onChange={e => setContextLink(e.target.value)}
                onBlur={() => save()}
                placeholder="https://…"
                style={{ ...inputStyle, paddingLeft: 30 }}
              />
            </div>
          </div>

          {/* Microsteps */}
          <div>
            <div className="flex items-center justify-between mb-2">
              {FL(lang === 'en' ? 'Micro-steps (Pomodoro)' : 'Các bước nhỏ (Pomodoro)')}
              <motion.button
                whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.96 }}
                onClick={aiBreakdown} disabled={aiLoading}
                className="flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full font-medium flex-shrink-0"
                style={{ background: 'var(--color-accent)', color: 'white', fontFamily: 'var(--font-sans)', opacity: aiLoading ? 0.7 : 1 }}
              >
                {aiLoading
                  ? <motion.span animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}>{Icon.ai}</motion.span>
                  : Icon.ai}
                {aiLoading ? (lang === 'en' ? 'Thinking…' : 'AI đang chia…') : (lang === 'en' ? 'AI Breakdown' : 'AI Chia nhỏ')}
              </motion.button>
            </div>

            <div className="flex flex-col gap-1">
              <AnimatePresence mode="popLayout">
                {subtasks.map((s, i) => (
                  <motion.button key={i}
                    initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -8 }}
                    onClick={() => toggleSubtask(i)}
                    className="flex items-center gap-2.5 text-left py-2 px-3 rounded-xl w-full"
                    style={{
                      background: s.done ? (isDark ? 'rgba(124,58,237,0.1)' : 'rgba(201,164,245,0.12)') : 'transparent',
                      border: `1px solid ${s.done ? 'var(--color-border-subtle)' : 'transparent'}`,
                      transition: 'background 0.18s',
                    }}
                  >
                    <span className="flex-shrink-0" style={{
                      width: 15, height: 15, borderRadius: 4,
                      border: `1.5px solid ${s.done ? 'var(--color-accent)' : 'var(--color-text-muted)'}`,
                      background: s.done ? 'var(--color-accent)' : 'transparent',
                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                      transition: 'all 0.15s',
                    }}>
                      {s.done && (
                        <svg width="8" height="8" viewBox="0 0 8 8" fill="none" stroke="white" strokeWidth="1.5">
                          <path d="M1.5 4L3 5.5 6.5 2"/>
                        </svg>
                      )}
                    </span>
                    <span className="flex-1 text-sm leading-snug" style={{
                      color: s.done ? 'var(--color-accent)' : 'var(--color-text-secondary)',
                      textDecoration: s.done ? 'line-through' : 'none',
                      opacity: s.done ? 0.65 : 1, fontFamily: 'var(--font-sans)',
                    }}>
                      {s.title}
                    </span>
                  </motion.button>
                ))}
              </AnimatePresence>

              {subtasks.length === 0 && !aiLoading && (
                <div className="flex flex-col items-center gap-2 py-5">
                  <motion.div animate={{ scale: [1,1.08,1], opacity: [0.25,0.45,0.25] }}
                    transition={{ duration: 3.5, repeat: Infinity, ease: 'easeInOut' }}
                    style={{ color: 'var(--color-accent)' }}>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2 L14 8.5 L21 10 L14 11.5 L12 18 L10 11.5 L3 10 L10 8.5 Z" opacity="0.6"/>
                    </svg>
                  </motion.div>
                  <p style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)', textAlign: 'center' }}>
                    {lang === 'en' ? 'Use "AI Breakdown" to generate 25-min Pomodoro steps' : 'Nhấn "AI Chia nhỏ" để tạo các bước 25 phút'}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-2 px-6 py-3 flex-shrink-0"
          style={{ borderTop: '1px solid var(--color-border-subtle)' }}>
          <motion.button whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
            onClick={() => { save(); onClose(); }}
            className="btn-primary text-xs px-5 py-2">
            {lang === 'en' ? 'Save & Close' : 'Lưu & Đóng'}
          </motion.button>
        </div>
      </div>
    </motion.div>
  );
}

/* ══════════════════════════════════════ MAIN ══ */
export default function TasksPage() {
  const { user }  = useAuthStore();
  const { lang, theme } = useThemeStore();
  const isDark = theme === 'dark';

  const [tasks, setTasks]       = useState([]);
  const [loading, setLoading]   = useState(true);
  const [selected, setSelected] = useState(null);
  const [addingIn, setAddingIn] = useState(null);
  const [toast, setToast]       = useState(null);

  const load = useCallback(async () => {
    if (!user?.username) return;
    setLoading(true);
    try {
      const res = await tasksAPI.getTasks(user.username);
      setTasks(res.data || []);
    } catch { /**/ }
    finally { setLoading(false); }
  }, [user]);

  useEffect(() => { load(); }, [load]);

  const showToast = (msg, type = 'info') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 2600);
  };

  const create = async (data) => {
    try {
      await tasksAPI.createTask(user.username, data);
      await load();
      setAddingIn(null);
      showToast('✦ Đã tạo nhiệm vụ', 'success');
    } catch { showToast('Lỗi khi tạo', 'error'); }
  };

  const update = async (id, data) => {
    setTasks(prev => prev.map(t => t.id === id ? { ...t, ...data } : t));
    if (selected?.id === id) setSelected(prev => ({ ...prev, ...data }));
    try { await tasksAPI.updateTask(user.username, id, data); }
    catch { showToast('Lỗi khi cập nhật', 'error'); await load(); }
  };

  const del = async (id) => {
    setTasks(prev => prev.filter(t => t.id !== id));
    if (selected?.id === id) setSelected(null);
    try { await tasksAPI.deleteTask(user.username, id); showToast('Đã xóa', 'info'); }
    catch { showToast('Lỗi khi xóa', 'error'); await load(); }
  };

  const total     = tasks.length;
  const doneCount = tasks.filter(t => t.status === 'done').length;
  const inProgress = tasks.filter(t => t.status === 'in_progress').length;

  return (
    <div className="flex flex-col relative overflow-hidden"
      style={{ height: 'calc(100vh - 3rem)', borderRadius: '1.25rem' }}>

      {/* Background */}
      <div className={`absolute inset-0 pointer-events-none ${isDark ? 'scene-bg-abyss' : 'scene-bg-sunset'}`}
        style={{ opacity: isDark ? 0.38 : 0.45, backgroundPosition: 'center 18%', borderRadius: '1.25rem' }}/>
      <div className="absolute inset-0 pointer-events-none" style={{
        background: isDark
          ? 'linear-gradient(to bottom, transparent 8%, var(--color-bg-primary) 48%)'
          : 'linear-gradient(to bottom, transparent 10%, var(--color-bg-primary) 45%)',
        borderRadius: '1.25rem',
      }}/>

      {/* Header */}
      <div className="relative z-10 flex items-end justify-between px-6 pt-5 pb-3 flex-shrink-0">
        <div>
          <h1 className="font-display text-2xl font-semibold" style={{ color: 'var(--color-text-primary)' }}>
            {lang === 'en' ? 'My Tasks' : 'Nhiệm vụ'}
          </h1>
          {total > 0 && (
            <p className="text-xs mt-0.5" style={{ color: 'var(--color-text-muted)' }}>
              {lang === 'en'
                ? `${doneCount}/${total} done · ${inProgress} in progress`
                : `${doneCount}/${total} hoàn thành · ${inProgress} đang làm`}
            </p>
          )}
        </div>
        {total > 0 && (
          <div className="flex items-center gap-3 px-4 py-2 rounded-full"
            style={{ background: isDark ? 'rgba(20,13,46,0.7)' : 'rgba(255,247,251,0.8)', border: '1px solid var(--color-border-subtle)', backdropFilter: 'blur(10px)' }}>
            {[
              { val: total,      label: lang === 'en' ? 'Total' : 'Tổng', color: 'var(--color-accent)' },
              { val: inProgress, label: lang === 'en' ? 'Active' : 'Làm', color: '#FFBFA3' },
              { val: doneCount,  label: lang === 'en' ? 'Done' : 'Xong',  color: '#86EFAC' },
            ].map((s, i) => (
              <div key={i} className="text-center" style={{ minWidth: 32 }}>
                <div className="font-display text-base font-semibold" style={{ color: s.color }}>{s.val}</div>
                <div style={{ fontSize: '0.58rem', color: 'var(--color-text-muted)', letterSpacing: '0.04em' }}>{s.label}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Progress strip */}
      {total > 0 && (
        <div className="relative z-10 mx-6 mb-1 flex-shrink-0"
          style={{ height: 2, background: 'var(--color-border-subtle)', borderRadius: 99, overflow: 'hidden' }}>
          <motion.div
            animate={{ width: `${Math.round((doneCount / total) * 100)}%` }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
            style={{ height: '100%', background: 'linear-gradient(90deg, var(--color-accent), #FFBFA3)', borderRadius: 99 }}
          />
        </div>
      )}

      {/* Main: Kanban board */}
      <div className="relative z-10 flex-1 min-h-0 overflow-hidden">
        <div className="flex gap-4 px-6 pb-5 pt-3 min-h-0 h-full w-full">
          {COLUMNS.map(col => {
            const colTasks = tasks.filter(t => t.status === col.id);
            const isAdding = addingIn === col.id;

            return (
              <div key={col.id} className="flex-1 flex flex-col min-w-0" style={{ minWidth: 180 }}>
                <div className="flex items-center gap-2 mb-2 flex-shrink-0 px-1">
                  <span style={{ width: 7, height: 7, borderRadius: '50%', background: col.dot, display: 'inline-block', flexShrink: 0 }}/>
                  <span className="font-display text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>
                    {lang === 'en' ? col.labelEn : col.label}
                  </span>
                  <span className="text-xs px-1.5 py-0.5 rounded-full"
                    style={{ background: 'var(--color-accent-subtle)', color: 'var(--color-text-muted)', border: '1px solid var(--color-border-subtle)' }}>
                    {colTasks.length}
                  </span>
                  <motion.button
                    whileHover={{ scale: 1.12 }} whileTap={{ scale: 0.9 }}
                    onClick={() => setAddingIn(isAdding ? null : col.id)}
                    className="ml-auto flex items-center justify-center rounded-lg"
                    style={{
                      width: 22, height: 22,
                      color: isAdding ? 'white' : 'var(--color-text-muted)',
                      background: isAdding ? 'var(--color-accent)' : 'var(--color-accent-subtle)',
                      border: '1px solid var(--color-border-subtle)',
                    }}
                  >{Icon.add}</motion.button>
                </div>

                <div className="flex-1 overflow-y-auto flex flex-col gap-2 p-2"
                  style={{
                    background: isDark ? 'rgba(13,11,26,0.38)' : 'rgba(255,247,251,0.32)',
                    border: '1px solid var(--color-border-subtle)',
                    borderRadius: '1rem', backdropFilter: 'blur(8px)',
                  }}>
                  <AnimatePresence>
                    {isAdding && (
                      <AddForm key="add-form"
                        isDark={isDark} lang={lang} status={col.id}
                        onSave={create} onCancel={() => setAddingIn(null)}
                      />
                    )}
                  </AnimatePresence>

                  {loading ? (
                    <div className="flex justify-center py-10">
                      <motion.div animate={{ rotate: 360 }} transition={{ duration: 1.4, repeat: Infinity, ease: 'linear' }}
                        style={{ width: 20, height: 20, border: '2px solid var(--color-accent)', borderTopColor: 'transparent', borderRadius: '50%' }}/>
                    </div>
                  ) : (
                    <AnimatePresence mode="popLayout">
                      {colTasks.map(t => (
                        <TaskCard key={t.id} task={t} isDark={isDark} lang={lang}
                          isSelected={selected?.id === t.id}
                          onSelect={setSelected}
                          onUpdate={update}
                          onDelete={del}
                        />
                      ))}
                    </AnimatePresence>
                  )}

                  {!loading && colTasks.length === 0 && !isAdding && (
                    <div className="flex flex-col items-center justify-center flex-1 py-8 gap-2">
                      <motion.div animate={{ opacity: [0.25,0.4,0.25] }} transition={{ duration: 3, repeat: Infinity }}
                        style={{ color: 'var(--color-accent)' }}>
                        <svg width="26" height="26" viewBox="0 0 26 26" fill="currentColor">
                          <path d="M13 1 L15.5 9.5 L24 12 L15.5 14.5 L13 23 L10.5 14.5 L2 12 L10.5 9.5 Z" opacity="0.4"/>
                        </svg>
                      </motion.div>
                      <p style={{ fontSize: '0.68rem', color: 'var(--color-text-muted)', textAlign: 'center' }}>
                        {lang === 'en' ? 'Empty — press + to add' : 'Trống — nhấn + để thêm'}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Task Detail Modal — centered, fixed overlay */}
        <AnimatePresence>
          {selected && (
            <motion.div
              key="detail-backdrop"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-50 flex items-center justify-center p-4"
              style={{ background: 'rgba(0,0,0,0.45)', backdropFilter: 'blur(5px)' }}
              onClick={e => e.target === e.currentTarget && setSelected(null)}
            >
              <DetailPanel
                task={selected}
                isDark={isDark}
                lang={lang}
                onClose={() => setSelected(null)}
                onUpdate={update}
                onDelete={del}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Toast */}
      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: 14, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 14 }}
            className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 px-5 py-2.5 rounded-full text-sm font-medium"
            style={{
              background: toast.type === 'error' ? 'rgba(248,113,113,0.15)' : 'rgba(167,139,250,0.15)',
              border: `1px solid ${toast.type === 'error' ? 'rgba(248,113,113,0.4)' : 'var(--color-border)'}`,
              color: toast.type === 'error' ? '#F87171' : 'var(--color-accent)',
              backdropFilter: 'blur(12px)', fontFamily: 'var(--font-sans)',
            }}
          >
            {toast.msg}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
