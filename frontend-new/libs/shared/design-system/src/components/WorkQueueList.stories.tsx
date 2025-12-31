import React from 'react';
import type { Meta, StoryObj } from '@storybook/react';
import { WorkQueueList } from './WorkQueueList';
import type { QueueItem } from './WorkQueueList';

const meta: Meta<typeof WorkQueueList> = {
  title: 'Lumina/WorkQueueList',
  component: WorkQueueList,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof WorkQueueList>;

const sampleItems: QueueItem[] = [
  {
    id: '1',
    type: 'escalation',
    status: 'pending',
    priority: 'critical',
    title: 'SLA Breach Escalation',
    description: 'Order #45920 requires immediate manager attention',
    caseId: 'ORD-45920',
    dueAt: new Date(Date.now() - 2 * 60 * 60 * 1000), // Overdue
    createdAt: new Date(Date.now() - 6 * 60 * 60 * 1000),
    assignee: { id: '1', name: 'John Smith' },
  },
  {
    id: '2',
    type: 'approval',
    status: 'pending',
    priority: 'high',
    title: 'Approve Large Order',
    description: 'Order value exceeds $50,000 threshold',
    caseId: 'ORD-45925',
    dueAt: new Date(Date.now() + 4 * 60 * 60 * 1000), // Due in 4 hours
    createdAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
  },
  {
    id: '3',
    type: 'review',
    status: 'in_progress',
    priority: 'medium',
    title: 'Review Compliance Documents',
    description: '5 documents pending compliance review',
    dueAt: new Date(Date.now() + 24 * 60 * 60 * 1000),
    createdAt: new Date(Date.now() - 4 * 60 * 60 * 1000),
    assignee: { id: '2', name: 'Jane Doe' },
  },
  {
    id: '4',
    type: 'automation_recommendation',
    status: 'pending',
    priority: 'low',
    title: 'Automation Opportunity',
    description: 'Consider automating address verification step',
    createdAt: new Date(Date.now() - 12 * 60 * 60 * 1000),
  },
  {
    id: '5',
    type: 'case_action',
    status: 'completed',
    priority: 'info',
    title: 'Update Customer Contact',
    description: 'Customer requested contact preference update',
    caseId: 'ORD-45800',
    createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000),
  },
];

export const Default: Story = {
  args: {
    items: sampleItems,
    onItemClick: (item) => console.log('View item:', item.id),
    onCompleteItem: (id) => console.log('Complete item:', id),
    showStats: true,
  },
};

export const WithFiltering: Story = {
  args: {
    items: sampleItems,
    onItemClick: (item) => console.log('View item:', item.id),
    filterStatus: 'pending',
  },
};

export const LimitedItems: Story = {
  args: {
    items: sampleItems,
    maxItems: 3,
    showStats: true,
  },
};

export const Empty: Story = {
  args: {
    items: [],
  },
};
