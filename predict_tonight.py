from models.match_predictor import NBAMatchPredictor
from nba_api.stats.static import teams
import pandas as pd
import numpy as np
import sys
import os
import logging
import matplotlib.pyplot as plt
import seaborn as sns

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_team_id(team_name):
    """Get team ID from team name"""
    nba_teams = teams.get_teams()
    team = [t for t in nba_teams if team_name.lower() in t['full_name'].lower()]
    if team:
        return team[0]['id']
    else:
        logger.error(f"Team not found: {team_name}")
        return None

def get_team_stats(games_df, team_id):
    """Get team stats from games dataframe"""
    team_games = games_df[games_df['TEAM_ID'] == team_id].sort_values('GAME_DATE', ascending=False)
    
    if len(team_games) == 0:
        logger.error(f"No games found for team ID: {team_id}")
        return None
    
    # Calculate rolling averages
    recent_games = team_games.head(10)  # Last 10 games
    
    stats = {
        'PTS_ROLLING_AVG_5': recent_games['PTS'].mean(),
        'FG_PCT_ROLLING_AVG_5': recent_games['FG_PCT'].mean(),
        'FT_PCT_ROLLING_AVG_5': recent_games['FT_PCT'].mean(),
        'FG3_PCT_ROLLING_AVG_5': recent_games['FG3_PCT'].mean(),
        'AST_ROLLING_AVG_5': recent_games['AST'].mean(),
        'REB_ROLLING_AVG_5': recent_games['REB'].mean(),
        'FTA_ROLLING_AVG_5': recent_games['FTA'].mean(),
        'FT_DRAWING_RATE_ROLLING_AVG_5': (recent_games['FTA'] / recent_games['FGA']).mean() if recent_games['FGA'].sum() > 0 else 0,
        'WIN_STREAK': sum(1 for wl in recent_games['WL'].head(5) if wl == 'W'),
        'TOV_ROLLING_AVG_5': recent_games['TOV'].mean(),
        'STL_ROLLING_AVG_5': recent_games['STL'].mean(),
        'OVERTIME_RATE': (recent_games['MIN'] > 240).mean()
    }
    
    return stats

