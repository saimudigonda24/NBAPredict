from models.match_predictor import NBAMatchPredictor
import sys

try:
    # Create predictor instance
    print("Creating predictor instance...")
    predictor = NBAMatchPredictor()
    
    # Load the model
    print("Loading model...")
    predictor.load_model('models/match_predictor_with_overtime')
    
    # Display model accuracy
    print("\n" + "="*50)
    print(f"MODEL ACCURACY: {predictor.accuracy:.2%}")
    print("="*50)
    
    print("\nModel was successfully loaded and accuracy retrieved.")
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 