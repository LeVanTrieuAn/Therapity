/**
 * Therapity — MindMap Canvas Component
 *
 * Renders nodes and edges returned from POST /api/v1/chat/mindmap
 * using pure SVG + Framer Motion — no external graph library needed.
 *
 * Graph data shape:
 * {
 *   nodes: [{ id, label, color }],
 *   edges: [{ source, target, label, is_contradiction }],
 *   current_step: "kham_pha" | "soi_chieu",
 *   focus_node_id: string | null
 * }
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

/* ── Layout: simple force-directed positions ─────────────── */
function computeLayout(nodes, edges) {
  if (!nodes || nodes.length === 0) return {};

  const positions = {};
  const W = 560, H = 400;
  const cx = W / 2, cy = H / 2;

  if (nodes.length === 1) {
    positions[nodes[0].id] = { x: cx, y: cy };
    return positions;
  }

  // First node at center, rest in a spiral ring
  positions[nodes[0].id] = { x: cx, y: cy };

  const placed = [nodes[0].id];
  let ringRadius = 110;
  let ring = [];

  // Group remaining by adjacency to already-placed
  const remaining = nodes.slice(1);

  // Simple radial layout: spread evenly by index
  remaining.forEach((node, i) => {
    const angle = (i / Math.max(remaining.length, 1)) * 2 * Math.PI - Math.PI / 2;
    const r = 100 + Math.floor(i / 6) * 90;
    positions[node.id] = {
      x: cx + r * Math.cos(angle),
      y: cy + r * Math.sin(angle) * 0.75, // flatten vertically
    };
  });

  return positions;
}

/* ── Node colors mapped to design system ─────────────────── */
function mapNodeColor(color, isDark) {
  // Backend sends: #16A34A (normal) or #ffb4ab (contradiction)
  if (!color) return isDark ? '#7C3AED' : '#B07FD4';
  if (color === '#16A34A' || color.toLowerCase() === '#16a34a') {
    return isDark ? '#6DB97B' : '#6DB97B';
  }
  if (color === '#ffb4ab' || color.toLowerCase() === '#ffb4ab') {
    return isDark ? '#F87171' : '#E06B8A';
  }
  return color;
}

/* ── Single Node ─────────────────────────────────────────── */
function MindNode({ node, pos, isFocus, isDark, onHover, hovered }) {
  const nodeColor = mapNodeColor(node.color, isDark);
  const isHovered = hovered === node.id;

  return (
    <motion.g
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: 'spring', stiffness: 260, damping: 20, delay: 0.05 }}
      style={{ cursor: 'default' }}
      onMouseEnter={() => onHover(node.id)}
      onMouseLeave={() => onHover(null)}
    >
      {/* Focus ring (blinking for contradiction) */}
      {isFocus && (
        <motion.circle
          cx={pos.x} cy={pos.y} r={34}
          fill="none"
          stroke={nodeColor}
          strokeWidth={2}
          animate={{ opacity: [0.3, 1, 0.3], r: [32, 38, 32] }}
          transition={{ duration: 1.6, repeat: Infinity, ease: 'easeInOut' }}
        />
      )}

      {/* Glow */}
      <circle
        cx={pos.x} cy={pos.y} r={isHovered ? 30 : 26}
        fill={nodeColor}
        opacity={0.15}
        style={{ transition: 'r 0.2s' }}
      />

      {/* Main circle */}
      <motion.circle
        cx={pos.x} cy={pos.y}
        r={isHovered ? 24 : 20}
        fill={isDark ? '#1A1035' : '#FFF7FB'}
        stroke={nodeColor}
        strokeWidth={isHovered ? 2.5 : 1.8}
        animate={{ r: isHovered ? 24 : 20 }}
        transition={{ type: 'spring', stiffness: 300, damping: 24 }}
      />

      {/* Inner dot */}
      <circle cx={pos.x} cy={pos.y} r={6} fill={nodeColor} opacity={0.9}/>

      {/* Label */}
      <text
        x={pos.x}
        y={pos.y + 36}
        textAnchor="middle"
        fill={isDark ? '#E2D9F3' : '#2D1B4E'}
        fontSize={10}
        fontFamily="DM Sans, system-ui, sans-serif"
        fontWeight={isFocus || isHovered ? '600' : '400'}
        style={{ pointerEvents: 'none', userSelect: 'none' }}
      >
        {node.label && node.label.length > 20 ? node.label.slice(0, 18) + '…' : node.label}
      </text>
    </motion.g>
  );
}

/* ── Edge ────────────────────────────────────────────────── */
function MindEdge({ edge, positions, isDark }) {
  const from = positions[edge.source];
  const to = positions[edge.target];
  if (!from || !to) return null;

  const mx = (from.x + to.x) / 2;
  const my = (from.y + to.y) / 2 - 20;
  const path = `M ${from.x} ${from.y} Q ${mx} ${my} ${to.x} ${to.y}`;

  const strokeColor = edge.is_contradiction
    ? (isDark ? '#F87171' : '#E06B8A')
    : (isDark ? 'rgba(124,58,237,0.45)' : 'rgba(176,127,212,0.45)');

  return (
    <motion.g initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.15 }}>
      <path
        d={path}
        stroke={strokeColor}
        strokeWidth={edge.is_contradiction ? 1.8 : 1.2}
        strokeDasharray={edge.is_contradiction ? '5 3' : 'none'}
        fill="none"
      />
      {/* Edge label */}
      {edge.label && (
        <text
          x={mx} y={my - 5}
          textAnchor="middle"
          fill={isDark ? '#7A6B9A' : '#A98FBE'}
          fontSize={9}
          fontFamily="DM Sans, system-ui"
          style={{ pointerEvents: 'none' }}
        >
          {edge.label.length > 16 ? edge.label.slice(0, 14) + '…' : edge.label}
        </text>
      )}
    </motion.g>
  );
}

