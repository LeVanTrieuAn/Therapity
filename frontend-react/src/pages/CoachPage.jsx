import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import useAuthStore from '../store/authStore';
import useThemeStore from '../store/themeStore';
import { chatAPI } from '../services/api';
import MindMap from '../components/MindMap';

/* ── Breathing dots typing indicator ─────────────────────── */
function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bubble-ai flex items-center gap-1.5 py-3 px-4" style={{ maxWidth: 'fit-content' }}>
        {[0, 0.18, 0.36].map((delay, i) => (
          <motion.span key={i} className="block w-2 h-2 rounded-full"
            style={{ background: 'var(--color-accent)' }}
            animate={{ scale: [0.7, 1.2, 0.7], opacity: [0.4, 1, 0.4] }}
            transition={{ duration: 1.1, repeat: Infinity, delay, ease: 'easeInOut' }}/>
        ))}
      </div>
    </div>
  );
}

/* ── Celestial orb icon ───────────────────────────────────── */
function OrbIcon({ size = 28 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none">
      <circle cx="16" cy="16" r="14" fill="var(--color-accent-light)" stroke="var(--color-accent)" strokeWidth="1"/>
      <path d="M10 16 A7 7 0 0 1 22 16 A5 5 0 0 0 10 16Z" fill="var(--color-accent)" opacity="0.7"/>
      <circle cx="16" cy="16" r="2.5" fill="var(--color-accent)"/>
      <circle cx="14" cy="14" r="1" fill="white" opacity="0.8"/>
    </svg>
  );
}

/* ── Tarot-style toggle button for mindmap panel ─────────── */
function MapToggle({ open, onToggle, step }) {
  return (
    <motion.button
      onClick={onToggle}
      whileHover={{ scale: 1.04 }}
      whileTap={{ scale: 0.96 }}
      className="flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold transition-all"
      style={{
        background: open ? 'var(--color-accent)' : 'var(--color-accent-subtle)',
        color: open ? 'white' : 'var(--color-accent)',
        border: '1px solid var(--color-border)',
      }}
    >
      {/* Node icon */}
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="6" cy="12" r="3"/><circle cx="18" cy="6" r="3"/><circle cx="18" cy="18" r="3"/>
        <line x1="9" y1="10.5" x2="15.5" y2="7.5"/><line x1="9" y1="13.5" x2="15.5" y2="16.5"/>
      </svg>
      {open ? 'Ẩn bản đồ' : 'Bản đồ tư duy'}
      {step === 'soi_chieu' && !open && (
        <span className="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse"/>
      )}
    </motion.button>
  );
}

const msgVariants = {
  hidden: { opacity: 0, y: 16, scale: 0.96 },
  show: { opacity: 1, y: 0, scale: 1, transition: { type: 'spring', stiffness: 280, damping: 24 } },
};

