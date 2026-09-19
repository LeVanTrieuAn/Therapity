/**
 * Therapity — DiaryPage
 *
 * Layout: 3 columns
 *  LEFT   — Folder tree + entry list (Obsidian vault panel)
 *  CENTER — Rich text editor (markdown toolbar + content area)
 *  RIGHT  — Knowledge graph (Obsidian-style node graph)
 *
 * Design System: DESIGN_SYSTEM.md
 *  - Fonts: Playfair Display (headings) / DM Sans (body)
 *  - Colors: var(--color-*) tokens only
 *  - Icons: flat geometric SVG — NO icon libraries
 *  - Animations: Framer Motion
 *  - Background: scene-bg-sunset (light) / scene-bg-abyss (dark)
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import useAuthStore from '../store/authStore';
import useThemeStore from '../store/themeStore';
import { diaryAPI } from '../services/api';

/* ══════════════════════════════════════════════════════════════
   TASTE-SKILL SVG ICONS — geometric only
   ══════════════════════════════════════════════════════════════ */
const Icon = {
  // ✦ Diamond star — new entry
  newEntry: (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="currentColor">
      <path d="M7 0.5 L8.1 5.9 L13.5 7 L8.1 8.1 L7 13.5 L5.9 8.1 L0.5 7 L5.9 5.9 Z"/>
    </svg>
  ),
  // ▽ Triangle — folder
  folder: (
    <svg width="13" height="13" viewBox="0 0 13 13" fill="currentColor">
      <polygon points="6.5,2 12,10 1,10" opacity="0.8"/>
      <polygon points="6.5,5 10,10 3,10" fill="var(--color-bg-primary)" opacity="0.5"/>
    </svg>
  ),
  // ○ Ring — entry
  entry: (
    <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
      <circle cx="5" cy="5" r="3.5" stroke="currentColor" strokeWidth="1.2"/>
      <circle cx="5" cy="5" r="1.2" fill="currentColor"/>
    </svg>
  ),
  // ☽ Crescent — AI insight
  ai: (
    <svg width="13" height="13" viewBox="0 0 13 13" fill="currentColor">
      <path d="M6.5 1 A5.5 5.5 0 0 1 6.5 12 A4 4 0 0 0 6.5 1 Z"/>
      <circle cx="9.5" cy="3.5" r="0.9"/>
    </svg>
  ),
  // ✕ Close / delete
  trash: (
    <svg width="12" height="12" viewBox="0 0 12 12" fill="none" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round">
      <line x1="3" y1="3" x2="9" y2="9"/><line x1="9" y1="3" x2="3" y2="9"/>
    </svg>
  ),
  // ◎ Eye — graph view
  graph: (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.1"/>
      <ellipse cx="7" cy="7" rx="2.5" ry="3.5" stroke="currentColor" strokeWidth="1"/>
      <circle cx="7" cy="7" r="1.2" fill="currentColor"/>
    </svg>
  ),
  // ✤ Compass — mood
  mood: (
    <svg width="13" height="13" viewBox="0 0 13 13" fill="currentColor">
      <path d="M6.5 0.5 L7.4 5.6 L12.5 6.5 L7.4 7.4 L6.5 12.5 L5.6 7.4 L0.5 6.5 L5.6 5.6 Z" opacity="0.85"/>
      <circle cx="6.5" cy="6.5" r="1.5" fill="none" stroke="currentColor" strokeWidth="0.7"/>
    </svg>
  ),
  // ← Arrow — back
  back: (
    <svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round">
      <path d="M8 2.5 L4 6.5 L8 10.5"/><line x1="4" y1="6.5" x2="11" y2="6.5"/>
    </svg>
  ),
  // ✓ Save tick
  save: (
    <svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M2.5 7 L5 9.5 L10.5 4"/>
    </svg>
  ),
  // Bold B
  bold: (
    <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
      <path d="M3 2h3.5a2.5 2.5 0 0 1 0 5H3zm0 5h4a2.5 2.5 0 0 1 0 5H3z" opacity="0.9"/>
    </svg>
  ),
  // Italic I
  italic: (
    <svg width="12" height="12" viewBox="0 0 12 12" fill="currentColor">
      <rect x="4.5" y="2" width="3" height="1.2" rx="0.5"/>
      <rect x="4.5" y="8.8" width="3" height="1.2" rx="0.5"/>
      <line x1="7" y1="3.2" x2="5" y2="8.8" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/>
    </svg>
  ),
  // # Heading
  heading: (
    <svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round">
      <line x1="2" y1="2.5" x2="2" y2="10.5"/>
      <line x1="11" y1="2.5" x2="11" y2="10.5"/>
      <line x1="2" y1="6.5" x2="11" y2="6.5"/>
    </svg>
  ),
  // — List
  list: (
    <svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round">
      <line x1="4" y1="3.5" x2="11" y2="3.5"/>
      <line x1="4" y1="6.5" x2="11" y2="6.5"/>
      <line x1="4" y1="9.5" x2="11" y2="9.5"/>
      <circle cx="2" cy="3.5" r="0.8" fill="currentColor"/>
      <circle cx="2" cy="6.5" r="0.8" fill="currentColor"/>
      <circle cx="2" cy="9.5" r="0.8" fill="currentColor"/>
    </svg>
  ),
  // > Quote
  quote: (
    <svg width="13" height="13" viewBox="0 0 13 13" fill="currentColor">
      <path d="M2 4h2.5L3 7.5h2L3.5 11H1.5L3 7.5H1z" opacity="0.75"/>
      <path d="M7 4h2.5L8 7.5h2L8.5 11H6.5L8 7.5H6z" opacity="0.75"/>
    </svg>
  ),
};

/* ══════════════════════════════════════════════════════════════
   MOOD OPTIONS — theme-synced colors
   ══════════════════════════════════════════════════════════════ */
const MOODS = [
  { key: 'Calm',      label: 'Bình yên',   colorL: '#C9A4F5', colorD: '#7C3AED' },
  { key: 'Happy',     label: 'Vui vẻ',     colorL: '#FFBFA3', colorD: '#D97706' },
  { key: 'Sad',       label: 'Buồn bã',    colorL: '#A5B4FC', colorD: '#6366F1' },
  { key: 'Anxious',   label: 'Lo lắng',    colorL: '#F4A8C6', colorD: '#DB2777' },
  { key: 'Angry',     label: 'Bực bội',    colorL: '#F4607E', colorD: '#F87171' },
  { key: 'Grateful',  label: 'Biết ơn',    colorL: '#B07FD4', colorD: '#A78BFA' },
];

