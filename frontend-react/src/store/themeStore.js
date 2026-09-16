import { create } from 'zustand';

const useThemeStore = create((set) => ({
  theme: localStorage.getItem('therapity_theme') || 'dark',
  lang: localStorage.getItem('therapity_lang') || 'vi',

  toggleTheme: () => {
    set((state) => {
      const newTheme = state.theme === 'dark' ? 'light' : 'dark';
      localStorage.setItem('therapity_theme', newTheme);
      document.documentElement.classList.toggle('dark', newTheme === 'dark');
      document.documentElement.classList.toggle('light', newTheme === 'light');
      return { theme: newTheme };
    });
  },

  setLang: (lang) => {
    localStorage.setItem('therapity_lang', lang);
    set({ lang });
  },

  toggleLang: () => {
    set((state) => {
      const newLang = state.lang === 'vi' ? 'en' : 'vi';
      localStorage.setItem('therapity_lang', newLang);
      return { lang: newLang };
    });
  },
}));

// Apply theme on initial load
const savedTheme = localStorage.getItem('therapity_theme') || 'dark';
document.documentElement.classList.toggle('dark', savedTheme === 'dark');
document.documentElement.classList.toggle('light', savedTheme === 'light');

export default useThemeStore;
