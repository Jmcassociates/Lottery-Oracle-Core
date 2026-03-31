from app.services.fetchers import (
    VirginiaPowerballFetcher, 
    VirginiaMegaMillionsFetcher,
    VirginiaCash5Fetcher,
    VirginiaPick5Fetcher,
    VirginiaPick4Fetcher,
    VirginiaPick3Fetcher,
    TexasCashFiveFetcher,
    TexasPick3Fetcher,
    TexasDaily4Fetcher,
    NewYorkLottoFetcher,
    NewYorkTake5Fetcher,
    NewYorkPick3Fetcher,
    NewYorkPick4Fetcher
)

# JMc - [2026-03-28] - Centralized Game Configurations. 
# Enables rapid expansion to new states and unified sync health tracking.
GAMES = {
    "Powerball": {
        "state": "NAT",
        "white_max": 69,
        "special_max": 26,
        "fetcher": VirginiaPowerballFetcher,
        "scraper_config": {
            "url": "https://www.valottery.com/data/draw-games/powerball",
            "game_id": "game-20",
            "type": "scrape"
        },
        "scouter_config": {
            "max_start_ball": 34,
            "max_consecutive": 2
        },
        "prize_tiers": {
            (5, True): "JACKPOT",
            (5, False): 1000000,
            (4, True): 50000,
            (4, False): 100,
            (3, True): 100,
            (3, False): 7,
            (2, True): 7,
            (1, True): 4,
            (0, True): 4
        }
    },
    "MegaMillions": {
        "state": "NAT",
        "white_max": 70,
        "special_max": 24, # Post 2025 rule
        "fetcher": VirginiaMegaMillionsFetcher,
        "scraper_config": {
            "url": "https://www.valottery.com/data/draw-games/megamillions",
            "game_id": "game-15",
            "type": "scrape"
        },
        "scouter_config": {
            "max_start_ball": 20,
            "max_consecutive": 2
        },
        "prize_tiers": {
            (5, True): "JACKPOT",
            (5, False): 1000000,
            (4, True): 10000,
            (4, False): 500,
            (3, True): 200,
            (3, False): 10,
            (2, True): 10,
            (1, True): 4,
            (0, True): 2
        }
    },
    "VirginiaCash5": {
        "state": "VA",
        "white_max": 45,
        "special_max": 0, # No special ball
        "fetcher": VirginiaCash5Fetcher,
        "scraper_config": {
            "url": "https://www.valottery.com/data/draw-games/cash5",
            "game_id": "game-1030",
            "type": "scrape_amount_only",
            "next_draw": "Draws Daily 11:00 PM"
        },
        "scouter_config": {
            "max_start_ball": 20,
            "max_consecutive": 2
        },
        "prize_tiers": {
            (5, False): "JACKPOT",
            (4, False): 200,
            (3, False): 5,
            (2, False): 1
        }
    },
    "VirginiaPick5": {
        "state": "VA",
        "white_max": 9,
        "special_max": 0,
        "fetcher": VirginiaPick5Fetcher,
        "scraper_config": {
            "type": "fixed",
            "jackpot": "$50,000 Top Prize",
            "next_draw": "Draws Daily 1:59 PM & 11:00 PM"
        },
        "scouter_config": {
            "min_sum": 20,
            "max_sum": 26,
            "max_repeats": 3
        },
        "prize_tiers": {
            (5, False): 50000
        }
    },
    "VirginiaPick4": {
        "state": "VA",
        "white_max": 9,
        "special_max": 0,
        "fetcher": VirginiaPick4Fetcher,
        "scraper_config": {
            "type": "fixed",
            "jackpot": "$5,000 Top Prize",
            "next_draw": "Draws Daily 1:59 PM & 11:00 PM"
        },
        "scouter_config": {
            "min_sum": 16,
            "max_sum": 20,
            "max_repeats": 2
        },
        "prize_tiers": {
            (4, False): 5000
        }
    },
    "VirginiaPick3": {
        "state": "VA",
        "white_max": 9,
        "special_max": 0,
        "fetcher": VirginiaPick3Fetcher,
        "scraper_config": {
            "type": "fixed",
            "jackpot": "$500 Top Prize",
            "next_draw": "Draws Daily 1:59 PM & 11:00 PM"
        },
        "scouter_config": {
            "min_sum": 11,
            "max_sum": 16,
            "max_repeats": 2
        },
        "prize_tiers": {
            (3, False): 500
        }
    },
    "TexasCashFive": {
        "state": "TX",
        "white_max": 35,
        "special_max": 0,
        "fetcher": TexasCashFiveFetcher,
        "scraper_config": {
            "type": "fixed",
            "jackpot": "$25,000 Top Prize",
            "next_draw": "Draws Daily 10:12 PM CT"
        },
        "scouter_config": {
            "max_start_ball": 15, # JMc - 2026-03-18 - Lower spread for a 35 ball game compared to 45 ball Cash5
            "max_consecutive": 2
        },
        "prize_tiers": {
            (5, False): "JACKPOT",
            (4, False): 350,
            (3, False): 15,
            (2, False): 2 # Free ticket usually, count as 2 for ROI
        }
    },
    "TexasPick3": {
        "state": "TX",
        "white_max": 9,
        "special_max": 0,
        "fetcher": TexasPick3Fetcher,
        "scraper_config": {
            "type": "fixed",
            "jackpot": "$500 Top Prize",
            "next_draw": "Draws 4x Daily (Mon-Sat)"
        },
        "scouter_config": {
            "min_sum": 11,
            "max_sum": 16,
            "max_repeats": 2
        },
        "prize_tiers": {
            (3, False): 500
        }
    },
    "TexasDaily4": {
        "state": "TX",
        "white_max": 9,
        "special_max": 0,
        "fetcher": TexasDaily4Fetcher,
        "scraper_config": {
            "type": "fixed",
            "jackpot": "$5,000 Top Prize",
            "next_draw": "Draws 4x Daily (Mon-Sat)"
        },
        "scouter_config": {
            "min_sum": 16,
            "max_sum": 20,
            "max_repeats": 2
        },
        "prize_tiers": {
            (4, False): 5000
        }
    },
    "NewYorkLotto": {
        "state": "NY",
        "white_max": 59,
        "special_max": 59, # Bonus ball is from same pool
        "fetcher": NewYorkLottoFetcher,
        "scraper_config": {
            "type": "fixed",
            "jackpot": "Variable",
            "next_draw": "Wed & Sat 8:15 PM"
        },
        "scouter_config": {
            "max_start_ball": 25,
            "max_consecutive": 2,
            "valid_odd_counts": [2, 3, 4] # JMc - [2026-03-18] - 6-ball game logic.
        },
        "prize_tiers": {
            (6, False): "JACKPOT",
            (5, True): 25000,
            (5, False): 1500,
            (4, False): 15,
            (3, False): 1
        }
    },
    "NewYorkTake5": {
        "state": "NY",
        "white_max": 39,
        "special_max": 0,
        "fetcher": NewYorkTake5Fetcher,
        "scraper_config": {
            "type": "fixed",
            "jackpot": "Rolling",
            "next_draw": "Daily 2:30 PM & 10:30 PM"
        },
        "scouter_config": {
            "max_start_ball": 15,
            "max_consecutive": 2
        },
        "prize_tiers": {
            (5, False): "JACKPOT",
            (4, False): 500,
            (3, False): 25,
            (2, False): 2
        }
    },
    "NewYorkNumbers": {
        "state": "NY",
        "white_max": 9,
        "special_max": 0,
        "fetcher": NewYorkPick3Fetcher,
        "scraper_config": {
            "type": "fixed",
            "jackpot": "$500 Top Prize",
            "next_draw": "Daily 2:30 PM & 10:30 PM"
        },
        "scouter_config": {
            "min_sum": 11,
            "max_sum": 16,
            "max_repeats": 2
        },
        "prize_tiers": {
            (3, False): 500
        }
    },
    "NewYorkWin4": {
        "state": "NY",
        "white_max": 9,
        "special_max": 0,
        "fetcher": NewYorkPick4Fetcher,
        "scraper_config": {
            "type": "fixed",
            "jackpot": "$5,000 Top Prize",
            "next_draw": "Daily 2:30 PM & 10:30 PM"
        },
        "scouter_config": {
            "min_sum": 16,
            "max_sum": 20,
            "max_repeats": 2
        },
        "prize_tiers": {
            (4, False): 5000
        }
    }
}
