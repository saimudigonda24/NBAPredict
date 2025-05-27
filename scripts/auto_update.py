import os
import sys
import pandas as pd
from datetime import datetime, timedelta
import logging
import time
import argparse

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nba_api.stats.endpoints import leaguegamefinder
from models.match_predictor import NBAMatchPredictor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auto_update.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutoUpdater:
    def __init__(self, data_dir='data', retrain=False):
        """Initialize the auto updater"""
        self.data_dir = data_dir
        self.retrain = retrain
        self.current_season = "2024-25"  # Hardcoded to 2024-25 season
        logger.info(f"Using hardcoded season: {self.current_season}")
        
        # Create necessary directories
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs('logs', exist_ok=True)
    
    def _get_latest_data_file(self):
        """Find the most recent data file"""
        data_files = [f for f in os.listdir(self.data_dir) 
                      if f.startswith('team_games_') and f.endswith('.csv')]
        
        if not data_files:
            logger.info("No existing data files found. Will fetch all games.")
            return None
            
        latest_file = max(data_files)
        return os.path.join(self.data_dir, latest_file)
    
    def _get_last_update_date(self):
        """Get the date of the most recent game in the dataset"""
        latest_file = self._get_latest_data_file()
        
        if latest_file is None:
            # If no existing file, use a date from the beginning of the season
            # October 1st of the current season's starting year
            return "2024-10-01"  # Start of 2024-25 season
        
        try:
            df = pd.read_csv(latest_file)
            if 'GAME_DATE' in df.columns and not df.empty:
                return df['GAME_DATE'].max()
            else:
                logger.warning("No game date column found or empty dataset")
                return None
        except Exception as e:
            logger.error(f"Error reading latest data file: {str(e)}")
            return None
    
    def fetch_all_games(self, season="2024-25", max_retries=3):
        """Fetch all games for a season directly using leaguegamefinder"""
        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching all games for season {season}, attempt {attempt+1}/{max_retries}")
                gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable=season)
                games_df = gamefinder.get_data_frames()[0]
                
                if games_df.empty:
                    logger.warning(f"No games found for season {season}")
                    if attempt < max_retries - 1:
                        time.sleep((attempt + 1) * 2)
                        continue
                    return pd.DataFrame()
                
                logger.info(f"Successfully fetched {len(games_df)} games")
                
                # Remove duplicate games (since each game appears twice, once for each team)
                if 'GAME_ID' in games_df.columns:
                    logger.info(f"Total games before removing duplicates: {len(games_df)}")
                    games_df = games_df.drop_duplicates(subset=['GAME_ID'], keep='first')
                    logger.info(f"Total games after removing duplicates: {len(games_df)}")
                
                return games_df
                
            except Exception as e:
                logger.error(f"Error fetching games (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    # Exponential backoff
                    time.sleep((attempt + 1) * 2)
                    continue
                return pd.DataFrame()
    
    def update_data(self):
        """Update the dataset with new games"""
        last_update = self._get_last_update_date()
        
        if last_update is None:
            logger.info("Fetching all games for the current season")
            logger.info(f"Using season: {self.current_season}")
            all_games = self.fetch_all_games(season=self.current_season)
        else:
            logger.info(f"Fetching games since {last_update}")
            # Convert to datetime for comparison
            last_update_date = pd.to_datetime(last_update)
            
            logger.info(f"Using season: {self.current_season}")
            all_games = self.fetch_all_games(season=self.current_season)
            
            # Filter for new games only if we have data
            if not all_games.empty and 'GAME_DATE' in all_games.columns:
                logger.info(f"Total games fetched: {len(all_games)}")
                all_games['GAME_DATE'] = pd.to_datetime(all_games['GAME_DATE'])
                new_games = all_games[all_games['GAME_DATE'] > last_update_date]
                
                # Convert back to string format
                all_games['GAME_DATE'] = all_games['GAME_DATE'].dt.strftime('%Y-%m-%d')
                
                if len(new_games) == 0:
                    logger.info("No new games found since last update")
                    logger.info("This could be due to the NBA API not having updated data yet.")
                    logger.info("Try again later or check the NBA API status.")
                    return False
                
                logger.info(f"Found {len(new_games)} new games")
                
                # Merge with existing data if available
                latest_file = self._get_latest_data_file()
                if latest_file is not None:
                    try:
                        existing_data = pd.read_csv(latest_file)
                        logger.info(f"Existing data has {len(existing_data)} games")
                        # Convert to datetime for comparison
                        existing_data['GAME_DATE'] = pd.to_datetime(existing_data['GAME_DATE'])
                        # Filter out any potential duplicates
                        existing_data = existing_data[existing_data['GAME_DATE'] <= last_update_date]
                        logger.info(f"After filtering, existing data has {len(existing_data)} games")
                        # Convert back to string format
                        existing_data['GAME_DATE'] = existing_data['GAME_DATE'].dt.strftime('%Y-%m-%d')
                        
                        # Combine existing and new data
                        all_games = pd.concat([existing_data, new_games], ignore_index=True)
                        logger.info(f"Combined dataset now has {len(all_games)} games")
                    except Exception as e:
                        logger.error(f"Error merging with existing data: {str(e)}")
        
        # Save the updated dataset
        if not all_games.empty:
            today = datetime.now().strftime("%Y%m%d")
            output_path = f'{self.data_dir}/team_games_{today}.csv'
            all_games.to_csv(output_path, index=False)
            
            # Also save as latest for easy reference
            latest_path = f'{self.data_dir}/team_games_latest.csv'
            all_games.to_csv(latest_path, index=False)
            
            logger.info(f"Saved updated dataset with {len(all_games)} games to {output_path}")
            return True
        else:
            logger.warning("No games data was collected")
            logger.warning("This could be due to the NBA API not having updated data or an issue with the API connection.")
            logger.warning("Please check your internet connection and try again later.")
            
            # For debugging, let's check what teams are available
            try:
                from nba_api.stats.static import teams
                all_teams = teams.get_teams()
                logger.info(f"NBA API reports {len(all_teams)} teams available")
                for team in all_teams[:5]:  # Print first 5 teams for debugging
                    logger.info(f"Team: {team['full_name']} (ID: {team['id']})")
            except Exception as e:
                logger.error(f"Error fetching teams list: {str(e)}")
            
            return False
    
    def retrain_model(self):
        """Retrain the model with the updated dataset"""
        if not self.retrain:
            logger.info("Model retraining skipped (not requested)")
            return
            
        latest_path = f'{self.data_dir}/team_games_latest.csv'
        if not os.path.exists(latest_path):
            logger.error("Cannot retrain model: No data file found")
            return
            
        try:
            logger.info("Loading latest data for model retraining")
            games_df = pd.read_csv(latest_path)
            
            logger.info("Initializing model")
            predictor = NBAMatchPredictor()
            
            logger.info(f"Starting model training with {len(games_df)} games")
            predictor.train(games_df)
            
            # Save the model with timestamp
            today = datetime.now().strftime("%Y%m%d")
            predictor.save_model(f'models/match_predictor_{today}')
            
            # Also save as the default model
            predictor.save_model('models/match_predictor_with_overtime')
            
            logger.info("Model retraining completed and saved")
        except Exception as e:
            logger.error(f"Error retraining model: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Auto-update NBA game data and optionally retrain the model')
    parser.add_argument('--retrain', action='store_true', help='Retrain the model after updating data')
    parser.add_argument('--force', action='store_true', help='Force update even if no new games are found')
    args = parser.parse_args()
    
    try:
        logger.info("Starting auto-update process")
        updater = AutoUpdater(retrain=args.retrain)
        
        # Update the dataset
        success = updater.update_data()
        
        # Retrain the model if requested and update was successful or force flag is set
        if (success or args.force) and args.retrain:
            updater.retrain_model()
            
        logger.info("Auto-update process completed")
        
    except Exception as e:
        logger.error(f"Error in auto-update process: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main() 