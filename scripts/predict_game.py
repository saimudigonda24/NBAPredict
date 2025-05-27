import os
import sys
import pandas as pd
import numpy as np
import logging
import json
from datetime import datetime
import glob

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.match_predictor import NBAMatchPredictor

# Add color codes for terminal output
BLUE = '\033[94m'
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
END = '\033[0m'

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_latest_data_file(data_dir='data', prefix='training_data_'):
    """Get the most recent data file"""
    files = glob.glob(f"{data_dir}/{prefix}*.csv")
    if not files:
        return f"{data_dir}/{prefix}latest.csv"
    return max(files, key=os.path.getctime)

def get_latest_roster_file(roster_dir='data/rosters', prefix='team_rosters_'):
    """Get the most recent roster file"""
    files = glob.glob(f"{roster_dir}/{prefix}*.json")
    if not files:
        return None
    return max(files, key=os.path.getctime)

def get_roster_info(team_abbrev):
    """Get current roster information for a team"""
    roster_file = get_latest_roster_file()
    if not roster_file:
        logger.warning(f"No roster files found. Unable to display roster for {team_abbrev}")
        return None
    
    try:
        with open(roster_file, 'r') as f:
            rosters = json.load(f)
        
        # Find team by abbreviation
        team_data = None
        for team_id, team_info in rosters.items():
            if team_info['abbreviation'] == team_abbrev:
                team_data = team_info
                break
        
        if team_data is None:
            logger.warning(f"Team {team_abbrev} not found in roster data")
            return None
        
        return team_data
        
    except Exception as e:
        logger.error(f"Error loading roster data: {str(e)}")
        return None

def get_team_stats(df, team_abbrev, num_games=5):
    """Get the latest stats for a team from the last N games"""
    team_games = df[df['TEAM_ABBREVIATION'] == team_abbrev].sort_values('GAME_DATE', ascending=False).head(num_games)
    
    if team_games.empty:
        logger.error(f"No data found for team {team_abbrev}")
        return None
    
    latest_game = team_games.iloc[0]
    
    # Calculate stats from recent games
    stats = {
        'PTS_ROLLING_AVG_5': team_games['PTS'].mean(),
        'FG_PCT_ROLLING_AVG_5': team_games['FG_PCT'].mean(),
        'FT_PCT_ROLLING_AVG_5': team_games['FT_PCT'].mean(),
        'FG3_PCT_ROLLING_AVG_5': team_games['FG3_PCT'].mean(),
        'AST_ROLLING_AVG_5': team_games['AST'].mean(),
        'REB_ROLLING_AVG_5': team_games['REB'].mean(),
        'FTA_ROLLING_AVG_5': team_games['FTA'].mean(),
        'TOV_ROLLING_AVG_5': team_games['TOV'].mean(),
        'STL_ROLLING_AVG_5': team_games['STL'].mean()
    }
    
    # Calculate FT drawing rate
    ft_drawing_rates = []
    for _, game in team_games.iterrows():
        if game['FGA'] > 0:
            ft_drawing_rates.append(game['FTA'] / game['FGA'])
        else:
            ft_drawing_rates.append(0)
    
    stats['FT_DRAWING_RATE_ROLLING_AVG_5'] = np.mean(ft_drawing_rates)
    
    # Win streak (count of wins in last 5 games)
    stats['WIN_STREAK'] = team_games['WL'].apply(lambda x: 1 if x == 'W' else 0).sum()
    
    # Team ID
    stats['TEAM_ID'] = latest_game['TEAM_ID']
    
    # Latest game date
    stats['LATEST_GAME_DATE'] = latest_game['GAME_DATE']
    
    return stats

def print_team_roster(team_data):
    """Print team roster in a formatted table"""
    if team_data is None:
        return
    
    team_name = team_data['name']
    team_abbr = team_data['abbreviation']
    roster = team_data['roster']
    
    print(f"\n{BOLD}{team_name} ({team_abbr}) Current Roster{END}")
    print("-" * 50)
    print(f"{BOLD}{'Player Name':<30} {'Position':<10}{END}")
    print("-" * 50)
    
    for player in roster:
        print(f"{player['name']:<30} {player['position']:<10}")

