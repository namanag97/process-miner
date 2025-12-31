import React from 'react';
import type { Meta, StoryObj } from '@storybook/react';
import { ObjectCard, ObjectCardGrid } from './ObjectCard';
import { Button, Space } from 'antd';
import { EditOutlined, DeleteOutlined, DownloadOutlined } from '@ant-design/icons';

const meta: Meta<typeof ObjectCard> = {
  title: 'Lumina/ObjectCard',
  component: ObjectCard,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof ObjectCard>;

export const Gallery: Story = {
  render: () => (
    <ObjectCardGrid columns={3}>
      <ObjectCard
        type="workspace"
        title="Procurement Analysis"
        subtitle="Shared with 12 users"
        status="active"
        metadata={[
          { label: 'Processes', value: 8 },
          { label: 'Created', value: '2d ago' },
        ]}
        timestamp="Dec 15, 2024"
        onClick={() => {}}
      />
      
      <ObjectCard
        type="event_log"
        title="SAP_Export_2024.csv"
        subtitle="1.2 GB • CSV Format"
        status="completed"
        metadata={[
          { label: 'Events', value: '8.4M' },
          { label: 'Cases', value: '250K' },
          { label: 'Quality', value: '98%' },
        ]}
        actions={
          <Space>
            <Button size="small" icon={<DownloadOutlined />} />
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Space>
        }
        onClick={() => {}}
      />
      
      <ObjectCard
        type="prediction"
        title="SLA Breach Predictor"
        subtitle="Next Activity model"
        status="running"
        metadata={[
          { label: 'Accuracy', value: '94.2%' },
          { label: 'Drift', value: 'Low' },
        ]}
        onClick={() => {}}
      />

      <ObjectCard
        type="model"
        title="O2C Standard BPMN"
        subtitle="Inductive Miner discovery"
        status="draft"
        metadata={[
          { label: 'Fitness', value: '0.85' },
          { label: 'Precision', value: '0.91' },
        ]}
        onClick={() => {}}
      />

      <ObjectCard
        type="connection"
        title="PostgreSQL Prod"
        subtitle="db.atlassian.com:5432"
        status="active"
        metadata={[
          { label: 'Tables', value: 42 },
          { label: 'Last Sync', value: '1h ago' },
        ]}
        onClick={() => {}}
      />

      <ObjectCard
        type="alert"
        title="Late Shipment Detected"
        subtitle="Case #ORD-45920"
        status="failed"
        metadata={[
          { label: 'Delay', value: '4.5h' },
          { label: 'Value', value: '$12,400' },
        ]}
        actions={<Button size="small" type="primary">Acknowledge</Button>}
        onClick={() => {}}
      />
    </ObjectCardGrid>
  ),
};

export const Selected: Story = {
  args: {
    type: 'workspace',
    title: 'Selected Workspace',
    subtitle: 'This card is currently selected',
    selected: true,
    status: 'active',
  },
};

export const Loading: Story = {
  args: {
    type: 'event_log',
    title: 'Loading Data...',
    loading: true,
  },
};
