import axios, { AxiosError } from 'axios';
import { MatchPredictionRequest, Prediction, Team, TeamStats } from '../types';

const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://nba-predict-api.onrender.com'  // Update this with your actual Render URL after deployment
  : 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 second timeout
});

// Error handling interceptor
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      const errorData = error.response.data as { detail?: string };
      console.error('API Error:', errorData);
      throw new Error(errorData.detail || 'An error occurred');
    } else if (error.request) {
      // The request was made but no response was received
      console.error('No response received:', error.request);
      throw new Error('No response received from server');
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error('Request setup error:', error.message);
      throw new Error('Error setting up request');
    }
  }
);

export const getTeams = async (): Promise<Team[]> => {
  try {
    const response = await api.get('/teams');
    return response.data;
  } catch (error) {
    console.error('Error fetching teams:', error);
    throw error;
  }
};

export const getTeamStats = async (teamId: number): Promise<TeamStats> => {
  try {
    const response = await api.get(`/teams/${teamId}/stats`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching stats for team ${teamId}:`, error);
    throw error;
  }
};

export const getNextGame = async (): Promise<{
  homeTeam: Team;
  awayTeam: Team;
  date: string;
  time: string;
}> => {
  try {
    const response = await api.get('/next-game');
    return response.data;
  } catch (error) {
    console.error('Error fetching next game:', error);
    throw error;
  }
};

export const predictMatch = async (request: MatchPredictionRequest): Promise<Prediction> => {
  try {
    const response = await api.post('/predict', request);
    return response.data;
  } catch (error) {
    console.error('Error making prediction:', error);
    throw error;
  }
};

export const getHistoricalPredictions = async (): Promise<Prediction[]> => {
  try {
    const response = await api.get('/predictions/history');
    return response.data;
  } catch (error) {
    console.error('Error fetching historical predictions:', error);
    throw error;
  }
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
  try {
    const response = await api.get(`/teams/compare/${team1Id}/${team2Id}`);
    return response.data;
  } catch (error) {
    console.error(`Error comparing teams ${team1Id} and ${team2Id}:`, error);
    throw error;
  }
}; 