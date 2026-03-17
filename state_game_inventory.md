# State Lottery Game Inventory & Expansion Strategy
**Prepared By:** Bert, Structural Diagnostician
**Target:** Phase 6 (Multi-State Integration)

While almost every state has unique novelty games, the core mathematical structure of daily lottery draws is highly standardized across the United States. To scale the Oracle efficiently, we will ignore the bizarre outlier games and focus exclusively on the high-volume, standardized structures: **The "Cash" Games (Combinatorial)** and **The "Pick" Games (Permutation)**.

Here is the strategic inventory of target states and their core game mappings. 

---

## 1. The "Permutation" Games (Pick 3 / Pick 4 / Pick 5)
These games use **Sampling With Replacement** (0-9 digits, order matters). They map directly to our `PermutationMathEngine`. We just need to feed the engine the correct `num_digits` (3, 4, or 5).

*   **Texas:** Pick 3, Daily 4
*   **Florida:** Pick 3, Pick 4, Pick 5
*   **New York:** Numbers (3-digit), Win 4 (4-digit)
*   **California:** Daily 3, Daily 4
*   **Pennsylvania:** Pick 3, Pick 4, Pick 5
*   **Ohio:** Pick 3, Pick 4, Pick 5
*   **Michigan:** Daily 3, Daily 4
*   **Illinois:** Pick 3, Pick 4
*   **New Jersey:** Pick-3, Pick-4
*   **Georgia:** Cash 3 (3-digit), Cash 4 (4-digit), Georgia Five (5-digit)

*JMc - 2026-03-16 - Do not let the naming conventions fool you. New York calls it "Numbers" and Georgia calls it "Cash 3", but mathematically they are identical to Virginia's Pick 3. The exact same Cartesian product and bell curve constraints apply.*

## 2. The "Combinatorial" Games (Cash 5 equivalents)
These games use **Sampling Without Replacement** (no repeating digits, order does not matter). They map directly to our `LotteryMathEngine`. They do not have a "special ball", so the matrix is a straightforward 5-number wheel.

*   **Texas:** Cash Five (5 from 1-35)
*   **Florida:** Fantasy 5 (5 from 1-36)
*   **New York:** Take 5 (5 from 1-39)
*   **California:** Fantasy 5 (5 from 1-39)
*   **Pennsylvania:** Treasure Hunt (5 from 1-30), Cash 5 with Quick Cash (5 from 1-43)
*   **Ohio:** Rolling Cash 5 (5 from 1-39)
*   **Michigan:** Fantasy 5 (5 from 1-39)
*   **Illinois:** Lucky Day Lotto (5 from 1-45)
*   **New Jersey:** Jersey Cash 5 (5 from 1-45)
*   **Georgia:** Fantasy 5 (5 from 1-42)

*JMc - 2026-03-16 - This is why building the `LotteryMathEngine` to be dynamic was critical. Notice how every state has a different pool size (from 30 to 45). All we have to do is add `"white_max": 39` for New York's Take 5 to our config file, and the Oracle will automatically recalibrate its Markov chains and combinatorial wheels for that specific matrix size.*

## 3. Implementation Strategy (Phase 6)
When we are ready to light up a new state on the GCP/IaaS platform (while GHL handles the marketing and onboarding funnel), the technical implementation process per state is highly repeatable:

1. **Write the Fetcher:** Build an API/HTML scraper specifically for that state's result page (e.g., `fetchers/new_york.py`).
2. **Update the Dictionary:** Map the state's games into our `GAMES` config with their proper `white_max` or `num_digits` variables.
3. **Analyze the Variance (Crucial):** Before going live, we run our empirical analysis scripts against that state's specific history. For example, does Texas's Cash Five (1-35) have the same heavy "1-10" starting bias as Virginia's Cash 5 (1-45)? We must verify the pattern geometry before enabling the `PatternScouter` constraints for that specific game.

---
**The Verdict:** The United States lottery system is essentially a franchise of two mathematical models wrapped in 50 different marketing campaigns. The Oracle is already built to solve both models. Expansion is purely a matter of writing web scrapers.