/* ── Main MindMap Component ──────────────────────────────── */
export default function MindMap({ graphData, isLoading, isDark, className = '' }) {
  const [hovered, setHovered] = useState(null);
  const containerRef = useRef(null);
  const [svgSize, setSvgSize] = useState({ w: 560, h: 380 });

  useEffect(() => {
    if (!containerRef.current) return;
    const ro = new ResizeObserver(([entry]) => {
      setSvgSize({ w: entry.contentRect.width, h: Math.max(300, entry.contentRect.height) });
    });
    ro.observe(containerRef.current);
    return () => ro.disconnect();
  }, []);

  if (!graphData || (!graphData.nodes?.length && !isLoading)) {
    return (
      <div ref={containerRef} className={`flex items-center justify-center ${className}`}
        style={{ minHeight: 200 }}>
        <div className="text-center space-y-2">
          <svg width="48" height="48" viewBox="0 0 48 48" fill="none" className="mx-auto opacity-30">
            <circle cx="24" cy="24" r="20" stroke="var(--color-accent)" strokeWidth="1.5"/>
            <circle cx="24" cy="24" r="4" fill="var(--color-accent)"/>
            {[0,72,144,216,288].map((deg,i) => {
              const r = 14, rad = deg * Math.PI / 180;
              return <circle key={i} cx={24 + r * Math.sin(rad)} cy={24 - r * Math.cos(rad)} r="2.5" fill="var(--color-accent)" opacity="0.6"/>;
            })}
          </svg>
          <p style={{ color: 'var(--color-text-muted)', fontSize: '0.78rem' }}>
            Bản đồ tư duy sẽ xuất hiện<br/>sau khi bạn chia sẻ…
          </p>
        </div>
      </div>
    );
  }

  const nodes = graphData.nodes || [];
  const edges = graphData.edges || [];
  const focusId = graphData.focus_node_id;
  const step = graphData.current_step;

  // Scale positions to current SVG size
  const BASE_W = 560, BASE_H = 380;
  const rawPos = computeLayout(nodes, edges);
  const positions = {};
  Object.entries(rawPos).forEach(([id, p]) => {
    positions[id] = {
      x: (p.x / BASE_W) * svgSize.w,
      y: (p.y / BASE_H) * svgSize.h,
    };
  });

  return (
    <div ref={containerRef} className={`relative ${className}`} style={{ minHeight: 200 }}>
      {/* Step indicator */}
      <div className="absolute top-2 left-2 z-10 flex items-center gap-1.5">
        <div className="w-1.5 h-1.5 rounded-full" style={{
          background: step === 'soi_chieu' ? 'var(--color-danger)' : 'var(--color-success)',
          boxShadow: step === 'soi_chieu' ? '0 0 6px var(--color-danger)' : '0 0 6px var(--color-success)',
        }}/>
        <span style={{ fontSize: '0.68rem', color: 'var(--color-text-muted)', fontFamily: 'DM Sans' }}>
          {step === 'soi_chieu' ? 'Soi chiếu' : 'Khám phá'}
        </span>
      </div>

      {/* Loading overlay */}
      <AnimatePresence>
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="absolute inset-0 flex items-center justify-center z-20 rounded-xl"
            style={{ background: isDark ? 'rgba(13,11,26,0.6)' : 'rgba(254,243,248,0.6)', backdropFilter: 'blur(4px)' }}
          >
            <motion.div
              animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
              style={{ width: 24, height: 24, border: '2px solid var(--color-accent)', borderTopColor: 'transparent', borderRadius: '50%' }}
            />
          </motion.div>
        )}
      </AnimatePresence>

      <svg width="100%" height={svgSize.h} style={{ overflow: 'visible' }}>
        {/* Defs: radial gradient bg */}
        <defs>
          <radialGradient id="mapbg" cx="50%" cy="50%" r="70%">
            <stop offset="0%" stopColor={isDark ? 'rgba(124,58,237,0.06)' : 'rgba(201,164,245,0.06)'}/>
            <stop offset="100%" stopColor="transparent"/>
          </radialGradient>
        </defs>
        <rect width="100%" height="100%" fill="url(#mapbg)" rx="12"/>

        {/* Edges first (behind nodes) */}
        {edges.map((edge, i) => (
          <MindEdge key={i} edge={edge} positions={positions} isDark={isDark}/>
        ))}

        {/* Nodes */}
        {nodes.map(node => (
          positions[node.id] && (
            <MindNode
              key={node.id}
              node={node}
              pos={positions[node.id]}
              isFocus={node.id === focusId}
              isDark={isDark}
              onHover={setHovered}
              hovered={hovered}
            />
          )
        ))}
      </svg>

      {/* Hovered tooltip */}
      <AnimatePresence>
        {hovered && nodes.find(n => n.id === hovered) && (
          <motion.div
            initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
            className="absolute bottom-2 left-2 right-2 px-3 py-2 rounded-lg text-xs z-10"
            style={{
              background: isDark ? 'rgba(26,16,53,0.95)' : 'rgba(255,247,251,0.95)',
              border: '1px solid var(--color-border)',
              color: 'var(--color-text-primary)',
              fontFamily: 'DM Sans',
              backdropFilter: 'blur(8px)',
            }}
          >
            {nodes.find(n => n.id === hovered)?.label}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
