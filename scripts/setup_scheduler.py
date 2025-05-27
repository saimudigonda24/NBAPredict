#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import argparse
from datetime import datetime

def get_absolute_path(relative_path):
    """Convert relative path to absolute path"""
    return os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), relative_path))

def setup_cron_job(frequency, retrain=False):
    """Set up a cron job for automatic updates"""
    # Get the absolute paths
    script_path = get_absolute_path("scripts/auto_update.py")
    python_path = sys.executable
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_path = get_absolute_path("logs/cron_update.log")
    
    # Build the command
    retrain_flag = "--retrain" if retrain else ""
    command = f"cd {project_path} && {python_path} {script_path} {retrain_flag} >> {log_path} 2>&1"
    
    # Determine cron schedule based on frequency
    if frequency == "daily":
        # Run at 3:00 AM every day
        schedule = "0 3 * * *"
    elif frequency == "weekly":
        # Run at 3:00 AM every Monday
        schedule = "0 3 * * 1"
    elif frequency == "gameday":
        # Run at 10:00 AM and 11:00 PM (before and after games) every day
        # Note: This creates two cron jobs
        schedule1 = "0 10 * * *"
        schedule2 = "0 23 * * *"
        add_cron_job(schedule1, command)
        schedule = schedule2
    else:
        raise ValueError(f"Unknown frequency: {frequency}")
    
    # Add the cron job
    add_cron_job(schedule, command)
    
    print(f"Cron job set up to run {frequency}")
    print(f"Command: {command}")
    print(f"Schedule: {schedule}")

def add_cron_job(schedule, command):
    """Add a cron job to the system"""
    # Get existing crontab
    try:
        existing_crontab = subprocess.check_output("crontab -l", shell=True, text=True)
    except subprocess.CalledProcessError:
        # No existing crontab
        existing_crontab = ""
    
    # Check if job already exists
    if command in existing_crontab:
        print("Cron job already exists. Skipping.")
        return
    
    # Add new job
    new_crontab = existing_crontab.strip() + f"\n{schedule} {command}\n"
    
    # Write to temporary file
    temp_file = "/tmp/nba_predict_crontab"
    with open(temp_file, "w") as f:
        f.write(new_crontab)
    
    # Install new crontab
    subprocess.run(f"crontab {temp_file}", shell=True, check=True)
    
    # Clean up
    os.unlink(temp_file)

def setup_launchd_job(frequency, retrain=False):
    """Set up a launchd job for automatic updates on macOS"""
    # Get the absolute paths
    script_path = get_absolute_path("scripts/auto_update.py")
    python_path = sys.executable
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_path = get_absolute_path("logs/launchd_update.log")
    
    # Build the command
    retrain_flag = "--retrain" if retrain else ""
    
    # Create plist file
    plist_name = "com.nba.predict.autoupdate"
    plist_path = os.path.expanduser(f"~/Library/LaunchAgents/{plist_name}.plist")
    
    # Determine schedule based on frequency
    if frequency == "daily":
        # Run at 3:00 AM every day
        hour = 3
        minute = 0
    elif frequency == "weekly":
        # Run at 3:00 AM every Monday
        hour = 3
        minute = 0
        weekday = 1
    elif frequency == "gameday":
        # Run at 10:00 AM and 11:00 PM (before and after games) every day
        # For simplicity, we'll just do 11:00 PM in this example
        hour = 23
        minute = 0
    else:
        raise ValueError(f"Unknown frequency: {frequency}")
    
    # Create plist content
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{plist_name}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{script_path}</string>
        {"<string>--retrain</string>" if retrain else ""}
    </array>
    <key>WorkingDirectory</key>
    <string>{project_path}</string>
    <key>StandardOutPath</key>
    <string>{log_path}</string>
    <key>StandardErrorPath</key>
    <string>{log_path}</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>{hour}</integer>
        <key>Minute</key>
        <integer>{minute}</integer>
        {"<key>Weekday</key><integer>" + str(weekday) + "</integer>" if frequency == "weekly" else ""}
    </dict>
</dict>
</plist>
"""
    
    # Write plist file
    with open(plist_path, "w") as f:
        f.write(plist_content)
    
    # Load the job
    subprocess.run(f"launchctl load {plist_path}", shell=True, check=True)
    
    print(f"LaunchAgent set up to run {frequency}")
    print(f"Plist file: {plist_path}")

def setup_windows_task(frequency, retrain=False):
    """Set up a scheduled task on Windows"""
    # Get the absolute paths
    script_path = get_absolute_path("scripts/auto_update.py")
    python_path = sys.executable
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Build the command
    retrain_flag = "--retrain" if retrain else ""
    command = f'"{python_path}" "{script_path}" {retrain_flag}'
    
    # Determine schedule based on frequency
    if frequency == "daily":
        # Run at 3:00 AM every day
        schedule = "/SC DAILY /TN NBA_Predict_Update /TR"
        time = "/ST 03:00"
    elif frequency == "weekly":
        # Run at 3:00 AM every Monday
        schedule = "/SC WEEKLY /D MON /TN NBA_Predict_Update /TR"
        time = "/ST 03:00"
    elif frequency == "gameday":
        # Run at 10:00 AM and 11:00 PM (before and after games) every day
        # For simplicity, we'll just do 11:00 PM in this example
        schedule = "/SC DAILY /TN NBA_Predict_Update /TR"
        time = "/ST 23:00"
    else:
        raise ValueError(f"Unknown frequency: {frequency}")
    
    # Create batch file to run the command
    batch_path = os.path.join(project_path, "scripts", "run_update.bat")
    with open(batch_path, "w") as f:
        f.write(f"cd /d {project_path}\n")
        f.write(f"{command}\n")
    
    # Set up the task
    task_command = f'schtasks /Create {schedule} "{batch_path}" {time} /F'
    
    try:
        subprocess.run(task_command, shell=True, check=True)
        print(f"Windows Task Scheduler job set up to run {frequency}")
        print(f"Command: {command}")
    except subprocess.CalledProcessError as e:
        print(f"Error setting up Windows task: {e}")
        print("You may need to run this script as administrator.")

def main():
    parser = argparse.ArgumentParser(description='Set up automatic scheduling for NBA data updates')
    parser.add_argument('--frequency', choices=['daily', 'weekly', 'gameday'], default='daily',
                        help='How often to run the updates (default: daily)')
    parser.add_argument('--retrain', action='store_true', 
                        help='Retrain the model after each update')
    args = parser.parse_args()
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs"), exist_ok=True)
    
    # Detect operating system
    system = platform.system()
    
    print(f"Setting up automatic updates to run {args.frequency}")
    print(f"Retrain model: {args.retrain}")
    
    if system == "Darwin":  # macOS
        print("Detected macOS. Setting up LaunchAgent...")
        setup_launchd_job(args.frequency, args.retrain)
    elif system == "Linux":
        print("Detected Linux. Setting up cron job...")
        setup_cron_job(args.frequency, args.retrain)
    elif system == "Windows":
        print("Detected Windows. Setting up scheduled task...")
        setup_windows_task(args.frequency, args.retrain)
    else:
        print(f"Unsupported operating system: {system}")
        print("Please set up scheduling manually.")
    
    print("\nSetup complete!")
    print("To run an update immediately, use: python scripts/auto_update.py")

if __name__ == "__main__":
    main() 