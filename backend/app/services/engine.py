import itertools
from collections import defaultdict, Counter

class PatternScouter:
    """
    JMc - 2026-03-15 - The Mathematical Bouncer.
    Filters out combinations that exist on the extreme, dead edges of the statistical bell curve.
    """
    @staticmethod
    def is_valid_pattern(ticket: tuple, game_name: str, max_white: int) -> bool:
        # 1. Odd/Even Constraint (Must be 3:2 or 2:3)
        odd_count = sum(1 for n in ticket if n % 2 != 0)
        if odd_count not in [2, 3]:
            return False

        # 2. Zone Spread Constraint
        sorted_ticket = sorted(ticket)
        first_ball = sorted_ticket[0]

        # MegaMillions specifically hates starting high (only 7% start > 20)
        # We aggressively route around any ticket starting > 20 for MegaMillions.
        if game_name == "MegaMillions" and first_ball > 20:
            return False
            
        # Powerball only has 3% of draws starting > 34.
        if game_name == "Powerball" and first_ball > 34:
            return False

        # Cash4Life behaves similarly to Powerball, rejecting > 34.
        if game_name == "Cash4Life" and first_ball > 34:
            return False

        # Cash5 has a massive 1-10 clustering, rejecting > 20.
        if game_name == "Cash5" and first_ball > 20:
            return False

        return True

