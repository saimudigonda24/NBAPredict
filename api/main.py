from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
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
from api.services.nba_api import NBAApiService

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

@app.get("/", response_class=HTMLResponse)
async def root():
    """Home page for NBA Predictor API"""
    return """
    <!DOCTYPE html>
    <html>
        <head>
            <title>NBA Predictor</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
            <style>
                :root {
                    --primary: #1d428a;
                    --secondary: #c9082a;
                    --background: #f8f9fa;
                    --card-bg: #ffffff;
                    --text: #2c3e50;
                    --text-light: #6c757d;
                }
                
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: 'Inter', sans-serif;
                    background-color: var(--background);
                    color: var(--text);
                    line-height: 1.6;
                }
                
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                }
                
                header {
                    background: linear-gradient(135deg, var(--primary), #2a5298);
                    color: white;
                    padding: 2rem 0;
                    margin-bottom: 2rem;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }
                
                .header-content {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .logo {
                    font-size: 2rem;
                    font-weight: 700;
                    display: flex;
                    align-items: center;
                    gap: 1rem;
                }
                
                .nav-links {
                    display: flex;
                    gap: 2rem;
                }
                
                .nav-links a {
                    color: white;
                    text-decoration: none;
                    font-weight: 500;
                    transition: opacity 0.2s;
                }
                
                .nav-links a:hover {
                    opacity: 0.8;
                }
                
                .section {
                    background: var(--card-bg);
                    border-radius: 12px;
                    padding: 2rem;
                    margin-bottom: 2rem;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                }
                
                .section-title {
                    font-size: 1.5rem;
                    color: var(--primary);
                    margin-bottom: 1.5rem;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }
                
                .games-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 1.5rem;
                }
                
                .game-card {
                    background: white;
                    border-radius: 8px;
                    padding: 1.5rem;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
                    transition: transform 0.2s;
                }
                
                .game-card:hover {
                    transform: translateY(-2px);
                }
                
                .team {
                    display: flex;
                    align-items: center;
                    gap: 1rem;
                    margin-bottom: 1rem;
                }
                
                .team-logo {
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    background: #eee;
                }
                
                .vs {
                    text-align: center;
                    color: var(--text-light);
                    font-weight: 600;
                    margin: 1rem 0;
                }
                
                .prediction {
                    background: linear-gradient(135deg, #f6f9fc, #edf2f7);
                    border-radius: 8px;
                    padding: 1rem;
                    margin-top: 1rem;
                }
                
                .stats-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 1rem;
                }
                
                .stat-card {
                    background: white;
                    padding: 1rem;
                    border-radius: 8px;
                    text-align: center;
                }
                
                .stat-value {
                    font-size: 1.5rem;
                    font-weight: 600;
                    color: var(--primary);
                }
                
                .stat-label {
                    color: var(--text-light);
                    font-size: 0.9rem;
                }
                
                .api-section {
                    background: linear-gradient(135deg, #f8f9fa, #e9ecef);
                    border-radius: 12px;
                    padding: 2rem;
                }
                
                .endpoint {
                    background: white;
                    padding: 1rem;
                    border-radius: 8px;
                    margin: 0.5rem 0;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .method {
                    background: var(--primary);
                    color: white;
                    padding: 0.25rem 0.75rem;
                    border-radius: 4px;
                    font-size: 0.9rem;
                    font-weight: 500;
                }
                
                .docs-link {
                    display: inline-block;
                    background: var(--primary);
                    color: white;
                    padding: 0.75rem 1.5rem;
                    border-radius: 6px;
                    text-decoration: none;
                    font-weight: 500;
                    margin-top: 1rem;
                    transition: background-color 0.2s;
                }
                
                .docs-link:hover {
                    background: #2a5298;
                }
                
                @media (max-width: 768px) {
                    .header-content {
                        flex-direction: column;
                        text-align: center;
                        gap: 1rem;
                    }
                    
                    .nav-links {
                        flex-direction: column;
                        gap: 1rem;
                    }
                }
            </style>
        </head>
        <body>
            <header>
                <div class="container">
                    <div class="header-content">
                        <div class="logo">
                            🏀 NBA Predictor
                        </div>
                        <nav class="nav-links">
                            <a href="#games">Today's Games</a>
                            <a href="#predictions">Predictions</a>
                            <a href="#players">Player Stats</a>
                            <a href="#api">API</a>
                        </nav>
                    </div>
                </div>
            </header>

            <div class="container">
                <section id="games" class="section">
                    <h2 class="section-title">🎮 Games Playing Today</h2>
                    <div class="games-grid">
                        <div class="game-card">
                            <div class="team">
                                <div class="team-logo"></div>
                                <div>
                                    <h3>Lakers</h3>
                                    <p>Home</p>
                                </div>
                            </div>
                            <div class="vs">VS</div>
                            <div class="team">
                                <div class="team-logo"></div>
                                <div>
                                    <h3>Celtics</h3>
                                    <p>Away</p>
                                </div>
                            </div>
                            <div class="prediction">
                                <h4>Prediction</h4>
                                <p>Lakers win probability: 65%</p>
                            </div>
                        </div>
                        <!-- More game cards will be dynamically added -->
                    </div>
                </section>

                <section id="predictions" class="section">
                    <h2 class="section-title">🎯 Match Predictions</h2>
                    <div class="stats-grid">
                        <div class="stat-card">
                            <div class="stat-value">85%</div>
                            <div class="stat-label">Prediction Accuracy</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">1,234</div>
                            <div class="stat-label">Predictions Made</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-value">92%</div>
                            <div class="stat-label">Model Confidence</div>
                        </div>
                    </div>
                </section>

                <section id="players" class="section">
                    <h2 class="section-title">👥 Player Predictions</h2>
                    <div class="games-grid">
                        <div class="game-card">
                            <h3>LeBron James</h3>
                            <p>Points: 28.5</p>
                            <p>Rebounds: 7.2</p>
                            <p>Assists: 8.1</p>
                        </div>
                        <!-- More player cards will be dynamically added -->
                    </div>
                </section>

                <section id="api" class="api-section">
                    <h2 class="section-title">🔌 API Documentation</h2>
                    <p>Access our powerful NBA prediction API to integrate predictions into your application.</p>
                    
                    <div class="endpoint">
                        <span class="method">GET</span>
                        <span>/teams</span>
                        <span>List all NBA teams</span>
                    </div>
                    <div class="endpoint">
                        <span class="method">GET</span>
                        <span>/teams/{id}/stats</span>
                        <span>Get team statistics</span>
                    </div>
                    <div class="endpoint">
                        <span class="method">POST</span>
                        <span>/predict</span>
                        <span>Make a match prediction</span>
                    </div>
                    
                    <a href="/docs" class="docs-link">View Full API Documentation</a>
                </section>
            </div>

            <script>
                // This will be replaced with actual API calls to populate the data
                async function loadTodayGames() {
                    try {
                        const response = await fetch('/next-game');
                        const games = await response.json();
                        // Update the games grid with actual data
                    } catch (error) {
                        console.error('Error loading games:', error);
                    }
                }

                // Load initial data
                loadTodayGames();
            </script>
        </body>
    </html>
    """

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