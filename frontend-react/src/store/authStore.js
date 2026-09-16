import { create } from 'zustand';

const useAuthStore = create((set) => ({
  user: JSON.parse(localStorage.getItem('therapity_user') || 'null'),
  token: localStorage.getItem('therapity_token') || null,
  isAuthenticated: !!localStorage.getItem('therapity_token'),

  login: (userData, token, refreshToken) => {
    localStorage.setItem('therapity_user', JSON.stringify(userData));
    localStorage.setItem('therapity_token', token);
    if (refreshToken) localStorage.setItem('therapity_refresh_token', refreshToken);
    set({ user: userData, token, isAuthenticated: true });
  },

  logout: () => {
    localStorage.removeItem('therapity_user');
    localStorage.removeItem('therapity_token');
    localStorage.removeItem('therapity_refresh_token');
    set({ user: null, token: null, isAuthenticated: false });
  },

  updateUser: (updates) => {
    set((state) => {
      const updated = { ...state.user, ...updates };
      localStorage.setItem('therapity_user', JSON.stringify(updated));
      return { user: updated };
    });
  },
}));

export default useAuthStore;
