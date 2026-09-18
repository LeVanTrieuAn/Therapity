import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import useAuthStore from '../store/authStore';
import useThemeStore from '../store/themeStore';
import { chatAPI } from '../services/api';

/* ── Breathing dots typing indicator ─────────────────────── */
function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bubble-ai flex items-center gap-1.5 py-3 px-4" style={{ maxWidth: 'fit-content' }}>
        {[0, 0.18, 0.36].map((delay, i) => (
          <motion.span key={i}
            className="block w-2 h-2 rounded-full"
            style={{ background: 'var(--color-accent)' }}
            animate={{ scale: [0.7, 1.2, 0.7], opacity: [0.4, 1, 0.4] }}
            transition={{ duration: 1.1, repeat: Infinity, delay, ease: 'easeInOut' }}
          />
        ))}
      </div>
    </div>
  );
}

/* ── Wave backdrop (light mode subtle decoration) ────────── */
function WaveBg() {
  return (
    <div className="absolute bottom-0 left-0 right-0 overflow-hidden pointer-events-none" style={{ height: '100px' }}>
      <svg viewBox="0 0 1440 100" preserveAspectRatio="none" style={{ width: '100%', height: '100%' }}>
        <path d="M0,50 C360,100 1080,0 1440,50 L1440,100 L0,100 Z" fill="var(--color-accent)" opacity="0.04"/>
        <path d="M0,70 C480,20 960,100 1440,60 L1440,100 L0,100 Z" fill="var(--color-accent)" opacity="0.06"/>
      </svg>
    </div>
  );
}

/* ── Celestial orb icon (for AI avatar) ─────────────────── */
function OrbIcon({ size = 32 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none">
      <circle cx="16" cy="16" r="14" fill="var(--color-accent-light)" stroke="var(--color-accent)" strokeWidth="1"/>
      <path d="M10 16 A7 7 0 0 1 22 16 A5 5 0 0 0 10 16Z" fill="var(--color-accent)" opacity="0.7"/>
      <circle cx="16" cy="16" r="2.5" fill="var(--color-accent)"/>
      <circle cx="14" cy="14" r="1" fill="white" opacity="0.8"/>
      {[0,72,144,216,288].map((deg,i) => {
        const r = 12, rad = (deg * Math.PI) / 180;
        return <circle key={i} cx={16 + r * Math.sin(rad)} cy={16 - r * Math.cos(rad)} r="1" fill="var(--color-accent)" opacity="0.5"/>;
      })}
    </svg>
  );
}

const msgVariants = {
  hidden: { opacity: 0, y: 16, scale: 0.96 },
  show: { opacity: 1, y: 0, scale: 1, transition: { type: 'spring', stiffness: 280, damping: 24 } },
};