def predict_game(home_team_abbr, away_team_abbr):
    """Predict the outcome of a game between two teams"""
    print(f"{BOLD}NBA Game Prediction: {away_team_abbr} vs {home_team_abbr} (Home){END}")
    print("=" * 60)
    
    try:
        # Load the latest training data
        data_file = get_latest_data_file()
        print(f"Loading data from: {os.path.basename(data_file)}...")
        df = pd.read_csv(data_file)
        print(f"Loaded {len(df)} game records through {df['GAME_DATE'].max()}")
        
        # Load the trained model
        print("Loading model...")
        predictor = NBAMatchPredictor()
        try:
            predictor.load_model('models/match_predictor_model.h5')
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            print("Error loading pre-trained model. Please train the model first.")
            return
        
        # Get team stats
        print("\nGetting team stats...")
        home_stats = get_team_stats(df, home_team_abbr)
        away_stats = get_team_stats(df, away_team_abbr)
        
        if home_stats is None or away_stats is None:
            print("Could not get stats for one or both teams")
            return
        
        # Get team rosters
        home_roster = get_roster_info(home_team_abbr)
        away_roster = get_roster_info(away_team_abbr)
        
        # Make prediction
        print("\nMaking prediction...")
        home_win_prob = predictor.predict_match(
            home_stats['TEAM_ID'], 
            away_stats['TEAM_ID'],
            home_stats,
            away_stats
        )
        
        # Print results
        print(f"\n{BOLD}============ PREDICTION RESULTS ============{END}")
        print(f"Home Team ({home_team_abbr}) win probability: {GREEN if home_win_prob > 0.5 else RED}{home_win_prob:.2%}{END}")
        print(f"Away Team ({away_team_abbr}) win probability: {GREEN if home_win_prob < 0.5 else RED}{(1-home_win_prob):.2%}{END}")
        
        print(f"\n{BOLD}============ TEAM STATS ============{END}")
        print(f"{home_team_abbr} scoring:  {home_stats['PTS_ROLLING_AVG_5']:.1f} PPG, {home_stats['FG_PCT_ROLLING_AVG_5']:.3f} FG%, {home_stats['FG3_PCT_ROLLING_AVG_5']:.3f} 3PT%")
        print(f"{away_team_abbr} scoring:  {away_stats['PTS_ROLLING_AVG_5']:.1f} PPG, {away_stats['FG_PCT_ROLLING_AVG_5']:.3f} FG%, {away_stats['FG3_PCT_ROLLING_AVG_5']:.3f} 3PT%")
        
        print(f"\n{BOLD}Free Throw Analysis:{END}")
        print(f"{home_team_abbr} FT stats: {home_stats['FTA_ROLLING_AVG_5']:.1f} FTA, {home_stats['FT_PCT_ROLLING_AVG_5']:.3f} FT%, {home_stats['FT_DRAWING_RATE_ROLLING_AVG_5']:.3f} FTA/FGA")
        print(f"{away_team_abbr} FT stats: {away_stats['FTA_ROLLING_AVG_5']:.1f} FTA, {away_stats['FT_PCT_ROLLING_AVG_5']:.3f} FT%, {away_stats['FT_DRAWING_RATE_ROLLING_AVG_5']:.3f} FTA/FGA")
        
        print(f"\nWin streaks: {home_team_abbr} {home_stats['WIN_STREAK']}/5, {away_team_abbr} {away_stats['WIN_STREAK']}/5")
        
        # Predicted winner
        predicted_winner = f"{home_team_abbr} (Home)" if home_win_prob > 0.5 else f"{away_team_abbr} (Away)"
        print(f"\n{BOLD}Predicted winner: {GREEN}{predicted_winner}{END} ({max(home_win_prob, 1-home_win_prob):.2%} confidence)")
        
        print(f"\n{BOLD}Last Games Played:{END}")
        print(f"{home_team_abbr}: {home_stats['LATEST_GAME_DATE']}")
        print(f"{away_team_abbr}: {away_stats['LATEST_GAME_DATE']}")
        
        # Print rosters if available
        if home_roster:
            print_team_roster(home_roster)
        
        if away_roster:
            print_team_roster(away_roster)
        
        return home_win_prob
        
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        print(f"An error occurred: {str(e)}")
        return None

def main():
    """Run prediction for user-specified teams"""
    if len(sys.argv) < 3:
        # Default to Pacers-Knicks game
        home_team = 'NYK'
        away_team = 'IND'
        print(f"{YELLOW}No teams specified, using default: {away_team} @ {home_team}{END}")
    else:
        away_team = sys.argv[1].upper()
        home_team = sys.argv[2].upper()
    
    predict_game(home_team, away_team)

if __name__ == "__main__":
    main() 