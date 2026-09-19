/**
 * Therapity — MindMap Canvas (v2 · Hoàng Hôn / Đại Dương theme)
 *
 * Visual language:
 *  - Light: sunset ocean palette  — lavender sky, coral sun, rose horizon
 *  - Dark:  abyss ocean palette   — midnight navy, violet stars, bioluminescence
 *
 * Node shapes: celestial gems (4-pointed diamond facets)
 * Edges:       smooth cubic Bézier wave curves
 * Background:  radial gradient sky + subtle constellation grid
 *
 * Graph data shape:
 * {
 *   nodes: [{ id, label, color }],
 *   edges: [{ source, target, label, is_contradiction }],
 *   current_step: "kham_pha" | "soi_chieu",
 *   focus_node_id: string | null
 * }
 */

import { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

/* ══════════════════════════════════════════════════════════════
   LAYOUT — radial force with golden angle spiral
   ══════════════════════════════════════════════════════════════ */
function computeLayout(nodes, edges, W = 560, H = 400) {
  if (!nodes?.length) return {};
  const cx = W / 2, cy = H / 2;
  const positions = {};

  if (nodes.length === 1) {
    positions[nodes[0].id] = { x: cx, y: cy };
    return positions;
  }

  // Build adjacency for center detection
  const degree = {};
  nodes.forEach(n => { degree[n.id] = 0; });
  (edges || []).forEach(e => {
    if (degree[e.source] !== undefined) degree[e.source]++;
    if (degree[e.target] !== undefined) degree[e.target]++;
  });

  // Node with highest degree → center
  const sorted = [...nodes].sort((a, b) => (degree[b.id] || 0) - (degree[a.id] || 0));
  positions[sorted[0].id] = { x: cx, y: cy };

  // Golden angle spiral for rest
  const GOLDEN = 2.39996; // radians
  const rest = sorted.slice(1);
  rest.forEach((node, i) => {
    const angle = i * GOLDEN;
    const ring = Math.floor(i / 6);
    const r = 100 + ring * 85;
    positions[node.id] = {
      x: Math.min(Math.max(cx + r * Math.cos(angle), 40), W - 40),
      y: Math.min(Math.max(cy + r * Math.sin(angle) * 0.7, 36), H - 36),
    };
  });

  return positions;
}

/* ══════════════════════════════════════════════════════════════
   COLOR MAPPING — design system palette
   ══════════════════════════════════════════════════════════════ */
const PALETTE = {
  light: {
    normal:       { fill: '#FFF7FB', stroke: '#C9A4F5', inner: '#B07FD4', glow: 'rgba(176,127,212,0.25)' },
    contradiction:{ fill: '#FFF0F3', stroke: '#F4607E', inner: '#E06B8A', glow: 'rgba(240,96,126,0.25)' },
    focus:        { ring: '#FFBFA3' },
    edge:         { normal: 'rgba(176,127,212,0.5)', contradiction: '#F4607E' },
    edgeLabel:    '#A98FBE',
    text:         '#2D1B4E',
    textFocus:    '#7C3AED',
    stepDot:      { kham_pha: '#6DB97B', soi_chieu: '#F4607E' },
  },
  dark: {
    normal:       { fill: '#140D2E', stroke: '#7C3AED', inner: '#A78BFA', glow: 'rgba(124,58,237,0.3)' },
    contradiction:{ fill: '#1F0D18', stroke: '#F87171', inner: '#F87171', glow: 'rgba(248,113,113,0.3)' },
    focus:        { ring: '#FFBFA3' },
    edge:         { normal: 'rgba(124,58,237,0.5)', contradiction: '#F87171' },
    edgeLabel:    '#6B5A8A',
    text:         '#E2D9F3',
    textFocus:    '#A78BFA',
    stepDot:      { kham_pha: '#6DB97B', soi_chieu: '#F87171' },
  },
};

function nodeStyle(color, isDark) {
  const p = isDark ? PALETTE.dark : PALETTE.light;
  if (!color) return p.normal;
  if (color === '#16A34A' || color.toLowerCase() === '#16a34a') return p.normal;
  if (color === '#ffb4ab' || color.toLowerCase() === '#ffb4ab') return p.contradiction;
  return p.normal;
}

/* ══════════════════════════════════════════════════════════════
   GEM NODE — 4-pointed diamond facet shape
   ══════════════════════════════════════════════════════════════ */
function gemPath(cx, cy, r) {
  // 4-pointed diamond star
  const o = r * 0.38;
  return `M ${cx} ${cy - r}
    L ${cx + o} ${cy - o}
    L ${cx + r} ${cy}
    L ${cx + o} ${cy + o}
    L ${cx} ${cy + r}
    L ${cx - o} ${cy + o}
    L ${cx - r} ${cy}
    L ${cx - o} ${cy - o}
    Z`;
}

function MindNode({ node, pos, isFocus, isDark, onHover, hovered }) {
  const style = nodeStyle(node.color, isDark);
  const p = isDark ? PALETTE.dark : PALETTE.light;
  const isHov = hovered === node.id;
  const R = isHov ? 22 : 18;
  const labelColor = (isFocus || isHov) ? p.textFocus : p.text;

  // Wrap label to 2 lines if long
  const label = node.label || '';
  const words = label.split(' ');
  let line1 = '', line2 = '';
  let cur = '';
  for (const w of words) {
    if ((cur + ' ' + w).trim().length <= 12) {
      cur = (cur + ' ' + w).trim();
    } else if (!line1) {
      line1 = cur;
      cur = w;
    } else {
      cur = cur + ' ' + w;
    }
  }
  if (!line1) { line1 = cur; line2 = ''; }
  else { line2 = cur.length > 14 ? cur.slice(0, 13) + '…' : cur; }

  return (
    <motion.g
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: 'spring', stiffness: 250, damping: 18, delay: 0.04 }}
      style={{ cursor: 'default' }}
      onMouseEnter={() => onHover(node.id)}
      onMouseLeave={() => onHover(null)}
    >
      {/* Glow aura */}
      <motion.ellipse
        cx={pos.x} cy={pos.y}
        rx={R + 10} ry={R + 6}
        fill={style.glow}
        animate={{ rx: isHov ? R + 14 : R + 10, opacity: isFocus ? [0.4, 1, 0.4] : 0.7 }}
        transition={isFocus
          ? { duration: 1.6, repeat: Infinity, ease: 'easeInOut' }
          : { duration: 0.25 }
        }
      />

      {/* Focus orbit ring */}
      {isFocus && (
        <motion.circle
          cx={pos.x} cy={pos.y}
          r={R + 14}
          fill="none"
          stroke={p.focus.ring}
          strokeWidth={1.2}
          strokeDasharray="4 4"
          opacity={0.7}
          animate={{ rotate: 360 }}
          style={{ transformOrigin: `${pos.x}px ${pos.y}px` }}
          transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
        />
      )}

      {/* Diamond gem body */}
      <motion.path
        d={gemPath(pos.x, pos.y, R)}
        fill={style.fill}
        stroke={style.stroke}
        strokeWidth={isHov ? 2.2 : 1.6}
        animate={{ d: gemPath(pos.x, pos.y, R) }}
        transition={{ type: 'spring', stiffness: 300, damping: 24 }}
        style={{ filter: isHov ? `drop-shadow(0 2px 8px ${style.glow})` : 'none' }}
      />

      {/* Inner facet highlight */}
      <path
        d={gemPath(pos.x, pos.y, R * 0.45)}
        fill={style.inner}
        opacity={0.35}
        style={{ pointerEvents: 'none' }}
      />

      {/* Center dot */}
      <circle cx={pos.x} cy={pos.y} r={3.5} fill={style.inner} opacity={0.95}/>
      <circle cx={pos.x - 2} cy={pos.y - 2} r={1.2} fill="white" opacity={0.7}/>

      {/* Label */}
      <text
        x={pos.x}
        y={pos.y + R + 14}
        textAnchor="middle"
        fill={labelColor}
        fontSize={9.5}
        fontFamily="DM Sans, system-ui, sans-serif"
        fontWeight={isFocus || isHov ? '600' : '400'}
        style={{ pointerEvents: 'none', userSelect: 'none' }}
      >
        {line1}
      </text>
      {line2 && (
        <text
          x={pos.x}
          y={pos.y + R + 26}
          textAnchor="middle"
          fill={labelColor}
          fontSize={9.5}
          fontFamily="DM Sans, system-ui, sans-serif"
          fontWeight={isFocus || isHov ? '600' : '400'}
          style={{ pointerEvents: 'none', userSelect: 'none' }}
          opacity={0.85}
        >
          {line2}
        </text>
      )}
    </motion.g>
  );
}

