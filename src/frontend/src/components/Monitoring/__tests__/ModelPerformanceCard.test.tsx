import React from 'react';
import { render, screen } from '@testing-library/react';
import { ThemeProvider, createTheme } from '@mui/material';
import ModelPerformanceCard from '../ModelPerformanceCard';
import type { ModelPerformance } from '../../../services/monitoring';

const theme = createTheme();

const mockModelPerformance: ModelPerformance[] = [
  {
    modelId: '1',
    modelName: 'Model A',
    metrics: {
      accuracy: 0.95,
      latency: 150,
      throughput: 1000,
      errorRate: 0.02,
    },
    status: 'healthy',
    lastUpdated: '2025-02-15T20:00:00Z',
  },
  {
    modelId: '2',
    modelName: 'Model B',
    metrics: {
      accuracy: 0.88,
      latency: 200,
      throughput: 800,
      errorRate: 0.05,
    },
    status: 'degraded',
    lastUpdated: '2025-02-15T20:00:00Z',
  },
];

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('ModelPerformanceCard', () => {
  it('shows loading state when isLoading is true', () => {
    renderWithTheme(<ModelPerformanceCard data={[]} isLoading={true} />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('displays model performance data correctly', () => {
    renderWithTheme(<ModelPerformanceCard data={mockModelPerformance} isLoading={false} />);
    
    // Check title
    expect(screen.getByText('Model Performance')).toBeInTheDocument();
    
    // Check model status chips
    expect(screen.getByText(/Model A: healthy/i)).toBeInTheDocument();
    expect(screen.getByText(/Model B: degraded/i)).toBeInTheDocument();
    
    // Check model status chips
    mockModelPerformance.forEach(model => {
      expect(screen.getByText(`${model.modelName}: ${model.status}`)).toBeInTheDocument();
    });

    // Verify chart container exists
    expect(screen.getByTestId('model-performance-chart')).toBeInTheDocument();
  });

  it('handles empty data gracefully', () => {
    renderWithTheme(<ModelPerformanceCard data={[]} isLoading={false} />);
    expect(screen.getByText('Model Performance')).toBeInTheDocument();
    expect(screen.getByTestId('model-performance-chart')).toBeInTheDocument();
  });

  it('displays model metrics correctly', () => {
    renderWithTheme(<ModelPerformanceCard data={mockModelPerformance} isLoading={false} />);
    
    mockModelPerformance.forEach(model => {
      const chipText = `${model.modelName}: ${model.status}`;
      const chip = screen.getByText(chipText);
      expect(chip).toBeInTheDocument();
      
      // Verify chip has correct color based on status
      const chipElement = chip.closest('.MuiChip-root');
      if (model.status === 'healthy') {
        expect(chipElement).toHaveClass('MuiChip-colorSuccess');
      } else if (model.status === 'degraded') {
        expect(chipElement).toHaveClass('MuiChip-colorWarning');
      }
    });
  });
});
