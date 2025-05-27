import requests
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class NBAApiService:
    BASE_URL = "https://stats.nba.com/stats"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://www.nba.com/',
    }

    def __init__(self):
        self.teams_cache = None
        self.schedule_cache = None
        self.last_cache_update = None
        self.cache_duration = timedelta(minutes=30)

    def _get_teams(self) -> List[Dict]:
        """Get all NBA teams"""
        if self.teams_cache and self.last_cache_update and datetime.now() - self.last_cache_update < self.cache_duration:
            return self.teams_cache

        try:
            response = requests.get(
                f"{self.BASE_URL}/leaguestandingsv3",
                headers=self.HEADERS
            )
            response.raise_for_status()
            data = response.json()
            
            teams = []
            for team in data['resultSets'][0]['rowSet']:
                teams.append({
                    'id': team[0],
                    'name': team[1],
                    'abbreviation': team[2],
                    'wins': team[3],
                    'losses': team[4],
                    'win_percentage': team[5],
                })
            
            self.teams_cache = teams
            self.last_cache_update = datetime.now()
            return teams
        except Exception as e:
            logger.error(f"Error fetching teams: {str(e)}")
            return []

    def get_next_game(self) -> Optional[Dict]:
        """Get the next scheduled NBA game"""
        if self.schedule_cache and self.last_cache_update and datetime.now() - self.last_cache_update < self.cache_duration:
            return self.schedule_cache

        try:
            # Get today's date in YYYY-MM-DD format
            today = datetime.now().strftime('%Y-%m-%d')
            
            response = requests.get(
                f"{self.BASE_URL}/scoreboardv2",
                params={
                    'DayOffset': '0',
                    'LeagueID': '00',
                    'gameDate': today
                },
                headers=self.HEADERS
            )
            response.raise_for_status()
            data = response.json()
            
            if not data['resultSets'][0]['rowSet']:
                # If no games today, get tomorrow's games
                tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
                response = requests.get(
                    f"{self.BASE_URL}/scoreboardv2",
                    params={
                        'DayOffset': '1',
                        'LeagueID': '00',
                        'gameDate': tomorrow
                    },
                    headers=self.HEADERS
                )
                response.raise_for_status()
                data = response.json()

            if data['resultSets'][0]['rowSet']:
                game = data['resultSets'][0]['rowSet'][0]
                next_game = {
                    'homeTeam': {
                        'id': game[6],
                        'name': game[7],
                        'abbreviation': game[8]
                    },
                    'awayTeam': {
                        'id': game[3],
                        'name': game[4],
                        'abbreviation': game[5]
                    },
                    'date': game[0],
                    'time': game[1]
                }
                self.schedule_cache = next_game
                self.last_cache_update = datetime.now()
                return next_game
            
            return None
        except Exception as e:
            logger.error(f"Error fetching next game: {str(e)}")
            return None

    def get_team_stats(self, team_id: int) -> Optional[Dict]:
        """Get current season stats for a team"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/teamdashboardbygeneralsplits",
                params={
                    'TeamID': team_id,
                    'Season': '2023-24',
                    'SeasonType': 'Regular Season',
                    'MeasureType': 'Base'
                },
                headers=self.HEADERS
            )
            response.raise_for_status()
            data = response.json()
            
            if data['resultSets'][0]['rowSet']:
                stats = data['resultSets'][0]['rowSet'][0]
                return {
                    'teamId': team_id,
                    'pointsPerGame': stats[3],
                    'fieldGoalPercentage': stats[4],
                    'threePointPercentage': stats[6],
                    'freeThrowPercentage': stats[8],
                    'assistsPerGame': stats[15],
                    'reboundsPerGame': stats[13],
                    'winStreak': stats[1],
                    'lastTenGames': stats[2]
                }
            return None
        except Exception as e:
            logger.error(f"Error fetching team stats: {str(e)}")
            return None 