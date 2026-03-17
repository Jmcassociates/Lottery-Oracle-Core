import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, 
  AreaChart, Area 
} from 'recharts';
import './Landing.css';

interface JackpotData {
  [game: string]: {
    jackpot: string;
    next_draw: string;
  }
}

const startData = [
  { name: '1 to 2', Powerball: 13.4, MegaMillions: 11.2 },
  { name: '3 to 10', Powerball: 40.9, MegaMillions: 39.8 },
  { name: '11 to 20', Powerball: 27.9, MegaMillions: 41.8 },
  { name: '21 to 34', Powerball: 14.6, MegaMillions: 6.1 },
  { name: '35+', Powerball: 3.2, MegaMillions: 1.0 },
];

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

const LandingPage = () => {
  const [jackpots, setJackpots] = useState<JackpotData | null>(null);

  useEffect(() => {
    fetch('/api/jackpots')
      .then(res => res.json())
      .then(data => setJackpots(data))
      .catch(err => console.error("Failed to load jackpots", err));
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
          We don't predict the future; we architect against it. The Lottery Oracle deploys a dual-engine mathematical framework—Combinatorial Wheeling for high-volatility matrix games and Cartesian Permutation Analysis for daily Pick games—to maximize your coverage while aggressively purging combinations that live on the dead edges of probability.
        </p>
      </header>

      <section className="jackpot-section">
        <h2>Current Opportunities</h2>
        <div className="jackpot-grid" style={{ flexWrap: 'wrap' }}>
          {['Powerball', 'MegaMillions', 'Cash4Life', 'Cash5', 'Pick3', 'Pick4', 'Pick5'].map(game => (
            <div key={game} className="jackpot-card" style={{ minWidth: '250px', marginBottom: '1rem' }}>
              <h3>{
                game === 'MegaMillions' ? 'Mega Millions' : 
                game === 'Cash4Life' ? 'Cash 4 Life' :
                game === 'Cash5' ? 'Cash 5' :
                game.replace('Pick', 'Pick ')
              }</h3>
              {jackpots ? (
                <>
                  <div className="amount" style={{ fontSize: game.startsWith('Pick') ? '1.5rem' : '2rem' }}>
                    {jackpots[game]?.jackpot || (game.startsWith('Pick') ? '$500 - $50,000' : 'Pending...')}
                  </div>
                  <div className="draw-date">
                    {jackpots[game]?.next_draw || (game.startsWith('Pick') ? 'Draws Twice Daily' : 'Pending...')}
                  </div>
                </>
              ) : (
                <div className="loading-skeleton">Loading API data...</div>
              )}
            </div>
          ))}
        </div>
      </section>

      <section className="chart-section">
        <h2>The Mathematical Reality</h2>
        <p className="chart-subtitle">
          A "Quick Pick" treats every number as having an equal probability. The empirical data proves otherwise. Our engine actively routes around the dead edges of probability that the state hopes you bet on.
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

      <section className="marketing-section">
        <div className="feature">
          <h3>The Prophet</h3>
          <p>A dual-modal analytical core. It utilizes Markov Chains for sequence transition modeling and Poisson frequency analysis to identify high-tension clusters across both combinatorial matrices and permutation datasets.</p>
        </div>
        <div className="feature">
          <h3>The Pragmatist</h3>
          <p>The deployment engine. It applies Greedy Combinatorial Wheeling for large matrix games and Cartesian product filtering for Pick games, ensuring maximum statistical coverage with zero mathematical redundancy.</p>
        </div>
        <div className="feature">
          <h3>The Pattern Scouter</h3>
          <p>Enforces game-specific spatial filters and Odd/Even ratios. Routes around low-probability distributions and ensures you never play a historical jackpot collision.</p>
        </div>
        <div className="feature">
          <h3>The Vault</h3>
          <p>Save your tickets securely. Generate professional PDF manifests to manage syndicates or easily punch numbers into your state lottery app.</p>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;