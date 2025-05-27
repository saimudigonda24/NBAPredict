// Utility function to format date
function formatDate(date) {
    return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Function to update the last updated timestamp
function updateLastUpdated() {
    const timestamp = document.getElementById('last-updated');
    if (timestamp) {
        timestamp.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
    }
}

// Function to fetch and display today's games
async function loadTodayGames() {
    try {
        const response = await fetch('/next-game');
        const games = await response.json();
        const gamesContainer = document.getElementById('games-container');
        
        if (gamesContainer) {
            gamesContainer.innerHTML = games.map(game => `
                <div class="card">
                    <div class="team">
                        <img src="${game.home_team_logo}" alt="${game.home_team}" class="team-logo">
                        <div>
                            <h3>${game.home_team}</h3>
                            <p>Home</p>
                        </div>
                    </div>
                    <div class="vs">VS</div>
                    <div class="team">
                        <img src="${game.away_team_logo}" alt="${game.away_team}" class="team-logo">
                        <div>
                            <h3>${game.away_team}</h3>
                            <p>Away</p>
                        </div>
                    </div>
                    <div class="prediction">
                        <h4>Prediction</h4>
                        <p>${game.home_team} win probability: ${game.home_win_probability}%</p>
                        <p>Predicted score: ${game.predicted_home_score}-${game.predicted_away_score}</p>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading games:', error);
    }
}

// Function to fetch and display player predictions
async function loadPlayerPredictions() {
    try {
        const response = await fetch('/player-predictions');
        const players = await response.json();
        const playersContainer = document.getElementById('players-container');
        
        if (playersContainer) {
            playersContainer.innerHTML = players.map(player => `
                <div class="card">
                    <div class="team">
                        <img src="${player.team_logo}" alt="${player.team}" class="team-logo">
                        <div>
                            <h3>${player.name}</h3>
                            <p>${player.team}</p>
                        </div>
                    </div>
                    <div class="prediction">
                        <h4>Today's Predictions</h4>
                        <p>Points: ${player.predicted_points}</p>
                        <p>Rebounds: ${player.predicted_rebounds}</p>
                        <p>Assists: ${player.predicted_assists}</p>
                        <p>Confidence: ${player.prediction_confidence}%</p>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading player predictions:', error);
    }
}

// Function to fetch and display overall predictions
async function loadOverallPredictions() {
    try {
        const response = await fetch('/overall-predictions');
        const predictions = await response.json();
        const predictionsContainer = document.getElementById('predictions-container');
        
        if (predictionsContainer) {
            predictionsContainer.innerHTML = `
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">${predictions.accuracy}%</div>
                        <div class="stat-label">Prediction Accuracy</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${predictions.total_predictions}</div>
                        <div class="stat-label">Total Predictions</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${predictions.model_confidence}%</div>
                        <div class="stat-label">Model Confidence</div>
                    </div>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading overall predictions:', error);
    }
}

// Initialize data loading based on current page
document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;
    
    if (path === '/games' || path === '/') {
        loadTodayGames();
    } else if (path === '/players') {
        loadPlayerPredictions();
    } else if (path === '/predictions') {
        loadOverallPredictions();
    }
    
    // Update timestamp
    updateLastUpdated();
    
    // Refresh data every 5 minutes
    setInterval(() => {
        if (path === '/games' || path === '/') {
            loadTodayGames();
        } else if (path === '/players') {
            loadPlayerPredictions();
        } else if (path === '/predictions') {
            loadOverallPredictions();
        }
        updateLastUpdated();
    }, 300000); // 5 minutes
}); 