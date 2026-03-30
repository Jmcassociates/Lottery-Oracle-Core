import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { setToken } from '../utils/auth';

const API_BASE = import.meta.env.VITE_API_URL || '';

const MagicLinkVerify = () => {
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying');
  const [errorMessage, setErrorMessage] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const verifyToken = async () => {
      const token = searchParams.get('token');
      
      if (!token) {
        setStatus('error');
        setErrorMessage('No access token found in transmission.');
        return;
      }

      try {
        const res = await fetch(`${API_BASE}/api/auth/verify-magic-link`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token }),
        });

        const data = await res.json();

        if (res.ok) {
          setToken(data.access_token, data.tier, data.is_admin);
          setStatus('success');
          // Redirect after a short delay for UX
          setTimeout(() => navigate('/dashboard'), 1500);
        } else {
          setStatus('error');
          setErrorMessage(data.detail || 'The magic link has expired or has been corrupted.');
        }
      } catch (err) {
        setStatus('error');
        setErrorMessage('Could not connect to the Oracle API.');
      }
    };

    verifyToken();
  }, [searchParams, navigate]);

  return (
    <div style={{ maxWidth: '400px', margin: '150px auto', padding: '2rem', background: 'var(--panel-bg)', borderRadius: '12px', border: '1px solid var(--border)', textAlign: 'center' }}>
      {status === 'verifying' && (
        <>
          <h2 style={{ color: 'var(--accent)' }}>Verifying Identity...</h2>
          <p style={{ color: 'var(--text-muted)' }}>Decrypting access credentials from the Vault.</p>
        </>
      )}

      {status === 'success' && (
        <>
          <h2 style={{ color: '#10b981' }}>Identity Confirmed</h2>
          <p style={{ color: 'var(--text-muted)' }}>Welcome back to the Syndicate. Opening the Vault...</p>
        </>
      )}

      {status === 'error' && (
        <>
          <h2 style={{ color: '#ef4444' }}>Verification Failed</h2>
          <p style={{ color: 'var(--text-muted)' }}>{errorMessage}</p>
          <button onClick={() => navigate('/login')} className="btn-secondary" style={{ marginTop: '1.5rem' }}>
            Back to Login
          </button>
        </>
      )}
    </div>
  );
};

export default MagicLinkVerify;
