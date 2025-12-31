import React from 'react';
import type { Meta, StoryObj } from '@storybook/react';
import { StatusBadge, SeverityBadge } from './StatusBadge';
import { Space, Card, Typography } from 'antd';

const { Title } = Typography;

const meta: Meta<typeof StatusBadge> = {
  title: 'Lumina/StatusBadge',
  component: StatusBadge,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof StatusBadge>;

export const AllStatuses: Story = {
  render: () => (
    <Space direction="vertical" size="large">
      <Space size="middle" wrap>
        <StatusBadge status="pending" />
        <StatusBadge status="running" />
        <StatusBadge status="completed" />
        <StatusBadge status="failed" />
        <StatusBadge status="stale" />
        <StatusBadge status="active" />
        <StatusBadge status="archived" />
        <StatusBadge status="draft" />
      </Space>
      
      <Title level={5}>Sizes</Title>
      <Space size="middle">
        <StatusBadge status="completed" size="small" />
        <StatusBadge status="completed" size="default" />
        <StatusBadge status="completed" size="large" />
      </Space>
      
      <Title level={5}>No Label</Title>
      <Space size="middle">
        <StatusBadge status="pending" showLabel={false} />
        <StatusBadge status="running" showLabel={false} />
        <StatusBadge status="completed" showLabel={false} />
      </Space>
      
      <Title level={5}>Dot Variant</Title>
      <Space size="middle">
        <StatusBadge status="running" dotOnly />
        <StatusBadge status="completed" dotOnly />
        <StatusBadge status="failed" dotOnly pulse />
      </Space>
    </Space>
  ),
};

export const Severities: Story = {
  render: () => (
    <Space direction="vertical" size="large">
      <Space size="middle" wrap>
        <SeverityBadge severity="critical" />
        <SeverityBadge severity="high" />
        <SeverityBadge severity="medium" />
        <SeverityBadge severity="low" />
        <SeverityBadge severity="info" />
      </Space>
      
      <Title level={5}>Compact</Title>
      <Space size="middle">
        <SeverityBadge severity="critical" showLabel={false} />
        <SeverityBadge severity="high" showLabel={false} />
        <SeverityBadge severity="medium" showLabel={false} />
      </Space>
    </Space>
  ),
};

export const Interactive: Story = {
  args: {
    status: 'running',
    showLabel: true,
    size: 'default',
  },
};
