# Phase 6: Multi-State Architecture Blueprint
**Author:** James McCabe (ModernCYPH3R)

The Oracle platform currently processes the Virginia Lottery. To expand into a national SaaS product, the core mathematical engine and dashboard will be deployed via Docker/Nginx on Google Cloud Platform (GCP) or another IaaS provider, scaling to handle 40+ independent state lottery commissions. Meanwhile, GoHighLevel (GHL) will serve as the external frontend for marketing funnels, payment processing, CRM, and email sequences. 

This document outlines the structural refactoring required for Multi-State Support.

---

## 1. Database Schema Refactor
The current `DrawRecord` and `SavedTicketBatch` schemas assume all games are globally unique. We must introduce `state` context.

*   **Action:** Add a `state_code` (e.g., 'VA', 'TX', 'NY', 'NAT' for national) column to `DrawRecord` and `SavedTicketBatch`.
*   **Unique Constraints:** The compound uniqueness constraint must change from `(game_name, draw_date)` to `(state_code, game_name, draw_date)`.
*   **National Games (Powerball / Mega Millions):** These should be stored with a `state_code` of 'NAT'. When a user selects *any* state in the UI, the backend will merge the 'NAT' games with that specific state's local games.

## 2. The Fetcher Factory Expansion
State lotteries do not share a unified API. Virginia uses a relatively clean JSON/CSV endpoint. Other states use raw HTML tables, obscure XML feeds, or third-party syndicators.

*   **Action:** Restructure `app/services/fetchers.py` into a directory modularized by state:
    *   `app/services/fetchers/virginia.py`
    *   `app/services/fetchers/texas.py`
    *   `app/services/fetchers/national.py` (For Powerball/MegaMillions direct feeds if available, otherwise defaulting to a reliable primary state like VA).
*   **The Cron Router:** The 03:00 EDT sync must be rewritten to iterate through a registry of active states, firing the specific fetcher classes for each region.

## 3. API & Configuration Dictionary
The hardcoded `GAMES` dictionary in `main.py` must become dynamic.

*   **Action:** Shift from a flat dictionary to a nested JSON configuration (or database table) mapping States -> Games.
    ```json
    {
      "VA": {
        "Cash5": { "white_max": 45, "special_max": 0, "type": "combinatorial" },
        "Pick3": { "white_max": 9, "special_max": 0, "type": "permutation" }
      },
      "TX": {
        "TwoStep": { "white_max": 35, "special_max": 0, "type": "combinatorial" }
      },
      "NAT": {
        "Powerball": { "white_max": 69, "special_max": 26, "type": "combinatorial" }
      }
    }
    ```

## 4. Frontend UI/UX
The dashboard and landing page must adapt to a user's location.

*   **Action:** Add a global `State Selector` dropdown in the navigation bar.
*   **State Persistence:** Save the user's selected state in `localStorage` (and eventually the `User` database model).
*   **Dynamic Rendering:** When a state is selected, the frontend calls `GET /api/games?state=VA`. The backend returns the combined list of `NAT` games + `VA` games, instantly rebuilding the Jackpot Grid and Target Game selector.

## 5. The Math Engine (Zero Changes Required)
Because we built the `LotteryMathEngine` (Combinatorial) and `PermutationMathEngine` (Cartesian) to be entirely game-agnostic, **zero changes are required to the core mathematical logic.** As long as the Fetcher provides the correct matrix dimensions (`white_max`, `num_digits`), the Oracle will mathematically dismantle a Texas game just as easily as a Virginia game.

---
*JMc - [Date Pending] - The math scales infinitely. The only bottleneck is data normalization. The priority is building a robust abstraction layer for the Fetchers so that when Texas decides to change their HTML layout, it doesn't break the Virginia cron jobs.*
