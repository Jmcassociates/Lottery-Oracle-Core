import { useState, useEffect, useRef } from 'react';
import { fetchWithAuth, getTier, logout } from '../utils/auth';
import mermaid from 'mermaid';

// JMc - [2026-04-01] - Initialize Mermaid with high-contrast dark theme.
mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  securityLevel: 'loose',
  fontFamily: 'Segoe UI, system-ui, sans-serif'
});

const API_BASE = import.meta.env.VITE_API_URL || '';

interface JackpotData {
  [game: string]: {
    jackpot: string;
    next_draw: string;
    state?: string;
  }
}

// JMc - [2026-04-01] - Robust Mermaid component to handle React lifecycle rendering.
const MermaidDiagram = ({ chart }: { chart: string }) => {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (ref.current) {
      // Clear previous processing
      ref.current.removeAttribute('data-processed');
      ref.current.innerHTML = ''; 
      
      const renderChart = async () => {
        try {
          const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`;
          const { svg } = await mermaid.render(id, chart);
          if (ref.current) ref.current.innerHTML = svg;
        } catch (e) {
          console.error("Mermaid Render Error:", e);
        }
      };
      renderChart();
    }
  }, [chart]);

  return <div ref={ref} className="mermaid-render" style={{ display: 'flex', justifyContent: 'center', width: '100%', minHeight: '300px' }} />;
};

const Dashboard = () => {
  const [statesList, setStatesList] = useState<string[]>(['VA']);
  const [games, setGames] = useState<string[]>([]);
  const [allGames, setAllGames] = useState<{id: string, name: string, state: string}[]>([]);
  const [selectedGame, setSelectedGame] = useState<string>('Powerball');
  const [selectedState, setSelectedState] = useState<string>('VA');
  const [tickets, setTickets] = useState<any[]>([]);
  const [savedBatches, setSavedBatches] = useState<any[]>([]);
  const [batchResults, setBatchResults] = useState<Record<number, any>>({});
  const [checkingBatch, setCheckingBatch] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedBatch, setExpandedBatch] = useState<number | null>(null);
  
  const [jackpots, setJackpots] = useState<JackpotData | null>(null);
  const [recentDraws, setRecentDraws] = useState<Record<string, any>>({});

  const tier = getTier();
  const maxTickets = tier === 'pro' ? 50 : 5;
  const [numTickets, setNumTickets] = useState<number>(tier === 'pro' ? 20 : 5);

  useEffect(() => {
    const ts = new Date().getTime();
    fetch(`${API_BASE}/api/states?_t=${ts}`)
      .then(res => res.json())
      .then(data => {
        if (data.states && data.states.length > 0) {
          setStatesList(data.states);
          if (!data.states.includes(selectedState)) setSelectedState(data.states[0]);
        }
      })
      .catch(err => console.error("Failed to load states:", err));
  }, []);

  useEffect(() => {
    const ts = new Date().getTime();
    fetch(`${API_BASE}/api/games?_t=${ts}`)
      .then(res => res.json())
      .then(data => {
        if (data.games_full) {
          setAllGames(data.games_full);
          data.games_full.forEach((g: any) => {
             fetchWithAuth(`/api/history/${g.id}?limit=1&_t=${ts}`)
              .then(res => res.json())
              .then(history => {
                if (history && history.length > 0) setRecentDraws(prev => ({...prev, [g.id]: history[0]}));
              })
              .catch(err => console.error(`Failed history for ${g.id}:`, err));
          });
        }
      })
      .catch(err => console.error("Failed games roster load:", err));

    fetch(`${API_BASE}/api/jackpots?_t=${ts}`)
      .then(res => res.json())
      .then(data => setJackpots(data))
      .catch(err => console.error("Failed global jackpots load:", err));
  }, []);

  useEffect(() => {
    const ts = new Date().getTime();
    fetch(`${API_BASE}/api/games?state=${selectedState}&_t=${ts}`)
      .then(res => res.json())
      .then(data => {
        if (data.games) {
          setGames(data.games);
          setSelectedGame(data.games[0]);
        }
      })
      .catch(err => console.error("Failed local games load:", err));
    loadSavedTickets();
  }, [selectedState]);

  const loadSavedTickets = async () => {
    try {
      const res = await fetchWithAuth('/api/my-tickets');
      if (res.ok) setSavedBatches(await res.json());
    } catch (e) { console.error("Failed vault load:", e); }
  };

  const handleUpgrade = () => {
    window.location.href = "https://oracle.moderncyph3r.com/offering-page";
  };

  const generateTickets = async () => {
    setLoading(true); setError(null); setTickets([]);
    try {
      const safeNumTickets = Math.min(Math.max(1, numTickets), maxTickets);
      const res = await fetchWithAuth(`/api/generate/${selectedGame}?num_tickets=${safeNumTickets}`, { method: 'POST' });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Generation failed');
      setTickets(data.tickets);
      loadSavedTickets(); 
    } catch (e: any) { setError(e.message || "An unexpected error occurred");
    } finally { setLoading(false); }
  };

  const checkBatch = async (batchId: number) => {
    setCheckingBatch(batchId);
    try {
      const res = await fetchWithAuth(`/api/check-batch/${batchId}`);
      if (res.ok) {
        const data = await res.json();
        setBatchResults(prev => ({ ...prev, [batchId]: data }));
      }
    } catch (e) { console.error("Failed check:", e); } finally { setCheckingBatch(null); }
  };

  const deleteBatch = async (batchId: number) => {
    if (!window.confirm("Are you sure?")) return;
    try {
      const res = await fetchWithAuth(`/api/batches/${batchId}`, { method: 'DELETE' });
      if (res.ok) {
        setSavedBatches(prev => prev.filter(b => b.id !== batchId));
        setExpandedBatch(null);
      }
    } catch (e) { console.error("Failed delete:", e); }
  };

  const exportBatch = async (batchId: number, gameName: string) => {
    try {
      const tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
      const res = await fetchWithAuth(`/api/export-batch/${batchId}?tz=${encodeURIComponent(tz)}`);
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `Oracle_Manifest_${gameName}_${batchId}.pdf`;
        document.body.appendChild(a);
        a.click(); a.remove(); window.URL.revokeObjectURL(url);
      }
    } catch (e) { console.error("Failed export:", e); }
  };

  const MathRealitySection = () => (
    <section style={{ marginBottom: '4rem', padding: '2.5rem', background: 'rgba(30, 41, 59, 0.9)', borderRadius: '16px', border: '1px solid var(--border)', boxShadow: '0 8px 32px rgba(0,0,0,0.6)' }}>
      <h2 style={{ fontSize: '2rem', color: '#ffffff', marginBottom: '1.5rem', borderBottom: '2px solid var(--accent)', paddingBottom: '0.75rem', display: 'inline-block' }}>
        The Mathematical Reality: Organizing the Variance
      </h2>
      <p style={{ fontSize: '1.2rem', color: '#f1f5f9', lineHeight: '1.7', marginBottom: '2.5rem' }}>
        The Oracle doesn't predict the future; it <strong>organizes the variance</strong>. Every draw is an independent event, and the ping-pong balls do not have memory. We apply raw empirical data to a game of pure, brutal mathematical variance.
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '2rem', marginBottom: '3.5rem' }}>
        <div style={{ padding: '1.75rem', background: 'var(--panel-bg)', borderRadius: '12px', borderLeft: '4px solid var(--accent)' }}>
          <h3 style={{ color: '#ffffff', marginTop: 0, fontSize: '1.25rem' }}>01. The Prophet</h3>
          <p style={{ fontSize: '1rem', color: '#e2e8f0', lineHeight: '1.5' }}>
            <strong>Autonomous Seeding:</strong> Scans a decade of historical data using <strong>Markov Chains</strong> (40%), <strong>Poisson Distribution</strong> (40%), and <strong>Base Frequency</strong> (20%) to build a high-tension 15-number Smart Pool.
          </p>
        </div>
        <div style={{ padding: '1.75rem', background: 'var(--panel-bg)', borderRadius: '12px', borderLeft: '4px solid #8b5cf6' }}>
          <h3 style={{ color: '#ffffff', marginTop: 0, fontSize: '1.25rem' }}>02. The Pragmatist</h3>
          <p style={{ fontSize: '1rem', color: '#e2e8f0', lineHeight: '1.5' }}>
            <strong>Combinatorial Wheeling:</strong> Takes the Smart Pool and establishes maximum coverage across 3,003 possible variations, prioritizing 3-number triplets to ensure structural integrity in every batch.
          </p>
        </div>
        <div style={{ padding: '1.75rem', background: 'var(--panel-bg)', borderRadius: '12px', borderLeft: '4px solid #10b981' }}>
          <h3 style={{ color: '#ffffff', marginTop: 0, fontSize: '1.25rem' }}>03. The Pattern Scouter</h3>
          <p style={{ fontSize: '1rem', color: '#e2e8f0', lineHeight: '1.5' }}>
            <strong>The Purge:</strong> Enforces strict geometric filters. We reject odd/even outliers, spatial spread traps, consecutive sequences, and historical jackpot collisions.
          </p>
        </div>
      </div>

      {/* JMc - [2026-04-03] - The Oracle Doctrine Integration */}
      <div style={{ padding: '2rem', background: 'rgba(15, 23, 42, 0.8)', borderRadius: '12px', border: '1px solid #334155', marginBottom: '3.5rem' }}>
        <h3 style={{ color: '#38bdf8', marginTop: 0, textTransform: 'uppercase', letterSpacing: '1px', fontSize: '1.1rem' }}>The Oracle Doctrine: The 15-Number Fulcrum</h3>
        <p style={{ color: '#cbd5e1', fontSize: '1rem', lineHeight: '1.6' }}>
          When wheeling a 15-number pool, permutations explode to <strong>3,003 combinations</strong>. Expanding to 20 numbers would require 15,504 variations—a six-figure budget for a single draw. The Oracle Doctrine ruthlessly restricts the 'Smart Pool' to 15 numbers to maintain the <strong>triplet guarantee</strong>: if 3 winning numbers fall anywhere in your 15-number pool, the Pragmatist ensures you hold at least one ticket with that match.
        </p>
        <div style={{ marginTop: '1.5rem', padding: '1.25rem', background: 'rgba(245, 158, 11, 0.1)', borderLeft: '4px solid #f59e0b', borderRadius: '4px' }}>
          <strong style={{ color: '#f59e0b', display: 'block', marginBottom: '0.5rem' }}>CONTROLLED ENTROPY: THE INDIVIDUALIZED ORACLE</strong>
          <p style={{ margin: 0, color: '#e2e8f0', fontSize: '0.95rem', fontStyle: 'italic' }}>
            We do not run a syndicate. The Pragmatist dynamically shuffles the 3,003 base combinations <em>before</em> wheeling. Every user receives a mathematically vetted, high-coverage batch that is <strong>completely unique to their terminal.</strong>
          </p>
        </div>
      </div>

      <div style={{ padding: '2.5rem', background: '#020617', borderRadius: '16px', border: '1px solid var(--border)' }}>
        <h4 style={{ textAlign: 'center', color: '#ffffff', textTransform: 'uppercase', letterSpacing: '2px', marginBottom: '2.5rem', fontSize: '0.9rem', fontWeight: 'bold' }}>
          Autonomous Architecture Flow
        </h4>
        <MermaidDiagram chart={`graph TD
    DB[(10-Year Database)] --> PROPHET[The Prophet Algorithm]
    
    subgraph Scoring Models
        PROPHET --> |40% Weight| M[Markov Chain]
        PROPHET --> |40% Weight| P[Poisson Tension]
        PROPHET --> |20% Weight| F[Frequency]
    end
    
    M & P & F --> POOL[15-Number Smart Pool]
    
    POOL --> PRAGMATIST[The Pragmatist]
    PRAGMATIST --> |Wheeling| ALL[3,003 Combinations]
    
    ALL --> SCOUTER{Pattern Scouter}
    
    SCOUTER -->|Approve| FINAL[Final Optimized Batch]
    
    style DB fill:#1e293b,stroke:#334155,color:#fff
    style PROPHET fill:#1e3a8a,stroke:#3b82f6,color:#fff
    style POOL fill:#064e3b,stroke:#10b981,color:#fff
    style PRAGMATIST fill:#4c1d95,stroke:#8b5cf6,color:#fff
    style SCOUTER fill:#92400e,stroke:#f59e0b,color:#fff
    style FINAL fill:#065f46,stroke:#10b981,color:#fff`} />
      </div>
    </section>
  );

  return (
    <div className="container">
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>Oracle Command Terminal</h1>
          <p className="subtitle">Operational Sector Dashboard</p>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <select value={selectedState} onChange={(e) => setSelectedState(e.target.value)}
            style={{ padding: '0.5rem', borderRadius: '4px', background: 'var(--panel-bg)', color: 'var(--text-main)', border: '1px solid var(--border)' }}
          >
            {statesList.map(st => (
              <option key={st} value={st}>{st === 'VA' ? 'Virginia (VA)' : st === 'TX' ? 'Texas (TX)' : st === 'NY' ? 'New York (NY)' : st}</option>
            ))}
          </select>

          {/* JMc - [2026-04-03] - Technician Account Hub */}
          <div className="account-menu">
            <button className="btn-secondary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              Account ▾
            </button>
            <div className="dropdown-content">
              <div className="dropdown-header">Active Protocol</div>
              <div className="dropdown-tier">
                {tier === 'pro' ? 'Pro Tier' : 'Free Tier'}
              </div>
              
              <a href="https://oracle.moderncyph3r.com/offering-page" className="dropdown-item">
                {tier === 'pro' ? 'Manage Subscription' : 'Upgrade to Pro'}
              </a>
              
              <a href="https://oracle.moderncyph3r.com/support" target="_blank" rel="noreferrer" className="dropdown-item">
                Contact Support
              </a>
              
              <div className="dropdown-divider"></div>
              <div onClick={logout} className="dropdown-item" style={{ color: '#ef4444' }}>
                Logout System
              </div>
            </div>
          </div>
        </div>
      </header>

      <main>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
           <h2 style={{ margin: 0, fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--text-muted)' }}>Global Pulse Ticker</h2>
           <span style={{ fontSize: '0.75rem', color: 'var(--accent)', fontWeight: 'bold' }}>SYSTEM ONLINE • MATRICES EXPANDING WEEKLY</span>
        </div>
        <div className="ticker-container">
          <div className="ticker-track">
            {[...(allGames.length > 0 ? allGames : [{id: 'Powerball', name: 'Powerball', state: 'National'}]), ...(allGames.length > 0 ? allGames : [{id: 'Powerball', name: 'Powerball', state: 'National'}])].map((game, idx) => (
              <div key={`${game.id}-${idx}`} className="ticker-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                  <span style={{ fontSize: '0.65rem', color: 'var(--accent)', fontWeight: 'bold', textTransform: 'uppercase' }}>{game.state}</span>
                  <span style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>{recentDraws[game.id]?.date || ''}</span>
                </div>
                <div style={{ fontSize: '0.9rem', fontWeight: 'bold', marginBottom: '0.25rem', color: 'white' }}>{game.name}</div>
                <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: 'white', marginBottom: '0.5rem' }}>{jackpots?.[game.id]?.jackpot || 'Syncing...'}</div>
                {recentDraws[game.id] && (
                  <div style={{ display: 'flex', gap: '0.25rem' }}>
                   {recentDraws[game.id].white_balls.slice(0, 5).map((w: number, i: number) => (
                     <span key={i} style={{ width: '18px', height: '18px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--ball-bg)', color: 'var(--ball-text)', borderRadius: '50%', fontWeight: 'bold', fontSize: '0.6rem' }}>{w.toString().padStart(2, '0')}</span>
                   ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        <section className="control-panel">
          <div style={{ display: 'flex', gap: '2rem', flex: 1 }}>
            <div className="selector" style={{ flex: 1 }}>
              <label>Target Game Matrix:</label>
              <select value={selectedGame} onChange={(e) => setSelectedGame(e.target.value)}>
                {games.map(g => <option key={g} value={g}>{g}</option>)}
              </select>
            </div>
            <div className="selector" style={{ flex: 1 }}>
              <label>Volume (Max {maxTickets}):</label>
              <input type="number" min="1" max={maxTickets} value={numTickets} onChange={(e) => setNumTickets(parseInt(e.target.value) || 1)}
                style={{ padding: '0.75rem 1.5rem', background: 'var(--bg-color)', border: '1px solid var(--border)', color: 'var(--text-main)', borderRadius: '6px' }}
              />
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-end', paddingBottom: '2px' }}>
            <button onClick={generateTickets} disabled={loading} className="btn-primary" style={{ height: 'calc(100% - 22px)' }}>{loading ? 'Compiling...' : 'Execute Generation'}</button>
          </div>
        </section>

        {error && (
          <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', padding: '1rem', borderRadius: '8px', marginBottom: '2rem', border: '1px solid #ef4444' }}>
            <strong>System Halt:</strong> {error}
          </div>
        )}

        {tier !== 'pro' && <MathRealitySection />}

        {tickets.length > 0 && (
          <section className="results" style={{ marginBottom: '4rem' }}>
            <h2>New Deployment Sequence</h2>
            <div className="ticket-grid">
              {tickets.map((t, idx) => (
                <div key={idx} className="ticket">
                  <div className="white-balls">{t.white_balls.map((w: number, i: number) => <span key={i} className="ball">{w.toString().padStart(2, '0')}</span>)}</div>
                  {t.special_ball !== null && <span className="special-ball">{t.special_ball.toString().padStart(2, '0')}</span>}
                </div>
              ))}
            </div>
          </section>
        )}

        <section className="vault">
          <h2>The Vault (Historical Artifacts)</h2>
          {savedBatches.length === 0 ? <p style={{ color: 'var(--text-muted)' }}>No historical artifacts found.</p> : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {savedBatches.map(batch => (
                <div key={batch.id} style={{ background: 'var(--panel-bg)', borderRadius: '8px', border: '1px solid var(--border)', overflow: 'hidden' }}>
                  <div onClick={() => setExpandedBatch(expandedBatch === batch.id ? null : batch.id)}
                    style={{ padding: '1rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}
                  >
                    <div><strong>{batch.game_name}</strong><span style={{ fontSize: '0.85rem', color: 'var(--text-muted)', display: 'block' }}>{new Date(batch.created_at).toLocaleString()} • {batch.tickets.length} Tickets</span></div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                      <div style={{ color: 'var(--accent)', fontWeight: 'bold' }}>{expandedBatch === batch.id ? 'Hide ↑' : 'View ↓'}</div>
                      <button onClick={(e) => { e.stopPropagation(); deleteBatch(batch.id); }} className="btn-secondary" style={{ color: '#ef4444', borderColor: '#ef4444' }}>Delete</button>
                    </div>
                  </div>
                  {expandedBatch === batch.id && (
                    <div style={{ padding: '1.5rem', borderTop: '1px solid var(--border)', background: 'rgba(0,0,0,0.2)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
                        <h3 style={{ margin: 0 }}>Generated Combinations</h3>
                        <div style={{ display: 'flex', gap: '1rem' }}>
                          <button onClick={() => exportBatch(batch.id, batch.game_name)} className="btn-secondary">📄 PDF</button>
                          <button onClick={() => checkBatch(batch.id)} disabled={checkingBatch === batch.id} className="btn-primary">Run Reality Check</button>
                        </div>
                      </div>
                      
                      {batchResults[batch.id] && (
                        <div style={{ marginBottom: '2rem', padding: '1.5rem', borderRadius: '8px', background: 'var(--bg-color)', border: '1px solid var(--border)' }}>
                          <h3 style={{ marginTop: 0 }}>Reality Check Report</h3>
                          <div style={{ display: 'flex', gap: '2rem' }}>
                            <div><div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Spent</div><div style={{ fontSize: '1.2rem', color: '#ef4444' }}>${batchResults[batch.id].total_spent}</div></div>
                            <div><div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Won</div><div style={{ fontSize: '1.2rem', color: '#10b981' }}>${batchResults[batch.id].total_won}</div></div>
                            <div><div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Net ROI</div><div style={{ fontSize: '1.2rem', color: batchResults[batch.id].net_roi > 0 ? '#10b981' : '#ef4444' }}>${batchResults[batch.id].net_roi}</div></div>
                          </div>
                        </div>
                      )}

                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
                        {batch.tickets.map((t: any) => (
                          <div key={t.id} style={{ display: 'flex', gap: '0.5rem', padding: '0.75rem', background: 'var(--panel-bg)', borderRadius: '6px', border: '1px solid var(--border)' }}>
                            {t.white_balls.map((w: number, i: number) => <span key={i} style={{ width: '28px', height: '28px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--ball-bg)', color: 'var(--ball-text)', borderRadius: '50%', fontWeight: 'bold', fontSize: '0.75rem' }}>{w.toString().padStart(2, '0')}</span>)}
                            {t.special_ball !== null && <span style={{ width: '28px', height: '28px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--special-ball-bg)', color: 'white', borderRadius: '50%', fontWeight: 'bold', fontSize: '0.75rem', marginLeft: 'auto' }}>{t.special_ball.toString().padStart(2, '0')}</span>}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>

        {tier === 'pro' && (
           <div style={{ marginTop: '5rem' }}>
              <MathRealitySection />
           </div>
        )}

        {tier === 'free' && (
          <section style={{ marginTop: '4rem', padding: '3rem', background: 'linear-gradient(135deg, var(--panel-bg) 0%, #1e3a8a 100%)', borderRadius: '16px', border: '1px solid var(--accent)', textAlign: 'center' }}>
            <h2 style={{ fontSize: '1.5rem', color: 'white' }}>Standard Terminal: Limit 5 Tickets</h2>
            <button onClick={handleUpgrade} className="btn-primary" style={{ marginTop: '1.5rem' }}>ELEVATE TO PRO TIER</button>
          </section>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
