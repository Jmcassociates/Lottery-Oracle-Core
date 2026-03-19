export const setToken = (token: string, tier: string) => {
  localStorage.setItem('oracle_token', token);
  localStorage.setItem('oracle_tier', tier);
};

export const getToken = () => localStorage.getItem('oracle_token');
export const getTier = () => localStorage.getItem('oracle_tier');

export const logout = () => {
  localStorage.removeItem('oracle_token');
  localStorage.removeItem('oracle_tier');
  window.location.href = '/login';
};

const API_BASE = import.meta.env.VITE_API_URL || '';

export const fetchWithAuth = async (url: string, options: RequestInit = {}) => {
  const token = getToken();
  if (!token) {
    throw new Error('No authentication token found');
  }

  const headers = new Headers(options.headers);
  headers.set('Authorization', `Bearer ${token}`);

  const fullUrl = url.startsWith('http') ? url : `${API_BASE}${url}`;

  const response = await fetch(fullUrl, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    logout();
  }

  return response;
};