import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  CircularProgress,
  LinearProgress,
  Fade,
  Grow,
  Slide,
} from '@mui/material';
import { getTeams, getTeamStats, predictMatch } from '../services/api';
import { Team, TeamStats, Prediction, MatchPredictionRequest } from '../types';
import { useAnimation } from '../hooks/useAnimation';

const MatchPrediction: React.FC = () => {
  const [teams, setTeams] = useState<Team[]>([]);
  const [homeTeam, setHomeTeam] = useState<Team | null>(null);
  const [awayTeam, setAwayTeam] = useState<Team | null>(null);
  const [homeStats, setHomeStats] = useState<TeamStats | null>(null);
  const [awayStats, setAwayStats] = useState<TeamStats | null>(null);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const isVisible = useAnimation(300);

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const data = await getTeams();
        setTeams(data);
      } catch (err) {
        setError('Failed to load teams');
      }
    };
    fetchTeams();
  }, []);

  useEffect(() => {
    const fetchHomeStats = async () => {
      if (homeTeam) {
        try {
          const stats = await getTeamStats(homeTeam.id);
          setHomeStats(stats);
        } catch (err) {
          setError('Failed to load home team statistics');
        }
      }
    };
    fetchHomeStats();
  }, [homeTeam]);

  useEffect(() => {
    const fetchAwayStats = async () => {
      if (awayTeam) {
        try {
          const stats = await getTeamStats(awayTeam.id);
          setAwayStats(stats);
        } catch (err) {
          setError('Failed to load away team statistics');
        }
      }
    };
    fetchAwayStats();
  }, [awayTeam]);

  const handlePredict = async () => {
    if (!homeTeam || !awayTeam || !homeStats || !awayStats) return;

    setLoading(true);
    setError(null);
    try {
      const request: MatchPredictionRequest = {
        homeTeamId: homeTeam.id,
        awayTeamId: awayTeam.id,
        homeTeamStats: homeStats,
        awayTeamStats: awayStats
      };
      const result = await predictMatch(request);
      setPrediction(result);
    } catch (err) {
      setError('Failed to generate prediction');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Fade in={isVisible} timeout={1000}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Match Prediction
        </Typography>

        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <FormControl fullWidth>
            <InputLabel>Home Team</InputLabel>
            <Select
              value={homeTeam?.id || ''}
              label="Home Team"
              onChange={(e) => {
                const team = teams.find(t => t.id === e.target.value);
                setHomeTeam(team || null);
              }}
            >
              {teams.map(team => (
                <MenuItem key={team.id} value={team.id}>
                  {team.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl fullWidth>
            <InputLabel>Away Team</InputLabel>
            <Select
              value={awayTeam?.id || ''}
              label="Away Team"
              onChange={(e) => {
                const team = teams.find(t => t.id === e.target.value);
                setAwayTeam(team || null);
              }}
            >
              {teams.map(team => (
                <MenuItem key={team.id} value={team.id}>
                  {team.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>

        {homeStats && (
          <Slide direction="right" in={!!homeStats} timeout={500}>
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                {homeTeam?.name} Statistics
              </Typography>
              <Typography>Wins: {homeStats.wins}</Typography>
              <Typography>Losses: {homeStats.losses}</Typography>
              <Typography>Points per Game: {homeStats.pointsPerGame}</Typography>
            </Box>
          </Slide>
        )}

        {awayStats && (
          <Slide direction="left" in={!!awayStats} timeout={500}>
            <Box sx={{ mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                {awayTeam?.name} Statistics
              </Typography>
              <Typography>Wins: {awayStats.wins}</Typography>
              <Typography>Losses: {awayStats.losses}</Typography>
              <Typography>Points per Game: {awayStats.pointsPerGame}</Typography>
            </Box>
          </Slide>
        )}

        <Button
          variant="contained"
          onClick={handlePredict}
          disabled={!homeTeam || !awayTeam || loading}
          fullWidth
          sx={{ mb: 3 }}
        >
          {loading ? <CircularProgress size={24} /> : 'Predict Match'}
        </Button>

        {error && (
          <Typography color="error" sx={{ mb: 2 }}>
            {error}
          </Typography>
        )}

        {prediction && (
          <Grow in={!!prediction} timeout={1000}>
            <Box>
              <Typography variant="h6" gutterBottom>
                Prediction Results
              </Typography>
              <Typography>
                Predicted Winner: {prediction.predictedWinner.name}
              </Typography>
              <Typography gutterBottom>
                Confidence: {(prediction.confidence * 100).toFixed(1)}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={prediction.confidence * 100}
                sx={{ height: 10, borderRadius: 5 }}
              />
            </Box>
          </Grow>
        )}
      </Paper>
    </Fade>
  );
};

export default MatchPrediction; 