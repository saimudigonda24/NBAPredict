import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  CircularProgress,
  Divider,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import { Team, TeamStats, Prediction } from '../types';
import { getTeams, getTeamStats, predictMatch, getNextGame } from '../services/api';

const NextGamePrediction: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [nextGame, setNextGame] = useState<{
    homeTeam: Team;
    awayTeam: Team;
    date: string;
    time: string;
  } | null>(null);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [homeStats, setHomeStats] = useState<TeamStats | null>(null);
  const [awayStats, setAwayStats] = useState<TeamStats | null>(null);

  useEffect(() => {
    const fetchNextGameData = async () => {
      try {
        const nextGameData = await getNextGame();
        setNextGame(nextGameData);

        // Fetch team stats
        const [homeTeamStats, awayTeamStats] = await Promise.all([
          getTeamStats(nextGameData.homeTeam.id),
          getTeamStats(nextGameData.awayTeam.id),
        ]);

        setHomeStats(homeTeamStats);
        setAwayStats(awayTeamStats);

        // Make prediction
        const predictionResult = await predictMatch({
          homeTeamId: nextGameData.homeTeam.id,
          awayTeamId: nextGameData.awayTeam.id,
          homeTeamStats: homeTeamStats,
          awayTeamStats: awayTeamStats,
        });

        setPrediction(predictionResult);
      } catch (error) {
        console.error('Error fetching next game data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchNextGameData();
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!nextGame || !prediction || !homeStats || !awayStats) {
    return (
      <Typography variant="h6" color="error">
        No upcoming game data available
      </Typography>
    );
  }

  // Prepare data for charts
  const teamComparisonData = [
    {
      name: 'Points per Game',
      [nextGame.homeTeam.name]: homeStats.pointsPerGame,
      [nextGame.awayTeam.name]: awayStats.pointsPerGame,
    },
    {
      name: 'Field Goal %',
      [nextGame.homeTeam.name]: homeStats.fieldGoalPercentage,
      [nextGame.awayTeam.name]: awayStats.fieldGoalPercentage,
    },
    {
      name: '3PT %',
      [nextGame.homeTeam.name]: homeStats.threePointPercentage,
      [nextGame.awayTeam.name]: awayStats.threePointPercentage,
    },
    {
      name: 'Free Throw %',
      [nextGame.homeTeam.name]: homeStats.freeThrowPercentage,
      [nextGame.awayTeam.name]: awayStats.freeThrowPercentage,
    },
    {
      name: 'Assists per Game',
      [nextGame.homeTeam.name]: homeStats.assistsPerGame,
      [nextGame.awayTeam.name]: awayStats.assistsPerGame,
    },
    {
      name: 'Rebounds per Game',
      [nextGame.homeTeam.name]: homeStats.reboundsPerGame,
      [nextGame.awayTeam.name]: awayStats.reboundsPerGame,
    },
  ];

  const radarData = [
    {
      subject: 'Win Streak',
      [nextGame.homeTeam.name]: homeStats.winStreak,
      [nextGame.awayTeam.name]: awayStats.winStreak,
    },
    {
      subject: 'Last 10 Games',
      [nextGame.homeTeam.name]: homeStats.lastTenGames,
      [nextGame.awayTeam.name]: awayStats.lastTenGames,
    },
  ];

  return (
    <Box sx={{ p: 3 }}>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Next Game Prediction
        </Typography>
        <Typography variant="h6" gutterBottom>
          {nextGame.homeTeam.name} vs {nextGame.awayTeam.name}
        </Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Date: {nextGame.date} at {nextGame.time}
        </Typography>
      </Paper>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Team Comparison
            </Typography>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={teamComparisonData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey={nextGame.homeTeam.name} fill="#2196f3" />
                <Bar dataKey={nextGame.awayTeam.name} fill="#f50057" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Performance Metrics
            </Typography>
            <ResponsiveContainer width="100%" height={400}>
              <RadarChart data={radarData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="subject" />
                <PolarRadiusAxis />
                <Radar
                  name={nextGame.homeTeam.name}
                  dataKey={nextGame.homeTeam.name}
                  stroke="#2196f3"
                  fill="#2196f3"
                  fillOpacity={0.6}
                />
                <Radar
                  name={nextGame.awayTeam.name}
                  dataKey={nextGame.awayTeam.name}
                  stroke="#f50057"
                  fill="#f50057"
                  fillOpacity={0.6}
                />
                <Legend />
              </RadarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Prediction Results
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1">
                  Predicted Winner: {prediction.predictedWinner.name}
                </Typography>
                <Typography variant="subtitle1">
                  Win Probability: {(prediction.homeWinProbability * 100).toFixed(1)}%
                </Typography>
                <Typography variant="subtitle1">
                  Confidence: {(prediction.confidence * 100).toFixed(1)}%
                </Typography>
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle1">
                  Home Team Form: {homeStats.winStreak > 0 ? 'Winning' : 'Losing'} Streak
                </Typography>
                <Typography variant="subtitle1">
                  Away Team Form: {awayStats.winStreak > 0 ? 'Winning' : 'Losing'} Streak
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default NextGamePrediction; 