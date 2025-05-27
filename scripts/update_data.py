import os
import sys
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
import logging
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.data_collector import NBADataCollector

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fetch_team_rosters():
    """Fetch the latest team rosters from NBA API"""
    print("Fetching current NBA team rosters...")
    
    # NBA Stats API endpoints
    base_url = "https://stats.nba.com/stats/"
    teams_endpoint = "leaguedashteamstats"
    roster_endpoint = "commonteamroster"
    
    # Headers to mimic browser request (required for NBA API)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.nba.com/',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
    }
    
    # Get current season
    current_year = datetime.now().year
    current_month = datetime.now().month
    season = f"{current_year-1}-{str(current_year)[2:]}" if current_month < 10 else f"{current_year}-{str(current_year+1)[2:]}"
    
    # Get all teams
    teams_params = {
        'MeasureType': 'Base',
        'PerMode': 'PerGame',
        'PlusMinus': 'N',
        'PaceAdjust': 'N',
        'Rank': 'N',
        'Season': season,
        'SeasonType': 'Playoffs' if datetime.now().month in [4, 5, 6] else 'Regular Season',
        'PORound': 0,
        'Outcome': '',
        'Location': '',
        'Month': 0,
        'SeasonSegment': '',
        'DateFrom': '',
        'DateTo': '',
        'OpponentTeamID': 0,
        'VsConference': '',
        'VsDivision': '',
        'GameSegment': '',
        'Period': 0,
        'LastNGames': 0,
    }
    
    teams_data = {}
    
    try:
        # Get teams
        response = requests.get(
            base_url + teams_endpoint,
            headers=headers,
            params=teams_params
        )
        response.raise_for_status()
        
        teams_json = response.json()
        teams_headers = teams_json['resultSets'][0]['headers']
        teams_data_raw = teams_json['resultSets'][0]['rowSet']
        
        team_id_index = teams_headers.index('TEAM_ID')
        team_name_index = teams_headers.index('TEAM_NAME')
        team_abbr_index = teams_headers.index('TEAM_ABBREVIATION')
        
        # Process teams data
        for team in teams_data_raw:
            team_id = team[team_id_index]
            team_name = team[team_name_index]
            team_abbr = team[team_abbr_index]
            
            teams_data[team_id] = {
                'team_id': team_id,
                'name': team_name,
                'abbreviation': team_abbr,
                'roster': []
            }
            
            # Delay to avoid rate limiting
            time.sleep(1)
            
            # Get roster for this team
            try:
                roster_params = {
                    'TeamID': team_id,
                    'Season': season
                }
                
                roster_response = requests.get(
                    base_url + roster_endpoint,
                    headers=headers,
                    params=roster_params
                )
                roster_response.raise_for_status()
                
                roster_json = roster_response.json()
                roster_headers = roster_json['resultSets'][0]['headers']
                roster_data_raw = roster_json['resultSets'][0]['rowSet']
                
                player_id_index = roster_headers.index('PLAYER_ID')
                player_name_index = roster_headers.index('PLAYER')
                player_pos_index = roster_headers.index('POSITION')
                
                # Process roster data
                for player in roster_data_raw:
                    teams_data[team_id]['roster'].append({
                        'player_id': player[player_id_index],
                        'name': player[player_name_index],
                        'position': player[player_pos_index]
                    })
                
                logger.info(f"Added {len(teams_data[team_id]['roster'])} players for {team_abbr}")
                
            except Exception as e:
                logger.error(f"Error fetching roster for {team_name}: {str(e)}")
        
        # Save roster data
        os.makedirs('data/rosters', exist_ok=True)
        today = datetime.now().strftime('%Y%m%d')
        with open(f'data/rosters/team_rosters_{today}.json', 'w') as f:
            json.dump(teams_data, f, indent=4)
        
        logger.info(f"Team rosters saved to data/rosters/team_rosters_{today}.json")
        
        return teams_data
        
    except Exception as e:
        logger.error(f"Error fetching team data: {str(e)}")
        return None

def update_training_data():
    """Update the training data with the latest games"""
    print("Updating training data with the latest games...")
    
    try:
        # Initialize data collector
        data_collector = NBADataCollector()
        
        # Collect new data
        training_data = data_collector.collect_training_data()
        
        if training_data is not None:
            today = datetime.now().strftime('%Y%m%d')
            training_data.to_csv(f'data/training_data_{today}.csv', index=False)
            
            # Also update the main training data file
            training_data.to_csv('data/training_data_latest.csv', index=False)
            
            logger.info(f"Training data updated with {len(training_data)} games")
            print(f"Successfully updated training data with {len(training_data)} games")
        else:
            logger.error("Failed to update training data")
            print("Failed to update training data. Check the logs for details.")
    
    except Exception as e:
        logger.error(f"Error updating training data: {str(e)}")
        print(f"Error updating training data: {str(e)}")

def main():
    """Update both team rosters and game data"""
    print("======== NBA Data Update ========")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("================================")
    
    # Fetch team rosters
    teams_data = fetch_team_rosters()
    
    # Update training data
    update_training_data()
    
    print("\nUpdate complete!")
    print("================================")

if __name__ == "__main__":
    main() 