import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import useAuthStore from './store/authStore';
import AppLayout from './components/Layout/AppLayout';
import LoginPage from './pages/LoginPage';
import OnboardingPage from './pages/OnboardingPage';
import DashboardPage from './pages/DashboardPage';
import CoachPage from './pages/CoachPage';
import DiaryPage from './pages/DiaryPage';
import TasksPage from './pages/TasksPage';
import AOAPage from './pages/AOAPage';
import CohortPage from './pages/CohortPage';

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuthStore();
  return isAuthenticated ? children : <Navigate to="/" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path="/" element={<LoginPage />} />

        {/* Onboarding (requires auth, no sidebar) */}
        <Route path="/onboarding" element={
          <ProtectedRoute><OnboardingPage /></ProtectedRoute>
        } />

        {/* Protected with Layout */}
        <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/coach" element={<CoachPage />} />
          <Route path="/diary" element={<DiaryPage />} />
          <Route path="/tasks" element={<TasksPage />} />
          <Route path="/aoa" element={<AOAPage />} />
          <Route path="/cohort" element={<CohortPage />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
