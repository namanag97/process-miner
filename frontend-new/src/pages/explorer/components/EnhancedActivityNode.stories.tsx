import type { Meta, StoryObj } from '@storybook/react';
import ReactFlow, { ReactFlowProvider } from 'reactflow';
import 'reactflow/dist/style.css';
import { EnhancedActivityNode } from './EnhancedActivityNode';

const meta: Meta<typeof EnhancedActivityNode> = {
  title: 'Explorer/EnhancedActivityNode',
  component: EnhancedActivityNode,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  decorators: [
    (Story) => (
      <div style={{ width: '300px', height: '200px', border: '1px solid #eee' }}>
        <ReactFlowProvider>
          <ReactFlow
            nodes={[
              {
                id: '1',
                type: 'enhanced',
                position: { x: 50, y: 50 },
                data: {}, // Data will be provided by Storybook args
              },
            ]}
            nodeTypes={{ enhanced: EnhancedActivityNode }}
          >
            <Story />
          </ReactFlow>
        </ReactFlowProvider>
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof EnhancedActivityNode>;

// Fix: The component expects NodeProps, but Storybook will pass args to the component directly.
// We need to wrap it to pass the correct structure.
const Template = (args: any) => {
  return (
    <div style={{ padding: 20 }}>
       <EnhancedActivityNode 
        id="1"
        type="enhanced"
        data={args}
        zIndex={0}
        isConnectable={true}
        xPos={0}
        yPos={0}
        dragging={false}
        selected={args.isSelected}
        dragHandle=".drag-handle"
       />
    </div>
  );
};

export const Default: Story = {
  args: {
    label: 'Receive Order',
    frequency: 1250,
    frequencyPercent: 85,
    avgDuration: 3600,
  },
  render: Template as any,
};

export const StartNode: Story = {
  args: {
    ...Default.args,
    isStart: true,
  },
  render: Template as any,
};

export const EndNode: Story = {
  args: {
    ...Default.args,
    isEnd: true,
  },
  render: Template as any,
};

export const PerformanceMode: Story = {
  args: {
    ...Default.args,
    showPerformance: true,
    performanceColor: '#EF4444', // Red for poor performance
    avgDuration: 86400 * 5, // 5 days
  },
  render: Template as any,
};

export const WithRework: Story = {
  args: {
    ...Default.args,
    hasRework: true,
  },
  render: Template as any,
};
