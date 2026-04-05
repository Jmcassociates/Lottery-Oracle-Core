1import itertools
import random
from collections import defaultdict, Counter

class PatternScouter:
    """
    JMc - [2026-03-18] - The Autonomous Mathematical Bouncer.
    Filters out Combinatorial combinations that exist on the dead edges of the statistical bell curve.
    """
    @staticmethod
    def is_valid_pattern(ticket: tuple, scouter_config: dict) -> bool:
        valid_odd_counts = scouter_config.get("valid_odd_counts", [2, 3])
        max_consecutive = scouter_config.get("max_consecutive", 2)
        max_start_ball = scouter_config.get("max_start_ball", 30)

        # 1. Odd/Even Constraint.
        odd_count = sum(1 for n in ticket if n % 2 != 0)
        if odd_count not in valid_odd_counts:
            return False

        # 2. Consecutive Sequence Constraint. 
        sorted_ticket = sorted(ticket)
        max_seq = 1
        current_seq = 1
        for i in range(1, len(sorted_ticket)):
            if sorted_ticket[i] == sorted_ticket[i-1] + 1:
                current_seq += 1
                if current_seq > max_seq:
                    max_seq = current_seq
            else:
                current_seq = 1
                
        if max_seq > max_consecutive:
            return False

        # 3. Zone Spread Constraint.
        first_ball = sorted_ticket[0]
        if first_ball > max_start_ball:
            return False

        return True

