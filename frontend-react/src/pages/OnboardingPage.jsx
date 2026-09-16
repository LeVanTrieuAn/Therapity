import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';
import { profileAPI } from '../services/api';

const STEPS = [
  { key: 'dob', titleVi: 'Ngày sinh của bạn?', titleEn: 'What is your date of birth?' },
  { key: 'gender', titleVi: 'Giới tính của bạn?', titleEn: 'What is your gender?', options: ['Nam', 'Nữ', 'Khác', 'Không muốn tiết lộ'] },
  { key: 'interests', titleVi: 'Sở thích của bạn?', titleEn: 'What are your interests?', multi: true, options: ['Đọc sách', 'Thể thao', 'Âm nhạc', 'Du lịch', 'Công nghệ', 'Nghệ thuật', 'Nấu ăn', 'Thiền & Yoga', 'Viết lách', 'Phim ảnh'] },
  { key: 'problems', titleVi: 'Bạn đang gặp vấn đề gì?', titleEn: 'What problems are you facing?', multi: true, options: ['Căng thẳng / Stress', 'Mất tập trung', 'Thiếu động lực', 'Lo âu', 'Khó kiểm soát cảm xúc', 'Thiếu mục tiêu sống', 'Trì hoãn', 'Tự ti'] },
  { key: 'goals', titleVi: 'Mục tiêu sử dụng ứng dụng?', titleEn: 'Your goals for using the app?', multi: true, options: ['Quản lý cảm xúc', 'Phát triển bản thân', 'Tăng năng suất', 'Xây dựng thói quen tốt', 'Tìm hiểu bản thân', 'Kết nối cộng đồng'] },
];

export default function OnboardingPage() {
  const [step, setStep] = useState(0);
  const [data, setData] = useState({});
  const [loading, setLoading] = useState(false);
  const { user, updateUser } = useAuthStore();
  const navigate = useNavigate();

  const current = STEPS[step];

  const handleSelect = (option) => {
    if (current.multi) {
      const arr = data[current.key] || [];
      const newArr = arr.includes(option) ? arr.filter(o => o !== option) : [...arr, option];
      setData({ ...data, [current.key]: newArr });
    } else {
      setData({ ...data, [current.key]: option });
    }
  };

  const handleNext = () => {
    if (step < STEPS.length - 1) setStep(step + 1);
    else handleFinish();
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

  const progress = ((step + 1) / STEPS.length) * 100;

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ background: 'var(--color-bg-primary)' }}>
      <div className="w-full max-w-lg animate-fade-in">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="h-1.5 rounded-full overflow-hidden" style={{ background: 'var(--color-border)' }}>
            <div className="h-full rounded-full transition-all duration-500" style={{ width: `${progress}%`, background: 'var(--color-accent)' }} />
          </div>
          <p className="text-xs mt-2 text-right" style={{ color: 'var(--color-text-muted)' }}>{step + 1} / {STEPS.length}</p>
        </div>

        <div className="glass-card">
          <h2 className="text-xl font-bold mb-2" style={{ color: 'var(--color-text-primary)' }}>{current.titleVi}</h2>

          {/* Options */}
          {current.options && (
            <div className="flex flex-wrap gap-2 mt-4">
              {current.options.map((opt) => {
                const selected = current.multi
                  ? (data[current.key] || []).includes(opt)
                  : data[current.key] === opt;
                return (
                  <button key={opt} onClick={() => handleSelect(opt)}
                    className="px-4 py-2 rounded-xl text-sm font-medium transition-all"
                    style={{
                      background: selected ? 'var(--color-accent)' : 'var(--color-bg-secondary)',
                      color: selected ? 'var(--color-text-inverse)' : 'var(--color-text-primary)',
                      border: `1px solid ${selected ? 'var(--color-accent)' : 'var(--color-border)'}`,
                    }}>
                    {opt}
                  </button>
                );
              })}
            </div>
          )}

          {/* Navigation */}
          <div className="flex justify-between mt-8">
            <button onClick={() => step > 0 && setStep(step - 1)} className="btn-ghost" disabled={step === 0}>
              ← Quay lại
            </button>
            <button onClick={handleNext} className="btn-primary" disabled={loading}>
              {loading ? '⏳ Đang lưu...' : step === STEPS.length - 1 ? 'Bắt đầu hành trình 🚀' : 'Tiếp theo →'}
            </button>
          </div>
        </div>

        {/* Skip */}
        <button onClick={() => navigate('/coach')} className="mt-4 w-full text-center text-sm hover:underline" style={{ color: 'var(--color-text-muted)' }}>
          Bỏ qua, tôi sẽ khám phá sau →
        </button>
      </div>
    </div>
  );
}
