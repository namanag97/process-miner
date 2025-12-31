import React from 'react';
import type { Meta, StoryObj } from '@storybook/react';
import { IntegrationPanel } from './IntegrationPanel';
import type { Integration } from './IntegrationPanel';

const meta: Meta<typeof IntegrationPanel> = {
  title: 'Lumina/IntegrationPanel',
  component: IntegrationPanel,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof IntegrationPanel>;

const sampleIntegrations: Integration[] = [
  {
    id: '1',
    type: 'slack',
    name: 'Slack - #process-alerts',
    status: 'active',
    enabled: true,
    lastSyncAt: new Date(Date.now() - 10 * 60 * 1000),
  },
  {
    id: '2',
    type: 'jira',
    name: 'Jira - Process Mining Project',
    status: 'active',
    enabled: true,
    lastSyncAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
  },
  {
    id: '3',
    type: 'email',
    name: 'SMTP - alerts@company.com',
    status: 'failed',
    enabled: false,
    lastSyncAt: new Date(Date.now() - 24 * 60 * 60 * 1000),
    errorMessage: 'SMTP authentication failed. Please check credentials.',
  },
  {
    id: '4',
    type: 'webhook',
    name: 'Custom Webhook',
    description: 'Sends data to internal API',
    status: 'active',
    enabled: true,
    lastSyncAt: new Date(Date.now() - 30 * 60 * 1000),
  },
];

export const Default: Story = {
  args: {
    integrations: sampleIntegrations,
    onConnect: (type) => console.log('Connect:', type),
    onDisconnect: (id) => console.log('Disconnect:', id),
    onConfigure: (integration) => console.log('Configure:', integration),
    onToggleEnabled: (id, enabled) => console.log('Toggle:', id, enabled),
    onSync: (id) => console.log('Sync:', id),
  },
};

export const SingleIntegration: Story = {
  args: {
    integrations: [sampleIntegrations[0]],
    onConnect: (type) => console.log('Connect:', type),
    onDisconnect: (id) => console.log('Disconnect:', id),
  },
};

export const WithErrors: Story = {
  args: {
    integrations: sampleIntegrations.filter((i) => i.status === 'failed' || i.status === 'active'),
    onConnect: (type) => console.log('Connect:', type),
    onConfigure: (integration) => console.log('Configure:', integration),
  },
};

export const Empty: Story = {
  args: {
    integrations: [],
    onConnect: (type) => console.log('Connect:', type),
  },
};
