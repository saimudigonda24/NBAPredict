#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import pandas as pd
from datetime import datetime, timedelta
import argparse

def get_absolute_path(relative_path):
    """Convert relative path to absolute path"""
    return os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), relative_path))

def check_data_freshness():
    """Check how recent the data is"""
    data_dir = get_absolute_path("data")
    
    # Find the most recent data file
    data_files = [f for f in os.listdir(data_dir) 
                  if f.startswith('team_games_') and f.endswith('.csv')]
    
    if not data_files:
        print("No data files found.")
        return
    
    latest_file = max(data_files)
    latest_path = os.path.join(data_dir, latest_file)
    
    # Get file creation/modification time
    file_time = datetime.fromtimestamp(os.path.getmtime(latest_path))
    time_since_update = datetime.now() - file_time
    
    print(f"Latest data file: {latest_file}")
    print(f"Last updated: {file_time.strftime('%Y-%m-%d %H:%M:%S')} ({time_since_update.days} days, {time_since_update.seconds // 3600} hours ago)")
    
    # Check the most recent game date in the data
    try:
        df = pd.read_csv(latest_path)
        if 'GAME_DATE' in df.columns and not df.empty:
            most_recent_game = df['GAME_DATE'].max()
            print(f"Most recent game in dataset: {most_recent_game}")
            
            # Calculate how many days behind we are
            today = datetime.now().strftime('%Y-%m-%d')
            days_behind = (datetime.now() - datetime.strptime(most_recent_game, '%Y-%m-%d')).days
            
            if days_behind <= 1:
                print("✅ Data is up-to-date (within 1 day)")
            elif days_behind <= 3:
                print("⚠️ Data is slightly outdated (within 3 days)")
            else:
                print(f"❌ Data is outdated ({days_behind} days behind)")
        else:
            print("No game date information found in the dataset.")
    except Exception as e:
        print(f"Error reading data file: {str(e)}")

def check_scheduler_status():
    """Check if the scheduler is active"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        plist_path = os.path.expanduser("~/Library/LaunchAgents/com.nba.predict.autoupdate.plist")
        
        if os.path.exists(plist_path):
            print(f"✅ LaunchAgent configuration exists: {plist_path}")
            
            # Check if it's loaded
            try:
                result = subprocess.run("launchctl list | grep com.nba.predict.autoupdate", 
                                      shell=True, text=True, capture_output=True)
                if result.returncode == 0:
                    print("✅ LaunchAgent is loaded and active")
                else:
                    print("❌ LaunchAgent exists but is not loaded")
                    print("   To load it, run: launchctl load ~/Library/LaunchAgents/com.nba.predict.autoupdate.plist")
            except Exception as e:
                print(f"Error checking LaunchAgent status: {str(e)}")
        else:
            print("❌ LaunchAgent configuration not found")
            print("   To set up automatic updates, run: python scripts/setup_scheduler.py")
    
    elif system == "Linux":
        try:
            result = subprocess.run("crontab -l | grep auto_update.py", 
                                  shell=True, text=True, capture_output=True)
            if result.returncode == 0:
                print("✅ Cron job is configured")
                print(f"   Configuration: {result.stdout.strip()}")
            else:
                print("❌ No cron job found for auto_update.py")
                print("   To set up automatic updates, run: python scripts/setup_scheduler.py")
        except Exception as e:
            print(f"Error checking cron status: {str(e)}")
    
    elif system == "Windows":
        try:
            result = subprocess.run("schtasks /query /tn NBA_Predict_Update", 
                                  shell=True, text=True, capture_output=True)
            if result.returncode == 0:
                print("✅ Windows Task Scheduler job is configured")
            else:
                print("❌ No scheduled task found for NBA_Predict_Update")
                print("   To set up automatic updates, run: python scripts/setup_scheduler.py")
        except Exception as e:
            print(f"Error checking scheduled task status: {str(e)}")
    
    else:
        print(f"Unsupported operating system: {system}")

def check_log_files():
    """Check the update log files"""
    logs_dir = get_absolute_path("logs")
    
    log_files = {
        "auto_update.log": "Auto Update Log",
        "launchd_update.log": "LaunchAgent Log (macOS)",
        "cron_update.log": "Cron Job Log (Linux)"
    }
    
    for log_file, description in log_files.items():
        log_path = os.path.join(logs_dir, log_file)
        
        if os.path.exists(log_path):
            file_time = datetime.fromtimestamp(os.path.getmtime(log_path))
            time_since_update = datetime.now() - file_time
            file_size = os.path.getsize(log_path) / 1024  # Size in KB
            
            print(f"\n{description}:")
            print(f"  Last modified: {file_time.strftime('%Y-%m-%d %H:%M:%S')} ({time_since_update.days} days, {time_since_update.seconds // 3600} hours ago)")
            print(f"  Size: {file_size:.2f} KB")
            
            # Show the last few lines of the log
            try:
                with open(log_path, 'r') as f:
                    lines = f.readlines()
                    last_lines = lines[-5:] if len(lines) >= 5 else lines
                    
                    print("  Last log entries:")
                    for line in last_lines:
                        print(f"    {line.strip()}")
            except Exception as e:
                print(f"  Error reading log file: {str(e)}")
        else:
            print(f"\n{description}: Not found")

def main():
    parser = argparse.ArgumentParser(description='Check the status of the NBA prediction automatic update system')
    parser.add_argument('--verbose', action='store_true', help='Show detailed information')
    args = parser.parse_args()
    
    print("=== NBA Prediction App Update System Status ===\n")
    
    print("Data Status:")
    check_data_freshness()
    
    print("\nScheduler Status:")
    check_scheduler_status()
    
    if args.verbose:
        check_log_files()
    
    print("\nTo run an update manually: python scripts/auto_update.py")
    print("To set up or modify the scheduler: python scripts/setup_scheduler.py")

if __name__ == "__main__":
    main() 