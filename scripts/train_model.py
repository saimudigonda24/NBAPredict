import os
import sys
import pandas as pd
import logging
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.data_fetcher import NBADataFetcher
from models.match_predictor import NBAMatchPredictor
from data.data_collector import NBADataCollector

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    print("Starting NBA prediction model training...")
    
    try:
        # Initialize data collector
        print("Initializing data collector...")
        data_collector = NBADataCollector()
        
        # Load or collect training data
        print("Loading training data...")
        try:
            training_data = pd.read_csv('data/training_data_20250519.csv')
            print(f"Loaded {len(training_data)} training samples")
        except FileNotFoundError:
            print("Training data not found, collecting new data...")
            training_data = data_collector.collect_training_data()
            print(f"Collected {len(training_data)} new training samples")
        
        # Initialize predictor
        print("\nInitializing model...")
        predictor = NBAMatchPredictor()
        
        # Train model with verbose output
        print("\nStarting model training...")
        try:
            history = predictor.train(
                training_data,
                verbose=1,  # Show progress for each epoch
                validation_split=0.2
            )
            
            # Print training results
            print("\nTraining completed successfully!")
            if history and hasattr(history, 'history'):
                print(f"Final training accuracy: {history.history['accuracy'][-1]:.4f}")
                print(f"Final validation accuracy: {history.history['val_accuracy'][-1]:.4f}")
            
            # Save the model
            predictor.save_model('models/match_predictor_model.h5')
            print("\nModel saved successfully!")
            
        except Exception as e:
            print(f"\nError during model training: {str(e)}")
            return False
            
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    main() 