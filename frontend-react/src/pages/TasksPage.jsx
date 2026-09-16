import useThemeStore from '../store/themeStore';

export default function TasksPage() {
  const { lang } = useThemeStore();
  return (
    <div>
      <h1 className="text-2xl font-bold mb-2" style={{ color: 'var(--color-text-primary)' }}>
        {lang === 'en' ? 'Tasks' : 'Nhiệm Vụ'}
      </h1>
      <p className="text-sm mb-6" style={{ color: 'var(--color-text-muted)' }}>
        {lang === 'en' ? 'Plan → Do → Check → Act' : 'Lập kế hoạch → Thực hiện → Kiểm tra → Cải tiến'}
      </p>
      <div className="card">
        <p style={{ color: 'var(--color-text-secondary)' }}>
          {lang === 'en' ? 'Tasks module coming soon...' : 'Module nhiệm vụ đang được xây dựng...'}
        </p>
      </div>
    </div>
  );
}
