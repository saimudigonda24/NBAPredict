import pytest
from unittest.mock import patch, Mock
from datetime import datetime
from services.nba_api import NBAApiService

@pytest.fixture
def nba_api():
    return NBAApiService()

@pytest.fixture
def mock_teams_response():
    return {
        'resultSets': [{
            'rowSet': [
                [1, 'Los Angeles Lakers', 'LAL', 30, 20, 0.6],
                [2, 'Boston Celtics', 'BOS', 35, 15, 0.7]
            ]
        }]
    }

@pytest.fixture
def mock_game_response():
    return {
        'resultSets': [{
            'rowSet': [[
                '2024-03-20',  # date
                '19:30',       # time
                'BOS',         # away team abbr
                '2',           # away team id
                'Boston Celtics', # away team name
                'BOS',         # away team abbr
                '1',           # home team id
                'Los Angeles Lakers', # home team name
                'LAL'          # home team abbr
            ]]
        }]
    }

@pytest.fixture
def mock_team_stats_response():
    return {
        'resultSets': [{
            'rowSet': [[
                1,  # team id
                5,  # win streak
                0.7, # last 10 games
                115.5, # points per game
                0.48, # field goal percentage
                0.38, # three point percentage
                0.82, # free throw percentage
                25.5, # assists per game
                45.2  # rebounds per game
            ]]
        }]
    }

def test_get_teams(nba_api, mock_teams_response):
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_teams_response
        mock_get.return_value.raise_for_status = Mock()
        
        teams = nba_api._get_teams()
        
        assert len(teams) == 2
        assert teams[0]['id'] == 1
        assert teams[0]['name'] == 'Los Angeles Lakers'
        assert teams[0]['abbreviation'] == 'LAL'
        assert teams[0]['wins'] == 30
        assert teams[0]['losses'] == 20
        assert teams[0]['win_percentage'] == 0.6

def test_get_next_game(nba_api, mock_game_response):
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_game_response
        mock_get.return_value.raise_for_status = Mock()
        
        next_game = nba_api.get_next_game()
        
        assert next_game is not None
        assert next_game['homeTeam']['id'] == 1
        assert next_game['homeTeam']['name'] == 'Los Angeles Lakers'
        assert next_game['awayTeam']['id'] == 2
        assert next_game['awayTeam']['name'] == 'Boston Celtics'
        assert next_game['date'] == '2024-03-20'
        assert next_game['time'] == '19:30'

def test_get_team_stats(nba_api, mock_team_stats_response):
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_team_stats_response
        mock_get.return_value.raise_for_status = Mock()
        
        stats = nba_api.get_team_stats(1)
        
        assert stats is not None
        assert stats['teamId'] == 1
        assert stats['pointsPerGame'] == 115.5
        assert stats['fieldGoalPercentage'] == 0.48
        assert stats['threePointPercentage'] == 0.38
        assert stats['freeThrowPercentage'] == 0.82
        assert stats['assistsPerGame'] == 25.5
        assert stats['reboundsPerGame'] == 45.2
        assert stats['winStreak'] == 5
        assert stats['lastTenGames'] == 0.7

def test_cache_mechanism(nba_api, mock_teams_response):
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = mock_teams_response
        mock_get.return_value.raise_for_status = Mock()
        
        # First call should make API request
        teams1 = nba_api._get_teams()
        assert mock_get.call_count == 1
        
        # Second call should use cache
        teams2 = nba_api._get_teams()
        assert mock_get.call_count == 1  # No additional API call
        
        assert teams1 == teams2  # Same data returned

def test_error_handling(nba_api):
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("API Error")
        
        # Test error handling in get_teams
        teams = nba_api._get_teams()
        assert teams == []
        
        # Test error handling in get_next_game
        next_game = nba_api.get_next_game()
        assert next_game is None
        
        # Test error handling in get_team_stats
        stats = nba_api.get_team_stats(1)
        assert stats is None 