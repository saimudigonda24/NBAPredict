from models.match_predictor import NBAMatchPredictor
import sys
import os
import tensorflow as tf
import joblib
import pandas as pd
import numpy as np

# Print environment information
print(f"Python version: {sys.version}")
print(f"TensorFlow version: {tf.__version__}")
print(f"Current directory: {os.getcwd()}")

# Check model files
model_path = 'models/match_predictor_with_overtime'
keras_file = f"{model_path}.keras"
encoders_file = f"{model_path}_encoders.joblib"

print(f"Checking if model files exist:")
print(f"  - {keras_file}: {os.path.exists(keras_file)}")
print(f"  - {encoders_file}: {os.path.exists(encoders_file)}")

# Try to load each component separately
print("\nTrying to load components separately:")
try:
    print("Loading TensorFlow model...")
    model = tf.keras.models.load_model(keras_file)
    print(f"Model loaded successfully with input shape: {model.input_shape}")
except Exception as e:
    print(f"Error loading TensorFlow model: {e}")

try:
    print("\nLoading encoders...")
    encoders = joblib.load(encoders_file)
    print(f"Encoders loaded successfully: {list(encoders.keys())}")
except Exception as e:
    print(f"Error loading encoders: {e}")

# Now try the full predictor
try:
    print("\nCreating predictor instance...")
    predictor = NBAMatchPredictor()
    
    print("Attempting to load model...")
    predictor.load_model(model_path)
    print("Model loaded successfully")
    
    # Try to make a prediction
    print("\nTesting prediction functionality...")
    
    # Check if we have any game data to test with
    data_files = [f for f in os.listdir('data') if f.startswith('team_games_') and f.endswith('.csv')]
    if data_files:
        latest_data = sorted(data_files)[-1]
        print(f"Using data file: {latest_data}")
        
        # Load the data
        games_df = pd.read_csv(f'data/{latest_data}')
        print(f"Loaded {len(games_df)} games")
        
        # Get a sample team
        sample_team = games_df['TEAM_ID'].iloc[0]
        sample_team_name = games_df['TEAM_NAME'].iloc[0]
        
        # Create dummy stats for prediction
        sample_stats = {
            'PTS_ROLLING_AVG_5': games_df['PTS'].mean(),
            'FG_PCT_ROLLING_AVG_5': games_df['FG_PCT'].mean(),
            'FT_PCT_ROLLING_AVG_5': games_df['FT_PCT'].mean(),
            'FG3_PCT_ROLLING_AVG_5': games_df['FG3_PCT'].mean(),
            'AST_ROLLING_AVG_5': games_df['AST'].mean(),
            'REB_ROLLING_AVG_5': games_df['REB'].mean(),
            'FTA_ROLLING_AVG_5': games_df['FTA'].mean(),
            'FT_DRAWING_RATE_ROLLING_AVG_5': 0.2,
            'WIN_STREAK': 3,
            'TOV_ROLLING_AVG_5': games_df['TOV'].mean(),
            'STL_ROLLING_AVG_5': games_df['STL'].mean(),
            'OVERTIME_RATE': 0.1
        }
        
        # Try to predict
        print(f"Attempting prediction for {sample_team_name} vs {sample_team_name}...")
        try:
            win_prob = predictor.predict_match(sample_team, sample_team, sample_stats, sample_stats)
            print(f"Prediction successful! Win probability: {win_prob:.4f}")
        except Exception as e:
            print(f"Error making prediction: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("No game data files found to test prediction")
    
except Exception as e:
    print(f"\nError in predictor: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 