import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone

from app.core.database import engine, Base, get_db
from app.core.models import DrawRecord, SavedTicketBatch, SavedTicket, User, SyncLog
from app.api.deps import get_current_user
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.core.config import GAMES, SYNC_STATE
from app.services.engine import LotteryMathEngine
from app.services.permutation_engine import PermutationMathEngine
from app.services.scraper import JackpotScraper
from app.services.exporter import PDFExporter
from app.services.email import EmailService
from app.api import auth, admin
from app.api.auth import GHL_WEBHOOK_SECRET
from migrate_v2 import migrate as run_schema_migration
from migrate_v2_1 import migrate as run_nat_migration

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)





from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
import threading

# JMc - [2026-03-31] - Defensive Rate Limiting
limiter = Limiter(key_func=get_remote_address)


# JMc - [2026-04-01] - Pre-boot cleanup to clear stale locks
def run_preboot_cleanup():
    db_gen = get_db()
    db = next(db_gen)
    try:
        # JMc - [2026-04-01] - Wide-net purge of all "ghost" sync logs.
        # If the server is rebooting, ANY log in 'IMPORTING' state is a zombie.
        # We use a 24-hour window to ensure we catch everything regardless of TZ drift.
        stale_threshold = datetime.utcnow() - timedelta(hours=24)
        stale_syncs = db.query(SyncLog).filter(
            SyncLog.status == "IMPORTING",
            SyncLog.executed_at < datetime.utcnow() # Catch all current and past
        ).all()
        
        for s in stale_syncs:
            s.status = "FAILED"
            s.error_message = "Protocol Interrupted: Server reboot or environment transition."
        
        if stale_syncs:
            db.commit()
            logger.info(f"Oracle - Bootup - Purged {len(stale_syncs)} stale sync records.")
    except Exception as e:
        logger.error(f"Oracle - Bootup - Pre-boot cleanup failed: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # JMc - [2026-03-31] - Temporarily disabled boot-time migration due to DB connection exhaustion.
    # Migration is still triggered inside run_sync_task().
    # JMc - [2026-04-01] - Cleanup stale sync logs to clear UI locks.
    run_preboot_cleanup()
    yield


app = FastAPI(title="Lottery Oracle API", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# JMc - [2026-03-18] - Enabled CORS since React Frontend directly calls this URL in Cloud Run
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://oracleapp.moderncyph3r.com",
        "https://oracle-frontend-ca5k2evwwq-ue.a.run.app",
        "http://localhost:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])


def run_sync_task():
    # DB Lock managed by SyncLog entries
    logger.info("Oracle - Manual Sync - [PHASE 0] Initializing Background Protocol...")
    sync_results = {}
    db = next(get_db())
    
    try:
        # JMc - [2026-03-31] - Migration Phase
        logger.info("Oracle - Manual Sync - [PHASE 1] Verification of Database Schema...")
        try:
            run_schema_migration()
            run_nat_migration()
            logger.info("Oracle - Manual Sync - [PHASE 1] Schema Alignment Confirmed.")
        except Exception as mig_err:
            logger.error(f"Oracle - Manual Sync - [PHASE 1] Schema Alignment FAILED: {mig_err}")

        import time
        for game_name, config in GAMES.items():
            logger.info(f"Oracle - Manual Sync - [PHASE 2] Initializing Stream for {game_name}...")
            
            # Record start of attempt
            log_entry = SyncLog(game_name=game_name, status="IMPORTING", new_records=0)
            db.add(log_entry)
            db.commit()
            
            try:
                fetcher = config["fetcher"]()
                logger.info(f"Oracle - Manual Sync - [PHASE 2] Connecting to {game_name} API...")
                new_count = fetcher.sync_to_db(db)
                
                log_entry.status = "SUCCESS" if new_count > 0 else "UP_TO_DATE"
                log_entry.new_records = new_count
                sync_results[game_name] = f"Added {new_count} new draws." if new_count > 0 else "Up to date."
                logger.info(f"Oracle - Manual Sync - [PHASE 2] {game_name} ingestion successful (+{new_count}).")
                
            except Exception as e:
                error_str = f"Ingestion Failure: {str(e)}"
                logger.error(f"Oracle - Manual Sync - [PHASE 2] {game_name} CRITICAL FAILURE: {e}")
                sync_results[game_name] = f"FAILED: {str(e)[:50]}"
                log_entry.status = "FAILED"
                log_entry.error_message = error_str
            
            db.commit()
            # JMc - [2026-04-01] - Increase delay to 3s to ensure state APIs (VA) reset rate limits.
            time.sleep(3)

        # Collect Final Metrics
        logger.info("Oracle - Manual Sync - [PHASE 3] Calculating Syndicate Pulse Metrics...")
        user_total = db.query(User).count()
        user_pro = db.query(User).filter(User.tier == "pro").count()
        total_records = db.query(DrawRecord).count()

        # Dispatch the Executive Briefing
        report_data = {
            "sync_results": sync_results,
            "user_total": user_total,
            "user_pro": user_pro,
            "total_records": total_records
        }
        
        admin_email = os.getenv("ADMIN_EMAIL", "james@moderncyph3r.com")
        EmailService.send_admin_report(admin_email, report_data)
        logger.info("Oracle - Manual Sync - [PHASE 4] Executive Briefing dispatched. Protocol terminated.")

    except Exception as global_err:
        logger.error(f"Oracle - Manual Sync - [PHASE 99] GLOBAL PROTOCOL FAILURE: {global_err}")
    finally:
        # DB Lock released naturally as status transitions from IMPORTING
        db.close()


@app.post("/api/admin/sync")
def trigger_sync(request: Request, db: Session = Depends(get_db)):
    """
    JMc - [2026-03-28] - Flexible Sync Trigger.
    """
    ghl_token = request.headers.get("X-GHL-Verify")
    is_authorized = False

    # 1. Check for the Cloud Scheduler/GHL secret
    if ghl_token == GHL_WEBHOOK_SECRET:
        is_authorized = True
        logger.info("Oracle - Manual Sync - Verified Cron/GHL trigger received.")
    
    # 2. Check for a valid Admin JWT session
    else:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                from app.core.security import ALGORITHM, SECRET_KEY
                from jose import jwt
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                email: str = payload.get("sub")
                if email:
                    user = db.query(User).filter(User.email == email).first()
                    if user and user.is_admin:
                        is_authorized = True
                        logger.info(f"Oracle - Manual Sync - Verified Admin session for {email}.")
            except Exception as e:
                logger.warning(f"Oracle - Manual Sync - JWT verification failed: {e}")

    if not is_authorized:
        logger.warning(f"Unauthorized sync attempt blocked from IP: {request.client.host}")
        raise HTTPException(status_code=403, detail="Administrative Clearance Required.")
        
        # JMc - [2026-03-31] - DB-backed Lock Check.
    # Prevents collisions in multi-instance environments.
    ten_mins_ago = datetime.utcnow() - timedelta(minutes=10)
    active_syncs = db.query(SyncLog).filter(
        SyncLog.status == "IMPORTING",
        SyncLog.executed_at >= ten_mins_ago
    ).count()

    if active_syncs > 0:
        logger.warning("Oracle - Manual Sync - Trigger rejected: DB-backed lock active.")
        raise HTTPException(status_code=409, detail="A synchronization protocol is already active in the cluster.")


    logger.info("Oracle - Manual Sync - Spawning background thread.")
    import threading
    thread = threading.Thread(target=run_sync_task)
    thread.start()
    return {"status": "Sync triggered in background"}




@app.get("/api/admin/health")
def admin_health_check():
    """
    JMc - [2026-03-18] - Simple status check for Cloud Scheduler uptime monitoring.
    """
    return {"status": "operational", "version": "2.1.0"}


@app.get("/api/states")
def list_states():
    """
    JMc - [2026-03-18] - Dynamically route the UI state selector based on configured GAMES.
    """
    states = list(set(v["state"] for v in GAMES.values() if v["state"] != "NAT"))
    states.sort()
    return {"states": states}

@app.get("/api/games")
def list_games(state: str = None):
    """
    JMc - [2026-03-18] - Dynamically route games by state.
    JMc - [2026-04-01] - Support 'games_full' roster for Global Pulse Ticker.
    """
    if state:
        games = [k for k, v in GAMES.items() if v["state"] in ("NAT", state)]
        return {"games": games}
    
    # Return full roster with metadata for ticker
    games_full = []
    for k, v in GAMES.items():
        state_label = "National" if v["state"] == "NAT" else v["state"]
        if state_label == "VA": state_label = "Virginia"
        if state_label == "TX": state_label = "Texas"
        if state_label == "NY": state_label = "New York"
        
        games_full.append({
            "id": k,
            "name": k.replace("Virginia", "").replace("Texas", "").replace("NewYork", ""),
            "state": state_label
        })
    
    return {
        "games": [k for k in GAMES.keys()], # Backward compatibility
        "games_full": games_full
    }

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

@app.post("/api/generate/{game_name}")
@limiter.limit("10/minute")
def generate_tickets(request: Request, game_name: str, num_tickets: int = 5, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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
