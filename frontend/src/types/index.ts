export interface Team {
  id: number;
  name: string;
  abbreviation: string;
}

export interface Prediction {
  homeTeam: Team;
  awayTeam: Team;
  homeWinProbability: number;
  predictedWinner: Team;
  confidence: number;
  timestamp: string;
}

export interface TeamStats {
  teamId: number;
  pointsPerGame: number;
  fieldGoalPercentage: number;
  threePointPercentage: number;
  freeThrowPercentage: number;
  assistsPerGame: number;
  reboundsPerGame: number;
  winStreak: number;
  lastTenGames: number;
}

export interface MatchPredictionRequest {
  homeTeamId: number;
  awayTeamId: number;
  homeTeamStats: TeamStats;
  awayTeamStats: TeamStats;
} 