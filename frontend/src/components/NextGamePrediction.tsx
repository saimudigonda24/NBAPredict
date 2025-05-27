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

// NBA team primary colors (abbreviation: hex color)
const TEAM_COLORS: Record<string, string> = {
  atl: '#E03A3E', bos: '#007A33', bkn: '#000000', cha: '#1D1160', chi: '#CE1141',
  cle: '#6F263D', dal: '#00538C', den: '#0E2240', det: '#C8102E', gsw: '#1D428A',
  hou: '#CE1141', ind: '#002D62', lac: '#C8102E', lal: '#552583', mem: '#5D76A9',
  mia: '#98002E', mil: '#00471B', min: '#0C2340', nop: '#0C2340', nyk: '#006BB6',
  okc: '#007AC1', orl: '#0077C0', phi: '#006BB6', phx: '#1D1160', por: '#E03A3E',
  sac: '#5A2D81', sas: '#C4CED4', tor: '#CE1141', uta: '#002B5C', was: '#002B5C',
};

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

  // Helper to get color by team abbreviation
  const getTeamColor = (abbr: string) => TEAM_COLORS[abbr.toLowerCase()] || '#eee';

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
                    <Box
                      sx={{
                        backgroundColor: getTeamColor(game.home_team),
                        color: '#fff',
                        borderRadius: 1,
                        px: 2,
                        py: 0.5,
                        fontWeight: 600,
                        fontSize: '1.1rem',
                        minWidth: 80,
                        textAlign: 'center',
                      }}
                    >
                      {game.home_team}
                    </Box>
                  </Box>
                  <Typography variant="h6">vs</Typography>
                  <Box display="flex" alignItems="center" gap={2}>
                    <img src={game.away_team_logo} alt={game.away_team} width={48} height={48} style={{ borderRadius: 8 }} />
                    <Box
                      sx={{
                        backgroundColor: getTeamColor(game.away_team),
                        color: '#fff',
                        borderRadius: 1,
                        px: 2,
                        py: 0.5,
                        fontWeight: 600,
                        fontSize: '1.1rem',
                        minWidth: 80,
                        textAlign: 'center',
                      }}
                    >
                      {game.away_team}
                    </Box>
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