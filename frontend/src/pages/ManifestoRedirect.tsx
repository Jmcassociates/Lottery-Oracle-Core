// JMc - [2026-04-05] - Identity Bridge Component.
// Captures prospects from the PDF manifesto and signals GHL before initiating download.
import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';

const API_BASE = import.meta.env.VITE_API_URL || '';

const ManifestoRedirect = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('Initializing Handshake...');

  useEffect(() => {
    const email = searchParams.get('email');
    
    const triggerHandshake = async () => {
      if (email) {
        try {
          // Signal the backend tripwire
          await fetch(`${API_BASE}/api/telemetry/prospect`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
          });
          setStatus('Identity Confirmed. Accessing Manifesto...');
        } catch (err) {
          console.error("Telemetry failed:", err);
        }
      }

      // Trigger the PDF download
      const link = document.createElement('a');
      link.href = '/ORACLE_DEAD_ZONE_REPORT.pdf';
      link.download = 'ORACLE_DEAD_ZONE_REPORT.pdf';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      // Redirect to register after a short delay to ensure download starts
      setTimeout(() => {
        navigate(email ? `/register?email=${encodeURIComponent(email)}` : '/register');
      }, 2000);
    };

    triggerHandshake();
  }, [searchParams, navigate]);

  return (
    <div style={{ 
      height: '100vh', 
      display: 'flex', 
      flexDirection: 'column',
      alignItems: 'center', 
      justifyContent: 'center', 
      background: '#020617', 
      color: '#f8fafc',
      fontFamily: 'sans-serif' 
    }}>
      <div className="loader" style={{ 
        border: '4px solid #1e293b', 
        borderTop: '4px solid #3b82f6', 
        borderRadius: '50%', 
        width: '40px', 
        height: '40px', 
        animation: 'spin 1s linear infinite',
        marginBottom: '20px'
      }} />
      <h2 style={{ color: '#38bdf8', textTransform: 'uppercase', letterSpacing: '2px' }}>{status}</h2>
      <p style={{ color: '#94a3b8' }}>Your secure transmission is being decrypted.</p>
      
      <style>{`
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
};

export default ManifestoRedirect;
