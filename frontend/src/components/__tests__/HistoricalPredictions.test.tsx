import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { describe, it, expect, beforeEach, vi, Mock } from 'vitest';
import HistoricalPredictions from '../HistoricalPredictions';
import { getHistoricalPredictions } from '../../services/api';
import type { Prediction } from '../../types';

// Mock the API calls
vi.mock('../../services/api', () => ({
  getHistoricalPredictions: vi.fn(),
}));

const mockPredictions: Prediction[] = [
  {
    id: 1,
    timestamp: '2024-02-20T10:00:00Z',
    homeTeam: { id: 1, name: 'Lakers' },
    awayTeam: { id: 2, name: 'Celtics' },
    predictedWinner: { id: 1, name: 'Lakers' },
    confidence: 0.75,
  },
  {
    id: 2,
    timestamp: '2024-02-19T10:00:00Z',
    homeTeam: { id: 3, name: 'Warriors' },
    awayTeam: { id: 4, name: 'Bucks' },
    predictedWinner: { id: 4, name: 'Bucks' },
    confidence: 0.65,
  },
];

describe('HistoricalPredictions', () => {
  beforeEach(() => {
    (getHistoricalPredictions as Mock).mockResolvedValue(mockPredictions);
  });

  it('renders the predictions table', async () => {
    render(<HistoricalPredictions />);
    
    await waitFor(() => {
      expect(screen.getByText(/historical predictions/i)).toBeInTheDocument();
      expect(screen.getByText(/lakers/i)).toBeInTheDocument();
      expect(screen.getByText(/celtics/i)).toBeInTheDocument();
    });
  });

  it('filters predictions by search term', async () => {
    render(<HistoricalPredictions />);
    
    await waitFor(() => {
      expect(screen.getByText(/lakers/i)).toBeInTheDocument();
    });

    const searchInput = screen.getByLabelText(/search teams/i);
    fireEvent.change(searchInput, { target: { value: 'Warriors' } });

    expect(screen.queryByText(/lakers/i)).not.toBeInTheDocument();
    expect(screen.getByText(/warriors/i)).toBeInTheDocument();
  });

  it('filters predictions by team', async () => {
    render(<HistoricalPredictions />);
    
    await waitFor(() => {
      expect(screen.getByText(/lakers/i)).toBeInTheDocument();
    });

    const teamFilter = screen.getByLabelText(/filter by team/i);
    fireEvent.mouseDown(teamFilter);
    fireEvent.click(screen.getByText('Warriors'));

    expect(screen.queryByText(/lakers/i)).not.toBeInTheDocument();
    expect(screen.getByText(/warriors/i)).toBeInTheDocument();
  });

  it('sorts predictions by date', async () => {
    render(<HistoricalPredictions />);
    
    await waitFor(() => {
      expect(screen.getByText(/date/i)).toBeInTheDocument();
    });

    const dateHeader = screen.getByText(/date/i);
    fireEvent.click(dateHeader);

    const rows = screen.getAllByRole('row');
    const firstRow = rows[1];
    expect(firstRow).toHaveTextContent('Warriors');
  });

  it('shows loading state while fetching data', () => {
    render(<HistoricalPredictions />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    (getHistoricalPredictions as Mock).mockRejectedValue(new Error('API Error'));
    
    render(<HistoricalPredictions />);
    
    await waitFor(() => {
      expect(screen.getByText(/failed to load historical predictions/i)).toBeInTheDocument();
    });
  });
}); 