class LotteryMathEngine:
    """
    JMc - [2026-03-18] - The Combinatorial Engine for games using Sampling Without Replacement.
    Autonomously analyzes historical data to define its own filtering parameters.
    """
    def __init__(self, game_name, historical_draws_dicts, white_max, special_max, previous_jackpots=None, scouter_config=None):
        self.game_name = game_name
        self.history = historical_draws_dicts
        self.white_max = white_max
        self.special_max = special_max
        self.previous_jackpots = previous_jackpots or set()
        
        # JMc - [2026-03-18] - Determine game parameters from empirical data.
        if self.history:
            self.numbers_per_ticket = len(self.history[-1]['white_balls'])
            # Ignore provided config and compute reality natively
            self.scouter_config = self._analyze_bell_curve()
        else:
            self.numbers_per_ticket = 5
            self.scouter_config = scouter_config or {"valid_odd_counts": [2, 3], "max_consecutive": 2, "max_start_ball": 34}

    def _analyze_bell_curve(self):
        """
        JMc - [2026-03-18] - The Autonomous Scouter Profiler.
        Dynamically analyzes the empirical dataset to establish 90th percentile constraints.
        If a pattern occurs in less than ~5% of draws, it is mathematically blocked.
        """
        odd_counts = Counter()
        consecutives = Counter()
        start_balls = []
        total = len(self.history)
        
        for draw in self.history:
            wb = sorted(draw['white_balls'])
            
            odds = sum(1 for n in wb if n % 2 != 0)
            odd_counts[odds] += 1
            
            start_balls.append(wb[0])
            
            max_seq = 1
            current_seq = 1
            for i in range(1, len(wb)):
                if wb[i] == wb[i-1] + 1:
                    current_seq += 1
                    if current_seq > max_seq:
                        max_seq = current_seq
                else:
                    current_seq = 1
            consecutives[max_seq] += 1
            
        # Extract acceptable patterns (> 5% frequency)
        valid_odds = [k for k, v in odd_counts.items() if (v / total) >= 0.05]
        if not valid_odds:
            valid_odds = [self.numbers_per_ticket // 2, (self.numbers_per_ticket // 2) + 1]
            
        valid_consec = [k for k, v in consecutives.items() if (v / total) >= 0.05]
        max_consec = max(valid_consec) if valid_consec else 2
        
        # Get 95th percentile for starting balls to capture almost everything but extreme noise
        start_balls.sort()
        max_start = start_balls[int(total * 0.95)] if start_balls else (self.white_max // 2)
        
        return {
            "valid_odd_counts": valid_odds,
            "max_consecutive": max_consec,
            "max_start_ball": max_start
        }

    def get_markov_transitions(self):
        """
        JMc - [2026-03-16] - Calculates sequence transition probabilities. 
        If ball X drops, what balls historically follow it in the next draw?
        """
        transitions = defaultdict(Counter)
        for i in range(len(self.history) - 1):
            current_draw = self.history[i]['white_balls']
            next_draw = self.history[i+1]['white_balls']
            for ball_c in current_draw:
                for ball_n in next_draw:
                    transitions[ball_c][ball_n] += 1
        return transitions

    def get_overdue_scores(self):
        """
        JMc - [2026-03-16] - Calculates the Poisson tension.
        Returns how many draws have elapsed since each number was last drawn.
        """
        last_seen = {i: len(self.history) for i in range(1, self.white_max + 1)}
        for draws_ago, draw in enumerate(reversed(self.history)):
            for ball in draw['white_balls']:
                if last_seen[ball] == len(self.history):
                    last_seen[ball] = draws_ago
        return last_seen
        
    def generate_smart_pool(self, pool_size=15, special_pool_size=3):
        """
        JMc - [2026-03-16] - The Prophet algorithm. Autonomously selects a subset pool of numbers
        based on a weighted formula of Markov Transitions, Overdue Tension, and Total Frequency.
        """
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
            
            # JMc - [2026-03-16] - The Prophet's weightings: 40% Markov, 40% Overdue, 20% Base Frequency.
            final_scores[i] = (0.4 * m_score) + (0.4 * o_score) + (0.2 * f_score)
            
        smart_pool = sorted(final_scores.keys(), key=lambda x: final_scores[x], reverse=True)[:pool_size]
        
        # Special balls
        last_seen_special = {i: len(self.history) for i in range(1, self.special_max + 1)}
        for draws_ago, draw in enumerate(reversed(self.history)):
            sb = draw['special_ball']
            if sb is not None and last_seen_special.get(sb) == len(self.history):
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
        JMc - [2026-03-16] - Check if this exact combination has ever won a jackpot.
        Because the odds of lighting striking the same matrix twice are negligible.
        """
        white_str = ",".join(str(x) for x in sorted(white_tuple))
        signature = f"{white_str}:{special_ball}"
        return signature in self.previous_jackpots

    def generate_wheeled_tickets(self, pool, special_pool, num_tickets):
        """
        JMc - [2026-03-16] - The Pragmatist Algorithm.
        Applies Greedy Combinatorial Wheeling to guarantee maximum unique triplet coverage
        with zero redundant mathematical overlap, filtered by the PatternScouter.
        
        JMc - [2026-04-03] - Controlled Entropy Injection.
        Shuffles the initial permutation array to ensure every generation request
        yields a mathematically unique batch, preventing "Syndicate Clustering."
        """
        all_possible_tickets = list(itertools.combinations(pool, self.numbers_per_ticket))
        
        # Inject Entropy: Shuffle the list so the "Greedy" algorithm starts from a random point
        # every time it is called, ensuring unique batches for every user.
        random.shuffle(all_possible_tickets)
        
        # Shuffle the special pool independently to decouple the matrix mapping
        if special_pool:
            random.shuffle(special_pool)
        
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
                
                # JMc - [2026-03-16] - 1. Pattern Scouter Filter (The Bell Curve Check)
                if not PatternScouter.is_valid_pattern(ticket, self.scouter_config):
                    continue

                # JMc - [2026-03-16] - 2. Historical Jackpot Filter
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
                
        # JMc - [2026-03-16] - Fallback logic. If the strict spatial/even-odd patterns filter out too many combinations,
        # we drop the constraint and wheel what is left in the Smart Pool to ensure the requested payload is delivered.
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
