import type { Meta, StoryObj } from '@storybook/react';
import { ClockCircleOutlined, UserOutlined, CheckCircleOutlined, DollarOutlined, RiseOutlined, ThunderboltOutlined } from '@ant-design/icons';
import { MetricCard } from './MetricCard';

const meta: Meta<typeof MetricCard> = {
  title: 'Design System/MetricCard',
  component: MetricCard,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: `
A card component for displaying key metrics and KPIs with optional trend indicators and status styling.

### Usage
\`\`\`tsx
import { MetricCard } from '@shared/design-system';

<MetricCard
  title="Total Cases"
  value={1234}
  prefix={<UserOutlined />}
  trend={{ value: 12.5, isPositive: true, label: 'vs last month' }}
  status="success"
/>
\`\`\`
        `,
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    title: {
      description: 'Label describing the metric',
      control: 'text',
    },
    value: {
      description: 'The main value to display (number or string)',
      control: 'text',
    },
    prefix: {
      description: 'Icon or text shown before the value',
      control: false,
    },
    suffix: {
      description: 'Text shown after the value (e.g., %, units)',
      control: 'text',
    },
    trend: {
      description: 'Trend indicator showing change from previous period',
      control: 'object',
    },
    status: {
      description: 'Visual status styling for the card',
      control: 'select',
      options: ['default', 'success', 'warning', 'error'],
    },
    loading: {
      description: 'Shows skeleton loading state',
      control: 'boolean',
    },
    onClick: {
      description: 'Makes card clickable with hover effects',
      action: 'clicked',
    },
  },
  decorators: [
    (Story) => (
      <div style={{ width: 300 }}>
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof MetricCard>;

export const Default: Story = {
  args: {
    title: 'Total Cases',
    value: 1234,
  },
};

export const WithPrefix: Story = {
  args: {
    title: 'Revenue',
    value: 45678,
    prefix: '$',
  },
};

export const WithSuffix: Story = {
  args: {
    title: 'Completion Rate',
    value: 94.5,
    suffix: '%',
  },
};

export const WithIconPrefix: Story = {
  name: 'With Icon Prefix',
  args: {
    title: 'Processing Speed',
    value: 1.2,
    suffix: 's',
    prefix: <ThunderboltOutlined />,
  },
};

export const WithPositiveTrend: Story = {
  args: {
    title: 'Active Users',
    value: 892,
    prefix: <UserOutlined />,
    trend: {
      value: 12.5,
      isPositive: true,
      label: 'vs last month',
    },
  },
};

export const WithNegativeTrend: Story = {
  args: {
    title: 'Avg Processing Time',
    value: '4.2h',
    prefix: <ClockCircleOutlined />,
    trend: {
      value: 8.3,
      isPositive: false,
      label: 'vs last week',
    },
  },
};

export const SuccessStatus: Story = {
  args: {
    title: 'Completed Tasks',
    value: 256,
    prefix: <CheckCircleOutlined />,
    status: 'success',
    trend: {
      value: 15.2,
      isPositive: true,
    },
  },
};

export const WarningStatus: Story = {
  args: {
    title: 'Pending Reviews',
    value: 42,
    status: 'warning',
  },
};

export const ErrorStatus: Story = {
  args: {
    title: 'Failed Jobs',
    value: 7,
    status: 'error',
    trend: {
      value: 3.2,
      isPositive: false,
    },
  },
};

export const Loading: Story = {
  args: {
    title: 'Loading Data',
    value: 0,
    loading: true,
  },
};

export const Clickable: Story = {
  args: {
    title: 'Total Events',
    value: 15234,
    onClick: () => alert('Card clicked!'),
  },
};

export const Complex: Story = {
  name: 'Full Featured',
  args: {
    title: 'Process Efficiency',
    value: 87.3,
    suffix: '%',
    status: 'success',
    trend: {
      value: 5.7,
      isPositive: true,
      label: 'improvement',
    },
    onClick: () => console.log('Clicked'),
  },
};

export const Currency: Story = {
  args: {
    title: 'Monthly Revenue',
    value: '2.4M',
    prefix: <DollarOutlined />,
    trend: {
      value: 18.2,
      isPositive: true,
      label: 'YoY growth',
    },
    status: 'success',
  },
};

export const GrowthMetric: Story = {
  args: {
    title: 'User Growth',
    value: '+847',
    prefix: <RiseOutlined />,
    suffix: 'users',
    trend: {
      value: 23.1,
      isPositive: true,
      label: 'this quarter',
    },
  },
};
