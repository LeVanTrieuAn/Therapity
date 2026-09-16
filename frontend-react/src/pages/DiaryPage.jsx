import useThemeStore from '../store/themeStore';

export default function DiaryPage() {
  const { lang } = useThemeStore();
  return (
    <div>
      <h1 className="text-2xl font-bold mb-2" style={{ color: 'var(--color-text-primary)' }}>
        {lang === 'en' ? 'Diary Vault' : 'Kho Nhật Ký'}
      </h1>
      <p className="text-sm mb-6" style={{ color: 'var(--color-text-muted)' }}>
        {lang === 'en' ? 'Your personal knowledge management space' : 'Không gian quản lý tri thức cá nhân của bạn'}
      </p>
      <div className="card">
        <p style={{ color: 'var(--color-text-secondary)' }}>
          {lang === 'en' ? 'Diary module coming soon...' : 'Module nhật ký đang được xây dựng...'}
        </p>
      </div>
    </div>
  );
}