/* ══════════════════════════════════════════════════════════════
   EDGE — cubic Bézier wave curve
   ══════════════════════════════════════════════════════════════ */
function MindEdge({ edge, positions, isDark, idx }) {
  const from = positions[edge.source];
  const to   = positions[edge.target];
  if (!from || !to) return null;

  const p = isDark ? PALETTE.dark : PALETTE.light;

  // Perpendicular offset for curve — alternate above/below by index
  const dx = to.x - from.x, dy = to.y - from.y;
  const len = Math.sqrt(dx * dx + dy * dy) || 1;
  const perp = { x: -dy / len, y: dx / len };
  const bend = 28 * (idx % 2 === 0 ? 1 : -1);
  const cx1 = from.x + dx * 0.35 + perp.x * bend;
  const cy1 = from.y + dy * 0.35 + perp.y * bend;
  const cx2 = from.x + dx * 0.65 + perp.x * bend;
  const cy2 = from.y + dy * 0.65 + perp.y * bend;

  const path = `M ${from.x} ${from.y} C ${cx1} ${cy1} ${cx2} ${cy2} ${to.x} ${to.y}`;
  const midX = from.x + dx * 0.5 + perp.x * bend * 0.7;
  const midY = from.y + dy * 0.5 + perp.y * bend * 0.7;

  const stroke = edge.is_contradiction
    ? p.edge.contradiction
    : p.edge.normal;

  return (
    <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 + idx * 0.04 }}>
      {/* Edge glow (contradiction only) */}
      {edge.is_contradiction && (
        <path d={path} stroke={stroke} strokeWidth={5} fill="none" opacity={0.12} strokeLinecap="round"/>
      )}

      {/* Main edge */}
      <path
        d={path}
        stroke={stroke}
        strokeWidth={edge.is_contradiction ? 1.8 : 1.2}
        strokeDasharray={edge.is_contradiction ? '5 3.5' : 'none'}
        fill="none"
        strokeLinecap="round"
        opacity={0.85}
      />

      {/* Arrow tip — small triangle at target */}
      {!edge.is_contradiction && (() => {
        // Direction at end of cubic: derivative at t=1 → 3*(P3-P2) → P3=to, P2=(cx2,cy2)
        const ex = to.x - cx2, ey = to.y - cy2;
        const el = Math.sqrt(ex * ex + ey * ey) || 1;
        const nx = ex / el, ny = ey / el;
        const ax = to.x - nx * 12, ay = to.y - ny * 12;
        const bx = ax - ny * 4, by = ay + nx * 4;
        const cx_ = ax + ny * 4, cy_ = ay - nx * 4;
        return <polygon points={`${to.x},${to.y} ${bx},${by} ${cx_},${cy_}`} fill={stroke} opacity={0.6}/>;
      })()}

      {/* Edge label */}
      {edge.label && (
        <text
          x={midX} y={midY - 5}
          textAnchor="middle"
          fill={p.edgeLabel}
          fontSize={8.5}
          fontFamily="DM Sans, system-ui"
          style={{ pointerEvents: 'none' }}
        >
          {edge.label.length > 16 ? edge.label.slice(0, 14) + '…' : edge.label}
        </text>
      )}
    </motion.g>
  );
}

