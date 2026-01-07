import React from 'react';
import type { Meta, StoryObj } from '@storybook/react';
import { PredictionModelCard } from './PredictionModelCard';
import type { PredictionModel } from './PredictionModelCard';
import { Row, Col } from 'antd';

const meta: Meta<typeof PredictionModelCard> = {
  title: 'Lumina/PredictionModelCard',
  component: PredictionModelCard,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof PredictionModelCard>;

const sampleModels: PredictionModel[] = [
  {
    id: '1',
    name: 'SLA Breach Predictor',
    type: 'next_activity',
    status: 'active',
    accuracy: 94,
    f1Score: 0.92,
    driftLevel: 'low',
    lastTrainedAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
    predictionCount: 15420,
    version: '2.1',
  },
  {
    id: '2',
    name: 'Case Duration Model',
    type: 'remaining_time',
    status: 'completed',
    accuracy: 87,
    f1Score: 0.84,
    driftLevel: 'none',
    lastTrainedAt: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000),
    predictionCount: 8900,
    version: '1.3',
  },
  {
    id: '3',
    name: 'Order Outcome Classifier',
    type: 'outcome',
    status: 'active',
    accuracy: 78,
    f1Score: 0.75,
    driftLevel: 'high',
    lastTrainedAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
    predictionCount: 24500,
    version: '1.0',
  },
  {
    id: '4',
    name: 'Resource Allocation',
    type: 'resource',
    status: 'running',
    driftLevel: 'none',
    version: '0.9',
  },
];

export const Gallery: Story = {
  render: () => (
    <Row gutter={[16, 16]}>
      {sampleModels.map((model) => (
        <Col xs={24} sm={12} lg={8} key={model.id}>
          <PredictionModelCard
            model={model}
            onClick={() => console.log('View model:', model.id)}
            onDeploy={() => console.log('Deploy model:', model.id)}
            onRetrain={() => console.log('Retrain model:', model.id)}
            onViewPredictions={() => console.log('View predictions:', model.id)}
          />
        </Col>
      ))}
    </Row>
  ),
};

export const HighDrift: Story = {
  args: {
    model: sampleModels[2],
    onRetrain: () => console.log('Retrain triggered'),
  },
};

export const Compact: Story = {
  args: {
    model: sampleModels[0],
    compact: true,
  },
};

export const Loading: Story = {
  args: {
    model: sampleModels[0],
    loading: true,
  },
};