export default function CoachPage() {
  const { user } = useAuthStore();
  const { lang, theme } = useThemeStore();
  const isDark = theme === 'dark';

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [mindmapLoading, setMindmapLoading] = useState(false);
  const [suggestedReplies, setSuggestedReplies] = useState([]);
  const [reasoning, setReasoning] = useState('');
  const [sessionTitle, setSessionTitle] = useState('');
  const [graphData, setGraphData] = useState(null);
  const [showMap, setShowMap] = useState(true);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  useEffect(() => { loadWelcome(); }, []);
  useEffect(() => { scrollToBottom(); }, [messages, loading]);

  const loadWelcome = async () => {
    try {
      setLoading(true);
      const res = await chatAPI.welcome({ username: user?.username, lang });
      const d = res.data;
      setMessages([{ role: 'assistant', content: d.question || 'Hãy chia sẻ điều gì đang khiến bạn bận tâm…' }]);
      setSuggestedReplies(d.suggested_replies || []);
      setReasoning(d.reasoning || '');
      setSessionTitle(d.title || '');
      // Welcome response already includes initial graph
      if (d.nodes) {
        setGraphData({ nodes: d.nodes, edges: d.edges || [], current_step: d.current_step, focus_node_id: d.focus_node_id });
      }
    } catch {
      setMessages([{ role: 'assistant', content: 'Chào bạn. Hãy chia sẻ điều gì đang khiến bạn bận tâm hôm nay?' }]);
    } finally { setLoading(false); }
  };

  /** Fetch mindmap separately after each user message */
  const fetchMindmap = async (msgs) => {
    if (msgs.length < 2) return; // Need at least 1 exchange
    try {
      setMindmapLoading(true);
      const res = await chatAPI.mindmap({
        messages: msgs.map(m => ({ role: m.role, content: m.content })),
        username: user?.username,
        graph_data: graphData || {},
      });
      if (res.data?.nodes) {
        setGraphData(res.data);
        // Auto-open map when contradiction detected
        if (res.data.current_step === 'soi_chieu' || res.data.focus_node_id) {
          setShowMap(true);
        }
      }
    } catch { /* silent */ }
    finally { setMindmapLoading(false); }
  };

  const sendMessage = async (text) => {
    if (!text.trim() || loading) return;
    const userMsg = { role: 'user', content: text.trim() };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput('');
    setSuggestedReplies([]);
    setLoading(true);
    inputRef.current?.focus();

    try {
      const res = await chatAPI.create({
        messages: newMessages.map(m => ({ role: m.role, content: m.content })),
        username: user?.username,
        total_user_messages: newMessages.filter(m => m.role === 'user').length,
        graph_data: graphData || {},
      });
      const d = res.data;
      const aiMsg = { role: 'assistant', content: d.question || d.content || 'Hãy chia sẻ thêm…' };
      const finalMsgs = [...newMessages, aiMsg];
      setMessages(finalMsgs);
      setSuggestedReplies(d.suggested_replies || []);
      setReasoning(d.reasoning || '');
      if (d.title) setSessionTitle(d.title);

      // Fetch mindmap after AI responds
      fetchMindmap(finalMsgs);
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.' }]);
    } finally { setLoading(false); }
  };

  const handleSubmit = (e) => { e.preventDefault(); sendMessage(input); };
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(input); }
  };

  const graphStep = graphData?.current_step;

  return (
    <div className="h-[calc(100vh-3rem)] flex gap-4 relative overflow-hidden" style={{ borderRadius: '1.25rem' }}>

      {/* ── Full-page background image ───────────────── */}
      <div
        className={`absolute inset-0 pointer-events-none ${isDark ? 'scene-bg-abyss' : 'scene-bg-sunset'}`}
        style={{
          opacity: isDark ? 0.6 : 0.72,
          backgroundPosition: 'center 25%',
          borderRadius: '1.25rem',
          overflow: 'hidden',
        }}
      />
      {/* Bottom fade */}
      <div className="absolute inset-0 pointer-events-none" style={{
        background: isDark
          ? 'linear-gradient(to bottom, transparent 15%, var(--color-bg-primary) 75%)'
          : 'linear-gradient(to bottom, transparent 20%, var(--color-bg-primary) 68%)',
        borderRadius: '1.25rem',
      }}/>

      {/* ══════════════════════════════════════════════
          LEFT: Chat panel
      ══════════════════════════════════════════════ */}
      <div className={`flex flex-col transition-all duration-300 relative z-10 px-5 pt-4 pb-3 ${showMap ? 'flex-1' : 'w-full'}`}>

        {/* Header */}
        <motion.div className="flex items-center justify-between mb-4"
          initial={{ opacity: 0, y: -12 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <div>
            <h1 className="font-display text-3xl font-semibold" style={{ color: 'var(--color-text-primary)' }}>
              {lang === 'en' ? 'Socratic Dialogue' : 'Đối thoại Socratic'}
            </h1>
            <p className="text-sm mt-0.5" style={{ color: 'var(--color-text-muted)' }}>
              {lang === 'en' ? 'Filter the noise · Find the core' : 'Lọc bỏ tiếng ồn · Tìm lại cốt lõi'}
            </p>
          </div>
          <div className="flex items-center gap-2">
            {sessionTitle && (
              <motion.span initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="badge">
                {sessionTitle}
              </motion.span>
            )}
            <MapToggle
              open={showMap}
              onToggle={() => setShowMap(v => !v)}
              step={graphStep}
            />
            <motion.div animate={{ rotate: [0, 20, -10, 0] }} transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}>
              <OrbIcon size={32} />
            </motion.div>
          </div>
        </motion.div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto space-y-4 pr-1 pb-2">
          <AnimatePresence initial={false}>
            {messages.map((msg, i) => (
              <motion.div key={i} variants={msgVariants} initial="hidden" animate="show"
                className={`flex items-end gap-2.5 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.role === 'assistant' && <div className="flex-shrink-0 mb-0.5"><OrbIcon size={26} /></div>}
                <div className={msg.role === 'user' ? 'bubble-user' : 'bubble-ai'}>
                  {msg.content}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          {loading && <TypingIndicator />}
          <div ref={messagesEndRef} />
        </div>

        {/* Reasoning */}
        <AnimatePresence>
          {reasoning && !loading && (
            <motion.div key="reasoning"
              initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}
              className="mt-2 px-4 py-2.5 rounded-xl text-xs italic overflow-hidden"
              style={{
                background: 'var(--color-accent-subtle)',
                color: 'var(--color-text-muted)',
                borderLeft: '2px solid var(--color-accent)',
                fontFamily: 'var(--font-display)',
                fontSize: '0.82rem',
              }}>
              <span style={{ opacity: 0.6 }}>✦</span> {reasoning}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Suggested replies */}
        <AnimatePresence>
          {suggestedReplies.length > 0 && !loading && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              className="flex flex-wrap gap-2 mt-3">
              {suggestedReplies.map((reply, i) => (
                <motion.button key={i} onClick={() => sendMessage(reply)}
                  initial={{ opacity: 0, scale: 0.92 }} animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.08 }}
                  whileHover={{ scale: 1.04, y: -1 }} whileTap={{ scale: 0.97 }}
                  className="text-xs px-3.5 py-2 rounded-full font-medium"
                  style={{
                    background: 'var(--color-accent-subtle)',
                    color: 'var(--color-accent)',
                    border: '1px solid var(--color-border)',
                  }}>
                  {reply}
                </motion.button>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Input */}
        <motion.form onSubmit={handleSubmit} className="mt-3 flex gap-2"
          initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              className="input resize-none overflow-hidden"
              style={{ minHeight: '48px', maxHeight: '120px', paddingRight: '1rem', lineHeight: '1.5' }}
              placeholder={lang === 'en' ? 'Share your thoughts…' : 'Chia sẻ suy nghĩ của bạn…'}
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                e.target.style.height = 'auto';
                e.target.style.height = e.target.scrollHeight + 'px';
              }}
              onKeyDown={handleKeyDown}
              disabled={loading}
              rows={1}
            />
          </div>
          <motion.button type="submit" className="btn-primary px-5 self-end"
            disabled={loading || !input.trim()}
            whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.96 }}
            style={{ height: '48px', minWidth: '80px' }}>
            {loading
              ? <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="animate-spin">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" opacity="0.3"/>
                  <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              : (lang === 'en' ? 'Send' : 'Gửi')
            }
          </motion.button>
        </motion.form>
      </div>

      {/* ══════════════════════════════════════════════
          RIGHT: Mind Map Panel
      ══════════════════════════════════════════════ */}
      <AnimatePresence>
        {showMap && (
          <motion.div
            key="mindmap-panel"
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 340, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 220, damping: 28 }}
            className="flex-shrink-0 flex flex-col overflow-hidden"
            style={{ width: 340 }}
          >
            <div className="glass-card flex flex-col h-full" style={{ padding: '1rem', gap: '0.75rem' }}>
              {/* Panel header */}
              <div className="flex items-center justify-between flex-shrink-0">
                <div>
                  <h3 className="font-display text-base font-semibold" style={{ color: 'var(--color-text-primary)' }}>
                    {lang === 'en' ? 'Mind Map' : 'Bản đồ tư duy'}
                  </h3>
                  <p className="text-xs mt-0.5" style={{ color: 'var(--color-text-muted)' }}>
                    {lang === 'en' ? 'Cognitive graph · grows over time' : 'Đồ thị nhận thức · tích lũy theo thời gian'}
                  </p>
                </div>
                {mindmapLoading && (
                  <motion.div animate={{ rotate: 360 }} transition={{ duration: 1.5, repeat: Infinity, ease: 'linear' }}
                    style={{ width: 16, height: 16, border: '2px solid var(--color-accent)', borderTopColor: 'transparent', borderRadius: '50%' }}/>
                )}
              </div>

              {/* Legend — theme-synced gem symbols */}
              <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5 flex-shrink-0">
                {/* Thought node */}
                <div className="flex items-center gap-1.5">
                  <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                    <path d="M5 0.5 L6.1 3.9 L9.5 5 L6.1 6.1 L5 9.5 L3.9 6.1 L0.5 5 L3.9 3.9 Z"
                      fill={isDark ? '#7C3AED' : '#C9A4F5'} stroke={isDark ? '#A78BFA' : '#B07FD4'} strokeWidth="0.4"/>
                  </svg>
                  <span style={{ fontSize: '0.67rem', color: 'var(--color-text-muted)', letterSpacing: '0.01em' }}>
                    {lang === 'en' ? 'Thought' : 'Suy nghĩ'}
                  </span>
                </div>
                {/* Contradiction node */}
                <div className="flex items-center gap-1.5">
                  <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                    <path d="M5 0.5 L6.1 3.9 L9.5 5 L6.1 6.1 L5 9.5 L3.9 6.1 L0.5 5 L3.9 3.9 Z"
                      fill={isDark ? '#1F0D18' : '#FFF0F3'} stroke={isDark ? '#F87171' : '#F4607E'} strokeWidth="0.4"/>
                  </svg>
                  <span style={{ fontSize: '0.67rem', color: 'var(--color-text-muted)', letterSpacing: '0.01em' }}>
                    {lang === 'en' ? 'Contradiction' : 'Mâu thuẫn'}
                  </span>
                </div>
                {/* Contradiction edge */}
                <div className="flex items-center gap-1.5">
                  <svg width="14" height="6" viewBox="0 0 14 6">
                    <line x1="0" y1="3" x2="14" y2="3"
                      stroke={isDark ? '#F87171' : '#F4607E'}
                      strokeWidth="1.2" strokeDasharray="3.5 2.5"/>
                  </svg>
                  <span style={{ fontSize: '0.67rem', color: 'var(--color-text-muted)', letterSpacing: '0.01em' }}>
                    {lang === 'en' ? 'Contradiction' : 'Mâu thuẫn'}
                  </span>
                </div>
                {/* Normal edge */}
                <div className="flex items-center gap-1.5">
                  <svg width="14" height="6" viewBox="0 0 14 6">
                    <line x1="0" y1="3" x2="11" y2="3"
                      stroke={isDark ? 'rgba(124,58,237,0.6)' : 'rgba(176,127,212,0.7)'}
                      strokeWidth="1.2"/>
                    <polygon points="14,3 10,1.2 10,4.8"
                      fill={isDark ? 'rgba(124,58,237,0.6)' : 'rgba(176,127,212,0.7)'}/>
                  </svg>
                  <span style={{ fontSize: '0.67rem', color: 'var(--color-text-muted)', letterSpacing: '0.01em' }}>
                    {lang === 'en' ? 'Connection' : 'Liên kết'}
                  </span>
                </div>
              </div>

              {/* Step phase badge */}
              {graphData?.current_step && (
                <div className="flex items-center gap-2 flex-shrink-0">
                  <motion.div
                    key={graphData.current_step}
                    initial={{ scale: 0.85, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
                    className="flex items-center gap-1.5 px-2.5 py-1 rounded-full"
                    style={{
                      background: graphData.current_step === 'soi_chieu'
                        ? (isDark ? 'rgba(248,113,113,0.12)' : 'rgba(244,96,126,0.10)')
                        : (isDark ? 'rgba(124,58,237,0.15)' : 'rgba(201,164,245,0.20)'),
                      border: `1px solid ${graphData.current_step === 'soi_chieu'
                        ? (isDark ? 'rgba(248,113,113,0.3)' : 'rgba(244,96,126,0.3)')
                        : (isDark ? 'rgba(124,58,237,0.3)' : 'rgba(176,127,212,0.4)')}`,
                    }}
                  >
                    <motion.div
                      className="w-1.5 h-1.5 rounded-full"
                      style={{
                        background: graphData.current_step === 'soi_chieu'
                          ? (isDark ? '#F87171' : '#F4607E')
                          : (isDark ? '#A78BFA' : '#B07FD4'),
                      }}
                      animate={{ scale: graphData.current_step === 'soi_chieu' ? [1, 1.4, 1] : 1 }}
                      transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
                    />
                    <span style={{
                      fontSize: '0.67rem', fontWeight: 600, letterSpacing: '0.03em',
                      color: graphData.current_step === 'soi_chieu'
                        ? (isDark ? '#F87171' : '#F4607E')
                        : (isDark ? '#A78BFA' : '#7C3AED'),
                    }}>
                      {graphData.current_step === 'soi_chieu'
                        ? (lang === 'en' ? 'Reflection' : 'Soi chiếu')
                        : (lang === 'en' ? 'Exploration' : 'Khám phá')}
                    </span>
                  </motion.div>
                </div>
              )}

              <div className="divider"/>

              {/* MindMap SVG */}
              <div className="flex-1 overflow-hidden rounded-xl" style={{
                background: isDark ? 'rgba(13,11,26,0.5)' : 'rgba(254,243,248,0.5)',
                border: '1px solid var(--color-border-subtle)',
                minHeight: 280,
              }}>
                <MindMap
                  graphData={graphData}
                  isLoading={mindmapLoading && !graphData?.nodes?.length}
                  isDark={isDark}
                  className="w-full h-full"
                />
              </div>

              {/* Node count */}
              {graphData?.nodes?.length > 0 && (
                <p style={{ fontSize: '0.7rem', color: 'var(--color-text-muted)', textAlign: 'center' }}>
                  {graphData.nodes.length} {lang === 'en' ? 'nodes' : 'nút'} · {graphData.edges?.length || 0} {lang === 'en' ? 'connections' : 'kết nối'}
                </p>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
