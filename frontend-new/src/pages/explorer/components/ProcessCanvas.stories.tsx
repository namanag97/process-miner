import type { Meta, StoryObj } from '@storybook/react';
import { ProcessCanvas } from './ProcessCanvas';

const meta: Meta<typeof ProcessCanvas> = {
  title: 'Explorer/ProcessCanvas',
  component: ProcessCanvas,
  parameters: {
    layout: 'fullscreen',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof ProcessCanvas>;

const sampleNodes = [
  { id: 'start', label: 'Receive Order', frequency: 1000, isStart: true },
  { id: 'n1', label: 'Check Credit', frequency: 950 },
  { id: 'n2', label: 'Approve Order', frequency: 800 },
  { id: 'n3', label: 'Reject Order', frequency: 150 },
  { id: 'n4', label: 'Ship Goods', frequency: 780 },
  { id: 'end', label: 'Order Complete', frequency: 930, isEnd: true },
];

const sampleEdges = [
  { source: 'start', target: 'n1', frequency: 1000, performance: 3600 },
  { source: 'n1', target: 'n2', frequency: 800, performance: 86400 },
  { source: 'n1', target: 'n3', frequency: 150, performance: 43200 },
  { source: 'n2', target: 'n4', frequency: 780, performance: 172800 },
  { source: 'n4', target: 'end', frequency: 780, performance: 3600 },
  { source: 'n3', target: 'end', frequency: 150, performance: 1200 },
];

export const Default: Story = {
  args: {
    dfgNodes: sampleNodes,
    dfgEdges: sampleEdges,
  },
  render: (args) => (
    <div style={{ width: '100%', height: '600px' }}>
      <ProcessCanvas {...args} />
    </div>
  ),
};

export const Complex: Story = {
  args: {
    dfgNodes: [
      ...sampleNodes,
      { id: 'n5', label: 'Request More Info', frequency: 300 },
      { id: 'n6', label: 'Manual Review', frequency: 200 },
    ],
    dfgEdges: [
      ...sampleEdges,
      { source: 'n1', target: 'n5', frequency: 200, performance: 120000 },
      { source: 'n5', target: 'n1', frequency: 180, performance: 240000 },
      { source: 'n2', target: 'n6', frequency: 150, performance: 180000 },
      { source: 'n6', target: 'n4', frequency: 140, performance: 60000 },
    ],
  },
  render: (args) => (
    <div style={{ width: '100%', height: '800px' }}>
      <ProcessCanvas {...args} />
    </div>
  ),
};
