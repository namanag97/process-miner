import type { Meta, StoryObj } from '@storybook/react';
import { ProcessKPIBar } from './ProcessKPIBar';

const meta: Meta<typeof ProcessKPIBar> = {
  title: 'Explorer/ProcessKPIBar',
  component: ProcessKPIBar,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof ProcessKPIBar>;

export const Default: Story = {
  args: {
    kpis: {
      totalCases: 12500,
      uniqueVariants: 420,
      uniqueActivities: 18,
      avgThroughputTime: 432000, // 5 days
      happyPathPercent: 72,
      reworkRate: 8.5,
      conformanceScore: 94,
    },
  },
};

export const WithTrends: Story = {
  args: {
    kpis: {
      totalCases: 12500,
      uniqueVariants: 420,
      uniqueActivities: 18,
      avgThroughputTime: 432000,
      happyPathPercent: 72,
      reworkRate: 8.5,
      conformanceScore: 94,
    },
    trends: {
      totalCases: { direction: 'up', percentChange: 12 },
      avgThroughputTime: { direction: 'down', percentChange: 5 },
      happyPathPercent: { direction: 'up', percentChange: 2 },
    },
  },
};

export const Compact: Story = {
  args: {
    ...Default.args,
    compact: true,
  },
};

export const PoorPerformance: Story = {
  args: {
    kpis: {
      totalCases: 5000,
      uniqueVariants: 1200,
      uniqueActivities: 45,
      avgThroughputTime: 1209600, // 14 days
      happyPathPercent: 15,
      reworkRate: 45.2,
      conformanceScore: 42,
    },
  },
};
