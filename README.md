# Lottery Oracle: Organized Futility 
**Author:** James McCabe (ModernCYPH3R)

Let's get one thing straight before you look at this source code: the lottery is a voluntary tax on people who are bad at math. It is a game of pure, brutal statistical variance. The ping-pong balls do not have memory. 

If you are looking for a repository containing a "Quantum AI Prediction Algorithm," go pay $570 to a scammer on the internet. 

This repository does not predict the future. It **architects against it.** 

The Lottery Oracle is a dual-engine mathematical deployment platform designed to take the state's `Math.random()` quick-pick garbage and replace it with empirical, highly structured probability matrices. We don't play the dead edges of the bell curve; we bring a supercomputer to a knife fight.

---

## 🏛️ The Architecture (v2.0)
This isn't a collection of hacked-together Python scripts. It is a hardened, containerized SaaS application designed to scale across state lines while maintaining strict mathematical segregation between game types.

*   **Compute Layer:** Python 3.11, FastAPI, SQLAlchemy, APScheduler, Gunicorn.
*   **Presentation Layer:** React 18, TypeScript, Vite, Recharts, Vanilla CSS.
*   **Infrastructure:** Rootless Docker & Nginx Reverse Proxy.
*   **Persistence:** Volume-mounted SQLite. 

## ⚙️ The Dual-Engine Core
Not all lotteries are mathematically equal. The Oracle treats every game as a unique statistical environment.

### 1. The Combinatorial Engine (`LotteryMathEngine`)
Built for large matrix games (Powerball, Mega Millions, Cash4Life, Cash5) that use **Sampling Without Replacement**.
*   **The Prophet:** Autonomously analyzes a decade of draw history using Markov Chains and Poisson Overdue algorithms to build a highly biased target pool of 15 numbers.
*   **The Pragmatist:** Applies Greedy Combinatorial Wheeling to select exact tickets from the pool, guaranteeing maximum triplet coverage with zero redundant mathematical overlap.
*   **The Pattern Scouter:** Enforces game-specific spatial filters. (e.g., Mega Millions mathematically hates starting above 20. The engine aggressively routes around this 93% statistical trap.)

### 2. The Permutation Engine (`PermutationMathEngine`)
Built for daily Pick games (Pick 3, Pick 4, Pick 5) that use **Sampling With Replacement** (order matters, digits repeat).
*   **Cartesian Matrices:** Generates exact permutations and forces them through a strict set of historical constraints.
*   **Sum-Banding:** Rejects tickets that fall outside the historical center of mass (e.g., rejecting any Pick 3 ticket that doesn't sum between 11 and 16).
*   **Repeating Ratios:** Dynamically adjusts the probability of Pairs and Quads based on the specific game's empirical history.

### 🔒 The Golden Rule: "Never Picked Before"
Both engines actively hash every generated combination against the entire historical database of the game. If a ticket has *ever* won a jackpot in the history of the universe, it is instantly burned. 

---

## 🛠️ Deployment Protocol
Because apparently, we didn't have enough layers of abstraction to hide the shame of this logic, the entire platform is Dockerized. 

**DOCKER WORKFLOW MANDATE:** ALWAYS execute `docker compose up -d --build` when making code changes. Never rely on `docker compose restart` unless strictly modifying environment variables. If you write code, you rebuild the image.

```bash
# Clone the matrix
git clone <private-repo-url>

# Spin up the containers (Backend + Frontend/Nginx)
docker compose up -d --build

# The cron fetchers will run daily at 07:00 UTC (03:00 EDT)
# View the dashboard at http://localhost
```

---

## 📜 The Syndicate Manifest
If you are running an office pool, do not show up with a smartphone screenshot of your numbers. The backend integrates `reportlab` to generate professional, high-contrast PDF "Oracle Deployment Manifests." It handles the local timezone conversions (UTC to EDT) so you have an exact, printable receipt of the math you just bought.

*JMc - 2026-03-16 - The math changes every time a ball drops; your deployment should too. Stop guessing.*