export default function CoachPage() {
  const { user } = useAuthStore();
  const { lang, theme } = useThemeStore();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestedReplies, setSuggestedReplies] = useState([]);
  const [reasoning, setReasoning] = useState('');
  const [sessionTitle, setSessionTitle] = useState('');
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
    } catch {
      setMessages([{ role: 'assistant', content: 'Chào bạn. Hãy chia sẻ điều gì đang khiến bạn bận tâm hôm nay?' }]);
    } finally { setLoading(false); }
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
      });
      const d = res.data;
      setMessages(prev => [...prev, { role: 'assistant', content: d.question || d.content || 'Hãy chia sẻ thêm…' }]);
      setSuggestedReplies(d.suggested_replies || []);
      setReasoning(d.reasoning || '');
      if (d.title) setSessionTitle(d.title);
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.' }]);
    } finally { setLoading(false); }
  };

  const handleSubmit = (e) => { e.preventDefault(); sendMessage(input); };
  const handleKeyDown = (e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(input); } };

  return (
    <div className="h-[calc(100vh-3rem)] flex flex-col relative overflow-hidden">
      <WaveBg />

      {/* ── Header ──────────────────────────────────── */}
      <motion.div
        className="flex items-center justify-between mb-5 relative z-10"
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
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
            <motion.span initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }}
              className="badge text-xs" style={{ fontFamily: 'var(--font-sans)' }}>
              {sessionTitle}
            </motion.span>
          )}
          <motion.div animate={{ rotate: [0, 20, -10, 0] }} transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}>
            <OrbIcon size={36} />
          </motion.div>
        </div>
      </motion.div>

      {/* ── Messages ─────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1 pb-2 relative z-10">
        <AnimatePresence initial={false}>
          {messages.map((msg, i) => (
            <motion.div key={i} variants={msgVariants} initial="hidden" animate="show"
              className={`flex items-end gap-2.5 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              {/* AI avatar */}
              {msg.role === 'assistant' && (
                <div className="flex-shrink-0 mb-0.5">
                  <OrbIcon size={28} />
                </div>
              )}
              <div className={msg.role === 'user' ? 'bubble-user' : 'bubble-ai'}>
                {msg.content}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>

        {loading && <TypingIndicator />}
        <div ref={messagesEndRef} />
      </div>

      {/* ── Reasoning ────────────────────────────────── */}
      <AnimatePresence>
        {reasoning && !loading && (
          <motion.div
            key="reasoning"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-2 px-4 py-2.5 rounded-xl text-xs italic overflow-hidden relative z-10"
            style={{
              background: 'var(--color-accent-subtle)',
              color: 'var(--color-text-muted)',
              borderLeft: '2px solid var(--color-accent)',
              fontFamily: 'var(--font-display)',
              fontSize: '0.82rem',
            }}
          >
            <span style={{ opacity: 0.6 }}>✦</span> {reasoning}
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Suggested replies ─────────────────────────── */}
      <AnimatePresence>
        {suggestedReplies.length > 0 && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="flex flex-wrap gap-2 mt-3 relative z-10"
          >
            {suggestedReplies.map((reply, i) => (
              <motion.button key={i} onClick={() => sendMessage(reply)}
                initial={{ opacity: 0, scale: 0.92 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.08 }}
                whileHover={{ scale: 1.04, y: -1 }}
                whileTap={{ scale: 0.97 }}
                className="text-xs px-3.5 py-2 rounded-full font-medium transition-all"
                style={{
                  background: 'var(--color-accent-subtle)',
                  color: 'var(--color-accent)',
                  border: '1px solid var(--color-border)',
                }}
              >
                {reply}
              </motion.button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Input ─────────────────────────────────────── */}
      <motion.form
        onSubmit={handleSubmit}
        className="mt-3 flex gap-2 relative z-10"
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
      >
        <div className="flex-1 relative">
          <textarea
            ref={inputRef}
            className="input resize-none overflow-hidden"
            style={{ minHeight: '48px', maxHeight: '120px', paddingRight: '3rem', lineHeight: '1.5' }}
            placeholder={lang === 'en' ? 'Share your thoughts…' : 'Chia sẻ suy nghĩ của bạn…'}
            value={input}
            onChange={(e) => { setInput(e.target.value); e.target.style.height = 'auto'; e.target.style.height = e.target.scrollHeight + 'px'; }}
            onKeyDown={handleKeyDown}
            disabled={loading}
            rows={1}
          />
        </div>
        <motion.button
          type="submit"
          className="btn-primary px-5 self-end"
          disabled={loading || !input.trim()}
          whileHover={{ scale: 1.04 }}
          whileTap={{ scale: 0.96 }}
          style={{ height: '48px', minWidth: '80px' }}
        >
          {loading
            ? <svg width="18" height="18" viewBox="0 0 24 24" fill="none" className="animate-spin"><circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" opacity="0.3"/><path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/></svg>
            : (lang === 'en' ? 'Send' : 'Gửi')
          }
        </motion.button>
      </motion.form>
    </div>
  );
}
