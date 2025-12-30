import type { Meta, StoryObj } from '@storybook/react';
import { ActivityDetailsPanel } from './ActivityDetailsPanel';

const meta: Meta<typeof ActivityDetailsPanel> = {
  title: 'Explorer/ActivityDetailsPanel',
  component: ActivityDetailsPanel,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof ActivityDetailsPanel>;

const sampleActivity = {
  id: 'act-1',
  name: 'Receive Order',
  totalOccurrences: 1250,
  casePercentage: 85,
  avgDurationSeconds: 3600,
  minDurationSeconds: 1200,
  maxDurationSeconds: 14400,
  resources: ['System', 'John Doe', 'Jane Smith', 'AI Agent', 'Expert Reviewer', 'Supervisor'],
};

export const Default: Story = {
  args: {
    activity: sampleActivity,
  },
  render: (args) => (
    <div style={{ width: '320px', border: '1px solid #eee' }}>
      <ActivityDetailsPanel {...args} />
    </div>
  ),
};

export const Empty: Story = {
  args: {
    activity: null,
  },
  render: (args) => (
    <div style={{ width: '320px', height: '200px', border: '1px solid #eee' }}>
      <ActivityDetailsPanel {...args} />
    </div>
  ),
};
