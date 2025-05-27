import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import MatchPrediction from '../MatchPrediction';
import { getTeams, getTeamStats, predictMatch } from '../../services/api';
import { describe, it, expect, beforeEach, vi } from 'vitest';

// Mock the API calls
vi.mock('../../services/api');

describe('MatchPrediction', () => {
  const mockTeams = [
    { id: 1, name: 'Lakers', abbreviation: 'LAL' },
    { id: 2, name: 'Celtics', abbreviation: 'BOS' },
  ];

  const mockStats = {
    teamId: 1,
    pointsPerGame: 110.5,
    fieldGoalPercentage: 0.45,
    threePointPercentage: 0.35,
    freeThrowPercentage: 0.80,
    assistsPerGame: 25.5,
    reboundsPerGame: 45.2,
    winStreak: 3,
    lastTenGames: 0.7,
    wins: 30,
    losses: 20,
    pointsAllowedPerGame: 105.5,
    stealsPerGame: 7.5,
    blocksPerGame: 4.5,
    turnoversPerGame: 13.2
  };

  const mockPrediction = {
    id: 1,
    homeTeam: mockTeams[0],
    awayTeam: mockTeams[1],
    homeWinProbability: 0.65,
    predictedWinner: mockTeams[0],
    confidence: 0.8,
    timestamp: new Date().toISOString()
  };

  beforeEach(() => {
    vi.mocked(getTeams).mockResolvedValue(mockTeams);
    vi.mocked(getTeamStats).mockResolvedValue(mockStats);
    vi.mocked(predictMatch).mockResolvedValue(mockPrediction);
  });

  it('renders the component', async () => {
    render(<MatchPrediction />);
    expect(screen.getByText('NBA Match Predictor')).toBeInTheDocument();
  });

  it('loads teams on mount', async () => {
    render(<MatchPrediction />);
    await waitFor(() => {
      expect(getTeams).toHaveBeenCalled();
    });
  });

  it('loads team stats when teams are selected', async () => {
    render(<MatchPrediction />);
    
    // Wait for teams to load
    await waitFor(() => {
      expect(getTeams).toHaveBeenCalled();
    });

    // Select teams
    const homeTeamSelect = screen.getByRole('combobox', { name: /home team/i });
    const awayTeamSelect = screen.getByRole('combobox', { name: /away team/i });

    fireEvent.mouseDown(homeTeamSelect);
    fireEvent.click(screen.getByText('Lakers'));
    fireEvent.mouseDown(awayTeamSelect);
    fireEvent.click(screen.getByText('Celtics'));

    // Check if stats were loaded
    await waitFor(() => {
      expect(getTeamStats).toHaveBeenCalledTimes(2);
    });
  });

  it('makes prediction when predict button is clicked', async () => {
    render(<MatchPrediction />);
    
    // Wait for teams to load
    await waitFor(() => {
      expect(getTeams).toHaveBeenCalled();
    });

    // Select teams
    const homeTeamSelect = screen.getByRole('combobox', { name: /home team/i });
    const awayTeamSelect = screen.getByRole('combobox', { name: /away team/i });

    fireEvent.mouseDown(homeTeamSelect);
    fireEvent.click(screen.getByText('Lakers'));
    fireEvent.mouseDown(awayTeamSelect);
    fireEvent.click(screen.getByText('Celtics'));

    // Wait for stats to load
    await waitFor(() => {
      expect(getTeamStats).toHaveBeenCalledTimes(2);
    });

    // Click predict button
    const predictButton = screen.getByRole('button', { name: /predict match/i });
    fireEvent.click(predictButton);

    // Check if prediction was made
    await waitFor(() => {
      expect(predictMatch).toHaveBeenCalled();
    });
  });
}); 