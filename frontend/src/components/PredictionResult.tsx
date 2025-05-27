import React from 'react';
import { Paper, Typography, Box, LinearProgress } from '@mui/material';
import { Prediction } from '../types';

interface PredictionResultProps {
  prediction: Prediction;
}

const PredictionResult: React.FC<PredictionResultProps> = ({ prediction }) => {
  const homeWinPercentage = prediction.homeWinProbability * 100;
  const awayWinPercentage = (1 - prediction.homeWinProbability) * 100;

  return (
    <Paper sx={{ p: 3, mt: 2 }}>
      <Typography variant="h5" gutterBottom align="center">
        Match Prediction
      </Typography>

      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" gutterBottom>
          {prediction.homeTeam.name} vs {prediction.awayTeam.name}
        </Typography>
        
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Typography variant="body2" sx={{ width: '100px' }}>
            {prediction.homeTeam.name}
          </Typography>
          <LinearProgress
            variant="determinate"
            value={homeWinPercentage}
            sx={{ flexGrow: 1, mx: 2, height: 10, borderRadius: 5 }}
          />
          <Typography variant="body2" sx={{ width: '60px', textAlign: 'right' }}>
            {homeWinPercentage.toFixed(1)}%
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Typography variant="body2" sx={{ width: '100px' }}>
            {prediction.awayTeam.name}
          </Typography>
          <LinearProgress
            variant="determinate"
            value={awayWinPercentage}
            sx={{ flexGrow: 1, mx: 2, height: 10, borderRadius: 5 }}
          />
          <Typography variant="body2" sx={{ width: '60px', textAlign: 'right' }}>
            {awayWinPercentage.toFixed(1)}%
          </Typography>
        </Box>
      </Box>

      <Box sx={{ textAlign: 'center' }}>
        <Typography variant="h6" color="primary">
          Predicted Winner: {prediction.predictedWinner.name}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Confidence: {(prediction.confidence * 100).toFixed(1)}%
        </Typography>
        <Typography variant="caption" color="text.secondary" display="block">
          Prediction made at: {new Date(prediction.timestamp).toLocaleString()}
        </Typography>
      </Box>
    </Paper>
  );
};

export default PredictionResult; 