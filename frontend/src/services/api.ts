import axios from 'axios';
import { MatchPredictionRequest, Prediction, Team, TeamStats } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getTeams = async (): Promise<Team[]> => {
  const response = await api.get('/teams');
  return response.data;
};

export const getTeamStats = async (teamId: number): Promise<TeamStats> => {
  const response = await api.get(`/teams/${teamId}/stats`);
  return response.data;
};

export const getNextGame = async (): Promise<{
  homeTeam: Team;
  awayTeam: Team;
  date: string;
  time: string;
}> => {
  const response = await api.get('/next-game');
  return response.data;
};

export const predictMatch = async (request: MatchPredictionRequest): Promise<Prediction> => {
  const response = await api.post('/predict', request);
  return response.data;
};

export const getHistoricalPredictions = async (): Promise<Prediction[]> => {
  const response = await api.get('/predictions');
  return response.data;
};

export const compareTeams = async (team1Id: number, team2Id: number): Promise<{
  team1: { info: Team; stats: TeamStats };
  team2: { info: Team; stats: TeamStats };
  comparison: {
    pointsPerGame: number;
    fieldGoalPercentage: number;
    threePointPercentage: number;
    freeThrowPercentage: number;
    assistsPerGame: number;
    reboundsPerGame: number;
  };
}> => {
  const response = await api.get(`/teams/compare/${team1Id}/${team2Id}`);
  return response.data;
}; 