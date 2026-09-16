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

// AOA API
export const aoaAPI = {
  getPosts: () => api.get('/aoa/posts'),
  createPost: (data) => api.post('/aoa/posts', data),
  addComment: (postId, data) => api.post(`/aoa/posts/${postId}/comments`, data),
  toggleLike: (postId, data) => api.post(`/aoa/posts/${postId}/like`, data),
  postAction: (postId, data) => api.post(`/aoa/posts/${postId}/action`, data),
  updatePost: (postId, data) => api.put(`/aoa/posts/${postId}`, data),
  reportPost: (postId, data) => api.post(`/aoa/posts/${postId}/report`, data),
  trending: () => api.post('/aoa/trending'),
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

export default api;
