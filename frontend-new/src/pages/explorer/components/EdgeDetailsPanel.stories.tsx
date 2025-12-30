import type { Meta, StoryObj } from '@storybook/react';
import { EdgeDetailsPanel } from './EdgeDetailsPanel';

const meta: Meta<typeof EdgeDetailsPanel> = {
  title: 'Explorer/EdgeDetailsPanel',
  component: EdgeDetailsPanel,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof EdgeDetailsPanel>;

const sampleEdge = {
  id: 'e-1',
  source: 'Check Credit',
  target: 'Approve Order',
  frequency: 850,
  frequencyPercent: 12.5,
  avgDurationSeconds: 86400,
  minDurationSeconds: 3600,
  maxDurationSeconds: 172800,
  probability: 0.85,
};

export const Default: Story = {
  args: {
    edge: sampleEdge,
    totalCases: 1000,
  },
  render: (args) => (
    <div style={{ width: '320px', border: '1px solid #eee' }}>
      <EdgeDetailsPanel {...args} />
    </div>
  ),
};

export const CriticalPath: Story = {
  args: {
    edge: {
      ...sampleEdge,
      avgDurationSeconds: 151200, // Close to max
    },
    totalCases: 1000,
  },
  render: (args) => (
    <div style={{ width: '320px', border: '1px solid #eee' }}>
      <EdgeDetailsPanel {...args} />
    </div>
  ),
};

export const Empty: Story = {
  args: {
    edge: null,
  },
  render: (args) => (
    <div style={{ width: '320px', height: '200px', border: '1px solid #eee' }}>
      <EdgeDetailsPanel {...args} />
    </div>
  ),
};