/* ══════════════════════════════════════════════════════════════
   CONSTELLATION BACKGROUND GRID
   ══════════════════════════════════════════════════════════════ */
function ConstellationBg({ w, h, isDark }) {
  const stars = Array.from({ length: isDark ? 28 : 14 }, (_, i) => ({
    x: ((i * 127 + 43) % (w - 20)) + 10,
    y: ((i * 83 + 21)  % (h - 20)) + 10,
    r: [1, 1.2, 1.5, 0.8][i % 4],
    op: 0.15 + (i % 5) * 0.07,
  }));

  return (
    <g style={{ pointerEvents: 'none' }}>
      {stars.map((s, i) => (
        <circle key={i} cx={s.x} cy={s.y} r={s.r}
          fill={isDark ? '#E2D9F3' : '#C9A4F5'} opacity={s.op}/>
      ))}
      {/* A few constellation line pairs */}
      {stars.slice(0, 6).map((s, i) => {
        if (i === 0) return null;
        const prev = stars[i - 1];
        const dist = Math.sqrt((s.x - prev.x) ** 2 + (s.y - prev.y) ** 2);
        if (dist > 120) return null;
        return (
          <line key={`cl-${i}`}
            x1={prev.x} y1={prev.y} x2={s.x} y2={s.y}
            stroke={isDark ? '#A78BFA' : '#C9A4F5'}
            strokeWidth={0.4}
            opacity={0.18}
          />
        );
      })}
    </g>
  );
}

