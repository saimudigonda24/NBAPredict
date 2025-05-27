import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  CircularProgress,
  Divider,
} from '@mui/material';
import { getTodaysGames, GameInfo } from '../services/api';

const NextGamePrediction: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [games, setGames] = useState<GameInfo[]>([]);

  useEffect(() => {
    const fetchGames = async () => {
      try {
        const todaysGames = await getTodaysGames();
        setGames(todaysGames);
      } catch (error) {
        console.error('Error fetching today\'s games:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchGames();
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (!games.length) {
    return (
      <Typography variant="h6" color="error">
        No NBA games scheduled for today.
      </Typography>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h4" gutterBottom>
          Today's NBA Games
        </Typography>
        <Grid container spacing={3}>
          {games.map((game) => (
            <Grid item xs={12} md={6} key={game.game_id}>
              <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box display="flex" alignItems="center" gap={2}>
                    <img src={game.home_team_logo} alt={game.home_team} width={48} height={48} style={{ borderRadius: 8 }} />
                    <Typography variant="h6">{game.home_team}</Typography>
                  </Box>
                  <Typography variant="h6">vs</Typography>
                  <Box display="flex" alignItems="center" gap={2}>
                    <img src={game.away_team_logo} alt={game.away_team} width={48} height={48} style={{ borderRadius: 8 }} />
                    <Typography variant="h6">{game.away_team}</Typography>
                  </Box>
                </Box>
                <Divider sx={{ my: 2 }} />
                <Typography variant="subtitle1" color="text.secondary">
                  Start Time: {game.start_time}
                </Typography>
                {game.prediction !== undefined && (
                  <Box mt={2} p={2} bgcolor="#f5f7fa" borderRadius={2}>
                    <Typography variant="subtitle2">
                      Prediction: {Math.round(game.prediction * 100)}% chance home team wins
                    </Typography>
                  </Box>
                )}
              </Paper>
            </Grid>
          ))}
        </Grid>
      </Paper>
    </Box>
  );
};

export default NextGamePrediction; 