function moodColor(moodKey, isDark) {
  const m = MOODS.find(m => m.key === moodKey) || MOODS[0];
  return isDark ? m.colorD : m.colorL;
}

/* ══════════════════════════════════════════════════════════════
   OBSIDIAN KNOWLEDGE GRAPH — pure SVG with zoom & pan
   ══════════════════════════════════════════════════════════════ */
function KnowledgeGraph({ entries, isDark, activeId, onSelectEntry }) {
  const svgRef = useRef(null);
  const [hovered, setHovered] = useState(null);
  const [svgSize, setSvgSize] = useState({ w: 320, h: 420 });

  // Pan & Zoom state
  const [transform, setTransform] = useState({ x: 0, y: 0, scale: 1 });
  const dragging = useRef(false);
  const lastPos = useRef({ x: 0, y: 0 });

  useEffect(() => {
    if (!svgRef.current) return;
    const ro = new ResizeObserver(([e]) => {
      setSvgSize({ w: e.contentRect.width, h: Math.max(300, e.contentRect.height) });
    });
    ro.observe(svgRef.current);
    return () => ro.disconnect();
  }, []);

  // Wheel zoom toward cursor
  const handleWheel = (e) => {
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.12 : 0.9;
    setTransform(prev => {
      const newScale = Math.min(Math.max(prev.scale * factor, 0.25), 6);
      const rect = svgRef.current?.getBoundingClientRect();
      if (!rect) return prev;
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      return {
        scale: newScale,
        x: mx - (mx - prev.x) * (newScale / prev.scale),
        y: my - (my - prev.y) * (newScale / prev.scale),
      };
    });
  };

  // Drag pan
  const handleMouseDown = (e) => {
    if (e.button !== 0) return;
    dragging.current = true;
    lastPos.current = { x: e.clientX, y: e.clientY };
  };

  const handleMouseMove = (e) => {
    if (!dragging.current) return;
    const dx = e.clientX - lastPos.current.x;
    const dy = e.clientY - lastPos.current.y;
    lastPos.current = { x: e.clientX, y: e.clientY };
    setTransform(prev => ({ ...prev, x: prev.x + dx, y: prev.y + dy }));
  };

  const stopDrag = () => { dragging.current = false; };

  const resetView = () => setTransform({ x: 0, y: 0, scale: 1 });
  const zoomIn  = () => setTransform(prev => ({ ...prev, scale: Math.min(prev.scale * 1.3, 6) }));
  const zoomOut = () => setTransform(prev => ({ ...prev, scale: Math.max(prev.scale * 0.77, 0.25) }));

  if (!entries.length) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-3">
        <motion.div
          animate={{ rotate: [0, 10, -10, 0], scale: [1, 1.05, 1] }}
          transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
        >
          <svg width="52" height="52" viewBox="0 0 52 52" fill="none">
            <circle cx="26" cy="26" r="23" stroke={isDark ? '#7C3AED' : '#C9A4F5'} strokeWidth="0.8" opacity="0.5"/>
            {[[26,10],[10,34],[42,34]].map(([x,y],i)=>(
              <g key={i}>
                <path d={`M${x} ${y-5} L${x+2.5} ${y+1.5} L${x+7} ${y} L${x+2.5} ${y-1.5} L${x} ${y+5} L${x-2.5} ${y-1.5} L${x-7} ${y} L${x-2.5} ${y+1.5} Z`}
                  fill={isDark ? '#7C3AED' : '#C9A4F5'} opacity="0.45"/>
              </g>
            ))}
            <line x1="26" y1="12" x2="13" y2="32" stroke={isDark ? 'rgba(124,58,237,0.4)' : 'rgba(176,127,212,0.4)'} strokeWidth="0.8"/>
            <line x1="26" y1="12" x2="39" y2="32" stroke={isDark ? 'rgba(124,58,237,0.4)' : 'rgba(176,127,212,0.4)'} strokeWidth="0.8"/>
            <line x1="13" y1="32" x2="39" y2="32" stroke={isDark ? 'rgba(124,58,237,0.3)' : 'rgba(176,127,212,0.3)'} strokeWidth="0.8" strokeDasharray="2 2"/>
          </svg>
        </motion.div>
        <p style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', textAlign: 'center' }}>
          Đồ thị tri thức<br/>sẽ hình thành khi bạn viết…
        </p>
      </div>
    );
  }

  // Build node positions: center-focused radial layout
  const W = svgSize.w, H = svgSize.h;
  const cx = W / 2, cy = H / 2;
  const nodePositions = {};

  // Group by folder
  const folders = [...new Set(entries.map(e => e.folder || ''))];
  const folderCenters = {};
  folders.forEach((f, fi) => {
    const angle = (fi / Math.max(folders.length, 1)) * 2 * Math.PI - Math.PI / 2;
    const r = folders.length > 1 ? Math.min(W, H) * 0.28 : 0;
    folderCenters[f] = { x: cx + r * Math.cos(angle), y: cy + r * Math.sin(angle) };
  });

  entries.forEach((e) => {
    const fc = folderCenters[e.folder || ''] || { x: cx, y: cy };
    const sameFolder = entries.filter(en => (en.folder || '') === (e.folder || ''));
    const idx = sameFolder.findIndex(en => en.id === e.id);
    const GOLDEN = 2.39996;
    const angle = idx * GOLDEN;
    const r = 32 + Math.floor(idx / 5) * 36;
    nodePositions[e.id] = {
      x: Math.min(Math.max(fc.x + r * Math.cos(angle), 28), W - 28),
      y: Math.min(Math.max(fc.y + r * Math.sin(angle) * 0.8, 28), H - 28),
    };
  });

  // Build edges: entries in same folder
  const edges = [];
  for (let i = 0; i < entries.length; i++) {
    for (let j = i + 1; j < entries.length; j++) {
      if ((entries[i].folder || '') === (entries[j].folder || '')) {
        const a = nodePositions[entries[i].id];
        const b = nodePositions[entries[j].id];
        if (a && b) {
          const dist = Math.sqrt((a.x-b.x)**2+(a.y-b.y)**2);
          if (dist < 140) edges.push([entries[i].id, entries[j].id]);
        }
      }
    }
  }

  // Wikilink edges: search for [[EntryTitle]] mentions
  const wikilinkEdges = [];
  entries.forEach(e => {
    const matches = (e.content || '').match(/\[\[([^\]]+)\]\]/g) || [];
    matches.forEach(match => {
      const ref = match.slice(2, -2).trim();
      const target = entries.find(en => en.title?.toLowerCase().includes(ref.toLowerCase()));
      if (target && target.id !== e.id) {
        wikilinkEdges.push([e.id, target.id]);
      }
    });
  });

  const zoomBtnBase = {
    width: 26, height: 26, borderRadius: 7,
    background: isDark ? 'rgba(14,10,30,0.88)' : 'rgba(255,247,251,0.92)',
    border: `1px solid ${isDark ? 'rgba(124,58,237,0.35)' : 'rgba(176,127,212,0.4)'}`,
    color: isDark ? '#A78BFA' : '#7C3AED',
    fontSize: '1rem', fontWeight: 700,
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    cursor: 'pointer', backdropFilter: 'blur(8px)',
  };

  return (
    <div
      ref={svgRef}
      className="relative w-full h-full"
      style={{ userSelect: 'none' }}
    >
      {/* Zoom Controls overlay */}
      <div style={{ position: 'absolute', top: 8, right: 8, zIndex: 10, display: 'flex', flexDirection: 'column', gap: 4 }}>
        <motion.button whileHover={{ scale: 1.12 }} whileTap={{ scale: 0.9 }} style={zoomBtnBase} onClick={zoomIn} title="Phóng to">+</motion.button>
        <motion.button whileHover={{ scale: 1.12 }} whileTap={{ scale: 0.9 }} style={zoomBtnBase} onClick={zoomOut} title="Thu nhỏ">−</motion.button>
        <motion.button whileHover={{ scale: 1.12 }} whileTap={{ scale: 0.9 }} style={{ ...zoomBtnBase, fontSize: '0.55rem', letterSpacing: '0.05em' }} onClick={resetView} title="Đặt lại">
          {/* Reset / home icon */}
          <svg width="11" height="11" viewBox="0 0 11 11" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round">
            <path d="M9.5 5.5 A4 4 0 1 1 5.5 1.5"/>
            <path d="M9.5 1.5 L9.5 5.5 L5.5 5.5" />
          </svg>
        </motion.button>
      </div>

      {/* Scale indicator */}
      <div style={{
        position: 'absolute', bottom: 20, right: 8, zIndex: 10,
        fontSize: '0.6rem', color: isDark ? '#4A3B6A' : '#C9B8D8',
        fontFamily: 'DM Sans, system-ui',
      }}>
        {Math.round(transform.scale * 100)}%
      </div>

      <svg
        width="100%"
        height={svgSize.h}
        style={{ borderRadius: '0.75rem', cursor: dragging.current ? 'grabbing' : 'grab', display: 'block' }}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={stopDrag}
        onMouseLeave={stopDrag}
      >
        <defs>
          <linearGradient id="kgBgL" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#EDD9F8" stopOpacity="0.4"/>
            <stop offset="100%" stopColor="#FFE8D6" stopOpacity="0.25"/>
          </linearGradient>
          <linearGradient id="kgBgD" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#100A25" stopOpacity="0.9"/>
            <stop offset="100%" stopColor="#080612" stopOpacity="0.95"/>
          </linearGradient>
          <radialGradient id="kgGlow" cx="50%" cy="50%" r="60%">
            <stop offset="0%" stopColor={isDark ? 'rgba(124,58,237,0.1)' : 'rgba(255,191,163,0.15)'}/>
            <stop offset="100%" stopColor="transparent"/>
          </radialGradient>
          <clipPath id="kgClip">
            <rect x="0" y="0" width={W} height={svgSize.h} rx="12"/>
          </clipPath>
        </defs>

        <rect x="0" y="0" width={W} height={svgSize.h} rx="12" fill={`url(#${isDark ? 'kgBgD' : 'kgBgL'})`}/>
        <rect x="0" y="0" width={W} height={svgSize.h} rx="12" fill="url(#kgGlow)"/>

        <g clipPath="url(#kgClip)">
          {/* Transformable content — zoom + pan */}
          <g transform={`translate(${transform.x}, ${transform.y}) scale(${transform.scale})`}>
            {/* Background stars */}
            {Array.from({length: isDark ? 20 : 10}, (_,i) => (
              <circle key={i} cx={((i*137+50)%W)} cy={((i*89+30)%(svgSize.h))}
                r={[0.8,1,1.2][i%3]} fill={isDark ? '#E2D9F3' : '#C9A4F5'}
                opacity={0.1+(i%4)*0.06}/>
            ))}

            {/* Folder edges */}
            {edges.map(([a, b], i) => {
              const pa = nodePositions[a], pb = nodePositions[b];
              if (!pa || !pb) return null;
              return (
                <line key={i} x1={pa.x} y1={pa.y} x2={pb.x} y2={pb.y}
                  stroke={isDark ? 'rgba(124,58,237,0.22)' : 'rgba(176,127,212,0.28)'}
                  strokeWidth="0.8"/>
              );
            })}

            {/* Wikilink edges */}
            {wikilinkEdges.map(([a, b], i) => {
              const pa = nodePositions[a], pb = nodePositions[b];
              if (!pa || !pb) return null;
              const mx = (pa.x+pb.x)/2, my = (pa.y+pb.y)/2 - 20;
              return (
                <path key={`wl-${i}`}
                  d={`M ${pa.x} ${pa.y} Q ${mx} ${my} ${pb.x} ${pb.y}`}
                  stroke={isDark ? 'rgba(248,113,113,0.4)' : 'rgba(244,96,126,0.4)'}
                  strokeWidth="1" strokeDasharray="3 2" fill="none"/>
              );
            })}

            {/* Nodes */}
            {entries.map(e => {
              const pos = nodePositions[e.id];
              if (!pos) return null;
              const isActive = e.id === activeId;
              const isHov = hovered === e.id;
              const R = isActive ? 10 : (isHov ? 8 : 6);
              const mc = moodColor(e.mood, isDark);
              return (
                <motion.g key={e.id}
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ type: 'spring', stiffness: 260, damping: 20 }}
                  style={{ cursor: 'pointer' }}
                  onClick={(ev) => { if (!dragging.current) { ev.stopPropagation(); onSelectEntry(e); } }}
                  onMouseEnter={() => setHovered(e.id)}
                  onMouseLeave={() => setHovered(null)}
                >
                  <circle cx={pos.x} cy={pos.y} r={R+7} fill={mc} opacity={isActive ? 0.2 : (isHov ? 0.15 : 0.08)}/>
                  {isActive && (
                    <motion.circle cx={pos.x} cy={pos.y} r={R+12}
                      fill="none" stroke={mc} strokeWidth="1"
                      opacity="0.5" strokeDasharray="3 3"
                      animate={{ rotate: 360 }}
                      style={{ transformOrigin: `${pos.x}px ${pos.y}px` }}
                      transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
                    />
                  )}
                  {/* Diamond gem node */}
                  <path
                    d={`M ${pos.x} ${pos.y-R} L ${pos.x+R*0.4} ${pos.y-R*0.4} L ${pos.x+R} ${pos.y} L ${pos.x+R*0.4} ${pos.y+R*0.4} L ${pos.x} ${pos.y+R} L ${pos.x-R*0.4} ${pos.y+R*0.4} L ${pos.x-R} ${pos.y} L ${pos.x-R*0.4} ${pos.y-R*0.4} Z`}
                    fill={isDark ? '#140D2E' : '#FFF7FB'}
                    stroke={mc} strokeWidth={isActive ? 2 : 1.2}
                  />
                  <circle cx={pos.x} cy={pos.y} r={R*0.35} fill={mc} opacity="0.9"/>
                  {/* Label on hover or active */}
                  {(isHov || isActive) && (
                    <g>
                      <rect
                        x={pos.x-45} y={pos.y+R+3}
                        width={90} height={14} rx="4"
                        fill={isDark ? 'rgba(20,13,46,0.92)' : 'rgba(255,247,251,0.95)'}
                        stroke={isDark ? 'rgba(124,58,237,0.3)' : 'rgba(176,127,212,0.3)'}
                        strokeWidth="0.5"
                      />
                      <text x={pos.x} y={pos.y+R+13} textAnchor="middle"
                        fill={isDark ? '#E2D9F3' : '#2D1B4E'}
                        fontSize="8.5" fontFamily="DM Sans, system-ui">
                        {e.title?.length > 13 ? e.title.slice(0,12)+'…' : e.title}
                      </text>
                    </g>
                  )}
                </motion.g>
              );
            })}
          </g>
        </g>

        {/* Hint text — fixed, outside transform */}
        <g>
          <text x="10" y={svgSize.h - 8}
            fill={isDark ? '#4A3B6A' : '#C9B8D8'} fontSize="7.5" fontFamily="DM Sans, system-ui">
            ✦ Cuộn để zoom · Kéo để di chuyển · Click node để mở
          </text>
        </g>
      </svg>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════
   MARKDOWN TOOLBAR
   ══════════════════════════════════════════════════════════════ */
