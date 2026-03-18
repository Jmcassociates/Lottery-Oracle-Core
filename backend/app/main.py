import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from apscheduler.schedulers.background import BackgroundScheduler

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
    VirginiaPick3Fetcher
)
from app.services.engine import LotteryMathEngine
from app.services.permutation_engine import PermutationMathEngine
from app.services.scraper import JackpotScraper
from app.services.exporter import PDFExporter
from app.api import auth

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Game Configurations
GAMES = {
    "Powerball": {
        "white_max": 69,
        "special_max": 26,
        "fetcher": VirginiaPowerballFetcher,
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
        "white_max": 70,
        "special_max": 24, # Post 2025 rule
        "fetcher": VirginiaMegaMillionsFetcher,
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
    "Cash4Life": {
        "white_max": 60,
        "special_max": 4,
        "fetcher": VirginiaCash4LifeFetcher,
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
    "Cash5": {
        "white_max": 45,
        "special_max": 0, # No special ball
        "fetcher": VirginiaCash5Fetcher,
        "prize_tiers": {
            (5, False): "JACKPOT",
            (4, False): 200,
            (3, False): 5,
            (2, False): 1
        }
    },
    "Pick5": {
        "white_max": 9,
        "special_max": 0,
        "fetcher": VirginiaPick5Fetcher,
        "prize_tiers": {
            (5, False): 50000
        }
    },
    "Pick4": {
        "white_max": 9,
        "special_max": 0,
        "fetcher": VirginiaPick4Fetcher,
        "prize_tiers": {
            (4, False): 5000
        }
    },
    "Pick3": {
        "white_max": 9,
        "special_max": 0,
        "fetcher": VirginiaPick3Fetcher,
        "prize_tiers": {
            (3, False): 500
        }
    }
}

scheduler = BackgroundScheduler()

def scheduled_sync():
    """Runs on a cron job to update DB."""
    logger.info("Running scheduled database sync...")
    db = next(get_db())
    for game_name, config in GAMES.items():
        fetcher = config["fetcher"]()
        fetcher.sync_to_db(db)
    logger.info("Sync complete.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    # JMc - 2026-03-15 - Running at 07:00 UTC (03:00 EDT) to ensure VA Lottery API is updated.
    scheduler.add_job(scheduled_sync, 'cron', hour=7, minute=0)
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(title="Lottery Oracle API", lifespan=lifespan)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

@app.get("/api/games")
def list_games():
    return {"games": list(GAMES.keys())}

@app.get("/api/jackpots")
def get_live_jackpots():
    return JackpotScraper.get_live_data()

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
        
    if game_name.startswith("Pick"):
        # JMc - [2026-03-16] - Route permutation games to the Cartesian engine.
        num_digits = 3 if game_name == "Pick3" else (4 if game_name == "Pick4" else 5)
        engine = PermutationMathEngine(game_name, formatted_history, num_digits, previous_jackpots)
        tickets, pool = engine.generate_tickets(num_tickets)
        special_pool = []
    else:
        # JMc - [2026-03-16] - Route combinatorial games to the Wheeling engine.
        engine = LotteryMathEngine(game_name, formatted_history, config["white_max"], config["special_max"], previous_jackpots)
        sp_size = 3 if config["special_max"] > 0 else 0
        pool, special_pool = engine.generate_smart_pool(pool_size=15, special_pool_size=sp_size)
        tickets = engine.generate_wheeled_tickets(pool, special_pool, num_tickets)
    
    batch = SavedTicketBatch(
        user_id=current_user.id,
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
            
            is_pick = batch.game_name.startswith("Pick")
            
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
