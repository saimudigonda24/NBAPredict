import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Fade,
  Grow,
  Slide,
} from '@mui/material';
import { getTeams, getTeamStats } from '../services/api';
import { Team, TeamStats } from '../types';
import { useAnimation } from '../hooks/useAnimation';

const TeamComparison: React.FC = () => {
  const [teams, setTeams] = useState<Team[]>([]);
  const [team1, setTeam1] = useState<Team | null>(null);
  const [team2, setTeam2] = useState<Team | null>(null);
  const [team1Stats, setTeam1Stats] = useState<TeamStats | null>(null);
  const [team2Stats, setTeam2Stats] = useState<TeamStats | null>(null);
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
    const fetchTeam1Stats = async () => {
      if (team1) {
        try {
          const stats = await getTeamStats(team1.id);
          setTeam1Stats(stats);
        } catch (err) {
          setError('Failed to load team 1 statistics');
        }
      }
    };
    fetchTeam1Stats();
  }, [team1]);

  useEffect(() => {
    const fetchTeam2Stats = async () => {
      if (team2) {
        try {
          const stats = await getTeamStats(team2.id);
          setTeam2Stats(stats);
        } catch (err) {
          setError('Failed to load team 2 statistics');
        }
      }
    };
    fetchTeam2Stats();
  }, [team2]);

  const renderStatComparison = (label: string, stat1: number, stat2: number) => {
    const difference = stat1 - stat2;
    const color = difference > 0 ? 'success.main' : difference < 0 ? 'error.main' : 'text.primary';

    return (
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
        <Typography>{label}</Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Typography>{stat1.toFixed(1)}</Typography>
          <Typography color={color}>
            {difference > 0 ? '+' : ''}{difference.toFixed(1)}
          </Typography>
          <Typography>{stat2.toFixed(1)}</Typography>
        </Box>
      </Box>
    );
  };

  return (
    <Fade in={isVisible} timeout={1000}>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Team Comparison
        </Typography>

        <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
          <FormControl fullWidth>
            <InputLabel>Team 1</InputLabel>
            <Select
              value={team1?.id || ''}
              label="Team 1"
              onChange={(e) => {
                const team = teams.find(t => t.id === e.target.value);
                setTeam1(team || null);
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
            <InputLabel>Team 2</InputLabel>
            <Select
              value={team2?.id || ''}
              label="Team 2"
              onChange={(e) => {
                const team = teams.find(t => t.id === e.target.value);
                setTeam2(team || null);
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

        {error && (
          <Typography color="error" sx={{ mb: 2 }}>
            {error}
          </Typography>
        )}

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
            <CircularProgress />
          </Box>
        )}

        {team1Stats && team2Stats && (
          <Grow in={!!team1Stats && !!team2Stats} timeout={1000}>
            <Box>
              <Typography variant="h6" gutterBottom>
                Statistics Comparison
              </Typography>
              {renderStatComparison('Wins', team1Stats.wins, team2Stats.wins)}
              {renderStatComparison('Losses', team1Stats.losses, team2Stats.losses)}
              {renderStatComparison('Points per Game', team1Stats.pointsPerGame, team2Stats.pointsPerGame)}
              {renderStatComparison('Points Allowed per Game', team1Stats.pointsAllowedPerGame, team2Stats.pointsAllowedPerGame)}
              {renderStatComparison('Field Goal %', team1Stats.fieldGoalPercentage * 100, team2Stats.fieldGoalPercentage * 100)}
              {renderStatComparison('3-Point %', team1Stats.threePointPercentage * 100, team2Stats.threePointPercentage * 100)}
              {renderStatComparison('Free Throw %', team1Stats.freeThrowPercentage * 100, team2Stats.freeThrowPercentage * 100)}
              {renderStatComparison('Rebounds per Game', team1Stats.reboundsPerGame, team2Stats.reboundsPerGame)}
              {renderStatComparison('Assists per Game', team1Stats.assistsPerGame, team2Stats.assistsPerGame)}
              {renderStatComparison('Steals per Game', team1Stats.stealsPerGame, team2Stats.stealsPerGame)}
              {renderStatComparison('Blocks per Game', team1Stats.blocksPerGame, team2Stats.blocksPerGame)}
              {renderStatComparison('Turnovers per Game', team1Stats.turnoversPerGame, team2Stats.turnoversPerGame)}
            </Box>
          </Grow>
        )}
      </Paper>
    </Fade>
  );
};

export default TeamComparison; 