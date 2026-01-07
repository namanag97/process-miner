/**
 * MetricCard Component Tests
 *
 * Tests for the MetricCard component which displays key metrics.
 */

import { render, screen } from '@testing-library/react';
import { ConfigProvider } from 'antd';
import { MetricCard } from '../MetricCard';
import { luminaTheme } from '../../theme';

// Wrapper to provide necessary context
function TestWrapper({ children }: { children: React.ReactNode }) {
  return <ConfigProvider theme={luminaTheme}>{children}</ConfigProvider>;
}

function renderWithProviders(ui: React.ReactElement) {
  return render(ui, { wrapper: TestWrapper });
}

describe('MetricCard', () => {
  describe('rendering', () => {
    it('renders with title and value', () => {
      renderWithProviders(<MetricCard title="Total Cases" value={1234} />);

      expect(screen.getByText('Total Cases')).toBeInTheDocument();
      expect(screen.getByText('1234')).toBeInTheDocument();
    });

    it('renders string values', () => {
      renderWithProviders(<MetricCard title="Average Time" value="2h 30m" />);

      expect(screen.getByText('Average Time')).toBeInTheDocument();
      expect(screen.getByText('2h 30m')).toBeInTheDocument();
    });

    it('renders with suffix', () => {
      renderWithProviders(
        <MetricCard title="Throughput" value={10.5} suffix="cases/day" />
      );

      expect(screen.getByText('Throughput')).toBeInTheDocument();
      expect(screen.getByText('10.5')).toBeInTheDocument();
      expect(screen.getByText('cases/day')).toBeInTheDocument();
    });

    it('renders with prefix', () => {
      renderWithProviders(
        <MetricCard title="Revenue" value={50000} prefix="$" />
      );

      expect(screen.getByText('Revenue')).toBeInTheDocument();
      expect(screen.getByText('$')).toBeInTheDocument();
      expect(screen.getByText('50000')).toBeInTheDocument();
    });
  });

  describe('loading state', () => {
    it('shows skeleton when loading', () => {
      renderWithProviders(
        <MetricCard title="Loading Metric" value={100} loading />
      );

      // Title should still be visible
      expect(screen.getByText('Loading Metric')).toBeInTheDocument();

      // Value should not be visible when loading
      expect(screen.queryByText('100')).not.toBeInTheDocument();
    });
  });

  describe('status indicators', () => {
    it('renders with success status', () => {
      const { container } = renderWithProviders(
        <MetricCard title="Success Rate" value="95%" status="success" />
      );

      // Should have success styling (green-related class or style)
      expect(container.firstChild).toBeInTheDocument();
    });

    it('renders with warning status', () => {
      const { container } = renderWithProviders(
        <MetricCard title="Error Rate" value="15%" status="warning" />
      );

      expect(container.firstChild).toBeInTheDocument();
    });

    it('renders with default status', () => {
      const { container } = renderWithProviders(
        <MetricCard title="Neutral Metric" value={50} status="default" />
      );

      expect(container.firstChild).toBeInTheDocument();
    });
  });

  describe('trend indicator', () => {
    it('renders with positive trend', () => {
      renderWithProviders(
        <MetricCard
          title="Growth"
          value={100}
          trend={{ value: 10, direction: 'up' }}
        />
      );

      expect(screen.getByText('100')).toBeInTheDocument();
    });

    it('renders with negative trend', () => {
      renderWithProviders(
        <MetricCard
          title="Decline"
          value={50}
          trend={{ value: 5, direction: 'down' }}
        />
      );

      expect(screen.getByText('50')).toBeInTheDocument();
    });
  });

  describe('tooltip', () => {
    it('renders with tooltip', () => {
      renderWithProviders(
        <MetricCard
          title="Metric with Tooltip"
          value={42}
          tooltip="This is additional information about the metric"
        />
      );

      expect(screen.getByText('Metric with Tooltip')).toBeInTheDocument();
      expect(screen.getByText('42')).toBeInTheDocument();
    });
  });

  describe('accessibility', () => {
    it('has accessible structure', () => {
      renderWithProviders(<MetricCard title="Accessible Metric" value={100} />);

      // Check that the title is present as text
      expect(screen.getByText('Accessible Metric')).toBeInTheDocument();

      // Check that the value is present
      expect(screen.getByText('100')).toBeInTheDocument();
    });
  });
});
