export const setToken = (token: string, tier: string, isAdmin: boolean = false) => {
  localStorage.setItem('oracle_token', token);
  localStorage.setItem('oracle_tier', tier);
  localStorage.setItem('oracle_is_admin', isAdmin ? '1' : '0');
};

export const getToken = () => localStorage.getItem('oracle_token');
export const getTier = () => localStorage.getItem('oracle_tier');
export const isAdmin = () => localStorage.getItem('oracle_is_admin') === '1';

// JMc - [2026-04-16] - Decodes the JWT sub field to retrieve the user's email identity.
export const getEmail = () => {
  const token = getToken();
  if (!token) return null;
  try {
    // JWT format: header.payload.signature
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));

    return JSON.parse(jsonPayload).sub;
  } catch (e) {
    console.error("Identity extraction failed:", e);
    return null;
  }
};

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