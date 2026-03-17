import random
from collections import Counter

class PermutationScouter:
    """
    JMc - [2026-03-16] - The Mathematical Bouncer for Permutations.
    Filters out Pick 3/4/5 combinations that exist on the dead edges of the bell curve.
    """
    @staticmethod
    def is_valid_pattern(ticket: tuple, game_name: str) -> bool:
        ticket_sum = sum(ticket)
        counts = list(Counter(ticket).values())
        counts.sort(reverse=True)
        max_repeats = counts[0]

        if game_name == "Pick3":
            # JMc - [2026-03-16] - Sum must be between 11 and 16 (captures the peak of the bell curve).
            if not (11 <= ticket_sum <= 16):
                return False
            # JMc - [2026-03-16] - Triples (3 of a kind) only happen 1% of the time. Reject them.
            if max_repeats == 3:
                return False

        elif game_name == "Pick4":
            # JMc - [2026-03-16] - Sum must be between 16 and 20.
            if not (16 <= ticket_sum <= 20):
                return False
            # JMc - [2026-03-16] - Quads are 0.1%, triples are 3.9%. Reject Quads and Triples.
            if max_repeats >= 3:
                return False

        elif game_name == "Pick5":
            # JMc - [2026-03-16] - Sum must be between 20 and 26.
            if not (20 <= ticket_sum <= 26):
                return False
            # JMc - [2026-03-16] - 4 of a kind and 5 of a kind are < 0.5%. Reject them.
            if max_repeats >= 4:
                return False

        return True

class PermutationMathEngine:
    """
    JMc - [2026-03-16] - The Cartesian Engine for games using Sampling With Replacement.
    Uses random sampling constrained by the PermutationScouter bell curve logic.
    """
    def __init__(self, game_name, historical_draws_dicts, num_digits, previous_jackpots=None):
        self.game_name = game_name
        self.history = historical_draws_dicts
        self.num_digits = num_digits
        self.previous_jackpots = previous_jackpots or set()

    def is_historical_jackpot(self, ticket_tuple):
        """
        JMc - [2026-03-16] - For permutations, order matters. We check the exact string sequence
        against the historical database. If it hit before, we burn it.
        """
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
            if not PermutationScouter.is_valid_pattern(ticket, self.game_name):
                continue
                
            # JMc - [2026-03-16] - 2. Historical Collision Check.
            if self.is_historical_jackpot(ticket):
                continue
                
            selected_tickets.append(ticket)
            
        # JMc - [2026-03-16] - Fallback if the constraints are somehow too tight 
        # (shouldn't happen with these ranges, but prevents infinite loops).
        if len(selected_tickets) < num_tickets:
            while len(selected_tickets) < num_tickets:
                ticket = tuple(random.choices(range(10), k=self.num_digits))
                if ticket not in selected_tickets and not self.is_historical_jackpot(ticket):
                    selected_tickets.append(ticket)

        final_tickets = []
        for t in selected_tickets:
            final_tickets.append({
                "white_balls": list(t),
                "special_ball": None
            })
            
        return final_tickets, list(range(10)) # JMc - [2026-03-16] - pool is always digits 0-9
