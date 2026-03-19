import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { setToken } from '../utils/auth';

const API_BASE = import.meta.env.VITE_API_URL || '';

const AuthPage = ({ mode }: { mode: 'login' | 'register' }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const endpoint = mode === 'login' ? '/api/auth/login' : '/api/auth/register';

      let body;
      let headers: HeadersInit = {};

      if (mode === 'login') {
        body = new URLSearchParams();
        body.append('username', email);
        body.append('password', password);
        headers = { 'Content-Type': 'application/x-www-form-urlencoded' };
      } else {
        body = JSON.stringify({ email, password });
        headers = { 'Content-Type': 'application/json' };
      }

      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers,
        body,
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Authentication failed');
      }

      setToken(data.access_token, data.tier);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '400px', margin: '100px auto', padding: '2rem', background: 'var(--panel-bg)', borderRadius: '12px', border: '1px solid var(--border)' }}>
      <h2 style={{ textAlign: 'center', marginBottom: '2rem' }}>
        {mode === 'login' ? 'Log In' : 'Create an Account'}
      </h2>

      {error && <div style={{ color: '#ef4444', marginBottom: '1rem', textAlign: 'center' }}>{error}</div>}

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem' }}>Email Address</label>
          <input 
            type="email" 
            value={email} 
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{ width: '100%', padding: '0.75rem', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--bg-color)', color: 'white' }}
          />
        </div>
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem' }}>Password</label>
          <input 
            type="password" 
            value={password} 
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{ width: '100%', padding: '0.75rem', borderRadius: '6px', border: '1px solid var(--border)', background: 'var(--bg-color)', color: 'white' }}
          />
        </div>

        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? 'Processing...' : (mode === 'login' ? 'Log In' : 'Sign Up')}
        </button>
      </form>

      <div style={{ marginTop: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        {mode === 'login' ? (
          <p>Don't have an account? <Link to="/register" style={{ color: 'var(--accent)' }}>Sign up</Link></p>
        ) : (
          <p>Already have an account? <Link to="/login" style={{ color: 'var(--accent)' }}>Log in</Link></p>
        )}
      </div>
    </div>
  );
};

export default AuthPage;