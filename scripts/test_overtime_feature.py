import sys
import os
import pandas as pd
import numpy as np
import logging
import matplotlib.pyplot as plt
import seaborn as sns
import traceback

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.match_predictor import NBAMatchPredictor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/overtime_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def analyze_overtime_impact(data_file):
    """Analyze the impact of overtime on game outcomes"""
    try:
        logger.info(f"Loading data from {data_file}")
        games_df = pd.read_csv(data_file)
        logger.info(f"Data loaded successfully with {len(games_df)} rows")
        
        # Check if MIN column exists
        if 'MIN' not in games_df.columns:
            logger.error(f"MIN column not found in data. Available columns: {games_df.columns.tolist()}")
            return None
        
        # Create overtime boolean
        games_df['IS_OVERTIME'] = (games_df['MIN'] > 240).astype(int)
        
        # Count overtime games
        ot_count = games_df['IS_OVERTIME'].sum()
        total_games = len(games_df)
        ot_percentage = (ot_count / total_games) * 100
        
        logger.info(f"Total games: {total_games}")
        logger.info(f"Overtime games: {ot_count} ({ot_percentage:.2f}%)")
        
        # Check if we have the necessary columns for analysis
        required_columns = ['IS_HOME', 'WL', 'TEAM_ABBREVIATION']
        missing_columns = [col for col in required_columns if col not in games_df.columns]
        
        if missing_columns:
            logger.warning(f"Missing columns for full analysis: {missing_columns}")
            logger.warning(f"Available columns: {games_df.columns.tolist()}")
            
            # If IS_HOME is missing but MATCHUP is available, derive it
            if 'IS_HOME' in missing_columns and 'MATCHUP' in games_df.columns:
                logger.info("Deriving IS_HOME from MATCHUP column")
                games_df['IS_HOME'] = games_df['MATCHUP'].apply(lambda x: 1 if 'vs.' in x else 0)
                missing_columns.remove('IS_HOME')
            
            # If WL is missing, we can't calculate win rates
            if 'WL' in missing_columns:
                logger.warning("Cannot calculate win rates without WL column")
                games_df['WIN'] = 0  # Placeholder
            else:
                games_df['WIN'] = (games_df['WL'] == 'W').astype(int)
        else:
            games_df['WIN'] = (games_df['WL'] == 'W').astype(int)
            games_df['IS_HOME'] = games_df['MATCHUP'].apply(lambda x: 1 if 'vs.' in x else 0)
        
        # Extract opponent abbreviation from MATCHUP column
        if 'MATCHUP' in games_df.columns:
            logger.info("Extracting opponent abbreviation from MATCHUP column")
            games_df['OPPONENT_ABBREV'] = games_df['MATCHUP'].apply(
                lambda x: x.split()[-1] if '@' in x else x.split('vs.')[-1].strip()
            )
            
            # Create mapping of team abbreviations to IDs
            team_abbrev_to_id = {}
            for _, row in games_df.drop_duplicates('TEAM_ABBREVIATION')[['TEAM_ABBREVIATION', 'TEAM_ID']].iterrows():
                team_abbrev_to_id[row['TEAM_ABBREVIATION']] = row['TEAM_ID']
            
            # Map opponent abbreviations to IDs
            games_df['OPPONENT_TEAM_ID'] = games_df['OPPONENT_ABBREV'].map(team_abbrev_to_id)
            logger.info(f"Successfully mapped {games_df['OPPONENT_TEAM_ID'].notna().sum()} opponent IDs")
        
        # Only proceed with win rate analysis if we have the necessary data
        if 'WIN' in games_df.columns and 'IS_HOME' in games_df.columns:
            try:
                # Analyze win rates in overtime vs regular time
                home_win_rate_ot = games_df[(games_df['IS_OVERTIME'] == 1) & (games_df['IS_HOME'] == 1)]['WIN'].mean()
                home_win_rate_reg = games_df[(games_df['IS_OVERTIME'] == 0) & (games_df['IS_HOME'] == 1)]['WIN'].mean()
                
                away_win_rate_ot = games_df[(games_df['IS_OVERTIME'] == 1) & (games_df['IS_HOME'] == 0)]['WIN'].mean()
                away_win_rate_reg = games_df[(games_df['IS_OVERTIME'] == 0) & (games_df['IS_HOME'] == 0)]['WIN'].mean()
                
                logger.info(f"Home team win rate in overtime: {home_win_rate_ot:.4f}")
                logger.info(f"Home team win rate in regulation: {home_win_rate_reg:.4f}")
                logger.info(f"Away team win rate in overtime: {away_win_rate_ot:.4f}")
                logger.info(f"Away team win rate in regulation: {away_win_rate_reg:.4f}")
            except Exception as e:
                logger.error(f"Error calculating win rates: {str(e)}")
                logger.error(traceback.format_exc())
        
        # Create output directory if it doesn't exist
        os.makedirs('data/analysis', exist_ok=True)
        
        # Visualize overtime distribution by team if team abbreviation is available
        if 'TEAM_ABBREVIATION' in games_df.columns:
            try:
                plt.figure(figsize=(14, 8))
                team_ot_counts = games_df.groupby('TEAM_ABBREVIATION')['IS_OVERTIME'].sum().sort_values(ascending=False)
                sns.barplot(x=team_ot_counts.index, y=team_ot_counts.values)
                plt.title('Number of Overtime Games by Team')
                plt.xticks(rotation=90)
                plt.tight_layout()
                plt.savefig('data/analysis/overtime_by_team.png')
                logger.info("Saved overtime by team visualization")
            except Exception as e:
                logger.error(f"Error creating team overtime visualization: {str(e)}")
                logger.error(traceback.format_exc())
        
        # Visualize win rates in overtime vs regulation if we have the data
        if 'WIN' in games_df.columns and 'IS_HOME' in games_df.columns:
            try:
                win_rates = pd.DataFrame({
                    'Game Type': ['Overtime', 'Regulation', 'Overtime', 'Regulation'],
                    'Team Type': ['Home', 'Home', 'Away', 'Away'],
                    'Win Rate': [home_win_rate_ot, home_win_rate_reg, away_win_rate_ot, away_win_rate_reg]
                })
                
                plt.figure(figsize=(10, 6))
                sns.barplot(x='Team Type', y='Win Rate', hue='Game Type', data=win_rates)
                plt.title('Win Rates in Overtime vs Regulation')
                plt.tight_layout()
                plt.savefig('data/analysis/overtime_win_rates.png')
                logger.info("Saved overtime win rates visualization")
            except Exception as e:
                logger.error(f"Error creating win rates visualization: {str(e)}")
                logger.error(traceback.format_exc())
        
        return games_df
        
    except Exception as e:
        logger.error(f"Error analyzing overtime impact: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def train_model_with_overtime(games_df):
    """Train the model with overtime feature and evaluate performance"""
    try:
        if games_df is None or games_df.empty:
            logger.error("Cannot train model: No data provided")
            return None
            
        logger.info("Training model with overtime feature")
        predictor = NBAMatchPredictor()
        
        # Ensure we have all required columns for the model
        required_columns = ['TEAM_ID', 'OPPONENT_TEAM_ID', 'IS_HOME', 'PTS', 'FG_PCT', 'FT_PCT', 
                           'FG3_PCT', 'AST', 'REB', 'FTA', 'TOV', 'STL', 'IS_OVERTIME']
        
        missing_columns = [col for col in required_columns if col not in games_df.columns]
        
        if missing_columns:
            logger.error(f"Missing columns required for model training: {missing_columns}")
            logger.info(f"Available columns: {games_df.columns.tolist()}")
            return None
        
        history = predictor.train(games_df)
        
        # Save the model
        os.makedirs('models', exist_ok=True)
        predictor.save_model('models/match_predictor_with_overtime')
        
        logger.info("Model training completed and saved to models/match_predictor_with_overtime")
        return predictor
        
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def main():
    try:
        # Create logs and data analysis directories if they don't exist
        os.makedirs('logs', exist_ok=True)
        os.makedirs('data/analysis', exist_ok=True)
        
        # Find the most recent data file
        data_dir = 'data'
        data_files = [f for f in os.listdir(data_dir) if f.startswith('team_games_') and f.endswith('.csv')]
        
        if not data_files:
            logger.error("No team_games data files found in data directory")
            return
            
        latest_file = max(data_files)
        data_path = os.path.join(data_dir, latest_file)
        
        # Analyze overtime impact
        logger.info(f"Using data file: {data_path}")
        games_df = analyze_overtime_impact(data_path)
        
        # Train model with overtime feature
        if games_df is not None and not games_df.empty:
            predictor = train_model_with_overtime(games_df)
            if predictor:
                logger.info("Analysis and model training completed successfully")
            else:
                logger.error("Model training failed")
        else:
            logger.error("Cannot proceed with model training due to data issues")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main() 