// JMc - [2026-03-16] - The Public Storefront. Showcases the empirical reality of the lottery to acquire users for the Oracle.
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, 
  AreaChart, Area 
} from 'recharts';
import mermaid from 'mermaid';
import './Landing.css';

// JMc - [2026-04-01] - Initialize Mermaid for architectural visualization.
mermaid.initialize({
  startOnLoad: true,
  theme: 'dark',
  securityLevel: 'loose',
  fontFamily: 'Segoe UI, system-ui, sans-serif'
});

interface JackpotData {
  [game: string]: {
    jackpot: string;
    next_draw: string;
    state?: string;
  }
}

// JMc - [2026-03-16] - Empirical data mapping the starting number probabilities.
const startData = [
  { name: '1 to 2', Powerball: 13.4, MegaMillions: 11.2 },
  { name: '3 to 10', Powerball: 40.9, MegaMillions: 39.8 },
  { name: '11 to 20', Powerball: 27.9, MegaMillions: 41.8 },
  { name: '21 to 34', Powerball: 14.6, MegaMillions: 6.1 },
  { name: '35+', Powerball: 3.2, MegaMillions: 1.0 },
];

// JMc - [2026-03-16] - Empirical data mapping the Pick 3 sum distribution bell curve.
const pick3Data = [
  { sum: '3-10', freq: 12.0 },
  { sum: '11', freq: 6.9 },
  { sum: '12', freq: 7.2 },
  { sum: '13', freq: 7.7 },
  { sum: '14', freq: 7.5 },
  { sum: '15', freq: 7.2 },
  { sum: '16', freq: 6.8 },
  { sum: '17-27', freq: 15.0 },
];

const API_BASE = import.meta.env.VITE_API_URL || '';

