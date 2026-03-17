#!/usr/bin/env python3
"""
JMc - [2026-03-07] - The Prophet & Pragmatist Math Engine
This module contains the heavy mathematical lifting for autonomous lottery selection.
It uses Markov chains and Overdue (Poisson-ish) analysis to autonomously generate a biased
pool of numbers, then uses a greedy combinatorial wheeling algorithm to maximize the
mathematical surface area of the requested number of tickets.

It's a beautiful, over-engineered solution to a statistically unwinnable game. Enjoy.
"""

import itertools
from collections import defaultdict, Counter

class LotteryMathEngine:
    def __init__(self, historical_data, white_max, special_max):
        """
        Initialize the engine with historical data.
        historical_data: list of dicts [{'date': dt, 'white_balls': [..], 'special_ball': int}, ...]
        Assumes data is sorted chronologically (oldest to newest).
        """
        self.history = historical_data
        self.white_max = white_max
        self.special_max = special_max

    def get_markov_transitions(self):
        """
        JMc - Calculate transition probabilities. If X is drawn, what is drawn next?
        This maps 'Draw N' to 'Draw N+1'.
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
        JMc - Calculate how many draws have elapsed since each number last appeared.
        Higher score = more "overdue".
        """
        # Default to max history length if never seen (which shouldn't happen, but safety first)
        last_seen = {i: len(self.history) for i in range(1, self.white_max + 1)}
        
        # Walk backwards from the most recent draw
        for draws_ago, draw in enumerate(reversed(self.history)):
            for ball in draw['white_balls']:
                if last_seen[ball] == len(self.history):
                    last_seen[ball] = draws_ago
                    
        return last_seen
        
    def generate_smart_pool(self, pool_size=15, special_pool_size=3):
        """
        JMc - The "Prophet". Autonomously selects a pool of numbers based on:
        40% Markov Chain probability, 40% Overdue Anomaly, 20% Historical Frequency.
        """
        if not self.history:
            # Fallback if no history is provided (Architect's Ledger: No silent failures)
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
        
        # Normalize and combine scores
        max_markov = max(markov_scores.values()) if markov_scores else 1
        max_overdue = max(overdue.values()) if overdue else 1
        max_freq = max(freq.values()) if freq else 1
        
        final_scores = {}
        for i in range(1, self.white_max + 1):
            m_score = (markov_scores[i] / max_markov) if max_markov else 0
            o_score = (overdue[i] / max_overdue) if max_overdue else 0
            f_score = (freq[i] / max_freq) if max_freq else 0
            
            # The secret sauce weighting
            final_scores[i] = (0.4 * m_score) + (0.4 * o_score) + (0.2 * f_score)
            
        # Select the top 'pool_size' white balls
        smart_pool = sorted(final_scores.keys(), key=lambda x: final_scores[x], reverse=True)[:pool_size]
        
        # Special balls get a similar treatment (Overdue + Frequency)
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

    def generate_wheeled_tickets(self, pool, special_pool, num_tickets, numbers_per_ticket=5):
        """
        JMc - The "Pragmatist". Takes the generated pool and applies a Greedy Combinatorial Wheel.
        It generates exactly `num_tickets` by iteratively selecting the combination that provides
        the highest number of previously uncovered triplets (3-number matches).
        This minimizes overlap and mathematically maximizes the "net" you cast over the pool.
        """
        # Generate all possible 5-number combinations from our 15-number pool (~3,003 combinations)
        all_possible_tickets = list(itertools.combinations(pool, numbers_per_ticket))
        
        covered_triplets = set()
        selected_tickets = []
        
        # Cap requested tickets to the mathematical maximum combinations
        num_tickets = min(num_tickets, len(all_possible_tickets))
        
        for _ in range(num_tickets):
            best_ticket = None
            best_new_coverage = -1
            
            # Evaluate every possible remaining ticket
            for ticket in all_possible_tickets:
                if ticket in selected_tickets:
                    continue
                    
                # A 5-number ticket contains 10 triplets
                ticket_triplets = set(itertools.combinations(ticket, 3))
                
                # How many of these triplets have we NOT covered yet?
                new_coverage = len(ticket_triplets - covered_triplets)
                
                if new_coverage > best_new_coverage:
                    best_new_coverage = new_coverage
                    best_ticket = ticket
                    
            if best_ticket:
                selected_tickets.append(best_ticket)
                covered_triplets.update(itertools.combinations(best_ticket, 3))
                
        # Attach the special balls (round-robin style to ensure distribution)
        final_tickets = []
        for i, t in enumerate(selected_tickets):
            sb = special_pool[i % len(special_pool)]
            final_tickets.append((list(t), sb))
            
        return final_tickets
