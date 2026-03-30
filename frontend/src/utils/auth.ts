export const setToken = (token: string, tier: string, isAdmin: boolean = false) => {
  localStorage.setItem('oracle_token', token);
  localStorage.setItem('oracle_tier', tier);
  localStorage.setItem('oracle_is_admin', isAdmin ? '1' : '0');
};

export const getToken = () => localStorage.getItem('oracle_token');
export const getTier = () => localStorage.getItem('oracle_tier');
export const isAdmin = () => localStorage.getItem('oracle_is_admin') === '1';

export const logout = () => {
  localStorage.removeItem('oracle_token');
  localStorage.removeItem('oracle_tier');
  localStorage.removeItem('oracle_is_admin');
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