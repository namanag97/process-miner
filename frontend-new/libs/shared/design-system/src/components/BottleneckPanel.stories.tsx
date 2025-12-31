import React from 'react';
import type { Meta, StoryObj } from '@storybook/react';
import { BottleneckPanel } from './BottleneckPanel';
import type { Bottleneck } from './BottleneckPanel';

const meta: Meta<typeof BottleneckPanel> = {
  title: 'Lumina/BottleneckPanel',
  component: BottleneckPanel,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof BottleneckPanel>;

const sampleBottlenecks: Bottleneck[] = [
  {
    id: '1',
    activity: 'Manager Approval',
    averageWaitTime: 86400, // 1 day
    medianWaitTime: 72000,
    maxWaitTime: 259200, // 3 days
    caseCount: 1250,
    impactScore: 92,
    percentile: 95,
    previousActivity: 'Submit Request',
    recommendations: [
      'Consider parallel approval workflow',
      'Add automatic escalation after 24 hours',
      'Delegate approval authority to team leads',
    ],
  },
  {
    id: '2',
    activity: 'Document Review',
    averageWaitTime: 43200, // 12 hours
    medianWaitTime: 36000,
    maxWaitTime: 172800,
    caseCount: 890,
    impactScore: 78,
    percentile: 88,
    previousActivity: 'Upload Documents',
    recommendations: ['Implement automated document validation'],
  },
  {
    id: '3',
    activity: 'Quality Check',
    averageWaitTime: 21600, // 6 hours
    medianWaitTime: 18000,
    maxWaitTime: 86400,
    caseCount: 2100,
    impactScore: 65,
    percentile: 75,
    previousActivity: 'Assembly Complete',
  },
  {
    id: '4',
    activity: 'Invoice Generation',
    averageWaitTime: 7200, // 2 hours
    medianWaitTime: 5400,
    maxWaitTime: 28800,
    caseCount: 3400,
    impactScore: 45,
    percentile: 60,
  },
  {
    id: '5',
    activity: 'Final Verification',
    averageWaitTime: 3600, // 1 hour
    medianWaitTime: 2700,
    maxWaitTime: 14400,
    caseCount: 1800,
    impactScore: 28,
    percentile: 40,
  },
];

export const Default: Story = {
  args: {
    bottlenecks: sampleBottlenecks,
    onActivityClick: (activity) => console.log('Filter by activity:', activity),
    maxItems: 5,
  },
};

export const ShowAll: Story = {
  args: {
    bottlenecks: sampleBottlenecks,
    maxItems: 10,
    showImpact: true,
  },
};

export const NoImpactBars: Story = {
  args: {
    bottlenecks: sampleBottlenecks.slice(0, 3),
    showImpact: false,
  },
};

export const Empty: Story = {
  args: {
    bottlenecks: [],
  },
};
