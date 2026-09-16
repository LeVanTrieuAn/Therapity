import useThemeStore from '../store/themeStore';

export default function CohortPage() {
  const { lang } = useThemeStore();
  return (
    <div>
      <h1 className="text-2xl font-bold mb-2" style={{ color: 'var(--color-text-primary)' }}>
        {lang === 'en' ? 'Learning Roadmap' : 'Lộ Trình Học Tập'}
      </h1>
      <p className="text-sm mb-6" style={{ color: 'var(--color-text-muted)' }}>
        {lang === 'en' ? 'Unlearn → Relearn → Execute — 12-week program' : 'Phá bỏ → Tái thiết → Vận hành — Chương trình 12 tuần'}
      </p>
      <div className="card">
        <p style={{ color: 'var(--color-text-secondary)' }}>
          {lang === 'en' ? 'Cohort module coming soon...' : 'Module lộ trình đang được xây dựng...'}
        </p>
      </div>
    </div>
  );
}
