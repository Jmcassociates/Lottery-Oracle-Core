// JMc - [2026-03-16] - Main Oracle Dashboard. Handles all authenticated interactions, Vault retrieval, and Reality Check execution.
import { useState, useEffect } from 'react';
import { fetchWithAuth, getTier, setToken, logout } from '../utils/auth';

interface JackpotData {
  [game: string]: {
    jackpot: string;
    next_draw: string;
  }
}

const Dashboard = () => {
  const [games, setGames] = useState<string[]>([]);
  const [selectedGame, setSelectedGame] = useState<string>('Powerball');
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
    // JMc - [2026-03-16] - Dynamically fetch available games from the API configuration.
    console.log("Dashboard mount - fetching games...");
    fetch('/api/games')
      .then(res => res.json())
      .then(data => {
        console.log("Games loaded:", data);
        if (data.games) {
          setGames(data.games);
          setSelectedGame(data.games[0]);
          
          // JMc - [2026-03-16] - Fetch recent draws for all games
          data.games.forEach((game: string) => {
            console.log(`Fetching history for ${game}...`);
            fetchWithAuth(`/api/history/${game}?limit=1`)
              .then(res => {
                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                return res.json();
              })
              .then(history => {
                console.log(`History for ${game}:`, history);
                if (history && history.length > 0) {
                  setRecentDraws(prev => ({...prev, [game]: history[0]}));
                }
              })
              .catch(err => console.error(`Failed to load history for ${game}:`, err));
          });
        }
      })
      .catch(err => console.error("Failed to load games:", err));
      
    // JMc - [2026-03-16] - Pull live jackpots from the scraper
    fetch('/api/jackpots')
      .then(res => res.json())
      .then(data => {
        console.log("Jackpots loaded:", data);
        setJackpots(data);
      })
      .catch(err => console.error("Failed to load jackpots:", err));
      
    loadSavedTickets();
  }, []);

  const loadSavedTickets = async () => {
    // JMc - [2026-03-16] - Fetch historical artifacts (batches) from the Vault.
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

  const handleUpgrade = async () => {
    try {
      const res = await fetchWithAuth('/api/user/upgrade', { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setToken(data.access_token, data.tier);
        window.location.reload(); 
      }
    } catch (e) {
      console.error("Upgrade failed", e);
    }
  };

  const generateTickets = async () => {
    // JMc - [2026-03-16] - Dispatch generation request to the selected Mathematical Engine.
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
    // JMc - [2026-03-16] - Trigger the Reality Check ROI calculator.
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

  const exportBatch = async (batchId: number, gameName: string) => {
    // JMc - [2026-03-16] - Fetch the PDF Manifest and force a local download.
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

  return (
    <div className="container">
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1>Oracle Back Office</h1>
          <p className="subtitle">Tier Protocol: <span style={{ color: 'var(--accent)', textTransform: 'uppercase' }}>{tier}</span></p>
        </div>
        <button onClick={logout} className="btn-secondary">Logout</button>
      </header>

      <main>
        {/* Information Dashboard */}
        <section className="info-dashboard" style={{ display: 'flex', gap: '2rem', marginBottom: '3rem', flexWrap: 'wrap' }}>
          {games.map(game => (
            <div key={game} style={{ flex: '1 1 300px', background: 'var(--panel-bg)', padding: '1.5rem', borderRadius: '12px', border: '1px solid var(--border)', minWidth: '300px' }}>
              <h3 style={{ marginTop: 0, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '1px', fontSize: '0.9rem', borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>
                {game === 'MegaMillions' ? 'Mega Millions' : game} Status
              </h3>
              
              <div style={{ marginBottom: '1.5rem' }}>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Current Jackpot</div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--accent)' }}>
                  {jackpots?.[game]?.jackpot || 'Pending...'}
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                  Next Draw: {jackpots?.[game]?.next_draw || 'Pending...'}
                </div>
              </div>

              <div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                  Latest Draw ({recentDraws[game] ? (() => {
                    const [y, m, d] = recentDraws[game].date.split('-');
                    return new Date(parseInt(y), parseInt(m) - 1, parseInt(d)).toLocaleDateString();
                  })() : '...'})
                </div>
                {recentDraws[game] ? (
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', flexWrap: 'wrap' }}>
                    {recentDraws[game].white_balls.map((w: number, i: number) => (
                      <span key={i} style={{ width: '28px', height: '28px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--ball-bg)', color: 'var(--ball-text)', borderRadius: '50%', fontWeight: 'bold', fontSize: '0.8rem' }}>
                        {w.toString().padStart(2, '0')}
                      </span>
                    ))}
                    {recentDraws[game].special_ball !== null && (
                      <span style={{ width: '28px', height: '28px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--special-ball-bg)', color: 'white', borderRadius: '50%', fontWeight: 'bold', fontSize: '0.8rem' }}>
                        {recentDraws[game].special_ball.toString().padStart(2, '0')}
                      </span>
                    )}
                  </div>
                ) : (
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Loading recent draw...</div>
                )}
              </div>
            </div>
          ))}
        </section>

        <section className="control-panel">
          <div style={{ display: 'flex', gap: '2rem', flex: 1 }}>
            <div className="selector" style={{ flex: 1 }}>
              <label>Target Game:</label>
              <select value={selectedGame} onChange={(e) => setSelectedGame(e.target.value)}>
                {games.map(g => <option key={g} value={g}>{g}</option>)}
              </select>
            </div>
            <div className="selector" style={{ flex: 1 }}>
              <label>Number of Tickets (Max {maxTickets}):</label>
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
            <div>
              <strong>System Halt:</strong> {error}
            </div>
            {error.includes('Upgrade to Pro') && (
              <button onClick={handleUpgrade} style={{ background: '#ef4444', color: 'white', border: 'none', padding: '0.5rem 1rem', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold' }}>
                Mock Upgrade (Bypass Billing)
              </button>
            )}
          </div>
        )}

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
          <h2>The Vault (Saved Batches)</h2>
          {savedBatches.length === 0 ? (
            <p style={{ color: 'var(--text-muted)' }}>No historical artifacts found in your sector.</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {savedBatches.map(batch => (
                <div key={batch.id} style={{ background: 'var(--panel-bg)', borderRadius: '8px', border: '1px solid var(--border)', overflow: 'hidden' }}>
                  
                  {/* Batch Header */}
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
                    <div style={{ color: 'var(--accent)', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      {expandedBatch === batch.id ? 'Hide Tickets ↑' : 'View Tickets ↓'}
                    </div>
                  </div>

                  {/* Expanded Tickets & Reality Check */}
                  {expandedBatch === batch.id && (
                    <div style={{ padding: '1.5rem', borderTop: '1px solid var(--border)', background: 'rgba(0,0,0,0.2)' }}>
                      
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                        <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Generated Combinations</h3>
                        <div style={{ display: 'flex', gap: '1rem' }}>
                          <button 
                            onClick={() => exportBatch(batch.id, batch.game_name)} 
                            style={{ background: 'transparent', color: 'var(--text-main)', border: '1px solid var(--border)', padding: '0.5rem 1rem', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', transition: 'all 0.2s ease', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                          >
                            <span>📄</span> Export PDF
                          </button>
                          <button 
                            onClick={() => checkBatch(batch.id)} 
                            disabled={checkingBatch === batch.id}
                            style={{ background: 'transparent', color: 'var(--accent)', border: '1px solid var(--accent)', padding: '0.5rem 1rem', borderRadius: '4px', cursor: 'pointer', fontWeight: 'bold', transition: 'all 0.2s ease' }}
                            onMouseOver={(e) => { e.currentTarget.style.background = 'var(--accent)'; e.currentTarget.style.color = 'white'; }}
                            onMouseOut={(e) => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = 'var(--accent)'; }}
                          >
                            {checkingBatch === batch.id ? 'Running Analysis...' : 'Run Reality Check'}
                          </button>
                        </div>
                      </div>

                      {/* Reality Check Results */}
                      {batchResults[batch.id] && (
                        <div style={{ marginBottom: '2rem', padding: '1.5rem', borderRadius: '8px', background: 'var(--bg-color)', border: '1px solid var(--border)' }}>
                          <h3 style={{ marginTop: 0, borderBottom: '1px solid var(--border)', paddingBottom: '0.5rem' }}>Reality Check Report</h3>
                          {batchResults[batch.id].status === 'pending' ? (
                            <p style={{ color: 'var(--text-muted)' }}>{batchResults[batch.id].message}</p>
                          ) : (
                            <div>
                              <div style={{ display: 'flex', gap: '2rem', marginBottom: '1.5rem' }}>
                                <div>
                                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Draws Checked</div>
                                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>{batchResults[batch.id].draws_checked}</div>
                                </div>
                                <div>
                                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total Spent</div>
                                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#ef4444' }}>${batchResults[batch.id].total_spent}</div>
                                </div>
                                <div>
                                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total Won</div>
                                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: batchResults[batch.id].total_won > 0 ? '#10b981' : 'var(--text-main)' }}>${batchResults[batch.id].total_won}</div>
                                </div>
                                <div>
                                  <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Net ROI</div>
                                  <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: batchResults[batch.id].net_roi > 0 ? '#10b981' : '#ef4444' }}>
                                    {batchResults[batch.id].net_roi > 0 ? '+' : ''}${batchResults[batch.id].net_roi}
                                  </div>
                                </div>
                              </div>

                              {batchResults[batch.id].details.map((drawResult: any, dIdx: number) => (
                                <div key={dIdx} style={{ marginBottom: '1rem', paddingBottom: '1rem', borderBottom: dIdx === batchResults[batch.id].details.length - 1 ? 'none' : '1px dashed var(--border)' }}>
                                  <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                                    Draw Date: {(() => {
                                      const [y, m, d] = drawResult.draw_date.split('T')[0].split('-');
                                      return new Date(parseInt(y), parseInt(m) - 1, parseInt(d)).toLocaleDateString();
                                    })()} | Winning Numbers: {drawResult.drawn_numbers.white_balls.join(', ')} {drawResult.drawn_numbers.special_ball !== null ? `[${drawResult.drawn_numbers.special_ball}]` : ''}
                                  </div>
                                  {drawResult.winning_tickets.length > 0 ? (
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginTop: '1rem' }}>
                                      {drawResult.winning_tickets.map((wt: any, wIdx: number) => {
                                        const isPick = batch.game_name.startsWith('Pick');
                                        return (
                                          <div key={wIdx} style={{ display: 'flex', alignItems: 'center', gap: '1rem', background: 'rgba(16, 185, 129, 0.1)', padding: '0.75rem', borderRadius: '6px', border: '1px solid rgba(16, 185, 129, 0.3)', flexWrap: 'wrap' }}>
                                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.2rem', minWidth: '130px' }}>
                                              <div style={{ color: '#10b981', fontWeight: 'bold', fontSize: '1rem' }}>
                                                ✓ Won ${wt.prize}
                                              </div>
                                              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                                                Matched {wt.matches.white} {wt.special_ball !== null ? (wt.matches.special ? '+ 1' : '+ 0') : ''}
                                              </div>
                                            </div>
                                            <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                                              {wt.white_balls.map((w: number, i: number) => {
                                                const isMatch = isPick 
                                                  ? w === drawResult.drawn_numbers.white_balls[i] 
                                                  : drawResult.drawn_numbers.white_balls.includes(w);
                                                return (
                                                  <span key={i} style={{ 
                                                    width: '28px', height: '28px', display: 'flex', alignItems: 'center', justifyContent: 'center', 
                                                    background: isMatch ? '#10b981' : 'var(--panel-bg)', 
                                                    color: isMatch ? 'white' : 'var(--text-muted)', 
                                                    borderRadius: '50%', fontWeight: 'bold', fontSize: '0.85rem',
                                                    border: isMatch ? 'none' : '1px solid var(--border)'
                                                  }}>
                                                    {w.toString().padStart(2, '0')}
                                                  </span>
                                                );
                                              })}
                                              {wt.special_ball !== null && (
                                                <span style={{ 
                                                  width: '28px', height: '28px', display: 'flex', alignItems: 'center', justifyContent: 'center', 
                                                  background: wt.matches.special ? '#10b981' : 'var(--panel-bg)', 
                                                  color: wt.matches.special ? 'white' : 'var(--text-muted)', 
                                                  borderRadius: '50%', fontWeight: 'bold', fontSize: '0.85rem', marginLeft: '0.5rem',
                                                  border: wt.matches.special ? 'none' : '1px solid var(--border)'
                                                }}>
                                                  {wt.special_ball.toString().padStart(2, '0')}
                                                </span>
                                              )}
                                            </div>
                                          </div>
                                        );
                                      })}
                                    </div>
                                  ) : (
                                    <div style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>No winning tickets for this draw.</div>
                                  )}
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      )}

                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem' }}>
                        {batch.tickets.map((t: any) => (
                          <div key={t.id} style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', padding: '0.75rem', background: 'var(--panel-bg)', borderRadius: '6px', border: '1px solid var(--border)' }}>
                            {t.white_balls.map((w: number, i: number) => (
                              <span key={i} style={{ width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--ball-bg)', color: 'var(--ball-text)', borderRadius: '50%', fontWeight: 'bold', fontSize: '0.9rem' }}>
                                {w.toString().padStart(2, '0')}
                              </span>
                            ))}
                            {t.special_ball !== null && (
                              <span style={{ width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--special-ball-bg)', color: 'white', borderRadius: '50%', fontWeight: 'bold', fontSize: '0.9rem', marginLeft: 'auto' }}>
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
      </main>
    </div>
  );
};

export default Dashboard;