function ToolbarButton({ icon, title, onClick }) {
  return (
    <motion.button
      type="button"
      title={title}
      onClick={onClick}
      whileHover={{ scale: 1.12 }}
      whileTap={{ scale: 0.92 }}
      className="flex items-center justify-center rounded-lg"
      style={{
        width: 28, height: 28,
        color: 'var(--color-text-muted)',
        background: 'transparent',
        border: '1px solid transparent',
        transition: 'all 0.15s',
      }}
      onMouseEnter={e => {
        e.currentTarget.style.background = 'var(--color-accent-subtle)';
        e.currentTarget.style.color = 'var(--color-accent)';
        e.currentTarget.style.borderColor = 'var(--color-border-subtle)';
      }}
      onMouseLeave={e => {
        e.currentTarget.style.background = 'transparent';
        e.currentTarget.style.color = 'var(--color-text-muted)';
        e.currentTarget.style.borderColor = 'transparent';
      }}
    >
      {icon}
    </motion.button>
  );
}

function execWysiwyg(command, value = null) {
  document.execCommand(command, false, value);
}

function insertWikilink() {
  const selection = window.getSelection();
  if (!selection.rangeCount) return;
  const range = selection.getRangeAt(0);
  const text = range.toString();
  document.execCommand('insertText', false, `[[${text}]]`);
}

