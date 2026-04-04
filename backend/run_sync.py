import os
import sys
import logging

# JMc - [2026-04-04] - Add current dir to path to support standalone execution in Docker
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "app"))

from app.main import run_sync_task

# Configure logging for the Job environment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("OracleSyncJob")

if __name__ == "__main__":
    """
    JMc - [2026-04-04] - Entry point for the Cloud Run Job.
    Cloud Run Jobs execute this script, finish, and the billing stops.
    """
    # Check if this is a manual trigger via environment variable
    is_manual = os.getenv("IS_MANUAL_SYNC", "false").lower() == "true"
    
    logger.info(f"Oracle Sync Job Initiated. Manual Override: {is_manual}")
    
    try:
        # We reuse the existing hardened logic from main.py
        run_sync_task(is_manual=is_manual)
        logger.info("Oracle Sync Job Completed Successfully.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Oracle Sync Job FAILED: {e}")
        sys.exit(1)
