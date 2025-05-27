export interface Team {
  id: number;
  name: string;
}

export interface TeamStats {
  wins: number;
  losses: number;
  pointsPerGame: number;
  pointsAllowedPerGame: number;
  fieldGoalPercentage: number;
  threePointPercentage: number;
  freeThrowPercentage: number;
  reboundsPerGame: number;
  assistsPerGame: number;
  stealsPerGame: number;
  blocksPerGame: number;
  turnoversPerGame: number;
}

export interface MatchPredictionRequest {
  homeTeamId: number;
  awayTeamId: number;
  homeTeamStats: TeamStats;
  awayTeamStats: TeamStats;
}

export interface Prediction {
  id: number;
  timestamp: string;
  homeTeam: Team;
  awayTeam: Team;
  predictedWinner: Team;
  confidence: number;
} 