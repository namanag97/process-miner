import type { Meta, StoryObj } from '@storybook/react';
import { Typography } from 'antd';
import { AppShell } from './AppShell';
import { PageHeader } from './PageHeader';
import { MetricCard } from './MetricCard';

const { Title, Paragraph } = Typography;

const meta: Meta<typeof AppShell> = {
  title: 'Design System/AppShell',
  component: AppShell,
  parameters: {
    layout: 'fullscreen',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof AppShell>;

const SampleContent = () => (
  <div>
    <PageHeader
      title="Dashboard"
      description="Overview of your process mining analytics"
    />
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 16 }}>
      <MetricCard title="Total Cases" value={1234} />
      <MetricCard
        title="Active Processes"
        value={42}
        trend={{ value: 12.5, isPositive: true }}
      />
      <MetricCard
        title="Completion Rate"
        value={94.5}
        suffix="%"
        status="success"
      />
    </div>
    <div style={{ marginTop: 24 }}>
      <Title level={4}>Welcome to Process Miner</Title>
      <Paragraph>
        This is a sample content area demonstrating the AppShell layout component.
        The sidebar navigation allows you to explore different sections of the application.
      </Paragraph>
    </div>
  </div>
);

export const Default: Story = {
  args: {
    children: <SampleContent />,
    activeId: 'home',
    onNavigate: (id) => console.log('Navigate to:', id),
  },
};

export const WithCustomUser: Story = {
  args: {
    children: <SampleContent />,
    userName: 'John Doe',
    userEmail: 'john.doe@company.com',
    activeId: 'explorer',
    onNavigate: (id) => console.log('Navigate to:', id),
  },
};

export const WithNotifications: Story = {
  args: {
    children: <SampleContent />,
    userName: 'Jane Smith',
    userEmail: 'jane.smith@company.com',
    notificationCount: 5,
    activeId: 'analytics',
    onNavigate: (id) => console.log('Navigate to:', id),
  },
};

export const WithCustomLogo: Story = {
  args: {
    children: <SampleContent />,
    logo: (
      <div style={{ fontWeight: 700, fontSize: 18, color: '#2563EB' }}>
        Custom Logo
      </div>
    ),
    logoCollapsed: (
      <div style={{ fontWeight: 700, fontSize: 20, color: '#2563EB' }}>
        CL
      </div>
    ),
    activeId: 'logs',
    onNavigate: (id) => console.log('Navigate to:', id),
  },
};

export const AIInsightsActive: Story = {
  args: {
    children: (
      <div>
        <PageHeader
          title="AI Insights"
          description="Discover patterns and anomalies in your processes"
        />
        <Paragraph>
          AI-powered insights help you identify bottlenecks, predict outcomes,
          and optimize your business processes.
        </Paragraph>
      </div>
    ),
    activeId: 'ai-insights',
    onNavigate: (id) => console.log('Navigate to:', id),
  },
};

export const SettingsActive: Story = {
  args: {
    children: (
      <div>
        <PageHeader title="Settings" description="Manage your application preferences" />
        <Paragraph>Configure your account and application settings here.</Paragraph>
      </div>
    ),
    activeId: 'settings',
    onNavigate: (id) => console.log('Navigate to:', id),
  },
};

export const TestBenchActive: Story = {
  args: {
    children: (
      <div>
        <PageHeader
          title="Test Bench"
          description="Experiment with process mining features"
        />
        <Paragraph>
          Use the test bench to experiment with different configurations and features.
        </Paragraph>
      </div>
    ),
    activeId: 'test-bench',
    userName: 'Developer',
    userEmail: 'dev@example.com',
    onNavigate: (id) => console.log('Navigate to:', id),
  },
};
