import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.core.database import engine, Base, get_db
from app.core.models import DrawRecord, SavedTicketBatch, SavedTicket, User
from app.core.security import get_current_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.services.fetchers import (
    VirginiaPowerballFetcher, 
    VirginiaMegaMillionsFetcher,
    VirginiaCash4LifeFetcher,
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
from app.services.engine import LotteryMathEngine
from app.services.permutation_engine import PermutationMathEngine
from app.services.scraper import JackpotScraper
from app.services.exporter import PDFExporter
from app.api import auth
from migrate_v2 import migrate as run_schema_migration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Game Configurations
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
    "VirginiaCash4Life": {
        "state": "VA",
        "white_max": 60,
        "special_max": 4,
        "fetcher": VirginiaCash4LifeFetcher,
        "scraper_config": {
            "type": "fixed",
            "jackpot": "$1,000/Day",
            "next_draw": "Draws Daily 9:00 PM"
        },
        "scouter_config": {
            "max_start_ball": 34,
            "max_consecutive": 2
        },
        "prize_tiers": {
            (5, True): "JACKPOT (1000/day)",
            (5, False): "1000/week",
            (4, True): 2500,
            (4, False): 500,
            (3, True): 100,
            (3, False): 25,
            (2, True): 10,
            (2, False): 4,
            (1, True): 2
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

from fastapi.middleware.cors import CORSMiddleware
import threading

@asynccontextmanager
async def lifespan(app: FastAPI):
    # JMc - [2026-03-18] - DB initialization moved to manual sync trigger 
    # to prevent boot-time crashes on connection failures.
    yield

app = FastAPI(title="Lottery Oracle API", lifespan=lifespan)

# JMc - [2026-03-18] - Enabled CORS since React Frontend directly calls this URL in Cloud Run
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

def run_sync_task():
    logger.info("Oracle - Manual Sync - Starting background ingestion...")
    try:
        # JMc - [2026-03-18] - Ensure the database schema is up to date before syncing.
        logger.info("Oracle - Manual Sync - Executing schema migration v2.0...")
        run_schema_migration()
        
        db = next(get_db())
        for game_name, config in GAMES.items():
            logger.info(f"Oracle - Manual Sync - Processing {game_name}...")
            fetcher = config["fetcher"]()
            fetcher.sync_to_db(db)
        logger.info("Oracle - Manual Sync - Background sync complete.")
    except Exception as e:
        logger.error(f"Oracle - Manual Sync - Error during background sync: {e}")

@app.post("/api/admin/sync")
def trigger_sync():
    """
    JMc - [2026-03-18] - Bootstrap Sync Trigger. 
    TEMPORARILY UNLOCKED for initial database provisioning.
    """
    logger.info("Oracle - Manual Sync - Unauthenticated request received (Bootstrap Mode).")
    thread = threading.Thread(target=run_sync_task)
    thread.start()
    return {"status": "Sync triggered in background"}

@app.get("/api/admin/stats")
def get_admin_stats(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    JMc - [2026-03-18] - System Pulse. 
    Returns database row counts and user metrics for the War Room blade.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Administrative Clearance Required.")
        
    game_stats = {}
    for game in GAMES.keys():
        count = db.query(DrawRecord).filter(DrawRecord.game_name.startswith(game)).count()
        game_stats[game] = count
        
    user_count = db.query(User).count()
    pro_users = db.query(User).filter(User.tier == "pro").count()
    
    return {
        "games": game_stats,
        "users": {
            "total": user_count,
            "pro": pro_users,
            "free": user_count - pro_users
        }
    }

@app.get("/api/states")
def list_states():
    """
    JMc - [2026-03-18] - Dynamically route the UI state selector based on configured GAMES.
    """
    states = list(set(v["state"] for v in GAMES.values() if v["state"] != "NAT"))
    states.sort()
    return {"states": states}

@app.get("/api/games")
def list_games(state: str = "VA"):
    """
    JMc - [2026-03-18] - Dynamically route games by state, plus national games.
    """
    games = [k for k, v in GAMES.items() if v["state"] in ("NAT", state)]
    return {"games": games}

@app.get("/api/jackpots")
def get_live_jackpots(state: str = "VA"):
    """
    JMc - [2026-03-18] - Return jackpots filtered by the active state.
    """
    all_jackpots = JackpotScraper.get_live_data(GAMES)
    filtered = {}
    for game_name, data in all_jackpots.items():
        if game_name in GAMES and GAMES[game_name]["state"] in ("NAT", state):
            filtered[game_name] = data
    return filtered

@app.get("/api/history/{game_name}")
def get_game_history(game_name: str, limit: int = 10, db: Session = Depends(get_db)):
    """
    JMc - [2026-03-16] - Returns historical draw data formatted for the frontend dashboard.
    Uses startswith to elegantly bundle Pick3 Day and Pick3 Night draws into a single response.
    """
    draws = db.query(DrawRecord).filter(DrawRecord.game_name.startswith(game_name))\
              .order_by(DrawRecord.draw_date.desc()).limit(limit).all()
    
    return [
        {
            "date": d.draw_date.isoformat(),
            "white_balls": [int(x) for x in d.white_balls.split(",")],
            "special_ball": d.special_ball
        } for d in draws
    ]

@app.post("/api/user/upgrade")
def upgrade_user_tier(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    JMc - [2026-03-16] - Mock Billing Bypass.
    In production (GoHighLevel handoff), this would process webhooks to upgrade tier status.
    """
    current_user.tier = "pro"
    db.commit()
    access_token = create_access_token(
        data={"sub": current_user.email}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "tier": "pro"}

@app.post("/api/generate/{game_name}")
def generate_tickets(game_name: str, num_tickets: int = 5, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    JMc - [2026-03-16] - The core Oracle generation controller.
    Dynamically routes combinatorial games to LotteryMathEngine and permutation games to PermutationMathEngine.
    """
    if game_name not in GAMES:
        raise HTTPException(status_code=404, detail="Game not found")
        
    if current_user.tier == "free":
        # JMc - [2026-03-16] - Free Tier limit logic. Must use EDT timezone translation 
        # to ensure the daily limit resets at Midnight EST, not Midnight UTC.
        import zoneinfo
        today = datetime.now(zoneinfo.ZoneInfo("America/New_York")).date()
        existing_gens = db.query(SavedTicketBatch).filter(
            SavedTicketBatch.user_id == current_user.id,
            SavedTicketBatch.game_name == game_name
        ).all()
        
        def _get_local_date(dt):
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(zoneinfo.ZoneInfo("America/New_York")).date()
            
        if any(_get_local_date(t.created_at) == today for t in existing_gens):
            raise HTTPException(status_code=403, detail="Free tier limit reached. Upgrade to Pro.")
        num_tickets = min(num_tickets, 5)
    else:
        if num_tickets > 50:
            raise HTTPException(status_code=400, detail="Pro tier is limited to 50 tickets.")
        
    config = GAMES[game_name]
    records = db.query(DrawRecord).filter(DrawRecord.game_name.startswith(game_name)).order_by(DrawRecord.draw_date.asc()).all()
                
    if not records:
        raise HTTPException(status_code=400, detail="No historical data available yet.")
        
    formatted_history = []
    previous_jackpots = set()
    
    for r in records:
        wb = [int(x) for x in r.white_balls.split(",")]
        formatted_history.append({"date": r.draw_date, "white_balls": wb, "special_ball": r.special_ball})
        previous_jackpots.add(f"{r.white_balls}:{r.special_ball}")
        
    scouter_config = config.get("scouter_config", {})
    
    if "Pick" in game_name or "Daily" in game_name or "Numbers" in game_name or "Win4" in game_name:
        # JMc - [2026-03-16] - Route permutation games to the Cartesian engine.
        num_digits = 3 if "Pick3" in game_name or "Numbers" in game_name else (4 if "Pick4" in game_name or "Daily4" in game_name or "Win4" in game_name else 5)
        engine = PermutationMathEngine(game_name, formatted_history, num_digits, previous_jackpots, scouter_config)
        tickets, pool = engine.generate_tickets(num_tickets)
        special_pool = []
    else:
        # JMc - [2026-03-16] - Route combinatorial games to the Wheeling engine.
        engine = LotteryMathEngine(game_name, formatted_history, config["white_max"], config["special_max"], previous_jackpots, scouter_config)
        sp_size = 3 if config["special_max"] > 0 else 0
        pool, special_pool = engine.generate_smart_pool(pool_size=15, special_pool_size=sp_size)
        tickets = engine.generate_wheeled_tickets(pool, special_pool, num_tickets)
    
    batch = SavedTicketBatch(
        user_id=current_user.id,
        state_code=config["state"],
        game_name=game_name,
        pool_white_balls=",".join(str(x) for x in pool),
        pool_special_balls=",".join(str(x) for x in special_pool) if special_pool else ""
    )
    db.add(batch)
    db.commit() 
    db.refresh(batch)
    
    saved_tickets_resp = []
    for t in tickets:
        db.add(SavedTicket(
            batch_id=batch.id,
            ticket_white_balls=",".join(str(x) for x in t['white_balls']),
            ticket_special_ball=t['special_ball']
        ))
        saved_tickets_resp.append(t)
        
    db.commit()
    
    return {
        "game": game_name,
        "batch_id": batch.id,
        "tickets": saved_tickets_resp
    }

@app.get("/api/my-tickets")
def get_my_tickets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    JMc - [2026-03-16] - Fetches the user's previously generated tickets from the Vault.
    """
    batches = db.query(SavedTicketBatch).filter(SavedTicketBatch.user_id == current_user.id)\
                .order_by(SavedTicketBatch.created_at.desc()).all()
                
    result = []
    for b in batches:
        # JMc - [2026-03-16] - SQLite stores naive datetimes in UTC. We must append 'Z' 
        # so the browser javascript explicitly translates it to local time.
        created_at_str = b.created_at.isoformat()
        if b.created_at.tzinfo is None:
            created_at_str += "Z"

        result.append({
            "id": b.id,
            "game_name": b.game_name,
            "created_at": created_at_str,
            "tickets": [
                {
                    "id": t.id,
                    "white_balls": [int(x) for x in t.ticket_white_balls.split(",")],
                    "special_ball": t.ticket_special_ball
                } for t in b.tickets
            ]
        })
    return result

@app.get("/api/check-batch/{batch_id}")
def check_batch_results(batch_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    JMc - [2026-03-16] - The Reality Check Engine. 
    Compares a saved batch against all draws that occurred AFTER the batch was created.
    """
    batch = db.query(SavedTicketBatch).filter(SavedTicketBatch.id == batch_id, SavedTicketBatch.user_id == current_user.id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    game_config = GAMES.get(batch.game_name)
    if not game_config:
        raise HTTPException(status_code=400, detail="Invalid game configuration")

    # JMc - [2026-03-16] - Find draws that happened on or after the day the batch was created.
    # Must explicitely cast UTC to EDT so we don't accidentally skip late-night draws.
    import zoneinfo
    created_at_utc = batch.created_at
    if created_at_utc.tzinfo is None:
        created_at_utc = created_at_utc.replace(tzinfo=timezone.utc)
    batch_date = created_at_utc.astimezone(zoneinfo.ZoneInfo("America/New_York")).date()
    
    draws = db.query(DrawRecord).filter(
        DrawRecord.game_name.startswith(batch.game_name),
        DrawRecord.draw_date >= batch_date
    ).order_by(DrawRecord.draw_date.asc()).all()

    if not draws:
        return {"status": "pending", "message": "No draws have occurred since these tickets were generated."}

    results = []
    total_spent = len(batch.tickets) * 2 # Assuming $2 per ticket per draw
    total_won = 0

    for draw in draws:
        draw_wb_list = [int(x) for x in draw.white_balls.split(",")]
        draw_wb_set = set(draw_wb_list)
        draw_sb = draw.special_ball
        
        draw_winnings = 0
        winning_tickets = []

        for ticket in batch.tickets:
            ticket_wb_list = [int(x) for x in ticket.ticket_white_balls.split(",")]
            ticket_wb_set = set(ticket_wb_list)
            ticket_sb = ticket.ticket_special_ball
            
            is_pick = "Pick" in batch.game_name or "Daily" in batch.game_name or "Numbers" in batch.game_name or "Win4" in batch.game_name
            
            if is_pick:
                # JMc - [2026-03-16] - Exact Match logic for permutation games (order matters).
                white_matches = len(ticket_wb_list) if ticket_wb_list == draw_wb_list else 0
            else:
                # JMc - [2026-03-16] - Intersection logic for combinatorial games (order doesn't matter).
                white_matches = len(ticket_wb_set.intersection(draw_wb_set))
            
            sb_match = (ticket_sb == draw_sb)
            
            prize = game_config["prize_tiers"].get((white_matches, sb_match), 0)
            
            if prize != 0:
                winning_tickets.append({
                    "ticket_id": ticket.id,
                    "white_balls": ticket_wb_list,
                    "special_ball": ticket_sb,
                    "matches": {"white": white_matches, "special": sb_match},
                    "prize": prize
                })
                if isinstance(prize, int):
                    draw_winnings += prize

        total_won += draw_winnings
        results.append({
            "draw_date": draw.draw_date.isoformat(),
            "drawn_numbers": {"white_balls": draw_wb_list, "special_ball": draw_sb},
            "winnings": draw_winnings,
            "winning_tickets": winning_tickets
        })

    return {
        "status": "checked",
        "batch_id": batch.id,
        "draws_checked": len(draws),
        "total_spent": total_spent * len(draws),
        "total_won": total_won,
        "net_roi": total_won - (total_spent * len(draws)),
        "details": results
    }

@app.get("/api/export-batch/{batch_id}")
def export_batch_to_pdf(batch_id: int, tz: str = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    JMc - [2026-03-16] - Syndicate Exporter. Generates a professional PDF manifest for a ticket batch.
    Accepts an optional 'tz' parameter to localize the timestamp.
    """
    batch = db.query(SavedTicketBatch).filter(SavedTicketBatch.id == batch_id, SavedTicketBatch.user_id == current_user.id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")

    created_at = batch.created_at
    if tz:
        try:
            import zoneinfo
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            created_at = created_at.astimezone(zoneinfo.ZoneInfo(tz))
        except Exception as e:
            logger.warning(f"Could not convert timezone to {tz}: {e}")

    tickets_data = [
        {
            "white_balls": [int(x) for x in t.ticket_white_balls.split(",")],
            "special_ball": t.ticket_special_ball
        } for t in batch.tickets
    ]

    pdf_buffer = PDFExporter.generate_ticket_pdf(
        batch_name=f"{batch.game_name} - Sequence #{batch.id}",
        tickets=tickets_data,
        created_at=created_at
    )

    filename = f"Oracle_Manifest_{batch.game_name}_{batch.id}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.delete("/api/batches/{batch_id}")
def delete_batch(batch_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """
    JMc - [2026-03-18] - Purge historical artifacts. 
    Deletes a saved batch and cascades to all associated tickets.
    """
    batch = db.query(SavedTicketBatch).filter(SavedTicketBatch.id == batch_id, SavedTicketBatch.user_id == current_user.id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found")
        
    db.delete(batch)
    db.commit()
    return {"status": "success", "message": "Batch purged"}
