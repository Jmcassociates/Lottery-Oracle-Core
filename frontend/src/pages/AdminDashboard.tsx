import { useState, useEffect, useRef } from 'react';
import { fetchWithAuth, isAdmin, logout } from '../utils/auth';
import { useNavigate } from 'react-router-dom';

interface AdminStats {
  status: string;
  sync_active: boolean;
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

interface SyncLog {
  id: number;
  game_name: string;
  status: string;
  new_records: number;
  error_message: string | null;
  executed_at: string;
}

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [logs, setLogs] = useState<SyncLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const pollInterval = useRef<number | null>(null);

  useEffect(() => {
    if (!isAdmin()) {
      navigate('/dashboard');
      return;
    }
    fetchData();
    
    return () => {
      if (pollInterval.current) window.clearInterval(pollInterval.current);
    };
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, usersRes, logsRes] = await Promise.all([
        fetchWithAuth('/api/admin/stats'),
        fetchWithAuth('/api/admin/users'),
        fetchWithAuth('/api/admin/logs?limit=30')
      ]);

      if (statsRes.ok && usersRes.ok && logsRes.ok) {
        const statsData: AdminStats = await statsRes.json();
        const logsData: SyncLog[] = await logsRes.json();
        
        setStats(statsData);
        setUsers(await usersRes.json());
        setLogs(logsData);

        // JMc - [2026-03-31] - Source of Truth: Check the actual DB-backed backend sync lock
        if (statsData.sync_active) {
            setIsSyncing(true);
            if (!pollInterval.current) startPolling();
        } else {
            setIsSyncing(false);
            if (pollInterval.current) stopPolling();
        }
      } else {
        setError("Technician clearance rejected by API.");
      }
    } catch (e) {
      setError("Communication failure with the Vault.");
    } finally {
      setLoading(false);
    }
  };

  const startPolling = () => {
    if (pollInterval.current) return;
    pollInterval.current = window.setInterval(() => {
      fetchData();
    }, 4000); // 4s polling for high fidelity feedback

    // Emergency cutoff after 15 minutes to prevent tab death
    setTimeout(() => {
      stopPolling();
    }, 900000);
  };

  const stopPolling = () => {
    if (pollInterval.current) {
      window.clearInterval(pollInterval.current);
      pollInterval.current = null;
    }
  };

  const triggerSync = async () => {
    if (!window.confirm("Initialize Global Re-sync Protocol? This will consume heavy CPU resources.")) return;
    
    try {
      setIsSyncing(true); // Immediate feedback
      const res = await fetchWithAuth('/api/admin/sync', { method: 'POST' });
      if (res.ok) {
        startPolling();
      } else if (res.status === 409) {
        alert("PROTOCOL ACTIVE: A synchronization is already in progress.");
        startPolling();
      } else {
        setIsSyncing(false);
        alert("Manual override failed. Check system logs.");
      }
    } catch (e) {
      setIsSyncing(false);
      alert("Communication error during trigger.");
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

  const toggleStatus = async (userId: number, currentStatus: boolean) => {
    const newStatus = !currentStatus;
    const action = newStatus ? "RE-ACTIVATE" : "DEACTIVATE";
    if (!window.confirm(`Are you sure you want to ${action} this protocol access?`)) return;

    try {
      const res = await fetchWithAuth(`/api/admin/users/${userId}/active`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: newStatus })
      });
      if (res.ok) {
        setUsers(users.map(u => u.id === userId ? { ...u, is_active: newStatus } : u));
      }
    } catch (e) {
      alert("Compliance override failed.");
    }
  };

  if (loading && !stats) return <div style={{ color: '#38bdf8', padding: '50px', textAlign: 'center', fontFamily: 'monospace' }}>INITIALIZING WAR ROOM...</div>;

  return (
    <div className="admin-layout" style={{ backgroundColor: '#020617', minHeight: '100vh', color: '#f8fafc', fontFamily: 'Inter, sans-serif', padding: '40px' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #1e293b', paddingBottom: '20px', marginBottom: '40px' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '24px', fontWeight: 800, color: '#ffffff', textTransform: 'uppercase', letterSpacing: '2px' }}>Oracle War Room</h1>
          <p style={{ margin: '5px 0 0 0', color: '#94a3b8', fontSize: '14px' }}>Administrative Pulse & Syndicate Control</p>
        </div>
        <div style={{ display: 'flex', gap: '20px' }}>
          <button onClick={fetchData} style={{ background: 'transparent', border: '1px solid #38bdf8', color: '#38bdf8', padding: '8px 16px', borderRadius: '4px', cursor: 'pointer' }}>Refresh Logic</button>
          <button onClick={() => navigate('/dashboard')} style={{ background: 'transparent', border: '1px solid #334155', color: '#cbd5e1', padding: '8px 16px', borderRadius: '4px', cursor: 'pointer' }}>Exit to Terminal</button>
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

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '30px', marginBottom: '40px' }}>
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
                    <span style={{ fontSize: '11px', textTransform: 'uppercase', padding: '4px 8px', borderRadius: '4px', background: user.tier === 'pro' ? '#064e3b' : '#1e293b', color: user.tier === 'pro' ? '#10b981' : '#94a3b8' }}>{user.tier}</span>
                  </td>
                  <td style={{ padding: '12px 8px', fontSize: '13px', color: '#64748b' }}>{new Date(user.created_at).toLocaleDateString()}</td>
                  <td style={{ padding: '12px 8px', textAlign: 'right' }}>
                    {!user.is_admin && (
                      <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                        <button onClick={() => toggleTier(user.id, user.tier)} style={{ background: 'transparent', border: '1px solid #334155', color: '#cbd5e1', fontSize: '12px', padding: '4px 8px', cursor: 'pointer', borderRadius: '4px' }}>
                          {user.tier === 'pro' ? 'Downgrade' : 'Upgrade to Pro'}
                        </button>
                        <button onClick={() => toggleStatus(user.id, user.is_active)} style={{ background: 'transparent', border: `1px solid ${user.is_active ? '#450a0a' : '#10b981'}`, color: user.is_active ? '#fca5a5' : '#10b981', fontSize: '12px', padding: '4px 8px', cursor: 'pointer', borderRadius: '4px' }}>
                          {user.is_active ? 'Deactivate' : 'Reactivate'}
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '25px' }}>
          <h3 style={{ margin: '0 0 20px 0', fontSize: '18px', color: '#ffffff' }}>Engine Sync Health</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            {stats && Object.entries(stats.sync_health).map(([game, data]) => {
                const inProgress = logs.find(l => l.game_name === game && l.status === 'IMPORTING');
                const statusColor = inProgress ? '#f59e0b' : (data.status === 'Up to date' ? '#10b981' : '#ef4444');
                const statusText = inProgress ? 'IMPORTING...' : data.status;
                return (
                    <div key={game} style={{ borderLeft: `3px solid ${statusColor}`, paddingLeft: '15px' }}>
                        <div style={{ fontSize: '14px', fontWeight: 'bold' }}>{game.replace('_', ' ')}</div>
                        <div style={{ fontSize: '12px', color: statusColor, fontWeight: inProgress ? 'bold' : 'normal' }}>{statusText}</div>
                        <div style={{ fontSize: '11px', color: '#64748b' }}>Last Draw: {data.last_sync}</div>
                    </div>
                );
            })}
          </div>
          <button 
            onClick={triggerSync}
            disabled={isSyncing}
            style={{ width: '100%', marginTop: '30px', background: isSyncing ? '#1e293b' : 'transparent', border: `1px solid ${isSyncing ? '#334155' : '#38bdf8'}`, color: isSyncing ? '#94a3b8' : '#38bdf8', padding: '12px', borderRadius: '6px', cursor: isSyncing ? 'not-allowed' : 'pointer', fontWeight: 'bold' }}
          >
            {isSyncing ? "SYNC PROTOCOL ACTIVE..." : "FORCE GLOBAL RE-SYNC"}
          </button>
        </div>
      </div>

      <div style={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '12px', padding: '25px' }}>
        <h3 style={{ margin: '0 0 20px 0', fontSize: '18px', color: '#ffffff' }}>Recent Sync Activity</h3>
        <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead style={{ position: 'sticky', top: 0, background: '#0f172a' }}>
              <tr style={{ borderBottom: '1px solid #1e293b', textAlign: 'left' }}>
                <th style={{ padding: '12px 8px', color: '#94a3b8', fontSize: '12px' }}>Timestamp</th>
                <th style={{ padding: '12px 8px', color: '#94a3b8', fontSize: '12px' }}>Game</th>
                <th style={{ padding: '12px 8px', color: '#94a3b8', fontSize: '12px' }}>Status</th>
                <th style={{ padding: '12px 8px', color: '#94a3b8', fontSize: '12px' }}>Result</th>
              </tr>
            </thead>
            <tbody>
              {logs.map(log => (
                <tr key={log.id} style={{ borderBottom: '1px solid #020617' }}>
                  <td style={{ padding: '10px 8px', fontSize: '12px', fontFamily: 'monospace', color: '#64748b' }}>{new Date(log.executed_at).toLocaleString()}</td>
                  <td style={{ padding: '10px 8px', fontSize: '13px', fontWeight: 'bold' }}>{log.game_name}</td>
                  <td style={{ padding: '10px 8px' }}>
                    <span style={{ fontSize: '10px', textTransform: 'uppercase', padding: '2px 6px', borderRadius: '3px', background: log.status === 'SUCCESS' ? '#064e3b' : log.status === 'FAILED' ? '#450a0a' : (log.status === 'IMPORTING' ? '#78350f' : '#1e293b'), color: log.status === 'SUCCESS' ? '#10b981' : log.status === 'FAILED' ? '#ef4444' : (log.status === 'IMPORTING' ? '#f59e0b' : '#94a3b8') }}>{log.status}</span>
                  </td>
                  <td style={{ padding: '10px 8px', fontSize: '12px', color: log.status === 'FAILED' ? '#fca5a5' : '#cbd5e1' }}>{log.status === 'FAILED' ? log.error_message : (log.status === 'IMPORTING' ? 'Processing data stream...' : `+${log.new_records} records`)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
