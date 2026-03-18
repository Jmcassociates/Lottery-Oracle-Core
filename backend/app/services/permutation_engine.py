import random
from collections import Counter

class PermutationScouter:
    """
    JMc - [2026-03-18] - The Autonomous Mathematical Bouncer for Permutations.
    Filters out Pick 3/4/5 combinations that exist on the dead edges of the bell curve.
    """
    @staticmethod
    def is_valid_pattern(ticket: tuple, scouter_config: dict) -> bool:
        ticket_sum = sum(ticket)
        counts = list(Counter(ticket).values())
        counts.sort(reverse=True)
        max_repeats_found = counts[0]

        min_sum = scouter_config.get("min_sum", 0)
        max_sum = scouter_config.get("max_sum", 999)
        max_repeats = scouter_config.get("max_repeats", 999)

        if not (min_sum <= ticket_sum <= max_sum):
            return False

        if max_repeats_found >= max_repeats:
            return False

        return True

class PermutationMathEngine:
    """
    JMc - [2026-03-18] - The Cartesian Engine for games using Sampling With Replacement.
    Autonomously analyzes historical data to define its own filtering parameters.
    """
    def __init__(self, game_name, historical_draws_dicts, num_digits, previous_jackpots=None, scouter_config=None):
        self.game_name = game_name
        self.history = historical_draws_dicts
        self.num_digits = num_digits
        self.previous_jackpots = previous_jackpots or set()
        
        if self.history:
            self.scouter_config = self._analyze_bell_curve()
        else:
            self.scouter_config = scouter_config or {"min_sum": 0, "max_sum": 999, "max_repeats": 999}

    def _analyze_bell_curve(self):
        """
        JMc - [2026-03-18] - The Autonomous Scouter Profiler for Permutations.
        Dynamically analyzes the empirical dataset to establish sum bands and repeat limits.
        """
        sums = []
        repeat_counts = Counter()
        total = len(self.history)
        
        for draw in self.history:
            wb = draw['white_balls']
            sums.append(sum(wb))
            
            counts = list(Counter(wb).values())
            counts.sort(reverse=True)
            repeat_counts[counts[0]] += 1
            
        sums.sort()
        # JMc - [2026-03-18] - Capture the middle 80% of the bell curve for sums
        min_sum = sums[int(total * 0.10)] if sums else 0
        max_sum = sums[int(total * 0.90)] if sums else (9 * self.num_digits)
        
        # JMc - [2026-03-18] - If a repeat pattern happens in < 2% of draws, reject it.
        valid_repeats = [k for k, v in repeat_counts.items() if (v / total) >= 0.02]
        
        # The scouter rejects if max_repeats_found >= max_repeats.
        # So we want the boundary to be 1 higher than the maximum valid repeat we found.
        max_repeats_allowed = max(valid_repeats) + 1 if valid_repeats else self.num_digits
        
        return {
            "min_sum": min_sum,
            "max_sum": max_sum,
            "max_repeats": max_repeats_allowed
        }

    def is_historical_jackpot(self, ticket_tuple):
        """
        JMc - [2026-03-16] - For permutations, order matters. We check the exact string sequence
        against the historical database. If it hit before, we burn it.
        """
        # JMc - [2026-03-18] - Historical Saturation Bypass. 
        # Texas Pick 3 has ~44,000 records. There are only 1,000 possible tickets. 
        # If the history completely eclipses the possible mathematical combinations (> 90%),
        # we MUST bypass the collision avoidance rule to prevent an infinite hang.
        total_combinations = 10 ** self.num_digits
        if len(self.previous_jackpots) > (total_combinations * 0.9):
            return False

        white_str = ",".join(str(x) for x in ticket_tuple)
        signature = f"{white_str}:None"
        return signature in self.previous_jackpots

    def generate_tickets(self, num_tickets):
        """
        JMc - [2026-03-16] - Pick 3/4/5 are Sampling With Replacement (order matters). 
        We use constrained random sampling forced through the Permutation Scouter bell curve.
        """
        selected_tickets = []
        attempts = 0
        max_attempts = num_tickets * 5000
        
        while len(selected_tickets) < num_tickets and attempts < max_attempts:
            attempts += 1
            
            # JMc - [2026-03-16] - Generate a random permutation (e.g., 4, 7, 2).
            ticket = tuple(random.choices(range(10), k=self.num_digits))
            
            if ticket in selected_tickets:
                continue
                
            # JMc - [2026-03-16] - 1. The Bell Curve Check.
            if not PermutationScouter.is_valid_pattern(ticket, self.scouter_config):
                continue
                
            # JMc - [2026-03-16] - 2. Historical Collision Check.
            if self.is_historical_jackpot(ticket):
                continue
                
            selected_tickets.append(ticket)
            
        # JMc - [2026-03-16] - Fallback if the constraints are somehow too tight 
        # (shouldn't happen with these ranges, but prevents infinite loops).
        if len(selected_tickets) < num_tickets:
            fallback_attempts = 0
            while len(selected_tickets) < num_tickets and fallback_attempts < 10000:
                fallback_attempts += 1
                ticket = tuple(random.choices(range(10), k=self.num_digits))
                if ticket not in selected_tickets and not self.is_historical_jackpot(ticket):
                    selected_tickets.append(ticket)
                    
            # Ultimate fail-safe: just generate unique tickets ignoring history
            while len(selected_tickets) < num_tickets:
                ticket = tuple(random.choices(range(10), k=self.num_digits))
                if ticket not in selected_tickets:
                    selected_tickets.append(ticket)

        final_tickets = []
        for t in selected_tickets:
            final_tickets.append({
                "white_balls": list(t),
                "special_ball": None
            })
            
        return final_tickets, list(range(10)) # JMc - [2026-03-16] - pool is always digits 0-9

