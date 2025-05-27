from nba_api.stats.endpoints import leaguegamefinder, commonplayerinfo, playergamelog, scoreboardv2
from nba_api.stats.static import teams, players
import pandas as pd
import time
from datetime import datetime
import logging
import random
import requests
from typing import List

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NBADataFetcher:
    def __init__(self):
        """Initialize the NBA data fetcher"""
        self.teams = teams.get_teams()
        self.team_dict = {team['id']: team['full_name'] for team in self.teams}
        
    def fetch_team_games(self, team_id, season=None, max_retries=3):
        """Fetch games for a specific team with retries"""
        for attempt in range(max_retries):
            try:
                # Format season string correctly if needed (e.g., "2024-25" to "2024-25")
                formatted_season = self._format_season_string(season)
                logger.info(f"Using season format: {formatted_season} for API call")
                
                gamefinder = leaguegamefinder.LeagueGameFinder(
                    team_id_nullable=team_id,
                    season_nullable=formatted_season
                )
                games_df = gamefinder.get_data_frames()[0]
                # Random delay between 1.5 and 3 seconds to avoid rate limiting
                time.sleep(random.uniform(1.5, 3.0))
                return games_df
            except requests.exceptions.RequestException as e:
                logger.error(f"Network error fetching team games (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    # Exponential backoff
                    time.sleep((attempt + 1) * 2)
                    continue
                return pd.DataFrame()
            except Exception as e:
                logger.error(f"Error fetching team games (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    # Exponential backoff
                    time.sleep((attempt + 1) * 2)
                    continue
                return pd.DataFrame()

    def _format_season_string(self, season):
        """Format season string correctly for NBA API"""
        if not season:
            return None
            
        # If season is already in correct format, return it
        if isinstance(season, str) and len(season) == 7 and "-" in season:
            return season
            
        # Try to handle different formats
        try:
            if isinstance(season, str) and season.isdigit() and len(season) == 4:
                # Convert single year (e.g., "2024") to "2024-25"
                year = int(season)
                return f"{year}-{str(year+1)[2:]}"
            elif isinstance(season, int):
                # Convert integer year to string format
                return f"{season}-{str(season+1)[2:]}"
        except Exception as e:
            logger.warning(f"Could not format season string: {season}. Error: {str(e)}")
            
        # Return original if we couldn't format it
        return season

    def fetch_player_info(self, player_id, max_retries=3):
        """Fetch detailed player information with retries"""
        for attempt in range(max_retries):
            try:
                player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
                info_df = player_info.get_data_frames()[0]
                time.sleep(random.uniform(1.5, 3.0))
                return info_df
            except requests.exceptions.RequestException as e:
                logger.error(f"Network error fetching player info (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep((attempt + 1) * 2)
                    continue
                return pd.DataFrame()
            except Exception as e:
                logger.error(f"Error fetching player info (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep((attempt + 1) * 2)
                    continue
                return pd.DataFrame()

    def fetch_player_games(self, player_id, season=None, max_retries=3):
        """Fetch game logs for a specific player with retries"""
        for attempt in range(max_retries):
            try:
                # Format season string correctly
                formatted_season = self._format_season_string(season)
                
                game_logs = playergamelog.PlayerGameLog(
                    player_id=player_id,
                    season=formatted_season
                )
                logs_df = game_logs.get_data_frames()[0]
                time.sleep(random.uniform(1.5, 3.0))
                return logs_df
            except requests.exceptions.RequestException as e:
                logger.error(f"Network error fetching player games (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep((attempt + 1) * 2)
                    continue
                return pd.DataFrame()
            except Exception as e:
                logger.error(f"Error fetching player games (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep((attempt + 1) * 2)
                    continue
                return pd.DataFrame()

    def fetch_all_team_games(self, season=None):
        """Fetch games for all teams with better error handling"""
        all_games = pd.DataFrame()
        
        # Format season string correctly
        formatted_season = self._format_season_string(season)
        logger.info(f"Fetching games for season: {formatted_season}")
        
        for team in self.teams:
            try:
                logger.info(f"Fetching games for {team['full_name']}")
                team_games = self.fetch_team_games(team['id'], formatted_season)
                
                if team_games.empty:
                    logger.warning(f"No games found for {team['full_name']}")
                    continue
                    
                all_games = pd.concat([all_games, team_games], ignore_index=True)
                logger.info(f"Successfully fetched {len(team_games)} games for {team['full_name']}")
                
            except Exception as e:
                logger.error(f"Error processing games for {team['full_name']}: {str(e)}")
                continue
                
        # Remove duplicate games (since each game appears twice, once for each team)
        if not all_games.empty and 'GAME_ID' in all_games.columns:
            logger.info(f"Total games fetched before removing duplicates: {len(all_games)}")
            all_games = all_games.drop_duplicates(subset=['GAME_ID'], keep='first')
            logger.info(f"Total games after removing duplicates: {len(all_games)}")
            
        return all_games

    def save_data(self, data, filename):
        """Save data to CSV file with error handling"""
        try:
            if data.empty:
                logger.warning(f"No data to save for {filename}")
                return
                
            output_path = f'data/{filename}_{datetime.now().strftime("%Y%m%d")}.csv'
            data.to_csv(output_path, index=False)
            logger.info(f"Data saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving data: {str(e)}")

def main():
    fetcher = NBADataFetcher()
    
    try:
        # Fetch and save team games
        current_season = "2024-25"
        logger.info(f"Starting data fetch for season {current_season}")
        
        all_games = fetcher.fetch_all_team_games(season=current_season)
        
        if not all_games.empty:
            fetcher.save_data(all_games, 'team_games')
            logger.info(f"Successfully processed {len(all_games)} total games")
        else:
            logger.error("No games data was collected")
            
    except Exception as e:
        logger.error(f"Fatal error in main execution: {str(e)}")
        
    logger.info("Data fetching completed")

if __name__ == "__main__":
    main() 