const LandingPage = () => {
  const [jackpots, setJackpots] = useState<JackpotData | null>(null);
  const [allGames, setAllGames] = useState<{id: string, name: string, state: string}[]>([]);
  const [recentDraws, setRecentDraws] = useState<Record<string, any>>({});

  useEffect(() => {
    // JMc - [2026-04-01] - Trigger Mermaid re-render.
    mermaid.contentLoaded();

    const ts = new Date().getTime();
    
    // Fetch Global Game Roster for Ticker
    fetch(`${API_BASE}/api/games?_t=${ts}`)
      .then(res => res.json())
      .then(data => {
        if (data.games_full) {
          setAllGames(data.games_full);
          // Fetch historical artifacts for the ticker balls
          data.games_full.forEach((g: any) => {
             fetch(`${API_BASE}/api/history/${g.id}?limit=1&_t=${ts}`)
              .then(res => res.json())
              .then(history => {
                if (history && history.length > 0) {
                  setRecentDraws(prev => ({...prev, [g.id]: history[0]}));
                }
              })
              .catch(err => console.error(`Failed history for ${g.id}`));
          });
        }
      })
      .catch(err => console.error("Failed games load"));

    // Fetch live unauthenticated jackpots
    fetch(`${API_BASE}/api/jackpots?_t=${ts}`)
      .then(res => res.json())
      .then(data => setJackpots(data))
      .catch(err => console.error("Failed jackpots load"));
  }, []);

  return (
    <div className="landing-container">
      <nav className="top-nav">
        <div className="logo">Lottery Oracle</div>
        <div className="nav-links">
          <Link to="/login" className="btn-secondary">Log In</Link>
          <Link to="/register" className="btn-primary">Start Playing Smarter</Link>
        </div>
      </nav>

      <header className="hero">
        <h1>Stop guessing. Start calculating.</h1>
        <p className="hero-subtitle">
          We don't predict the future; we architect against it. The Lottery Oracle deploys a dual-engine mathematical framework to maximize your coverage while aggressively purging combinations that live on the dead edges of probability.
        </p>
      </header>

      <section className="jackpot-section" style={{ padding: '2rem 0 4rem 0' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem', flexWrap: 'wrap', gap: '1rem' }}>
          <h2 style={{ margin: 0, fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '2px', color: 'var(--text-muted)' }}>Global Pulse Ticker</h2>
          <div style={{ fontSize: '0.75rem', color: '#38bdf8', fontWeight: 'bold' }}>
            SYSTEM ONLINE • MATRICES EXPANDING WEEKLY
          </div>
        </div>
        
        <div className="ticker-container">
          {(allGames.length > 0 ? allGames : [
            {id: 'Powerball', name: 'Powerball', state: 'National'},
            {id: 'MegaMillions', name: 'Mega Millions', state: 'National'},
            {id: 'VirginiaCash5', name: 'Cash 5', state: 'Virginia'}
          ]).map(game => (
            <div key={game.id} className="ticker-card" style={{ minWidth: '260px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                <span style={{ fontSize: '0.65rem', color: 'var(--accent)', fontWeight: 'bold', textTransform: 'uppercase' }}>{game.state}</span>
                <span style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>{recentDraws[game.id] ? recentDraws[game.id].date : ''}</span>
              </div>
              <div style={{ fontSize: '1rem', fontWeight: 'bold', marginBottom: '0.25rem', color: 'white' }}>{game.name}</div>
              <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--text-main)', marginBottom: '0.75rem' }}>
                {jackpots?.[game.id]?.jackpot || 'Syncing...'}
              </div>
              {recentDraws[game.id] && (
                <div style={{ display: 'flex', gap: '0.3rem' }}>
                   {recentDraws[game.id].white_balls.slice(0, 5).map((w: number, i: number) => (
                     <span key={i} style={{ width: '22px', height: '22px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--ball-bg)', color: 'var(--ball-text)', borderRadius: '50%', fontWeight: 'bold', fontSize: '0.7rem' }}>
                       {w.toString().padStart(2, '0')}
                     </span>
                   ))}
                   {recentDraws[game.id].special_ball !== null && (
                     <span style={{ width: '22px', height: '22px', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--special-ball-bg)', color: 'white', borderRadius: '50%', fontWeight: 'bold', fontSize: '0.7rem' }}>
                       {recentDraws[game.id].special_ball.toString().padStart(2, '0')}
                     </span>
                   )}
                </div>
              )}
            </div>
          ))}
        </div>
        <p style={{ marginTop: '1rem', fontSize: '0.85rem', color: 'var(--text-muted)', textAlign: 'center', fontStyle: 'italic' }}>
          * Currently analyzing high-volume pools in VA, TX, and NY. California and Florida matrices are currently being calibrated.
        </p>
      </section>

      <section className="chart-section">
        <h2>The Mathematical Reality: Organizing the Variance</h2>
        <p className="chart-subtitle" style={{ maxWidth: '800px', margin: '0 auto 3rem' }}>
          The Oracle doesn't predict the future; it <strong>organizes the variance</strong>. Every draw is an independent event, and the ping-pong balls do not have memory. We don't ask for "lucky numbers"; we apply raw empirical data to a game of pure, brutal mathematical variance.
        </p>
        
        <div className="chart-grid">
          <div className="chart-card">
            <h3>Starting Number Spatial Anomaly</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '1.5rem', textAlign: 'center' }}>
              Mega Millions heavily favors starting in the mid-teens, while Powerball allows a wider spread. A Quick Pick ignores this entirely.
            </p>
            <div style={{ width: '100%', height: 300 }}>
              <ResponsiveContainer>
                <BarChart data={startData} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                  <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={12} />
                  <YAxis stroke="var(--text-muted)" fontSize={12} tickFormatter={(val) => `${val}%`} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'var(--bg-color)', borderColor: 'var(--border)' }}
                    itemStyle={{ color: 'var(--text-main)' }}
                    formatter={(value) => [`${value}%`, '']}
                  />
                  <Legend wrapperStyle={{ paddingTop: '10px' }} />
                  <Bar dataKey="Powerball" fill="#ef4444" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="MegaMillions" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="chart-card">
            <h3>Pick 3 Sum Distribution Bell Curve</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '1.5rem', textAlign: 'center' }}>
              Over 12,000 draws mapped. The mathematical center of mass is a sum between 11 and 16. Our Permutation Engine rejects any ticket outside this pocket.
            </p>
            <div style={{ width: '100%', height: 300 }}>
              <ResponsiveContainer>
                <AreaChart data={pick3Data} margin={{ top: 5, right: 5, left: -20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                  <XAxis dataKey="sum" stroke="var(--text-muted)" fontSize={12} />
                  <YAxis stroke="var(--text-muted)" fontSize={12} tickFormatter={(val) => `${val}%`} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'var(--bg-color)', borderColor: 'var(--border)' }}
                    itemStyle={{ color: 'var(--text-main)' }}
                    formatter={(value) => [`${value}%`, 'Frequency']}
                  />
                  <Area type="monotone" dataKey="freq" stroke="#10b981" fill="#10b981" fillOpacity={0.3} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </section>

      {/* JMc - [2026-04-01] - Autonomous Architecture Section */}
      <section style={{ padding: '4rem 2rem', background: '#020617', borderTop: '1px solid var(--border)', borderBottom: '1px solid var(--border)' }}>
        <h2 style={{ textAlign: 'center', marginBottom: '1rem' }}>Autonomous Architecture Flow</h2>
        <p style={{ textAlign: 'center', color: 'var(--text-muted)', marginBottom: '4rem', maxWidth: '700px', margin: '0 auto 4rem' }}>
          Our engine is 100% autonomously seeded by raw empirical data. We bring a supercomputer to a knife fight.
        </p>
        
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
      </section>

      <section className="marketing-section">
        <div className="feature">
          <h3 style={{ color: 'var(--accent)' }}>01. The Prophet</h3>
          <p><strong>Autonomous Seeding:</strong> Scans a decade of historical data using <strong>Markov Chains</strong>, <strong>Poisson Distribution</strong>, and <strong>Base Frequency</strong> to build a high-tension 15-number Smart Pool.</p>
        </div>
        <div className="feature">
          <h3 style={{ color: '#8b5cf6' }}>02. The Pragmatist</h3>
          <p><strong>Combinatorial Wheeling:</strong> Takes the Smart Pool and establishes maximum coverage across 3,003 possible variations, prioritizing 3-number triplets to ensure structural integrity.</p>
        </div>
        <div className="feature">
          <h3 style={{ color: '#10b981' }}>03. The Pattern Scouter</h3>
          <p><strong>The Purge:</strong> Enforces strict geometric filters. We reject odd/even outliers, spatial spread traps, consecutive sequences, and historical jackpot collisions.</p>
        </div>
        <div className="feature">
          <h3 style={{ color: '#f59e0b' }}>04. The Vault</h3>
          <p><strong>Artifact Persistence:</strong> Save your tickets securely. Generate professional PDF manifests to manage syndicates or easily punch numbers into your state lottery app.</p>
        </div>
      </section>

      {/* JMc - [2026-04-01] - Final Call to Action */}
      <section style={{ padding: '6rem 2rem', textAlign: 'center', background: 'linear-gradient(180deg, #0f111a 0%, #1e3a8a 100%)' }}>
        <h2 style={{ fontSize: '2.5rem', marginBottom: '1.5rem' }}>Stop analyzing the map. Start driving the vehicle.</h2>
        <p style={{ fontSize: '1.2rem', color: 'var(--text-muted)', maxWidth: '700px', margin: '0 auto 3rem' }}>
          Access high-volume combinatorial coverage for Powerball, Mega Millions, and daily state games across the country.
        </p>
        <Link to="/register" className="btn-primary" style={{ fontSize: '1.2rem', padding: '1rem 3rem', boxShadow: '0 0 30px rgba(59, 130, 246, 0.4)' }}>
          ACTIVATE THE ORACLE
        </Link>
      </section>
    </div>
  );
};

export default LandingPage;