/* ══════════════════════════════════════════════════════════════
   EMPTY STATE
   ══════════════════════════════════════════════════════════════ */
function EmptyState({ isDark }) {
  const p = isDark ? PALETTE.dark : PALETTE.light;
  return (
    <div className="flex flex-col items-center justify-center gap-3 h-full" style={{ minHeight: 200 }}>
      <motion.div
        animate={{ rotate: [0, 15, -15, 0], scale: [1, 1.08, 1] }}
        transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
      >
        <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
          <defs>
            <radialGradient id="eg" cx="50%" cy="40%" r="60%">
              <stop offset="0%" stopColor={isDark ? '#A78BFA' : '#C9A4F5'} stopOpacity="0.3"/>
              <stop offset="100%" stopColor="transparent"/>
            </radialGradient>
          </defs>
          <circle cx="28" cy="28" r="26" fill="url(#eg)" stroke={isDark ? '#7C3AED' : '#C9A4F5'} strokeWidth="0.8" opacity="0.5"/>
          {/* 3 gem nodes */}
          {[[28, 14], [14, 36], [42, 36]].map(([x, y], i) => (
            <g key={i}>
              <path d={gemPath(x, y, 7)} fill={isDark ? '#1A1035' : '#FFF7FB'}
                stroke={isDark ? '#7C3AED' : '#C9A4F5'} strokeWidth="1.2" opacity="0.7"/>
              <circle cx={x} cy={y} r="2" fill={isDark ? '#A78BFA' : '#B07FD4'} opacity="0.8"/>
            </g>
          ))}
          {/* Connecting lines */}
          <line x1="28" y1="20" x2="18" y2="30" stroke={isDark ? 'rgba(124,58,237,0.4)' : 'rgba(176,127,212,0.4)'} strokeWidth="0.8"/>
          <line x1="28" y1="20" x2="38" y2="30" stroke={isDark ? 'rgba(124,58,237,0.4)' : 'rgba(176,127,212,0.4)'} strokeWidth="0.8"/>
          <line x1="18" y1="30" x2="38" y2="30" stroke={isDark ? 'rgba(124,58,237,0.4)' : 'rgba(176,127,212,0.4)'} strokeWidth="0.8" strokeDasharray="2 2"/>
        </svg>
      </motion.div>
      <div className="text-center space-y-0.5">
        <p style={{ color: isDark ? '#6B5A8A' : '#A98FBE', fontSize: '0.8rem', fontWeight: 500 }}>
          Bản đồ tư duy
        </p>
        <p style={{ color: isDark ? '#4A3B6A' : '#C9B8D8', fontSize: '0.72rem' }}>
          Sẽ hình thành sau khi bạn chia sẻ…
        </p>
      </div>
    </div>
  );
}

