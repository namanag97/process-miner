import React from 'react';
import type { Meta, StoryObj } from '@storybook/react';
import { AlertCard, AlertList } from './AlertCard';
import type { Alert } from './AlertCard';
import { Row, Col, Typography } from 'antd';

const { Title } = Typography;

const meta: Meta<typeof AlertCard> = {
  title: 'Lumina/AlertCard',
  component: AlertCard,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof AlertCard>;

const sampleAlerts: Alert[] = [
  {
    id: '1',
    type: 'sla_breach',
    severity: 'critical',
    status: 'active',
    title: 'SLA Breach - Order #45920',
    message: 'Order processing has exceeded the 24-hour SLA by 4.5 hours. Customer escalation likely.',
    caseId: 'ORD-45920',
    activityName: 'Manager Approval',
    triggeredAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
  },
  {
    id: '2',
    type: 'bottleneck',
    severity: 'high',
    status: 'active',
    title: 'Bottleneck Detected',
    message: 'Document Review step showing 85% increase in wait time over the past 4 hours.',
    triggeredAt: new Date(Date.now() - 30 * 60 * 1000),
  },
  {
    id: '3',
    type: 'deviation',
    severity: 'medium',
    status: 'acknowledged',
    title: 'Process Deviation',
    message: '12 cases skipped the required compliance check step in the last hour.',
    triggeredAt: new Date(Date.now() - 4 * 60 * 60 * 1000),
    acknowledgedAt: new Date(Date.now() - 2 * 60 * 60 * 1000),
  },
  {
    id: '4',
    type: 'prediction',
    severity: 'low',
    status: 'resolved',
    title: 'Predicted Delay',
    message: 'Order #45930 is predicted to miss its delivery deadline by 2 days.',
    caseId: 'ORD-45930',
    triggeredAt: new Date(Date.now() - 24 * 60 * 60 * 1000),
    resolvedAt: new Date(Date.now() - 12 * 60 * 60 * 1000),
  },
];

export const Gallery: Story = {
  render: () => (
    <Row gutter={[16, 16]}>
      {sampleAlerts.map((alert) => (
        <Col xs={24} lg={12} key={alert.id}>
          <AlertCard
            alert={alert}
            onClick={() => console.log('View alert:', alert.id)}
            onAcknowledge={() => console.log('Acknowledge:', alert.id)}
            onDismiss={() => console.log('Dismiss:', alert.id)}
            onNavigateToCase={() => console.log('Navigate to case:', alert.caseId)}
          />
        </Col>
      ))}
    </Row>
  ),
};

export const Critical: Story = {
  args: {
    alert: sampleAlerts[0],
    onAcknowledge: () => console.log('Acknowledged'),
    onDismiss: () => console.log('Dismissed'),
  },
};

export const Compact: Story = {
  render: () => (
    <div style={{ maxWidth: 400 }}>
      <Title level={5}>Compact Alert List</Title>
      {sampleAlerts.map((alert) => (
        <AlertCard
          key={alert.id}
          alert={alert}
          compact
          onClick={() => console.log('View alert:', alert.id)}
        />
      ))}
    </div>
  ),
};

export const AlertListComponent: Story = {
  render: () => (
    <div style={{ maxWidth: 600 }}>
      <AlertList
        alerts={sampleAlerts}
        onAlertClick={(alert) => console.log('View alert:', alert.id)}
        onAcknowledge={(id) => console.log('Acknowledge:', id)}
        onDismiss={(id) => console.log('Dismiss:', id)}
      />
    </div>
  ),
};
