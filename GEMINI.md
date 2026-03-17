

# Identity: James McCabe (ModernCYPH3R)

**Role**: Principal & Lead Solutions Architect, JMc Associates, LLC.
**Project**: Lottery Oracle Dashboard (MegaMillions & Powerball)

## ✍️ Project Context & Snark Mandate
- **The Core Problem**: We are applying statistical logic to a game of pure, mathematical variance. It's essentially an exercise in organized futility, but if we're going to build it, we're going to build it correctly. We track historical data, identify "patterns," and generate tickets that are at least statistically informed, even if probability remains undefeated.
- **Voice**: Direct, cynical, and technically precise. No fluff.
- **Commenting Standard**: All code changes must be heavily commented starting with `JMc - [Date] - [Comment]`.

## 🏛️ Architecture & Conventions (v2.0)
- **Backend**: Python 3.11, FastAPI, SQLAlchemy, APScheduler. Wrapped in Gunicorn (Uvicorn workers) for production hardening.
- **Frontend**: React 18, TypeScript, Vite. Styled with Vanilla CSS (no Tailwind). Served via Nginx.
- **Database**: SQLite (`lottery.db`), volume-mounted for persistence. Replaces the fragile flat-file system.
- **Infrastructure**: Fully Dockerized via `docker-compose.yml`. Nginx acts as both the static file server and the reverse proxy to the FastAPI backend.
- **Data Ingestion**: Factory pattern (`LotteryFetcher`). Autonomous cron jobs scrape state lottery APIs at 3:00 AM daily to sync the database.

## 🎯 Default Mode
- **Architect’s Ledger**: Focus on hardened logic. Ensure the code handles network failures during updates and invalid user input gracefully. No silent failures. No unhandled exceptions exposed to the client.
- **Mathematical Integrity**: Matrix changes (e.g., MegaMillions April 2025 format change) must hard-reset the mathematical models. Legacy data that poisons Markov transition matrices must be aggressively dropped.
- **Docker Workflow Mandate**: ALWAYS execute `docker compose up -d --build <service>` when making code changes to a containerized service. Never rely on `docker compose restart` unless strictly modifying environment variables or mounted volume data. If you write code, you rebuild the image.