import os
import sys
import time
import subprocess
import schedule
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='logs/scheduler.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

def create_log_dir():
    """Create logs directory if it doesn't exist"""
    os.makedirs('logs', exist_ok=True)

def run_update():
    """Run the data update script"""
    try:
        logger.info("Starting scheduled data update")
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'update_data.py')
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True
        )
        
        # Log output
        logger.info(f"Update script completed with exit code: {result.returncode}")
        if result.stdout:
            logger.info(f"Output: {result.stdout}")
        if result.stderr:
            logger.error(f"Errors: {result.stderr}")
            
        logger.info("Scheduled data update completed successfully")
        
    except Exception as e:
        logger.error(f"Error running scheduled update: {str(e)}")

def main():
    """Schedule and run daily updates"""
    create_log_dir()
    
    logger.info("Starting NBA data update scheduler")
    print("NBA Data Update Scheduler")
    print("=========================")
    print("This script will automatically update NBA data daily.")
    print("Updates are scheduled to run at:")
    print("- 5:00 AM (to get latest game results)")
    print("- 3:00 PM (to get roster updates for evening games)")
    
    # Schedule daily updates at 5 AM
    schedule.every().day.at("05:00").do(run_update)
    
    # Schedule another update at 3 PM for roster updates before evening games
    schedule.every().day.at("15:00").do(run_update)
    
    # Run immediately on startup
    print("\nRunning initial update now...")
    run_update()
    
    print("\nScheduler is running. Press Ctrl+C to stop.")
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\nScheduler stopped by user.")
            break
        except Exception as e:
            logger.error(f"Error in scheduler loop: {str(e)}")
            time.sleep(300)  # Wait 5 minutes on error before resuming

if __name__ == "__main__":
    main() 