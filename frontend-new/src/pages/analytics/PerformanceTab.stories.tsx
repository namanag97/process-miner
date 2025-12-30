import type { Meta, StoryObj } from '@storybook/react';
import { PerformanceTab } from './PerformanceTab';

const meta: Meta<typeof PerformanceTab> = {
  title: 'Analytics/PerformanceTab',
  component: PerformanceTab,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof PerformanceTab>;

const samplePerformanceData = {
  cycleTime: {
    minSeconds: 3600,
    maxSeconds: 2592000,
    avgSeconds: 432000,
    medianSeconds: 345600,
    percentile75: 604800,
  },
  throughput: {
    casesPerDay: 42.5,
    casesPerWeek: 300,
    casesPerMonth: 1250,
  },
  topBottlenecks: [
    {
      activity: 'Manual Review',
      avgWaitingTime: 172800,
      impactScore: 0.85,
    },
    {
      activity: 'Quality Check',
      avgWaitingTime: 86400,
      impactScore: 0.45,
    },
  ],
};

export const Default: Story = {
  args: {
    logId: 'test-log-id',
    data: samplePerformanceData,
    loading: false,
  },
};

export const Loading: Story = {
  args: {
    logId: 'test-log-id',
    loading: true,
  },
};

export const Empty: Story = {
  args: {
    logId: null,
    data: undefined,
  },
};
