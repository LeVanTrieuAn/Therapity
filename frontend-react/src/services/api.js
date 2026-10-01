import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

// Add JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('therapity_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  login: (data) => api.post('/auth/login', data),
  register: (data) => api.post('/auth/register', data),
  resetPassword: (data) => api.post('/auth/forgot-password/reset', data),
};

// Chat API
export const chatAPI = {
  welcome: (data) => api.post('/chat/welcome', data),
  create: (data) => api.post('/chat', data),
  mindmap: (data) => api.post('/chat/mindmap', data),
  getSessions: (username) => api.get(`/chat/sessions?username=${username}`),
  saveSessions: (data) => api.post('/chat/sessions', data),
  deleteSession: (id) => api.delete(`/chat/sessions/${id}`),
};

// Diary API
export const diaryAPI = {
  getEntries: (username) => api.get(`/diary/${username}`),
  createEntry: (username, data) => api.post(`/diary/${username}`, data),
  deleteEntry: (username, id) => api.delete(`/diary/${username}/${id}`),
  getFolders: (username) => api.get(`/diary/${username}/folders`),
  createFolder: (username, data) => api.post(`/diary/${username}/folders`, data),
  deleteFolder: (username, name) => api.delete(`/diary/${username}/folders/${name}`),
  generate: (data) => api.post('/diary/generate', data),
};

// Tasks API
export const tasksAPI = {
  getTasks: (username) => api.get(`/tasks/${username}`),
  createTask: (username, data) => api.post(`/tasks/${username}`, data),
  updateTask: (username, id, data) => api.put(`/tasks/${username}/${id}`, data),
  deleteTask: (username, id) => api.delete(`/tasks/${username}/${id}`),
  microsteps: (data) => api.post('/tasks/microsteps', data),
};


// Profile API
export const profileAPI = {
  getProfile: (username) => api.get(`/profile/${username}`),
  updateProfile: (username, data) => api.post(`/profile/${username}`, data),
  getOnboarding: (username) => api.get(`/profile/${username}/onboarding`),
  saveOnboarding: (username, data) => api.post(`/profile/${username}/onboarding`, data),
  getContext: (username) => api.get(`/profile/${username}/context`),
  getStats: (username) => api.get(`/profile/${username}/stats`),
  getMindset: (username) => api.get(`/profile/${username}/mindset`),
};

// Cohort / Roadmap API
export const cohortAPI = {
  getSyllabus: (username, week) => api.get(`/cohort/syllabus?username=${username}&week=${week}`),
  getActivity: () => api.get('/cohort/activity'),
  getMembers: () => api.get('/cohort/members'),
  getTasks: (username) => api.get(`/cohort/tasks/${username}`),
  checkContext: (username) => api.get(`/cohort/check-context?username=${username}`),
  join: (data) => api.post('/cohort/join', data),
  personalizeWeek: (data) => api.post('/cohort/personalize-week', data),
  patchTask: (taskId, data) => api.patch(`/cohort/tasks/${taskId}`, data),
  updateProgress: (data) => api.post('/cohort/update-progress', data),
  generateQuiz: (data) => api.post('/cohort/generate-quiz', data),
  submitQuiz: (data) => api.post('/cohort/submit-quiz', data),
  aiRetrospective: (data) => api.post('/cohort/ai-retrospective', data),
};

export default api;
