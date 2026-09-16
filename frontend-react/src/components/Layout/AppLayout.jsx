import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

export default function AppLayout() {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <main className="flex-1 ml-64 p-6 transition-all" style={{ background: 'var(--color-bg-primary)' }}>
        <Outlet />
      </main>
    </div>
  );
}
