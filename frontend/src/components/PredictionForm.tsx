import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Typography,
  Paper,
  Grid,
  CircularProgress,
} from '@mui/material';
import { Team, TeamStats, MatchPredictionRequest } from '../types';
import { getTeams, getTeamStats, predictMatch } from '../services/api';

const PredictionForm: React.FC = () => {
  const [teams, setTeams] = useState<Team[]>([]);
  const [homeTeam, setHomeTeam] = useState<number>('');
  const [awayTeam, setAwayTeam] = useState<number>('');
  const [homeStats, setHomeStats] = useState<TeamStats | null>(null);
  const [awayStats, setAwayStats] = useState<TeamStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [prediction, setPrediction] = useState<any>(null);

  useEffect(() => {
    const fetchTeams = async () => {
      try {
        const teamsData = await getTeams();
        setTeams(teamsData);
      } catch (error) {
        console.error('Error fetching teams:', error);
      }
    };
    fetchTeams();
  }, []);

  const handleTeamChange = async (teamId: number, isHome: boolean) => {
    if (isHome) {
      setHomeTeam(teamId);
      try {
        const stats = await getTeamStats(teamId);
        setHomeStats(stats);
      } catch (error) {
        console.error('Error fetching home team stats:', error);
      }
    } else {
      setAwayTeam(teamId);
      try {
        const stats = await getTeamStats(teamId);
        setAwayStats(stats);
      } catch (error) {
        console.error('Error fetching away team stats:', error);
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!homeTeam || !awayTeam || !homeStats || !awayStats) return;

    setLoading(true);
    try {
      const request: MatchPredictionRequest = {
        homeTeamId: homeTeam,
        awayTeamId: awayTeam,
        homeTeamStats: homeStats,
        awayTeamStats: awayStats,
      };
      const result = await predictMatch(request);
      setPrediction(result);
    } catch (error) {
      console.error('Error making prediction:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: 800, mx: 'auto', mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        NBA Match Predictor
      </Typography>
      <form onSubmit={handleSubmit}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Home Team</InputLabel>
              <Select
                value={homeTeam}
                onChange={(e) => handleTeamChange(e.target.value as number, true)}
                label="Home Team"
              >
                {teams.map((team) => (
                  <MenuItem key={team.id} value={team.id}>
                    {team.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Away Team</InputLabel>
              <Select
                value={awayTeam}
                onChange={(e) => handleTeamChange(e.target.value as number, false)}
                label="Away Team"
              >
                {teams.map((team) => (
                  <MenuItem key={team.id} value={team.id}>
                    {team.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12}>
            <Button
              type="submit"
              variant="contained"
              color="primary"
              fullWidth
              disabled={loading || !homeTeam || !awayTeam}
            >
              {loading ? <CircularProgress size={24} /> : 'Predict Match'}
            </Button>
          </Grid>
        </Grid>
      </form>

      {prediction && (
        <Box mt={4}>
          <Typography variant="h6" gutterBottom>
            Prediction Result
          </Typography>
          <Typography>
            Winner: {prediction.predictedWinner.name}
          </Typography>
          <Typography>
            Confidence: {(prediction.confidence * 100).toFixed(1)}%
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default PredictionForm; 