def predict_tonight_game():
    """Predict tonight's NBA playoff game"""
    try:
        # Load the model
        logger.info("Loading the prediction model...")
        predictor = NBAMatchPredictor()
        predictor.load_model('models/match_predictor_with_overtime')
        
        # Load the latest game data
        logger.info("Loading game data...")
        data_dir = 'data'
        data_files = [f for f in os.listdir(data_dir) if f.startswith('team_games_') and f.endswith('.csv')]
        latest_data = os.path.join(data_dir, sorted(data_files)[-1])
        logger.info(f"Using data file: {latest_data}")
        
        games_df = pd.read_csv(latest_data)
        
        # Tonight's game: Timberwolves vs Thunder
        home_team = "Minnesota Timberwolves"
        away_team = "Oklahoma City Thunder"
        
        # Get team IDs
        home_team_id = get_team_id(home_team)
        away_team_id = get_team_id(away_team)
        
        if not home_team_id or not away_team_id:
            logger.error("Could not find team IDs. Exiting.")
            sys.exit(1)
        
        # Get team stats
        home_team_stats = get_team_stats(games_df, home_team_id)
        away_team_stats = get_team_stats(games_df, away_team_id)
        
        if not home_team_stats or not away_team_stats:
            logger.error("Could not calculate team stats. Exiting.")
            sys.exit(1)
        
        # Make prediction
        logger.info(f"Predicting {home_team} vs {away_team}...")
        home_win_prob = predictor.predict_match(home_team_id, away_team_id, home_team_stats, away_team_stats)
        away_win_prob = 1 - home_win_prob
        
        # Display results
        print("\n" + "="*80)
        print(f"NBA PLAYOFF PREDICTION - {home_team} vs {away_team}")
        print("="*80)
        print(f"Game: Western Conference Finals - Game 2")
        print(f"Date: May 23, 2025")
        print(f"Location: Target Center, Minneapolis")
        
        print("\nMODEL PREDICTION (67% accuracy):")
        print(f"{home_team} win probability: {home_win_prob:.2%}")
        print(f"{away_team} win probability: {away_win_prob:.2%}")
        
        # Determine favorite
        favorite = home_team if home_win_prob > away_win_prob else away_team
        underdog = away_team if home_win_prob > away_win_prob else home_team
        win_prob = max(home_win_prob, away_win_prob)
        
        print(f"\nFavorite: {favorite} ({win_prob:.2%} chance to win)")
        print(f"Underdog: {underdog} ({(1-win_prob):.2%} chance to win)")
        
        # Overtime prediction
        ot_prob = (home_team_stats['OVERTIME_RATE'] + away_team_stats['OVERTIME_RATE']) / 2
        print(f"\nOvertime probability: {ot_prob:.2%}")
        
        # Recent Performance Analysis
        print("\nRECENT PERFORMANCE ANALYSIS:")
        print("---------------------------")
        
        # Home team recent stats
        print(f"\n{home_team} Last 10 Games:")
        print(f"Points per game: {home_team_stats['PTS_ROLLING_AVG_5']:.1f}")
        print(f"Field Goal %: {home_team_stats['FG_PCT_ROLLING_AVG_5']:.1%}")
        print(f"3-Point %: {home_team_stats['FG3_PCT_ROLLING_AVG_5']:.1%}")
        print(f"Assists per game: {home_team_stats['AST_ROLLING_AVG_5']:.1f}")
        print(f"Rebounds per game: {home_team_stats['REB_ROLLING_AVG_5']:.1f}")
        print(f"Turnovers per game: {home_team_stats['TOV_ROLLING_AVG_5']:.1f}")
        print(f"Current win streak: {home_team_stats['WIN_STREAK']} games")
        
        # Away team recent stats
        print(f"\n{away_team} Last 10 Games:")
        print(f"Points per game: {away_team_stats['PTS_ROLLING_AVG_5']:.1f}")
        print(f"Field Goal %: {away_team_stats['FG_PCT_ROLLING_AVG_5']:.1%}")
        print(f"3-Point %: {away_team_stats['FG3_PCT_ROLLING_AVG_5']:.1%}")
        print(f"Assists per game: {away_team_stats['AST_ROLLING_AVG_5']:.1f}")
        print(f"Rebounds per game: {away_team_stats['REB_ROLLING_AVG_5']:.1f}")
        print(f"Turnovers per game: {away_team_stats['TOV_ROLLING_AVG_5']:.1f}")
        print(f"Current win streak: {away_team_stats['WIN_STREAK']} games")
        
        # Key Factors Analysis
        print("\nKEY FACTORS ANALYSIS:")
        print("--------------------")
        
        # Compare key metrics
        print("\nOffensive Efficiency:")
        try:
            # Calculate offensive efficiency using available stats
            home_off_eff = home_team_stats['PTS_ROLLING_AVG_5'] / (home_team_stats['TOV_ROLLING_AVG_5'] + 1)  # Adding 1 to avoid division by zero
            away_off_eff = away_team_stats['PTS_ROLLING_AVG_5'] / (away_team_stats['TOV_ROLLING_AVG_5'] + 1)
            print(f"{home_team}: {home_off_eff:.1f} points per turnover")
            print(f"{away_team}: {away_off_eff:.1f} points per turnover")
        except Exception as e:
            print("Offensive efficiency calculation not available")
        
        print("\nDefensive Pressure:")
        try:
            home_def_pressure = home_team_stats['STL_ROLLING_AVG_5']
            away_def_pressure = away_team_stats['STL_ROLLING_AVG_5']
            print(f"{home_team}: {home_def_pressure:.1f} steals per game")
            print(f"{away_team}: {away_def_pressure:.1f} steals per game")
        except Exception as e:
            print("Defensive pressure calculation not available")
        
        # Create ASCII visualization
        print("\nWin Probability Visualization:")
        print("-----------------------------")
        
        # Calculate bar lengths (max 40 chars)
        max_length = 40
        home_bar_length = int(home_win_prob * max_length)
        away_bar_length = int(away_win_prob * max_length)
        
        # Create ASCII bars
        home_bar = "█" * home_bar_length
        away_bar = "█" * away_bar_length
        
        # Display with team names
        print(f"{home_team}: {home_bar} {home_win_prob:.2%}")
        print(f"{away_team}: {away_bar} {away_win_prob:.2%}")
        
        # Display model accuracy info
        print("\nModel Information:")
        print("------------------")
        print(f"Model accuracy: 67.00%")
        print(f"Model features: 15 (including overtime)")
        print(f"Data updated to: {os.path.basename(latest_data).replace('team_games_', '').replace('.csv', '')}")
        print("\nNote: This prediction is based on historical data and statistical analysis.")
        print("The model's accuracy is 67%, meaning it correctly predicts the winner in about 2 out of 3 games.")
        print("Please consider this prediction as one of many factors in your analysis.")
        
        # Save visualization to file but don't display
        plt.figure(figsize=(12, 8))
        teams = [home_team, away_team]
        win_probs = [home_win_prob, away_win_prob]
        colors = ['#78BE20' if home_team == "Minnesota Timberwolves" else '#007AC1', 
                 '#007AC1' if away_team == "Oklahoma City Thunder" else '#78BE20']  # Wolves green, Thunder blue
        
        plt.bar(teams, win_probs, color=colors)
        plt.ylim(0, 1)
        plt.title('Win Probability: Timberwolves vs Thunder', fontsize=16)
        plt.ylabel('Win Probability')
        plt.axhline(y=0.5, color='gray', linestyle='--', alpha=0.7)
        
        for i, prob in enumerate(win_probs):
            plt.text(i, prob + 0.02, f"{prob:.2%}", ha='center', fontsize=14)
        
        plt.tight_layout()
        plt.savefig('prediction_timberwolves_thunder.png')
        print("\nVisualization saved as 'prediction_timberwolves_thunder.png'")
        print("="*80)
        
    except Exception as e:
        logger.error(f"Error predicting game: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    predict_tonight_game() 