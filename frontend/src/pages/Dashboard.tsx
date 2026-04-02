import { useState, useEffect } from 'react';
import { fetchWithAuth, getTier, logout } from '../utils/auth';
import mermaid from 'mermaid';

// JMc - [2026-04-01] - Initialize Mermaid for architectural visualization.
mermaid.initialize({
  startOnLoad: true,
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
    // JMc - [2026-04-01] - Trigger Mermaid re-render.
    mermaid.contentLoaded();
  }, []);

  useEffect(() => {
    // JMc - [2026-03-18] - Fetch the available configured states autonomously.
    const ts = new Date().getTime();
    fetch(`${API_BASE}/api/states?_t=${ts}`)
      .then(res => res.json())
      .then(data => {
        if (data.states && data.states.length > 0) {
          setStatesList(data.states);
          if (!data.states.includes(selectedState)) {
             setSelectedState(data.states[0]);
          }
        }
      })
      .catch(err => console.error("Failed to load states:", err));
  }, []);

  useEffect(() => {
    // JMc - [2026-04-01] - Fetch ALL games across ALL states for the Global Pulse Ticker.
    const ts = new Date().getTime();
    fetch(`${API_BASE}/api/games?_t=${ts}`)
      .then(res => res.json())
      .then(data => {
        if (data.games_full) {
          setAllGames(data.games_full);
          // Pre-fetch recent draws for the ticker
          data.games_full.forEach((g: any) => {
             fetchWithAuth(`/api/history/${g.id}?limit=1&_t=${ts}`)
              .then(res => res.json())
              .then(history => {
                if (history && history.length > 0) {
                  setRecentDraws(prev => ({...prev, [g.id]: history[0]}));
                }
              })
              .catch(err => console.error(`Failed to load history for ${g.id}:`, err));
          });
        }
      })
      .catch(err => console.error("Failed to load global game roster:", err));

    // Pull jackpots for ALL games
    fetch(`${API_BASE}/api/jackpots?_t=${ts}`)
      .then(res => res.json())
      .then(data => setJackpots(data))
      .catch(err => console.error("Failed to load global jackpots:", err));
  }, []);

  useEffect(() => {
    // JMc - [2026-03-16] - Dynamically fetch available games for the selector.
    const ts = new Date().getTime();
    fetch(`${API_BASE}/api/games?state=${selectedState}&_t=${ts}`)
      .then(res => res.json())
      .then(data => {
        if (data.games) {
          setGames(data.games);
          setSelectedGame(data.games[0]);
        }
      })
      .catch(err => console.error("Failed to load local games:", err));
      
    loadSavedTickets();
  }, [selectedState]);

  const loadSavedTickets = async () => {
    try {
      const res = await fetchWithAuth('/api/my-tickets');
      if (res.ok) {
        const data = await res.json();
        setSavedBatches(data);
      }
    } catch (e) {
      console.error("Failed to load vault");
    }
  };

  const handleUpgrade = () => {
    window.location.href = "https://oracle.moderncyph3r.com/offering-page";
  };

  const generateTickets = async () => {
    setLoading(true);
    setError(null);
    setTickets([]);
    
    try {
      const safeNumTickets = Math.min(Math.max(1, numTickets), maxTickets);
      const res = await fetchWithAuth(`/api/generate/${selectedGame}?num_tickets=${safeNumTickets}`, {
        method: 'POST'
      });
      const data = await res.json();
      if (!res.ok) {
        if (res.status === 429) {
          throw new Error('Neural Link Throttled: Too many generation requests. Please wait a moment for the matrices to cool.');
        }
        throw new Error(data.detail || 'Generation failed');
      }
      setTickets(data.tickets);
      loadSavedTickets(); 
    } catch (e: any) {
      setError(e.message || "An unexpected error occurred");
    } finally {
      setLoading(false);
    }
  };

  const checkBatch = async (batchId: number) => {
    setCheckingBatch(batchId);
    try {
      const res = await fetchWithAuth(`/api/check-batch/${batchId}`);
      if (res.ok) {
        const data = await res.json();
        setBatchResults(prev => ({ ...prev, [batchId]: data }));
      }
    } catch (e) {
      console.error("Failed to check batch reality");
    } finally {
      setCheckingBatch(null);
    }
  };

  const deleteBatch = async (batchId: number) => {
    if (!window.confirm("Are you sure you want to permanently delete this batch? This cannot be undone.")) return;
    try {
      const res = await fetchWithAuth(`/api/batches/${batchId}`, { method: 'DELETE' });
      if (res.ok) {
        setSavedBatches(prev => prev.filter(b => b.id !== batchId));
        setExpandedBatch(null);
      }
    } catch (e) {
      console.error("Failed to delete batch");
    }
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
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
      }
    } catch (e) {
      console.error("Failed to export PDF");
    }
  };

  const MathRealitySection = () => (
    <section style={{ marginBottom: '4rem', padding: '2rem', background: 'rgba(15, 23, 42, 0.5)', borderRadius: '12px', border: '1px solid var(--border)' }}>
      <h2 style={{ fontSize: '1.8rem', color: 'var(--text-main)', marginBottom: '1rem', borderBottom: '2px solid var(--accent)', paddingBottom: '0.5rem', display: 'inline-block' }}>
        The Mathematical Reality: Organizing the Variance
      </h2>
      <p style={{ fontSize: '1.1rem', color: 'var(--text-muted)', lineHeight: '1.6', marginBottom: '2rem' }}>
        The Oracle doesn't predict the future; it <strong>organizes the variance</strong>. Every draw is an independent event, and the ping-pong balls do not have memory. We don't ask for "lucky numbers"; we apply raw empirical data to a game of pure, brutal mathematical variance.
      </p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '2rem', marginBottom: '3rem' }}>
        <div style={{ padding: '1.5rem', background: 'var(--panel-bg)', borderRadius: '8px', borderLeft: '4px solid var(--accent)' }}>
          <h3 style={{ color: 'var(--accent)', marginTop: 0 }}>01. The Prophet</h3>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
            <strong>Autonomous Seeding:</strong> Scans a decade of historical data using <strong>Markov Chains</strong> (40%), <strong>Poisson Distribution</strong> (40%), and <strong>Base Frequency</strong> (20%) to build a high-tension 15-number Smart Pool.
          </p>
        </div>
        <div style={{ padding: '1.5rem', background: 'var(--panel-bg)', borderRadius: '8px', borderLeft: '4px solid #8b5cf6' }}>
          <h3 style={{ color: '#8b5cf6', marginTop: 0 }}>02. The Pragmatist</h3>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
            <strong>Combinatorial Wheeling:</strong> Takes the Smart Pool and establishes maximum coverage across 3,003 possible variations, prioritizing 3-number triplets to ensure structural integrity in every batch.
          </p>
        </div>
        <div style={{ padding: '1.5rem', background: 'var(--panel-bg)', borderRadius: '8px', borderLeft: '4px solid #10b981' }}>
          <h3 style={{ color: '#10b981', marginTop: 0 }}>03. The Pattern Scouter</h3>
          <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
            <strong>The Purge:</strong> Enforces strict geometric filters. We reject odd/even outliers, spatial spread traps, consecutive sequences, and historical jackpot collisions.
          </p>
        </div>
      </div>
      <div style={{ padding: '2rem', background: '#020617', borderRadius: '12px', border: '1px solid var(--border)' }}>
        <h4 style={{ textAlign: 'center', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '2px', marginBottom: '1.5rem', fontSize: '0.8rem' }}>
          Autonomous Architecture Flow
        </h4>
        <div className="mermaid" style={{ display: 'flex', justifyContent: 'center' }}>
{`graph TD
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
    style FINAL fill:#065f46,stroke:#10b981,color:#fff`}
        </div>
      </div>
    </section>
  );

  return (
    <div className="container">
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>Oracle Command Terminal</h1>
          <p className="subtitle">Tier Protocol: <span style={{ color: 'var(--accent)', textTransform: 'uppercase' }}>{tier}</span></p>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <select
            value={selectedState}
            onChange={(e) => setSelectedState(e.target.value)}
            style={{ padding: '0.5rem', borderRadius: '4px', background: 'var(--panel-bg)', color: 'var(--text-main)', border: '1px solid var(--border)' }}
          >
            {statesList.map(st => (
              <option key={st} value={st}>{st === 'VA' ? 'Virginia (VA)' : st === 'TX' ? 'Texas (TX)' : st === 'NY' ? 'New York (NY)' : st}</option>
            ))}
          </select>
          <button onClick={logout} className="btn-secondary">Logout</button>
        </div>
      </header>

      <main>
        {/* JMc - [2026-04-01] - Global Pulse Ticker */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
           <h2 style={{ margin: 0, fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--text-muted)' }}>Global Pulse Ticker</h2>
           <span style={{ fontSize: '0.75rem', color: 'var(--accent)', fontWeight: 'bold' }}>SYSTEM ONLINE • MATRICES EXPANDING WEEKLY</span>
        </div>
        <div className="ticker-container">
          {(allGames.length > 0 ? allGames : [{id: 'Powerball', name: 'Powerball', state: 'National'}, {id: 'MegaMillions', name: 'Mega Millions', state: 'National'}]).map(game => (
            <div key={game.id} className="ticker-card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.65rem', color: 'var(--accent)', fontWeight: 'bold', textTransform: 'uppercase' }}>{game.state}</span>
                <span style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>{recentDraws[game.id] ? recentDraws[game.id].date : ''}</span>
              </div>
              <div style={{ fontSize: '0.9rem', fontWeight: 'bold', marginBottom: '0.25rem' }}>{game.name}</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: 'white', marginBottom: '0.5rem' }}>
                {jackpots?.[game.id]?.jackpot || 'Syncing...'}
              </div>
              {recentDraws[game.id] && (
                <div style={{ display: 'flex', gap: '0.25rem' }}>
                   {recentDraws[game.id].white_balls.slice(0, 5).map((w: number, i: number) => (
                     <span key={i} style={{ width: '18px', height: '18px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--ball-bg)', color: 'var(--ball-text)', borderRadius: '50%', fontWeight: 'bold', fontSize: '0.6rem' }}>
                       {w.toString().padStart(2, '0')}
                     </span>
                   ))}
                   {recentDraws[game.id].special_ball !== null && (
                     <span style={{ width: '18px', height: '18px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--special-ball-bg)', color: 'white', borderRadius: '50%', fontWeight: 'bold', fontSize: '0.6rem' }}>
                       {recentDraws[game.id].special_ball.toString().padStart(2, '0')}
                     </span>
                   )}
                </div>
              )}
            </div>
          ))}
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
              <input 
                type="number" 
                min="1" 
                max={maxTickets} 
                value={numTickets} 
                onChange={(e) => setNumTickets(parseInt(e.target.value) || 1)}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: 'var(--bg-color)',
                  border: '1px solid var(--border)',
                  color: 'var(--text-main)',
                  borderRadius: '6px',
                  fontSize: '1rem',
                  outline: 'none'
                }}
              />
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-end', paddingBottom: '2px' }}>
            <button onClick={generateTickets} disabled={loading} className="btn-primary" style={{ height: 'calc(100% - 22px)' }}>
              {loading ? 'Compiling Matrices...' : 'Execute Generation'}
            </button>
          </div>
        </section>

        {error && (
          <div style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', padding: '1rem', borderRadius: '8px', marginBottom: '2rem', border: '1px solid rgba(239, 68, 68, 0.3)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div><strong>System Halt:</strong> {error}</div>
            {error.includes('Upgrade to Pro') && (
              <button onClick={handleUpgrade} style={{ background: '#ef4444', color: 'white', border: 'none', padding: '0.5rem 1rem', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
                Elevate Tier
              </button>
            )}
          </div>
        )}

        {/* Free Tier: Show Math Reality here */}
        {tier !== 'pro' && <MathRealitySection />}

        {tickets.length > 0 && (
          <section className="results" style={{ marginBottom: '4rem' }}>
            <h2>New Deployment Sequence</h2>
            <div className="ticket-grid">
              {tickets.map((t, idx) => (
                <div key={idx} className="ticket">
                  <div className="white-balls">
                    {t.white_balls.map((w: number, i: number) => (
                      <span key={i} className="ball">{w.toString().padStart(2, '0')}</span>
                    ))}
                  </div>
                  {t.special_ball !== null && (
                    <span className="special-ball">{t.special_ball.toString().padStart(2, '0')}</span>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        <section className="vault">
          <h2>The Vault (Historical Artifacts)</h2>
          {savedBatches.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>No historical artifacts found in your sector.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {savedBatches.map(batch => (
                <div key={batch.id} style={{ background: 'var(--panel-bg)', borderRadius: '8px', border: '1px solid var(--border)', overflow: 'hidden' }}>
                  <div 
                    onClick={() => setExpandedBatch(expandedBatch === batch.id ? null : batch.id)}
                    style={{ padding: '1rem 1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer', background: expandedBatch === batch.id ? 'rgba(255,255,255,0.02)' : 'transparent' }}
                  >
                    <div>
                      <strong style={{ fontSize: '1.1rem', display: 'block', marginBottom: '0.2rem' }}>{batch.game_name}</strong>
                      <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                        {new Date(batch.created_at).toLocaleString()} • {batch.tickets.length} Tickets
                      </span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                      <div style={{ color: 'var(--accent)', fontWeight: 'bold' }}>{expandedBatch === batch.id ? 'Hide ↑' : 'View ↓'}</div>
                      <button onClick={(e) => { e.stopPropagation(); deleteBatch(batch.id); }} className="btn-secondary" style={{ padding: '0.25rem 0.75rem', color: '#ef4444', borderColor: '#ef4444' }}>Delete</button>
                    </div>
                  </div>

                  {expandedBatch === batch.id && (
                    <div style={{ padding: '1.5rem', borderTop: '1px solid var(--border)', background: 'rgba(0,0,0,0.2)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                        <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Generated Combinations</h3>
                        <div style={{ display: 'flex', gap: '1rem' }}>
                          <button onClick={() => exportBatch(batch.id, batch.game_name)} className="btn-secondary">📄 Export PDF</button>
                          <button onClick={() => checkBatch(batch.id)} disabled={checkingBatch === batch.id} className="btn-primary">{checkingBatch === batch.id ? 'Checking...' : 'Run Reality Check'}</button>
                        </div>
                      </div>

                      {batchResults[batch.id] && (
                        <div style={{ marginBottom: '2rem', padding: '1.5rem', borderRadius: '8px', background: 'var(--bg-color)', border: '1px solid var(--border)' }}>
                          <h3 style={{ marginTop: 0, borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>Reality Check Report</h3>
                          <div style={{ display: 'flex', gap: '2rem', marginBottom: '1.5rem' }}>
                            <div><div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Draws</div><div style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>{batchResults[batch.id].draws_checked}</div></div>
                            <div><div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Spent</div><div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#ef4444' }}>${batchResults[batch.id].total_spent}</div></div>
                            <div><div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Won</div><div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#10b981' }}>${batchResults[batch.id].total_won}</div></div>
                            <div><div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Net</div><div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: batchResults[batch.id].net_roi > 0 ? '#10b981' : '#ef4444' }}>${batchResults[batch.id].net_roi}</div></div>
                          </div>
                        </div>
                      )}

                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
                        {batch.tickets.map((t: any) => (
                          <div key={t.id} style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', padding: '0.75rem', background: 'var(--panel-bg)', borderRadius: '6px', border: '1px solid var(--border)' }}>
                            {t.white_balls.map((w: number, i: number) => (
                              <span key={i} style={{ width: '28px', height: '28px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--ball-bg)', color: 'var(--ball-text)', borderRadius: '50%', fontWeight: 'bold', fontSize: '0.75rem' }}>
                                {w.toString().padStart(2, '0')}
                              </span>
                            ))}
                            {t.special_ball !== null && (
                              <span style={{ width: '28px', height: '28px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--special-ball-bg)', color: 'white', borderRadius: '50%', fontWeight: 'bold', fontSize: '0.75rem', marginLeft: 'auto' }}>
                                {t.special_ball.toString().padStart(2, '0')}
                              </span>
                            )}
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

        {/* Pro Tier: Hide Math Reality behind Vault */}
        {tier === 'pro' && (
           <div style={{ marginTop: '5rem', opacity: 0.5 }}>
              <MathRealitySection />
           </div>
        )}

        {tier === 'free' && (
          <section style={{ marginTop: '4rem', padding: '3rem', background: 'linear-gradient(135deg, var(--panel-bg) 0%, #1e3a8a 100%)', borderRadius: '16px', border: '1px solid var(--accent)', textAlign: 'center' }}>
            <h2 style={{ fontSize: '1.5rem', color: 'white' }}>Standard Terminal: Limit 5 Tickets</h2>
            <p style={{ marginBottom: '2rem' }}>Elevate to Pro for 50 tickets per generation and advanced Markov matrices.</p>
            <button onClick={handleUpgrade} className="btn-primary">ELEVATE TO PRO TIER</button>
          </section>
        )}
      </main>
    </div>
  );
};

export default Dashboard;
