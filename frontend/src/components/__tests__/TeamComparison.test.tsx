import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { describe, it, expect, beforeEach, vi } from 'vitest';
import TeamComparison from '../TeamComparison';
import { getTeams, getTeamStats } from '../../services/api';

// Mock the API calls
vi.mock('../../services/api');

describe('TeamComparison', () => {
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

  beforeEach(() => {
    vi.mocked(getTeams).mockResolvedValue(mockTeams);
    vi.mocked(getTeamStats).mockResolvedValue(mockStats);
  });

  it('renders team selectors', async () => {
    render(<TeamComparison />);
    
    await waitFor(() => {
      expect(screen.getByRole('combobox', { name: /team 1/i })).toBeInTheDocument();
      expect(screen.getByRole('combobox', { name: /team 2/i })).toBeInTheDocument();
    });
  });

  it('loads and displays team stats when teams are selected', async () => {
    render(<TeamComparison />);
    
    const team1Select = screen.getByRole('combobox', { name: /team 1/i });
    const team2Select = screen.getByRole('combobox', { name: /team 2/i });

    fireEvent.mouseDown(team1Select);
    fireEvent.click(screen.getByText('Lakers'));
    fireEvent.mouseDown(team2Select);
    fireEvent.click(screen.getByText('Celtics'));

    await waitFor(() => {
      expect(getTeamStats).toHaveBeenCalledTimes(2);
    });
  });

  it('shows loading state while fetching data', async () => {
    vi.mocked(getTeamStats).mockImplementation(() => new Promise(resolve => setTimeout(() => resolve(mockStats), 100)));
    
    render(<TeamComparison />);
    
    const team1Select = screen.getByRole('combobox', { name: /team 1/i });
    fireEvent.mouseDown(team1Select);
    fireEvent.click(screen.getByText('Lakers'));

    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    vi.mocked(getTeamStats).mockRejectedValue(new Error('API Error'));
    
    render(<TeamComparison />);
    
    const team1Select = screen.getByRole('combobox', { name: /team 1/i });
    fireEvent.mouseDown(team1Select);
    fireEvent.click(screen.getByText('Lakers'));

    await waitFor(() => {
      expect(screen.getByText(/failed to load team 1 statistics/i)).toBeInTheDocument();
    });
  });
}); 