import { useState, useEffect, useRef } from 'react';
import useAuthStore from '../store/authStore';
import useThemeStore from '../store/themeStore';
import { chatAPI } from '../services/api';

export default function CoachPage() {
  const { user } = useAuthStore();
  const { lang } = useThemeStore();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [suggestedReplies, setSuggestedReplies] = useState([]);
  const [reasoning, setReasoning] = useState('');
  const [sessionTitle, setSessionTitle] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });

  useEffect(() => {
    loadWelcome();
  }, []);

  useEffect(() => { scrollToBottom(); }, [messages]);

  const loadWelcome = async () => {
    try {
      setLoading(true);
      const res = await chatAPI.welcome({ username: user?.username, lang });
      const d = res.data;
      setMessages([{ role: 'assistant', content: d.question || 'Chào bạn, hãy chia sẻ với tôi...' }]);
      setSuggestedReplies(d.suggested_replies || []);
      setReasoning(d.reasoning || '');
      setSessionTitle(d.title || '');
    } catch (err) {
      setMessages([{ role: 'assistant', content: 'Chào bạn, hãy chia sẻ điều gì đang khiến bạn bận tâm?' }]);
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

    try {
      const res = await chatAPI.create({
        messages: newMessages.map(m => ({ role: m.role, content: m.content })),
        username: user?.username,
        total_user_messages: newMessages.filter(m => m.role === 'user').length,
      });
      const d = res.data;
      const aiMsg = { role: 'assistant', content: d.question || d.content || 'Hãy chia sẻ thêm...' };
      setMessages(prev => [...prev, aiMsg]);
      setSuggestedReplies(d.suggested_replies || []);
      setReasoning(d.reasoning || '');
      if (d.title) setSessionTitle(d.title);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Xin lỗi, đã có lỗi xảy ra. Vui lòng thử lại.' }]);
    } finally { setLoading(false); }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  return (
    <div className="h-[calc(100vh-3rem)] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold" style={{ color: 'var(--color-text-primary)' }}>
            {lang === 'en' ? 'Socratic Dialogue' : 'Đối thoại Socratic'}
          </h1>
          <p className="text-sm" style={{ color: 'var(--color-text-muted)' }}>
            {lang === 'en' ? 'Filter the noise. Find the core.' : 'Lọc bỏ tiếng ồn. Tìm lại cốt lõi.'}
          </p>
        </div>
        {sessionTitle && <span className="badge">{sessionTitle}</span>}
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-2">
        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-slide-up`}>
            <div className="max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed"
              style={{
                background: msg.role === 'user' ? 'var(--color-accent)' : 'var(--color-bg-card)',
                color: msg.role === 'user' ? 'var(--color-text-inverse)' : 'var(--color-text-primary)',
                border: msg.role === 'user' ? 'none' : '1px solid var(--color-border)',
              }}>
              {msg.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start animate-fade-in">
            <div className="px-4 py-3 rounded-2xl text-sm" style={{ background: 'var(--color-bg-card)', border: '1px solid var(--color-border)' }}>
              <span className="inline-flex gap-1">
                <span className="w-2 h-2 rounded-full animate-bounce" style={{ background: 'var(--color-accent)', animationDelay: '0ms' }} />
                <span className="w-2 h-2 rounded-full animate-bounce" style={{ background: 'var(--color-accent)', animationDelay: '150ms' }} />
                <span className="w-2 h-2 rounded-full animate-bounce" style={{ background: 'var(--color-accent)', animationDelay: '300ms' }} />
              </span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Reasoning */}
      {reasoning && (
        <div className="mt-2 px-4 py-2 rounded-xl text-xs italic" style={{ background: 'var(--color-accent-subtle)', color: 'var(--color-text-muted)', borderLeft: '3px solid var(--color-accent)' }}>
          💭 {reasoning}
        </div>
      )}

      {/* Suggested Replies */}
      {suggestedReplies.length > 0 && !loading && (
        <div className="flex flex-wrap gap-2 mt-3">
          {suggestedReplies.map((reply, i) => (
            <button key={i} onClick={() => sendMessage(reply)} className="btn-secondary text-xs">
              {reply}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="mt-3 flex gap-2">
        <input
          className="input flex-1"
          placeholder={lang === 'en' ? 'Type your thoughts...' : 'Nhập suy nghĩ của bạn...'}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />
        <button type="submit" className="btn-primary" disabled={loading || !input.trim()}>
          {lang === 'en' ? 'Send' : 'Gửi'}
        </button>
      </form>
    </div>
  );
}
