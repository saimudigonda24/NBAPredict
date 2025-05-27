import React from 'react';
import { Box, Typography, Grid } from '@mui/material';
import { TeamStats } from '../types';

interface TeamStatsDisplayProps {
  stats: TeamStats;
}

const TeamStatsDisplay: React.FC<TeamStatsDisplayProps> = ({ stats }) => {
  const formatPercentage = (value: number) => `${(value * 100).toFixed(1)}%`;
  const formatNumber = (value: number) => value.toFixed(1);

  return (
    <Box sx={{ mt: 2 }}>
      <Typography variant="h6" gutterBottom>
        Team Statistics
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={6}>
          <Typography variant="body2" color="text.secondary">
            Points per Game
          </Typography>
          <Typography variant="body1">
            {formatNumber(stats.pointsPerGame)}
          </Typography>
        </Grid>
        <Grid item xs={6}>
          <Typography variant="body2" color="text.secondary">
            Field Goal %
          </Typography>
          <Typography variant="body1">
            {formatPercentage(stats.fieldGoalPercentage)}
          </Typography>
        </Grid>
        <Grid item xs={6}>
          <Typography variant="body2" color="text.secondary">
            Three Point %
          </Typography>
          <Typography variant="body1">
            {formatPercentage(stats.threePointPercentage)}
          </Typography>
        </Grid>
        <Grid item xs={6}>
          <Typography variant="body2" color="text.secondary">
            Free Throw %
          </Typography>
          <Typography variant="body1">
            {formatPercentage(stats.freeThrowPercentage)}
          </Typography>
        </Grid>
        <Grid item xs={6}>
          <Typography variant="body2" color="text.secondary">
            Assists per Game
          </Typography>
          <Typography variant="body1">
            {formatNumber(stats.assistsPerGame)}
          </Typography>
        </Grid>
        <Grid item xs={6}>
          <Typography variant="body2" color="text.secondary">
            Rebounds per Game
          </Typography>
          <Typography variant="body1">
            {formatNumber(stats.reboundsPerGame)}
          </Typography>
        </Grid>
        <Grid item xs={6}>
          <Typography variant="body2" color="text.secondary">
            Win Streak
          </Typography>
          <Typography variant="body1">
            {stats.winStreak}
          </Typography>
        </Grid>
        <Grid item xs={6}>
          <Typography variant="body2" color="text.secondary">
            Last 10 Games
          </Typography>
          <Typography variant="body1">
            {formatPercentage(stats.lastTenGames)}
          </Typography>
        </Grid>
      </Grid>
    </Box>
  );
};

export default TeamStatsDisplay; 