const wysiwygStyles = `
  .wysiwyg-editor h3 { font-family: var(--font-display); font-size: 1.15rem; margin-top: 0.8em; margin-bottom: 0.4em; }
  .wysiwyg-editor blockquote { border-left: 2px solid var(--color-accent); margin: 0.5em 0; padding: 0.25em 0.75em; color: var(--color-text-muted); font-style: italic; }
  .wysiwyg-editor ul { list-style-type: disc; padding-left: 1.5em; margin: 0.5em 0; }
  .wysiwyg-editor b, .wysiwyg-editor strong { font-weight: 600; color: var(--color-text-primary); }
  .wysiwyg-editor i, .wysiwyg-editor em { font-style: italic; }
  .wysiwyg-editor div { margin: 0.25em 0; }
`;

/* ══════════════════════════════════════════════════════════════
   MAIN DiaryPage
   ══════════════════════════════════════════════════════════════ */
export default function DiaryPage() {
  const { user } = useAuthStore();
  const { lang, theme } = useThemeStore();
  const isDark = theme === 'dark';

  // Data state
  const [entries, setEntries] = useState([]);
  const [folders, setFolders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);

  // UI state
  const [activeEntry, setActiveEntry] = useState(null);
  const [selectedFolder, setSelectedFolder] = useState(null); // null = All
  const [showGraph, setShowGraph] = useState(true);
  const [newFolderInput, setNewFolderInput] = useState('');
  const [showNewFolder, setShowNewFolder] = useState(false);
  const [toast, setToast] = useState(null);

  // Editor state
  const [editorTitle, setEditorTitle] = useState('');
  const [editorContent, setEditorContent] = useState('');
  const [editorFolder, setEditorFolder] = useState('');

  const textareaRef = useRef(null);
  const autoSaveTimer = useRef(null);

  /* ── Data Loading ───────────────────────────────────────── */
  const loadData = useCallback(async () => {
    if (!user?.username) return;
    try {
      setLoading(true);
      const [eRes, fRes] = await Promise.all([
        diaryAPI.getEntries(user.username),
        diaryAPI.getFolders(user.username),
      ]);
      setEntries(eRes.data || []);
      setFolders(fRes.data || []);
    } catch { /* silent */ }
    finally { setLoading(false); }
  }, [user]);

  useEffect(() => { loadData(); }, [loadData]);

  // Inject content when opening an entry
  useEffect(() => {
    if (textareaRef.current && activeEntry !== null) {
      if (textareaRef.current.innerHTML !== editorContent) {
        textareaRef.current.innerHTML = editorContent;
      }
    }
  }, [activeEntry?.id]);

  /* ── Toast helper ───────────────────────────────────────── */
  const showToast = (msg, type = 'info') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  /* ── Load entry into editor ─────────────────────────────── */
  const openEntry = (entry) => {
    setActiveEntry(entry);
    setEditorTitle(entry.title || '');
    setEditorContent(entry.content || '');
    setEditorMood(entry.mood || 'Calm');
    setEditorFolder(entry.folder || '');
    setPreview(false);
  };

  /* ── New entry ──────────────────────────────────────────── */
  const newEntry = () => {
    setActiveEntry({ id: null, ai_insight: '' });
    setEditorTitle('');
    setEditorContent('');
    setEditorFolder(selectedFolder || '');
    if (textareaRef.current) textareaRef.current.innerHTML = '';
    setTimeout(() => textareaRef.current?.focus(), 100);
  };

  /* ── Save ───────────────────────────────────────────────── */
  const saveEntry = async ({ withAI = false } = {}) => {
    if (!editorTitle.trim() && !editorContent.trim()) return;
    setSaving(true);
    if (withAI) setAiLoading(true);
    try {
      const res = await diaryAPI.createEntry(user.username, {
        id: activeEntry?.id || null,
        title: editorTitle || 'Không tiêu đề',
        content: editorContent,
        mood: editorMood,
        folder: editorFolder,
        skip_ai: !withAI,
      });
      const saved = res.data?.entry;
      if (saved) {
        setActiveEntry(saved);
        setEntries(prev => {
          const idx = prev.findIndex(e => e.id === saved.id);
          if (idx >= 0) { const n=[...prev]; n[idx]=saved; return n; }
          return [saved, ...prev];
        });
        showToast(withAI ? '✦ Đã lưu với AI soi chiếu' : '✓ Đã lưu', 'success');
      }
    } catch { showToast('Lỗi khi lưu', 'error'); }
    finally { setSaving(false); setAiLoading(false); }
  };

  /* ── Auto-save on content change ────────────────────────── */
  const handleContentChange = (val) => {
    setEditorContent(val);
    if (autoSaveTimer.current) clearTimeout(autoSaveTimer.current);
    autoSaveTimer.current = setTimeout(() => {
      if (activeEntry !== null) saveEntry({ withAI: false });
    }, 4000);
  };

  /* ── Delete entry ───────────────────────────────────────── */
  const deleteEntry = async (entry) => {
    if (!entry?.id) return;
    try {
      await diaryAPI.deleteEntry(user.username, entry.id);
      setEntries(prev => prev.filter(e => e.id !== entry.id));
      if (activeEntry?.id === entry.id) setActiveEntry(null);
      showToast('Đã xóa bài viết', 'info');
    } catch { showToast('Lỗi khi xóa', 'error'); }
  };

  /* ── Create folder ──────────────────────────────────────── */
  const createFolder = async () => {
    if (!newFolderInput.trim()) return;
    try {
      await diaryAPI.createFolder(user.username, { name: newFolderInput.trim() });
      setFolders(prev => [...prev, newFolderInput.trim()]);
      setNewFolderInput('');
      setShowNewFolder(false);
    } catch { showToast('Lỗi tạo folder', 'error'); }
  };

  /* ── Delete folder ──────────────────────────────────────── */
  const deleteFolder = async (name) => {
    try {
      await diaryAPI.deleteFolder(user.username, name);
      setFolders(prev => prev.filter(f => f !== name));
      setEntries(prev => prev.filter(e => e.folder !== name));
      if (selectedFolder === name) setSelectedFolder(null);
    } catch { showToast('Lỗi xóa folder', 'error'); }
  };

  /* ── Rendered entries (filtered) ────────────────────────── */
  const filteredEntries = selectedFolder
    ? entries.filter(e => e.folder === selectedFolder)
    : entries;

  /* ── No preview needed anymore ──────────────────────────── */

  return (
    <div className="h-[calc(100vh-3rem)] flex gap-3 relative overflow-hidden" style={{ borderRadius: '1.25rem' }}>
      <style>{wysiwygStyles}</style>
      {/* ── Background ───────────────────────────────────── */}
      <div
        className={`absolute inset-0 pointer-events-none ${isDark ? 'scene-bg-abyss' : 'scene-bg-sunset'}`}
        style={{ opacity: isDark ? 0.45 : 0.55, backgroundPosition: 'center 25%', borderRadius: '1.25rem' }}
      />
      <div className="absolute inset-0 pointer-events-none" style={{
        background: isDark
          ? 'linear-gradient(to bottom, transparent 10%, var(--color-bg-primary) 60%)'
          : 'linear-gradient(to bottom, transparent 15%, var(--color-bg-primary) 55%)',
        borderRadius: '1.25rem',
      }}/>

      {/* ══════════════════════════════════════════════════════
          LEFT: Vault Panel (folders + entry list)
      ══════════════════════════════════════════════════════ */}
      <motion.div
        className="relative z-10 flex flex-col flex-shrink-0"
        style={{
          width: 220,
          background: isDark ? 'rgba(13,11,26,0.88)' : 'rgba(255,247,251,0.88)',
          backdropFilter: 'blur(16px)',
          borderRight: '1px solid var(--color-border-subtle)',
          borderRadius: '1.25rem 0 0 1.25rem',
        }}
        initial={{ x: -220, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        transition={{ type: 'spring', stiffness: 220, damping: 26 }}
      >
        {/* Vault header */}
        <div className="px-4 pt-5 pb-3">
          <div className="flex items-center justify-between mb-1">
            <span className="font-display text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>
              {lang === 'en' ? 'Vault' : 'Kho nhật ký'}
            </span>
            <motion.button
              onClick={newEntry}
              whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.92 }}
              style={{ color: 'var(--color-accent)', display: 'flex', alignItems: 'center' }}
              title={lang === 'en' ? 'New entry' : 'Bài viết mới'}
            >
              {Icon.newEntry}
            </motion.button>
          </div>
          <p style={{ fontSize: '0.68rem', color: 'var(--color-text-muted)' }}>
            {entries.length} {lang === 'en' ? 'entries' : 'bài viết'}
          </p>
        </div>

        {/* Folders */}
        <div className="flex-1 overflow-y-auto px-2">
          {/* All entries */}
          <button
            onClick={() => setSelectedFolder(null)}
            className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-left mb-0.5"
            style={{
              background: selectedFolder === null ? 'var(--color-accent-subtle)' : 'transparent',
              color: selectedFolder === null ? 'var(--color-accent)' : 'var(--color-text-secondary)',
              fontSize: '0.8rem', fontWeight: selectedFolder === null ? 600 : 400,
              border: selectedFolder === null ? '1px solid var(--color-border-subtle)' : '1px solid transparent',
            }}
          >
            <span style={{ color: 'inherit', opacity: 0.7 }}>{Icon.entry}</span>
            <span>{lang === 'en' ? 'All entries' : 'Tất cả'}</span>
            <span className="ml-auto text-xs opacity-50">{entries.length}</span>
          </button>

          {/* Folder list */}
          {folders.map(f => (
            <div key={f} className="group flex items-center gap-1 mb-0.5">
              <button
                onClick={() => setSelectedFolder(f)}
                className="flex-1 flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-left"
                style={{
                  background: selectedFolder === f ? 'var(--color-accent-subtle)' : 'transparent',
                  color: selectedFolder === f ? 'var(--color-accent)' : 'var(--color-text-secondary)',
                  fontSize: '0.8rem', fontWeight: selectedFolder === f ? 600 : 400,
                  border: selectedFolder === f ? '1px solid var(--color-border-subtle)' : '1px solid transparent',
                }}
              >
                <span style={{ color: 'var(--color-accent)', opacity: 0.75 }}>{Icon.folder}</span>
                <span className="truncate">{f}</span>
                <span className="ml-auto text-xs opacity-50">{entries.filter(e=>e.folder===f).length}</span>
              </button>
              <button
                onClick={() => deleteFolder(f)}
                className="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded"
                style={{ color: 'var(--color-text-muted)', flexShrink: 0 }}
              >
                {Icon.trash}
              </button>
            </div>
          ))}

          {/* New folder button */}
          {showNewFolder ? (
            <div className="flex items-center gap-1 px-2 py-1">
              <input
                autoFocus
                value={newFolderInput}
                onChange={e => setNewFolderInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' ? createFolder() : e.key === 'Escape' && setShowNewFolder(false)}
                placeholder={lang === 'en' ? 'Folder name…' : 'Tên folder…'}
                style={{
                  flex: 1, fontSize: '0.78rem', background: 'var(--color-accent-subtle)',
                  border: '1px solid var(--color-border)', borderRadius: 6, padding: '3px 6px',
                  color: 'var(--color-text-primary)', outline: 'none',
                }}
              />
              <button onClick={createFolder} style={{ color: 'var(--color-accent)', display: 'flex' }}>{Icon.save}</button>
            </div>
          ) : (
            <button
              onClick={() => setShowNewFolder(true)}
              className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg mt-1"
              style={{ color: 'var(--color-text-muted)', fontSize: '0.75rem', background: 'transparent' }}
            >
              <span>+</span> {lang === 'en' ? 'New folder' : 'Folder mới'}
            </button>
          )}

          <div style={{ height: 1, background: 'var(--color-border-subtle)', margin: '0.5rem 0.5rem' }}/>

          {/* Entry list */}
          {loading ? (
            <div className="flex justify-center py-6">
              <motion.div animate={{ rotate: 360 }} transition={{ duration: 1.4, repeat: Infinity, ease: 'linear' }}
                style={{ width: 18, height: 18, border: '2px solid var(--color-accent)', borderTopColor: 'transparent', borderRadius: '50%' }}/>
            </div>
          ) : (
            <div className="space-y-0.5">
              <AnimatePresence>
                {filteredEntries.map(e => (
                  <motion.div
                    key={e.id}
                    initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -8 }}
                    className="group flex items-start gap-1"
                  >
                    <button
                      onClick={() => openEntry(e)}
                      className="flex-1 text-left px-2.5 py-2 rounded-lg"
                      style={{
                        background: activeEntry?.id === e.id ? 'var(--color-accent-light)' : 'transparent',
                        border: activeEntry?.id === e.id ? '1px solid var(--color-border-subtle)' : '1px solid transparent',
                      }}
                    >
                      <div className="flex items-center gap-1.5 mb-0.5">
                        <span style={{ color: moodColor(e.mood, isDark), flexShrink: 0 }}>{Icon.entry}</span>
                        <span className="truncate" style={{
                          fontSize: '0.78rem', fontWeight: activeEntry?.id === e.id ? 600 : 400,
                          color: 'var(--color-text-primary)',
                        }}>
                          {e.title || '(Không tiêu đề)'}
                        </span>
                      </div>
                      <p className="truncate" style={{ fontSize: '0.66rem', color: 'var(--color-text-muted)', paddingLeft: '1rem' }}>
                        {e.content?.slice(0, 36)}…
                      </p>
                    </button>
                    <button
                      onClick={() => deleteEntry(e)}
                      className="opacity-0 group-hover:opacity-100 transition-opacity p-1 mt-1 rounded"
                      style={{ color: 'var(--color-text-muted)', flexShrink: 0 }}
                    >
                      {Icon.trash}
                    </button>
                  </motion.div>
                ))}
              </AnimatePresence>
              {filteredEntries.length === 0 && !loading && (
                <p className="text-center py-6" style={{ fontSize: '0.72rem', color: 'var(--color-text-muted)' }}>
                  {lang === 'en' ? 'No entries yet…' : 'Chưa có bài viết…'}
                </p>
              )}
            </div>
          )}
        </div>
      </motion.div>

      {/* ══════════════════════════════════════════════════════
          CENTER: Editor
      ══════════════════════════════════════════════════════ */}
      <div className="relative z-10 flex-1 flex flex-col min-w-0 py-4 pr-2">
        {activeEntry === null ? (
          /* Welcome state */
          <motion.div
            className="flex-1 flex flex-col items-center justify-center gap-6"
            initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
          >
            <motion.div
              animate={{ rotate: [0, 12, -12, 0], scale: [1, 1.06, 1] }}
              transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
            >
              <svg width="72" height="72" viewBox="0 0 72 72" fill="none">
                <defs>
                  <radialGradient id="wg" cx="50%" cy="40%" r="60%">
                    <stop offset="0%" stopColor={isDark ? '#A78BFA' : '#C9A4F5'} stopOpacity="0.4"/>
                    <stop offset="100%" stopColor="transparent"/>
                  </radialGradient>
                </defs>
                <circle cx="36" cy="36" r="32" fill="url(#wg)" stroke={isDark ? '#7C3AED' : '#C9A4F5'} strokeWidth="0.8" opacity="0.5"/>
                <path d="M36 10 L39.5 24.5 L54 28 L39.5 31.5 L36 46 L32.5 31.5 L18 28 L32.5 24.5 Z"
                  fill={isDark ? '#7C3AED' : '#C9A4F5'} opacity="0.7"/>
                <circle cx="36" cy="28" r="3.5" fill="white" opacity="0.7"/>
                {/* Crescent */}
                <path d="M50 48 A8 8 0 0 1 50 64 A6 6 0 0 0 50 48 Z" fill={isDark ? '#A78BFA' : '#F4A8C6'} opacity="0.6"/>
                <circle cx="56" cy="52" r="1.5" fill={isDark ? '#A78BFA' : '#F4A8C6'} opacity="0.5"/>
              </svg>
            </motion.div>
            <div className="text-center">
              <h2 className="font-display text-2xl mb-2" style={{ color: 'var(--color-text-primary)' }}>
                {lang === 'en' ? 'Diary Vault' : 'Nhật ký · Tri thức'}
              </h2>
              <p style={{ color: 'var(--color-text-muted)', fontSize: '0.875rem', maxWidth: 320 }}>
                {lang === 'en'
                  ? 'Select an entry from the vault, or create a new one to begin reflecting.'
                  : 'Chọn một bài viết từ kho, hoặc tạo mới để bắt đầu soi chiếu.'}
              </p>
            </div>
            <motion.button
              onClick={newEntry}
              className="btn-primary flex items-center gap-2"
              whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.97 }}
            >
              <span>{Icon.newEntry}</span>
              {lang === 'en' ? 'New Entry' : 'Bài viết mới'}
            </motion.button>
          </motion.div>
        ) : (
          <motion.div
            className="flex-1 flex flex-col gap-3 min-h-0"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.3 }}
          >
            {/* Editor header */}
            <div className="flex items-center gap-2 flex-shrink-0">
              <button onClick={() => setActiveEntry(null)}
                style={{ color: 'var(--color-text-muted)', display: 'flex', padding: 4 }}>
                {Icon.back}
              </button>

              {/* Title input */}
              <input
                value={editorTitle}
                onChange={e => setEditorTitle(e.target.value)}
                placeholder={lang === 'en' ? 'Untitled…' : 'Tiêu đề…'}
                className="flex-1 font-display text-2xl bg-transparent outline-none border-none"
                style={{
                  color: 'var(--color-text-primary)',
                  fontFamily: 'var(--font-display)',
                  fontSize: '1.5rem',
                  fontWeight: 600,
                }}
              />

              {/* Mood selector removed per user request */}

              {/* Folder selector */}
              <select
                value={editorFolder}
                onChange={e => setEditorFolder(e.target.value)}
                style={{
                  fontSize: '0.75rem', background: 'var(--color-accent-subtle)',
                  color: 'var(--color-text-secondary)', border: '1px solid var(--color-border)',
                  borderRadius: 8, padding: '3px 6px', outline: 'none', maxWidth: 110,
                }}
              >
                <option value="">{lang === 'en' ? 'No folder' : 'Chưa phân loại'}</option>
                {folders.map(f => <option key={f} value={f}>{f}</option>)}
              </select>
            </div>

            {/* Markdown toolbar */}
            <div className="flex items-center gap-0.5 px-1 py-1 flex-shrink-0"
              style={{
                background: isDark ? 'rgba(20,13,46,0.6)' : 'rgba(255,247,251,0.7)',
                backdropFilter: 'blur(8px)',
                borderRadius: 10,
                border: '1px solid var(--color-border-subtle)',
              }}
            >
              <ToolbarButton icon={Icon.heading} title="Heading" onClick={() => execWysiwyg('formatBlock', 'H3')}/>
              <ToolbarButton icon={Icon.bold} title="Bold" onClick={() => execWysiwyg('bold')}/>
              <ToolbarButton icon={Icon.italic} title="Italic" onClick={() => execWysiwyg('italic')}/>
              <ToolbarButton icon={Icon.quote} title="Quote" onClick={() => execWysiwyg('formatBlock', 'BLOCKQUOTE')}/>
              <ToolbarButton icon={Icon.list} title="List" onClick={() => execWysiwyg('insertUnorderedList')}/>
              <div style={{ width: 1, height: 18, background: 'var(--color-border)', margin: '0 4px' }}/>
              {/* Wikilink */}
              <ToolbarButton
                icon={<svg width="13" height="13" viewBox="0 0 13 13" fill="none" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"><rect x="1" y="3" width="4.5" height="7" rx="1"/><rect x="7.5" y="3" width="4.5" height="7" rx="1"/><line x1="5.5" y1="6.5" x2="7.5" y2="6.5"/></svg>}
                title="Wikilink [[…]]"
                onClick={insertWikilink}
              />
              <div className="flex-1"/>
            </div>

            {/* Editor area */}
            <div className="flex-1 min-h-0 flex flex-col gap-3">
              <div className="flex-1 min-h-0 relative">
                  <div
                    ref={textareaRef}
                    contentEditable
                    onInput={e => handleContentChange(e.currentTarget.innerHTML)}
                    className="w-full h-full overflow-y-auto px-4 py-3 rounded-xl outline-none border-none wysiwyg-editor"
                    style={{
                      background: isDark ? 'rgba(20,13,46,0.6)' : 'rgba(255,247,251,0.7)',
                      backdropFilter: 'blur(12px)',
                      border: '1px solid var(--color-border-subtle)',
                      color: 'var(--color-text-primary)',
                      fontFamily: 'var(--font-sans)',
                      fontSize: '0.9375rem',
                      lineHeight: 1.75,
                      caretColor: 'var(--color-accent)',
                    }}
                  />
              </div>

              {/* AI Insight card */}
              <AnimatePresence>
                {activeEntry?.ai_insight && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}
                    className="flex-shrink-0 px-4 py-3 rounded-xl"
                    style={{
                      background: isDark ? 'rgba(124,58,237,0.08)' : 'rgba(201,164,245,0.12)',
                      border: '1px solid var(--color-border-subtle)',
                      backdropFilter: 'blur(8px)',
                    }}
                  >
                    <div className="flex items-center gap-2 mb-1.5">
                      <span style={{ color: 'var(--color-accent)' }}>{Icon.ai}</span>
                      <span style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--color-accent)', letterSpacing: '0.04em' }}>
                        {lang === 'en' ? 'SOCRATIC REFLECTION' : 'SOI CHIẾU SOCRATIC'}
                      </span>
                      {aiLoading && (
                        <motion.div animate={{ rotate: 360 }} transition={{ duration: 1.2, repeat: Infinity, ease: 'linear' }}
                          style={{ width: 12, height: 12, border: '1.5px solid var(--color-accent)', borderTopColor: 'transparent', borderRadius: '50%', marginLeft: 4 }}/>
                      )}
                    </div>
                    <p style={{ fontSize: '0.875rem', color: 'var(--color-text-secondary)', lineHeight: 1.65, fontStyle: 'italic' }}>
                      {activeEntry.ai_insight}
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Action buttons */}
              <div className="flex items-center gap-2 flex-shrink-0">
                <motion.button
                  onClick={() => saveEntry({ withAI: true })}
                  disabled={saving || !editorContent.trim()}
                  whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
                  className="btn-primary flex items-center gap-1.5 text-sm"
                  style={{ padding: '0.5rem 1rem' }}
                >
                  <span>{Icon.ai}</span>
                  {aiLoading ? (lang === 'en' ? 'Reflecting…' : 'Đang soi chiếu…')
                    : (lang === 'en' ? 'Save & Reflect' : 'Save & Reflect')}
                </motion.button>

                <span style={{ marginLeft: 'auto', fontSize: '0.7rem', color: 'var(--color-text-muted)' }}>
                  {editorContent.split(/\s+/).filter(Boolean).length} {lang === 'en' ? 'words' : 'từ'}
                </span>
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* ══════════════════════════════════════════════════════
          RIGHT: Knowledge Graph
      ══════════════════════════════════════════════════════ */}
      <AnimatePresence>
        {showGraph && (
          <motion.div
            key="graph-panel"
            className="relative z-10 flex-shrink-0 flex flex-col"
            style={{ width: 280 }}
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 280, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 220, damping: 28 }}
          >
            <div className="glass-card flex flex-col h-full" style={{ padding: '1rem', gap: '0.75rem', overflow: 'hidden' }}>
              {/* Graph header */}
              <div className="flex items-center justify-between flex-shrink-0">
                <div>
                  <h3 className="font-display text-sm font-semibold" style={{ color: 'var(--color-text-primary)' }}>
                    {lang === 'en' ? 'Knowledge Graph' : 'Đồ thị tri thức'}
                  </h3>
                  <p style={{ fontSize: '0.68rem', color: 'var(--color-text-muted)' }}>
                    {lang === 'en' ? 'Obsidian-style · all entries' : 'Phong cách Obsidian · tất cả bài viết'}
                  </p>
                </div>
                <span style={{ color: 'var(--color-accent)', opacity: 0.7 }}>{Icon.graph}</span>
              </div>

              {/* Mood legend removed per user request */}

              <div style={{ height: 1, background: 'var(--color-border-subtle)' }}/>

              {/* Graph */}
              <div className="flex-1 overflow-hidden rounded-xl" style={{
                border: '1px solid var(--color-border-subtle)',
                background: isDark ? 'rgba(13,11,26,0.4)' : 'rgba(254,243,248,0.4)',
                minHeight: 260,
              }}>
                <KnowledgeGraph
                  entries={entries}
                  isDark={isDark}
                  activeId={activeEntry?.id}
                  onSelectEntry={openEntry}
                />
              </div>

              {/* Stats */}
              <div className="flex justify-between flex-shrink-0" style={{ fontSize: '0.68rem', color: 'var(--color-text-muted)' }}>
                <span>✦ {entries.length} {lang === 'en' ? 'nodes' : 'nút'}</span>
                <span>
                  {entries.filter(e => (e.content || '').includes('[[')).length} {lang === 'en' ? 'wikilinks' : 'wikilinks'}
                </span>
                <span>{folders.length} {lang === 'en' ? 'folders' : 'folder'}</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Graph toggle button */}
      <motion.button
        onClick={() => setShowGraph(v => !v)}
        className="absolute right-4 top-4 z-20 flex items-center gap-1.5 px-2.5 py-1.5 rounded-full text-xs font-semibold"
        whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.96 }}
        style={{
          background: showGraph ? 'var(--color-accent)' : 'var(--color-accent-subtle)',
          color: showGraph ? 'white' : 'var(--color-accent)',
          border: '1px solid var(--color-border)',
        }}
      >
        {Icon.graph}
        {showGraph ? (lang === 'en' ? 'Hide graph' : 'Ẩn đồ thị') : (lang === 'en' ? 'Graph view' : 'Đồ thị')}
      </motion.button>

      {/* Toast */}
      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 16 }}
            className="absolute bottom-4 left-1/2 -translate-x-1/2 z-50 px-4 py-2.5 rounded-xl text-sm font-medium"
            style={{
              background: isDark ? 'rgba(20,13,46,0.95)' : 'rgba(255,247,251,0.97)',
              border: `1px solid ${toast.type === 'error' ? (isDark ? '#F87171' : '#F4607E') : 'var(--color-border)'}`,
              color: toast.type === 'error' ? (isDark ? '#F87171' : '#F4607E') : 'var(--color-text-primary)',
              backdropFilter: 'blur(16px)',
              boxShadow: '0 8px 32px var(--color-shadow-strong)',
            }}
          >
            {toast.msg}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
