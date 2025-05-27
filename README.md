# NBA Predictor App

A comprehensive NBA prediction application that forecasts All-Star Teams, MVP, Awards, and Match outcomes using machine learning.

## Features

- All-Star Team Predictions
- MVP and Awards Predictions
- Match Outcome Predictions
- Draft Pick Analysis
- Real-time Player Statistics
- Team Performance Analytics
- **Match Prediction**: Predict the outcome of NBA games using machine learning
- **Team Analysis**: Analyze team performance statistics
- **Overtime Prediction**: Model includes overtime data as a feature for more accurate predictions
- **Historical Data**: Leverages historical NBA game data for training

## Project Structure

```
NBA_Predict/
├── data/           # Data storage and processing
├── models/         # ML models and predictions
├── api/           # FastAPI backend
├── frontend/      # React frontend (to be added)
├── scripts/       # Utility scripts
└── tests/         # Test cases
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/NBA_Predict.git
cd NBA_Predict
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the API

To start the prediction API:
```bash
python api/main.py
```

The API will be available at http://localhost:8000

### Automatic Data Updates

The application includes an automatic data update system that can fetch the latest NBA game data and optionally retrain the model.

To run a manual update:
```bash
python scripts/auto_update.py
```

To run an update and retrain the model:
```bash
python scripts/auto_update.py --retrain
```

#### Setting Up Scheduled Updates

You can set up automatic scheduled updates using the setup script:

```bash
python scripts/setup_scheduler.py --frequency daily --retrain
```

Available frequency options:
- `daily`: Updates once per day (3:00 AM)
- `weekly`: Updates once per week (Monday at 3:00 AM)
- `gameday`: Updates twice per day (10:00 AM and 11:00 PM)

The script will configure the appropriate scheduler for your operating system (cron for Linux, LaunchAgent for macOS, Task Scheduler for Windows).

## Development

[To be added]

## Contributing

[To be added]

## License

MIT License

## Model Features

The prediction model uses the following features:
- Team IDs (encoded)
- Home/Away status
- Rolling averages (5 and 10 game windows) for:
  - Points
  - Field Goal Percentage
  - Free Throw Percentage
  - Three-Point Percentage
  - Assists
  - Rebounds
  - Free Throw Attempts
  - Turnovers
  - Steals
- Win streaks
- Free throw drawing rate
- Head-to-head win rate
- Overtime rate (percentage of games going to overtime) 