import useThemeStore from '../store/themeStore';

export default function AOAPage() {
  const { lang } = useThemeStore();
  return (
    <div>
      <h1 className="text-2xl font-bold mb-2" style={{ color: 'var(--color-text-primary)' }}>
        {lang === 'en' ? 'Ask of Anything' : 'Hỏi Mọi Người Bất Cứ Điều Gì'}
      </h1>
      <p className="text-sm mb-6" style={{ color: 'var(--color-text-muted)' }}>
        {lang === 'en' ? 'Community feed & trending discussions' : 'Bản tin cộng đồng & thảo luận xu hướng'}
      </p>
      <div className="card">
        <p style={{ color: 'var(--color-text-secondary)' }}>
          {lang === 'en' ? 'AOA Feed module coming soon...' : 'Module bản tin AOA đang được xây dựng...'}
        </p>
      </div>
    </div>
  );
}
