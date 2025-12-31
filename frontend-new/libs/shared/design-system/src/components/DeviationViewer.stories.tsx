import React from 'react';
import type { Meta, StoryObj } from '@storybook/react';
import { DeviationViewer } from './DeviationViewer';
import type { Deviation } from './DeviationViewer';

const meta: Meta<typeof DeviationViewer> = {
  title: 'Lumina/DeviationViewer',
  component: DeviationViewer,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof DeviationViewer>;

const sampleDeviations: Deviation[] = [
  {
    id: '1',
    caseId: 'ORD-12345',
    type: 'missing_activity',
    severity: 'critical',
    activity: 'Approve Order',
    description: 'Required approval step was skipped',
    timestamp: new Date(),
  },
  {
    id: '2',
    caseId: 'ORD-12346',
    type: 'wrong_order',
    severity: 'high',
    activity: 'Ship Order',
    expectedActivity: 'Pack Order',
    actualActivity: 'Ship Order',
    description: 'Shipment initiated before packing completion',
    timestamp: new Date(),
  },
  {
    id: '3',
    caseId: 'ORD-12347',
    type: 'timing_violation',
    severity: 'medium',
    activity: 'Process Payment',
    description: 'Payment processing exceeded 4-hour SLA',
    timestamp: new Date(),
  },
  {
    id: '4',
    caseId: 'ORD-12348',
    type: 'repeated_activity',
    severity: 'low',
    activity: 'Verify Address',
    description: 'Address verification performed 3 times',
    timestamp: new Date(),
  },
  {
    id: '5',
    caseId: 'ORD-12349',
    type: 'extra_activity',
    severity: 'info',
    activity: 'Manual Review',
    description: 'Unplanned manual review added to process',
    timestamp: new Date(),
  },
];

export const Default: Story = {
  args: {
    deviations: sampleDeviations,
    onCaseClick: (caseId) => console.log('Navigate to case:', caseId),
    showSummary: true,
  },
};

export const WithoutSummary: Story = {
  args: {
    deviations: sampleDeviations,
    showSummary: false,
  },
};

export const Empty: Story = {
  args: {
    deviations: [],
  },
};

export const Loading: Story = {
  args: {
    deviations: [],
    loading: true,
  },
};