/* ══════════════════════════════════════════════════════════════
   MAIN MINDMAP
   ══════════════════════════════════════════════════════════════ */
export default function MindMap({ graphData, isLoading, isDark, className = '' }) {
  const [hovered, setHovered] = useState(null);
  const containerRef = useRef(null);
  const [svgSize, setSvgSize] = useState({ w: 340, h: 380 });

  useEffect(() => {
    if (!containerRef.current) return;
    const ro = new ResizeObserver(([entry]) => {
      setSvgSize({
        w: Math.max(200, entry.contentRect.width),
        h: Math.max(280, entry.contentRect.height),
      });
    });
    ro.observe(containerRef.current);
    return () => ro.disconnect();
  }, []);

  const p = isDark ? PALETTE.dark : PALETTE.light;
  const hasData = graphData?.nodes?.length > 0;
  const nodes = graphData?.nodes || [];
  const edges = graphData?.edges || [];
  const focusId = graphData?.focus_node_id;
  const step = graphData?.current_step;

  // Scale positions to SVG viewport
  const BASE_W = 560, BASE_H = 400;
  const rawPos = computeLayout(nodes, edges, BASE_W, BASE_H);
  const positions = {};
  const PAD = 44;
  Object.entries(rawPos).forEach(([id, pos]) => {
    positions[id] = {
      x: PAD + ((pos.x - PAD) / (BASE_W - PAD * 2)) * (svgSize.w - PAD * 2),
      y: PAD + ((pos.y - PAD) / (BASE_H - PAD * 2)) * (svgSize.h - PAD * 2),
    };
  });

  return (
    <div ref={containerRef} className={`relative ${className}`} style={{ minHeight: 280 }}>

      {/* ── SVG Canvas ──────────────────────────────── */}
      <svg width="100%" height={svgSize.h} style={{ overflow: 'visible', borderRadius: '0.75rem' }}>
        <defs>
          {/* Sunset sky gradient (light) */}
          <linearGradient id="mmBgLight" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%"   stopColor="#EDD9F8" stopOpacity="0.55"/>
            <stop offset="50%"  stopColor="#FFDCE9" stopOpacity="0.45"/>
            <stop offset="100%" stopColor="#FFE8D6" stopOpacity="0.35"/>
          </linearGradient>
          {/* Abyss night gradient (dark) */}
          <linearGradient id="mmBgDark" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%"   stopColor="#100A25" stopOpacity="0.85"/>
            <stop offset="60%"  stopColor="#0D0B1A" stopOpacity="0.9"/>
            <stop offset="100%" stopColor="#080612" stopOpacity="0.95"/>
          </linearGradient>
          {/* Horizon glow */}
          <radialGradient id="mmGlow" cx="50%" cy="60%" r="50%">
            <stop offset="0%"   stopColor={isDark ? 'rgba(124,58,237,0.12)' : 'rgba(255,191,163,0.25)'}/>
            <stop offset="100%" stopColor="transparent"/>
          </radialGradient>
          {/* Clip rounded rect */}
          <clipPath id="mmClip">
            <rect x="0" y="0" width={svgSize.w} height={svgSize.h} rx="12" ry="12"/>
          </clipPath>
        </defs>

        {/* Background */}
        <rect
          x="0" y="0" width={svgSize.w} height={svgSize.h} rx="12"
          fill={`url(#${isDark ? 'mmBgDark' : 'mmBgLight'})`}
        />
        <rect x="0" y="0" width={svgSize.w} height={svgSize.h} rx="12" fill="url(#mmGlow)"/>

        <g clipPath="url(#mmClip)">
          {/* Constellation dots */}
          <ConstellationBg w={svgSize.w} h={svgSize.h} isDark={isDark}/>

          {/* Horizon line (light only) */}
          {!isDark && (
            <line
              x1="0" y1={svgSize.h * 0.65}
              x2={svgSize.w} y2={svgSize.h * 0.65}
              stroke="rgba(244,168,198,0.25)" strokeWidth="1"
            />
          )}

          {hasData && (
            <>
              {/* Edges */}
              {edges.map((edge, i) => (
                <MindEdge key={i} edge={edge} positions={positions} isDark={isDark} idx={i}/>
              ))}
              {/* Nodes */}
              {nodes.map(node =>
                positions[node.id] ? (
                  <MindNode
                    key={node.id}
                    node={node}
                    pos={positions[node.id]}
                    isFocus={node.id === focusId}
                    isDark={isDark}
                    onHover={setHovered}
                    hovered={hovered}
                  />
                ) : null
              )}
            </>
          )}
        </g>

        {/* Step indicator badge */}
        {step && (
          <g>
            <rect x="8" y="8" width={step === 'soi_chieu' ? 78 : 72} height="20" rx="10"
              fill={isDark ? 'rgba(20,13,46,0.85)' : 'rgba(255,247,251,0.85)'}
              stroke={isDark ? 'rgba(124,58,237,0.3)' : 'rgba(199,154,245,0.3)'}
              strokeWidth="0.8"
            />
            <circle cx="20" cy="18" r="4"
              fill={p.stepDot[step] || '#6DB97B'}
            />
            <text x="28" y="22" fill={isDark ? '#A78BFA' : '#7C3AED'}
              fontSize="9" fontFamily="DM Sans, system-ui" fontWeight="500">
              {step === 'soi_chieu' ? 'Soi chiếu' : 'Khám phá'}
            </text>
          </g>
        )}
      </svg>

      {/* Empty state (overlay) */}
      {!hasData && !isLoading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <EmptyState isDark={isDark}/>
        </div>
      )}

      {/* Loading spinner */}
      <AnimatePresence>
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="absolute inset-0 flex flex-col items-center justify-center gap-2 rounded-xl z-20"
            style={{
              background: isDark ? 'rgba(13,11,26,0.7)' : 'rgba(254,243,248,0.7)',
              backdropFilter: 'blur(6px)',
            }}
          >
            {/* Celestial spinner */}
            <svg width="36" height="36" viewBox="0 0 36 36">
              <motion.circle
                cx="18" cy="18" r="14"
                fill="none"
                stroke={isDark ? '#7C3AED' : '#C9A4F5'}
                strokeWidth="1.5"
                strokeDasharray="20 60"
                animate={{ rotate: 360 }}
                style={{ transformOrigin: '18px 18px' }}
                transition={{ duration: 1.4, repeat: Infinity, ease: 'linear' }}
              />
              <motion.path
                d={gemPath(18, 18, 6)}
                fill={isDark ? '#A78BFA' : '#B07FD4'}
                animate={{ scale: [0.9, 1.1, 0.9] }}
                style={{ transformOrigin: '18px 18px' }}
                transition={{ duration: 1.8, repeat: Infinity, ease: 'easeInOut' }}
              />
            </svg>
            <p style={{ fontSize: '0.72rem', color: isDark ? '#6B5A8A' : '#A98FBE' }}>
              Đang cập nhật bản đồ…
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Hovered tooltip */}
      <AnimatePresence>
        {hovered && nodes.find(n => n.id === hovered) && (
          <motion.div
            initial={{ opacity: 0, y: 6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 4 }}
            className="absolute bottom-2 left-2 right-2 px-3 py-2 rounded-xl text-xs z-10"
            style={{
              background: isDark ? 'rgba(20,13,46,0.95)' : 'rgba(255,247,251,0.97)',
              border: `1px solid ${isDark ? 'rgba(124,58,237,0.3)' : 'rgba(199,154,245,0.4)'}`,
              color: isDark ? '#E2D9F3' : '#2D1B4E',
              fontFamily: 'DM Sans, system-ui',
              backdropFilter: 'blur(12px)',
              boxShadow: isDark ? '0 4px 20px rgba(0,0,0,0.4)' : '0 4px 16px rgba(176,127,212,0.15)',
            }}
          >
            <span style={{ color: isDark ? '#A78BFA' : '#B07FD4', marginRight: 6 }}>✦</span>
            {nodes.find(n => n.id === hovered)?.label}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
