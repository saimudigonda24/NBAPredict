import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  TableSortLabel,
  Fade,
  Grow,
  Slide,
} from '@mui/material';
import { getHistoricalPredictions } from '../services/api';
import { Prediction } from '../types';
import { useAnimation } from '../hooks/useAnimation';

type SortField = 'date' | 'homeTeam' | 'awayTeam' | 'winner' | 'confidence';
type SortOrder = 'asc' | 'desc';

const HistoricalPredictions: React.FC = () => {
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState<SortField>('date');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [filterTeam, setFilterTeam] = useState<string>('');
  const isVisible = useAnimation(300);

  useEffect(() => {
    const fetchPredictions = async () => {
      setLoading(true);
      try {
        const data = await getHistoricalPredictions();
        setPredictions(data);
      } catch (err) {
        setError('Failed to load historical predictions');
      } finally {
        setLoading(false);
      }
    };
    fetchPredictions();
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const handleSort = (field: SortField) => {
    if (field === sortField) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('asc');
    }
  };

  const getUniqueTeams = () => {
    const teams = new Set<string>();
    predictions.forEach(prediction => {
      teams.add(prediction.homeTeam.name);
      teams.add(prediction.awayTeam.name);
    });
    return Array.from(teams).sort();
  };

  const filteredAndSortedPredictions = predictions
    .filter(prediction => {
      const searchLower = searchTerm.toLowerCase();
      const matchesSearch = 
        prediction.homeTeam.name.toLowerCase().includes(searchLower) ||
        prediction.awayTeam.name.toLowerCase().includes(searchLower) ||
        prediction.predictedWinner.name.toLowerCase().includes(searchLower);
      
      const matchesTeam = !filterTeam || 
        prediction.homeTeam.name === filterTeam ||
        prediction.awayTeam.name === filterTeam;

      return matchesSearch && matchesTeam;
    })
    .sort((a, b) => {
      let comparison = 0;
      switch (sortField) {
        case 'date':
          comparison = new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
          break;
        case 'homeTeam':
          comparison = a.homeTeam.name.localeCompare(b.homeTeam.name);
          break;
        case 'awayTeam':
          comparison = a.awayTeam.name.localeCompare(b.awayTeam.name);
          break;
        case 'winner':
          comparison = a.predictedWinner.name.localeCompare(b.predictedWinner.name);
          break;
        case 'confidence':
          comparison = a.confidence - b.confidence;
          break;
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });

  return (
    <Fade in={isVisible} timeout={1000}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Historical Predictions
        </Typography>

        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Search Teams"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              variant="outlined"
              size="small"
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth size="small">
              <InputLabel>Filter by Team</InputLabel>
              <Select
                value={filterTeam}
                label="Filter by Team"
                onChange={(e) => setFilterTeam(e.target.value)}
              >
                <MenuItem value="">All Teams</MenuItem>
                {getUniqueTeams().map(team => (
                  <MenuItem key={team} value={team}>{team}</MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
            <CircularProgress />
          </Box>
        )}

        {error && (
          <Typography color="error" sx={{ mt: 2 }}>
            {error}
          </Typography>
        )}

        {!loading && !error && (
          <Grow in={!loading && !error} timeout={1000}>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>
                      <TableSortLabel
                        active={sortField === 'date'}
                        direction={sortField === 'date' ? sortOrder : 'asc'}
                        onClick={() => handleSort('date')}
                      >
                        Date
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>
                      <TableSortLabel
                        active={sortField === 'homeTeam'}
                        direction={sortField === 'homeTeam' ? sortOrder : 'asc'}
                        onClick={() => handleSort('homeTeam')}
                      >
                        Home Team
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>
                      <TableSortLabel
                        active={sortField === 'awayTeam'}
                        direction={sortField === 'awayTeam' ? sortOrder : 'asc'}
                        onClick={() => handleSort('awayTeam')}
                      >
                        Away Team
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>
                      <TableSortLabel
                        active={sortField === 'winner'}
                        direction={sortField === 'winner' ? sortOrder : 'asc'}
                        onClick={() => handleSort('winner')}
                      >
                        Predicted Winner
                      </TableSortLabel>
                    </TableCell>
                    <TableCell>
                      <TableSortLabel
                        active={sortField === 'confidence'}
                        direction={sortField === 'confidence' ? sortOrder : 'asc'}
                        onClick={() => handleSort('confidence')}
                      >
                        Confidence
                      </TableSortLabel>
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredAndSortedPredictions.map((prediction, index) => (
                    <Slide
                      key={prediction.id}
                      direction="up"
                      in={true}
                      timeout={500}
                      style={{ transitionDelay: `${index * 50}ms` }}
                    >
                      <TableRow hover>
                        <TableCell>{formatDate(prediction.timestamp)}</TableCell>
                        <TableCell>{prediction.homeTeam.name}</TableCell>
                        <TableCell>{prediction.awayTeam.name}</TableCell>
                        <TableCell>{prediction.predictedWinner.name}</TableCell>
                        <TableCell>{(prediction.confidence * 100).toFixed(1)}%</TableCell>
                      </TableRow>
                    </Slide>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Grow>
        )}
      </Paper>
    </Fade>
  );
};

export default HistoricalPredictions; 