class LotteryMathEngine:
    def __init__(self, game_name, historical_draws_dicts, white_max, special_max, previous_jackpots=None):
        """
        historical_draws_dicts: list of dicts [{'date': dt, 'white_balls': [1,2,3], 'special_ball': 4}]
        previous_jackpots: set of strings e.g. {"14,21,33,42,59:24", ...}
        """
        self.game_name = game_name
        self.history = historical_draws_dicts
        self.white_max = white_max
        self.special_max = special_max
        self.previous_jackpots = previous_jackpots or set()

    def get_markov_transitions(self):
        transitions = defaultdict(Counter)
        for i in range(len(self.history) - 1):
            current_draw = self.history[i]['white_balls']
            next_draw = self.history[i+1]['white_balls']
            for ball_c in current_draw:
                for ball_n in next_draw:
                    transitions[ball_c][ball_n] += 1
        return transitions

    def get_overdue_scores(self):
        last_seen = {i: len(self.history) for i in range(1, self.white_max + 1)}
        for draws_ago, draw in enumerate(reversed(self.history)):
            for ball in draw['white_balls']:
                if last_seen[ball] == len(self.history):
                    last_seen[ball] = draws_ago
        return last_seen
        
    def generate_smart_pool(self, pool_size=15, special_pool_size=3):
        if not self.history:
            return list(range(1, pool_size+1)), list(range(1, special_pool_size+1))
            
        last_draw = self.history[-1]['white_balls']
        
        # 1. Markov Scoring
        transitions = self.get_markov_transitions()
        markov_scores = defaultdict(float)
        for ball in last_draw:
            total_transitions = sum(transitions[ball].values())
            if total_transitions > 0:
                for next_ball, count in transitions[ball].items():
                    markov_scores[next_ball] += count / total_transitions
                    
        # 2. Overdue Scoring
        overdue = self.get_overdue_scores()
        
        # 3. Frequency Scoring
        all_white = []
        all_special = []
        for draw in self.history:
            all_white.extend(draw['white_balls'])
            all_special.append(draw['special_ball'])
            
        freq = Counter(all_white)
        special_freq = Counter(all_special)
        
        # Normalize and combine
        max_markov = max(markov_scores.values()) if markov_scores else 1
        max_overdue = max(overdue.values()) if overdue else 1
        max_freq = max(freq.values()) if freq else 1
        
        final_scores = {}
        for i in range(1, self.white_max + 1):
            m_score = (markov_scores[i] / max_markov) if max_markov else 0
            o_score = (overdue[i] / max_overdue) if max_overdue else 0
            f_score = (freq[i] / max_freq) if max_freq else 0
            
            # The Prophet's weightings
            final_scores[i] = (0.4 * m_score) + (0.4 * o_score) + (0.2 * f_score)
            
        smart_pool = sorted(final_scores.keys(), key=lambda x: final_scores[x], reverse=True)[:pool_size]
        
        # Special balls
        last_seen_special = {i: len(self.history) for i in range(1, self.special_max + 1)}
        for draws_ago, draw in enumerate(reversed(self.history)):
            sb = draw['special_ball']
            if last_seen_special[sb] == len(self.history):
                last_seen_special[sb] = draws_ago
                
        max_s_overdue = max(last_seen_special.values()) if last_seen_special else 1
        max_s_freq = max(special_freq.values()) if special_freq else 1
        
        s_scores = {}
        for i in range(1, self.special_max + 1):
            o_score = (last_seen_special[i] / max_s_overdue) if max_s_overdue else 0
            f_score = (special_freq[i] / max_s_freq) if max_s_freq else 0
            s_scores[i] = (0.5 * o_score) + (0.5 * f_score)
            
        smart_special_pool = sorted(s_scores.keys(), key=lambda x: s_scores[x], reverse=True)[:special_pool_size]
        
        return sorted(smart_pool), sorted(smart_special_pool)

    def is_historical_jackpot(self, white_tuple, special_ball):
        """
        JMc - Check if this exact combination has ever won a jackpot.
        """
        white_str = ",".join(str(x) for x in sorted(white_tuple))
        signature = f"{white_str}:{special_ball}"
        return signature in self.previous_jackpots

    def generate_wheeled_tickets(self, pool, special_pool, num_tickets, numbers_per_ticket=5):
        """
        JMc - The Pragmatist. Now with PatternScouter and 'Never Picked Before' constraints.
        """
        all_possible_tickets = list(itertools.combinations(pool, numbers_per_ticket))
        
        covered_triplets = set()
        selected_tickets = []
        
        attempts = 0
        while len(selected_tickets) < num_tickets and attempts < len(all_possible_tickets) * 2:
            attempts += 1
            best_ticket = None
            best_new_coverage = -1
            
            for ticket in all_possible_tickets:
                if ticket in selected_tickets:
                    continue
                
                # 1. Pattern Scouter Filter (The Bell Curve Check)
                if not PatternScouter.is_valid_pattern(ticket, self.game_name, self.white_max):
                    continue

                # 2. Historical Jackpot Filter
                test_sb = special_pool[len(selected_tickets) % len(special_pool)] if special_pool else None
                if self.is_historical_jackpot(ticket, test_sb):
                    continue
                    
                ticket_triplets = set(itertools.combinations(ticket, 3))
                new_coverage = len(ticket_triplets - covered_triplets)
                
                if new_coverage > best_new_coverage:
                    best_new_coverage = new_coverage
                    best_ticket = ticket
                    
            if best_ticket:
                selected_tickets.append(best_ticket)
                covered_triplets.update(itertools.combinations(best_ticket, 3))
            else:
                break # No more valid tickets can be added
                
        # Fallback: If strict patterns filter out too many and we can't reach num_tickets,
        # we have to drop the pattern constraint and just wheel what's left.
        # This prevents the app from failing to generate requested tickets if the 15-ball pool
        # is mathematically stubborn.
        if len(selected_tickets) < num_tickets:
            for ticket in all_possible_tickets:
                if len(selected_tickets) >= num_tickets:
                    break
                if ticket in selected_tickets:
                    continue
                test_sb = special_pool[len(selected_tickets) % len(special_pool)] if special_pool else None
                if not self.is_historical_jackpot(ticket, test_sb):
                    selected_tickets.append(ticket)
                    covered_triplets.update(itertools.combinations(ticket, 3))
                
        final_tickets = []
        for i, t in enumerate(selected_tickets):
            sb = special_pool[i % len(special_pool)] if special_pool else None
            final_tickets.append({
                "white_balls": list(t),
                "special_ball": sb
            })
            
        return final_tickets
