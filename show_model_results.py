from models.match_predictor import NBAMatchPredictor
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import sys
import os

def display_image(image_path, title=None):
    """Display an image with optional title"""
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return False
        
    print(f"Displaying {title if title else image_path}...")
    img = mpimg.imread(image_path)
    plt.figure(figsize=(10, 8))
    plt.imshow(img)
    plt.axis('off')
    if title:
        plt.title(title)
    plt.show()
    return True

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
    print("="*50 + "\n")
    
    # Display model visualizations
    print("Model Evaluation Visualizations:\n")
    
    # 1. Confusion Matrix
    display_image('models/confusion_matrix.png', 'Confusion Matrix')
    
    # 2. Training History
    display_image('models/training_history.png', 'Training History')
    
    # 3. Team Win Rates
    display_image('models/team_win_rates.png', 'Team Win Rates')
    
    print("\nModel evaluation complete.")
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 