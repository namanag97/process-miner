import type { Meta, StoryObj } from '@storybook/react';
import { ReworkTab } from './ReworkTab';

const meta: Meta<typeof ReworkTab> = {
  title: 'Analytics/ReworkTab',
  component: ReworkTab,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof ReworkTab>;

const sampleReworkData = {
  reworkPercentage: 18.5,
  totalReworkCases: 1250,
  reworkActivities: [
    {
      activity: 'Check Credit',
      reworkCount: 450,
      casesWithRework: 380,
      reworkPercentage: 25.2,
    },
    {
      activity: 'Manual Review',
      reworkCount: 200,
      casesWithRework: 180,
      reworkPercentage: 12.5,
    },
  ],
};

export const Default: Story = {
  args: {
    logId: 'test-log-id',
    data: sampleReworkData,
    loading: false,
  },
};

export const Loading: Story = {
  args: {
    logId: 'test-log-id',
    loading: true,
  },
};
