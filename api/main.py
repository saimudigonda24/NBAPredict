from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel
import sys
import os
from typing import List, Optional
import logging
from datetime import datetime
import random
import json
from pathlib import Path
from nba_api.stats.endpoints import scoreboardv2

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.match_predictor import NBAMatchPredictor
from api.services.nba_api import NBAApiService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="NBA Predictor API")

# Mount static files
app.mount("/static", StaticFiles(directory="api/static"), name="static")

# Templates
templates = Jinja2Templates(directory="api/templates")

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

class Game(BaseModel):
    home_team: str
    away_team: str
    home_team_logo: str
    away_team_logo: str
    home_win_probability: float
    predicted_home_score: int
    predicted_away_score: int

class PlayerPrediction(BaseModel):
    name: str
    team: str
    team_logo: str
    predicted_points: float
    predicted_rebounds: float
    predicted_assists: float
    prediction_confidence: float

class OverallPrediction(BaseModel):
    accuracy: float
    total_predictions: int
    model_confidence: float

class GameInfo(BaseModel):
    game_id: str
    home_team: str
    away_team: str
    start_time: str
    home_team_logo: str
    away_team_logo: str
    prediction: Optional[float] = None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with today's games"""
    return templates.TemplateResponse(
        "home.html",
        {"request": request, "active_page": "home"}
    )

@app.get("/games", response_class=HTMLResponse)
async def games_page(request: Request):
    """Games page with today's games"""
    return templates.TemplateResponse(
        "games.html",
        {"request": request, "active_page": "games"}
    )

@app.get("/players", response_class=HTMLResponse)
async def players_page(request: Request):
    """Players page with player predictions"""
    return templates.TemplateResponse(
        "players.html",
        {"request": request, "active_page": "players"}
    )

@app.get("/predictions", response_class=HTMLResponse)
async def predictions_page(request: Request):
    """Predictions page with overall stats"""
    return templates.TemplateResponse(
        "predictions.html",
        {"request": request, "active_page": "predictions"}
    )

@app.get("/api", response_class=HTMLResponse)
async def api_page(request: Request):
    """API documentation page"""
    return templates.TemplateResponse(
        "api.html",
        {"request": request, "active_page": "api"}
    )

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

@app.get("/next-game", response_model=List[Game])
async def get_next_game():
    """Get predictions for today's games"""
    # This would be replaced with actual data from your model
    return [
        Game(
            home_team="Lakers",
            away_team="Celtics",
            home_team_logo="/static/images/lakers.png",
            away_team_logo="/static/images/celtics.png",
            home_win_probability=65.0,
            predicted_home_score=112,
            predicted_away_score=108
        )
    ]

@app.get("/player-predictions", response_model=List[PlayerPrediction])
async def get_player_predictions():
    """Get predictions for players in today's games"""
    # This would be replaced with actual data from your model
    return [
        PlayerPrediction(
            name="LeBron James",
            team="Lakers",
            team_logo="/static/images/lakers.png",
            predicted_points=28.5,
            predicted_rebounds=7.2,
            predicted_assists=8.1,
            prediction_confidence=85.0
        ),
        PlayerPrediction(
            name="Jayson Tatum",
            team="Celtics",
            team_logo="/static/images/celtics.png",
            predicted_points=25.8,
            predicted_rebounds=8.3,
            predicted_assists=4.2,
            prediction_confidence=82.0
        )
    ]

@app.get("/overall-predictions", response_model=OverallPrediction)
async def get_overall_predictions():
    """Get overall prediction statistics"""
    # This would be replaced with actual data from your model
    return OverallPrediction(
        accuracy=85.0,
        total_predictions=1234,
        model_confidence=92.0
    )

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

@app.get("/games/today", response_model=List[GameInfo])
async def get_todays_games():
    today = datetime.now().strftime("%m/%d/%Y")
    scoreboard = scoreboardv2.ScoreboardV2(game_date=today)
    games = scoreboard.get_normalized_dict()["GameHeader"]
    lines = []
    for game in games:
        home_team = game["HOME_TEAM_ABBREVIATION"]
        away_team = game["VISITOR_TEAM_ABBREVIATION"]
        start_time = game["GAME_STATUS_TEXT"]
        # Use local static images if available, else fallback to a CDN
        def logo_path(team_abbr):
            local_path = f"/static/images/{team_abbr.lower()}.png"
            if os.path.exists(f"api/static/images/{team_abbr.lower()}.png"):
                return local_path
            # fallback to a public NBA CDN if not found locally
            return f"https://cdn.nba.com/logos/nba/{team_abbr.upper()}/primary/L/logo.svg"
        lines.append(GameInfo(
            game_id=game["GAME_ID"],
            home_team=home_team,
            away_team=away_team,
            start_time=start_time,
            home_team_logo=logo_path(home_team),
            away_team_logo=logo_path(away_team),
            prediction=None  # TODO: Integrate your model here
        ))
    return lines

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 