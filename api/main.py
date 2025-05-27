from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
from typing import List, Optional
import logging
from datetime import datetime
import random

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.match_predictor import NBAMatchPredictor
from services.nba_api import NBAApiService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="NBA Predictor API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
match_predictor = NBAMatchPredictor()
nba_api = NBAApiService()

# Load the model
try:
    match_predictor.load_model('models/match_predictor_with_overtime')
    logger.info("Loaded model with overtime feature")
except Exception as e:
    logger.warning(f"Could not load model with overtime feature: {str(e)}")
    logger.info("Using default model")

# Pydantic models
class Team(BaseModel):
    id: int
    name: str
    abbreviation: str

class TeamStats(BaseModel):
    teamId: int
    pointsPerGame: float
    fieldGoalPercentage: float
    threePointPercentage: float
    freeThrowPercentage: float
    assistsPerGame: float
    reboundsPerGame: float
    winStreak: int
    lastTenGames: float

class MatchPredictionRequest(BaseModel):
    homeTeamId: int
    awayTeamId: int
    homeTeamStats: TeamStats
    awayTeamStats: TeamStats

class Prediction(BaseModel):
    homeTeam: Team
    awayTeam: Team
    homeWinProbability: float
    predictedWinner: Team
    confidence: float
    timestamp: str

class HistoricalPrediction(BaseModel):
    id: int
    prediction: Prediction
    actualWinner: Optional[Team]
    isCorrect: Optional[bool]
    createdAt: str

# In-memory storage for historical predictions
historical_predictions: List[HistoricalPrediction] = []

@app.get("/teams", response_model=List[Team])
async def get_teams():
    """Get all NBA teams"""
    teams = nba_api._get_teams()
    return [Team(id=t['id'], name=t['name'], abbreviation=t['abbreviation']) for t in teams]

@app.get("/teams/{team_id}/stats", response_model=TeamStats)
async def get_team_stats(team_id: int):
    """Get current stats for a team"""
    stats = nba_api.get_team_stats(team_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Team stats not found")
    return TeamStats(**stats)

@app.get("/next-game", response_model=dict)
async def get_next_game():
    """Get the next scheduled NBA game"""
    next_game = nba_api.get_next_game()
    if not next_game:
        raise HTTPException(status_code=404, detail="No upcoming games found")
    return next_game

@app.post("/predict", response_model=Prediction)
async def predict_match(request: MatchPredictionRequest):
    """Predict the outcome of a match"""
    try:
        # Get team info
        teams = nba_api._get_teams()
        home_team = next(t for t in teams if t['id'] == request.homeTeamId)
        away_team = next(t for t in teams if t['id'] == request.awayTeamId)
        
        # Get prediction from model
        win_probability = match_predictor.predict_match(
            str(request.homeTeamId),
            str(request.awayTeamId),
            request.homeTeamStats.dict(),
            request.awayTeamStats.dict()
        )
        
        if win_probability is None:
            raise HTTPException(status_code=500, detail="Prediction failed")
        
        predicted_winner = home_team if win_probability > 0.5 else away_team
        
        prediction = Prediction(
            homeTeam=Team(id=home_team['id'], name=home_team['name'], abbreviation=home_team['abbreviation']),
            awayTeam=Team(id=away_team['id'], name=away_team['name'], abbreviation=away_team['abbreviation']),
            homeWinProbability=float(win_probability),
            predictedWinner=Team(id=predicted_winner['id'], name=predicted_winner['name'], abbreviation=predicted_winner['abbreviation']),
            confidence=0.8,  # This should come from the model
            timestamp=datetime.now().isoformat()
        )

        # Store prediction in history
        historical_predictions.append(
            HistoricalPrediction(
                id=len(historical_predictions) + 1,
                prediction=prediction,
                actualWinner=None,
                isCorrect=None,
                createdAt=datetime.now().isoformat()
            )
        )
        
        return prediction
    except Exception as e:
        logger.error(f"Error making prediction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/predictions/history", response_model=List[HistoricalPrediction])
async def get_historical_predictions():
    """Get historical predictions"""
    return historical_predictions

@app.get("/teams/compare/{team1_id}/{team2_id}", response_model=dict)
async def compare_teams(team1_id: int, team2_id: int):
    """Compare two teams' statistics"""
    team1_stats = nba_api.get_team_stats(team1_id)
    team2_stats = nba_api.get_team_stats(team2_id)
    
    if not team1_stats or not team2_stats:
        raise HTTPException(status_code=404, detail="Team stats not found")
    
    teams = nba_api._get_teams()
    team1 = next(t for t in teams if t['id'] == team1_id)
    team2 = next(t for t in teams if t['id'] == team2_id)
    
    return {
        "team1": {
            "info": Team(id=team1['id'], name=team1['name'], abbreviation=team1['abbreviation']),
            "stats": TeamStats(**team1_stats)
        },
        "team2": {
            "info": Team(id=team2['id'], name=team2['name'], abbreviation=team2['abbreviation']),
            "stats": TeamStats(**team2_stats)
        },
        "comparison": {
            "pointsPerGame": team1_stats['pointsPerGame'] - team2_stats['pointsPerGame'],
            "fieldGoalPercentage": team1_stats['fieldGoalPercentage'] - team2_stats['fieldGoalPercentage'],
            "threePointPercentage": team1_stats['threePointPercentage'] - team2_stats['threePointPercentage'],
            "freeThrowPercentage": team1_stats['freeThrowPercentage'] - team2_stats['freeThrowPercentage'],
            "assistsPerGame": team1_stats['assistsPerGame'] - team2_stats['assistsPerGame'],
            "reboundsPerGame": team1_stats['reboundsPerGame'] - team2_stats['reboundsPerGame']
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        # Check if we can get teams data
        teams = nba_api._get_teams()
        if not teams:
            return {"status": "degraded", "message": "NBA API connection issue"}
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "nba_api": "healthy",
                "model": "healthy" if match_predictor.model is not None else "degraded"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 