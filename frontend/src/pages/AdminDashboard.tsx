import { useState, useEffect } from 'react';
import { fetchWithAuth, isAdmin, logout } from '../utils/auth';
import { useNavigate } from 'react-router-dom';

interface AdminStats {
  status: string;
  syndicate_metrics: {
    total_users: number;
    pro_tier: number;
    free_tier: number;
    acquisition_24h: number;
  };
  sync_health: Record<string, { status: string; last_sync: string }>;
}

interface UserRecord {
  id: number;
  email: string;
  tier: string;
  is_active: boolean;
  is_admin: boolean;
  created_at: string;
}

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAdmin()) {
      navigate('/dashboard');
      return;
    }
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [statsRes, usersRes] = await Promise.all([
        fetchWithAuth('/api/admin/stats'),
        fetchWithAuth('/api/admin/users')
      ]);

      if (statsRes.ok && usersRes.ok) {
        setStats(await statsRes.json());
        setUsers(await usersRes.json());
      } else {
        setError("Technician clearance rejected by API.");
      }
    } catch (e) {
      setError("Communication failure with the Vault.");
    } finally {
      setLoading(false);
    }
  };

  const toggleTier = async (userId: number, currentTier: string) => {
    const newTier = currentTier === 'pro' ? 'free' : 'pro';
    try {
      const res = await fetchWithAuth(`/api/admin/users/${userId}/tier`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tier: newTier })
      });
      if (res.ok) {
        setUsers(users.map(u => u.id === userId ? { ...u, tier: newTier } : u));
      }
    } catch (e) {
      alert("Manual override failed.");
    }
  };

  if (loading && !stats) return <div className="admin-loading">INITIALIZING WAR ROOM...</div>;

  return (
    <div className="admin-layout" style={{ backgroundColor: '#020617', minHeight: '100vh', color: '#f8fafc', fontFamily: 'Inter, sans-serif', padding: '40px' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1e293b', paddingBottom: '20px', marginBottom: '40px' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 800, color: '#ffffff', textTransform: 'uppercase', letterSpacing: '2px' }}>Oracle War Room</h1>
          <p style={{ margin: '5px 0 0 0', color: '#94a3b8', fontSize: '14px' }}>Administrative Pulse & Syndicate Control</p>
        </div>
        <div style={{ display: 'flex', gap: '20px' }}>
          <button onClick={() => navigate('/dashboard')} style={{ background: 'transparent', border: '1px solid #334155', color: '#cbd5e1', padding: '8px 16px', borderRadius: '4px', cursor: 'pointer' }}>Exit to Dashboard</button>
          <button onClick={logout} style={{ background: '#ef4444', border: 'none', color: '#ffffff', padding: '8px 16px', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>Terminate Session</button>
        </div>
      </header>

      {error && <div style={{ background: '#450a0a', border: '1px solid #ef4444', color: '#fca5a5', padding: '15px', borderRadius: '8px', marginBottom: '30px' }}>{error}</div>}

      <div className="stats-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '40px' }}>
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', padding: '20px', borderRadius: '12px' }}>
          <span style={{ fontSize: '12px', color: '#94a3b8', textTransform: 'uppercase' }}>Total Technicians</span>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#38bdf8' }}>{stats?.syndicate_metrics.total_users || 0}</div>
        </div>
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', padding: '20px', borderRadius: '12px' }}>
          <span style={{ fontSize: '12px', color: '#94a3b8', textTransform: 'uppercase' }}>Pro Subscribers</span>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#10b981' }}>{stats?.syndicate_metrics.pro_tier || 0}</div>
        </div>
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', padding: '20px', borderRadius: '12px' }}>
          <span style={{ fontSize: '12px', color: '#94a3b8', textTransform: 'uppercase' }}>Free Tier</span>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#94a3b8' }}>{stats?.syndicate_metrics.free_tier || 0}</div>
        </div>
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', padding: '20px', borderRadius: '12px' }}>
          <span style={{ fontSize: '12px', color: '#94a3b8', textTransform: 'uppercase' }}>24h Velocity</span>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#f59e0b' }}>+{stats?.syndicate_metrics.acquisition_24h || 0}</div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '30px' }}>
        {/* User Ledger */}
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '25px' }}>
          <h3 style={{ margin: '0 0 20px 0', fontSize: '18px', color: '#ffffff' }}>Syndicate Ledger</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #1e293b', textAlign: 'left' }}>
                <th style={{ padding: '12px 8px', color: '#94a3b8', fontSize: '13px' }}>Email</th>
                <th style={{ padding: '12px 8px', color: '#94a3b8', fontSize: '13px' }}>Tier</th>
                <th style={{ padding: '12px 8px', color: '#94a3b8', fontSize: '13px' }}>Joined</th>
                <th style={{ padding: '12px 8px', color: '#94a3b8', fontSize: '13px', textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map(user => (
                <tr key={user.id} style={{ borderBottom: '1px solid #020617' }}>
                  <td style={{ padding: '12px 8px', fontSize: '14px' }}>
                    {user.email}
                    {user.is_admin && <span style={{ marginLeft: '8px', fontSize: '10px', background: '#38bdf8', color: '#0f172a', padding: '2px 4px', borderRadius: '3px', fontWeight: 'bold' }}>ADMIN</span>}
                  </td>
                  <td style={{ padding: '12px 8px' }}>
                    <span style={{ 
                      fontSize: '11px', 
                      textTransform: 'uppercase', 
                      padding: '4px 8px', 
                      borderRadius: '4px',
                      background: user.tier === 'pro' ? '#064e3b' : '#1e293b',
                      color: user.tier === 'pro' ? '#10b981' : '#94a3b8'
                    }}>
                      {user.tier}
                    </span>
                  </td>
                  <td style={{ padding: '12px 8px', fontSize: '13px', color: '#64748b' }}>
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                  <td style={{ padding: '12px 8px', textAlign: 'right' }}>
                    {!user.is_admin && (
                      <button 
                        onClick={() => toggleTier(user.id, user.tier)}
                        style={{ background: 'transparent', border: '1px solid #334155', color: '#cbd5e1', fontSize: '12px', padding: '4px 8px', cursor: 'pointer', borderRadius: '4px' }}
                      >
                        {user.tier === 'pro' ? 'Downgrade' : 'Upgrade to Pro'}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Sync Health */}
        <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '25px' }}>
          <h3 style={{ margin: '0 0 20px 0', fontSize: '18px', color: '#ffffff' }}>Engine Sync Health</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            {stats && Object.entries(stats.sync_health).map(([game, data]) => (
              <div key={game} style={{ borderLeft: `3px solid ${data.status === 'Up to date' ? '#10b981' : '#ef4444'}`, paddingLeft: '15px' }}>
                <div style={{ fontSize: '14px', fontWeight: 'bold' }}>{game.replace('_', ' ')}</div>
                <div style={{ fontSize: '12px', color: '#94a3b8' }}>Last Sync: {data.last_sync}</div>
              </div>
            ))}
          </div>
          <button 
            onClick={() => alert("Global Re-sync Protocol initiated.")}
            style={{ width: '100%', marginTop: '30px', background: 'transparent', border: '1px solid #38bdf8', color: '#38bdf8', padding: '12px', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}
          >
            FORCE MANUAL RE-SYNC
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
