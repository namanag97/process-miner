import type { Meta, StoryObj } from '@storybook/react';
import { Button } from 'antd';
import { PlusOutlined, DownloadOutlined, ShareAltOutlined } from '@ant-design/icons';
import { PageHeader } from './PageHeader';

const meta: Meta<typeof PageHeader> = {
  title: 'Design System/PageHeader',
  component: PageHeader,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof PageHeader>;

export const Default: Story = {
  args: {
    title: 'Process Explorer',
    description: 'Analyze and visualize your process mining data',
  },
};

export const WithBreadcrumb: Story = {
  args: {
    title: 'Order Process Analysis',
    description: 'View detailed insights for order processing workflow',
    breadcrumb: [
      { label: 'Home', href: '/' },
      { label: 'Process Explorer', href: '/explorer' },
      { label: 'Order Process', onClick: () => console.log('Clicked') },
    ],
  },
};

export const WithBackButton: Story = {
  args: {
    title: 'Process Details',
    description: 'Detailed view of the selected process',
    showBack: true,
    onBack: () => console.log('Back clicked'),
  },
};

export const WithActions: Story = {
  args: {
    title: 'Event Logs',
    description: 'Manage your uploaded event logs',
    actions: (
      <>
        <Button icon={<ShareAltOutlined />}>Share</Button>
        <Button icon={<DownloadOutlined />}>Export</Button>
        <Button type="primary" icon={<PlusOutlined />}>
          Upload Log
        </Button>
      </>
    ),
  },
};

export const Complete: Story = {
  args: {
    title: 'Dashboard Analytics',
    description: 'Comprehensive overview of all process metrics',
    breadcrumb: [
      { label: 'Home', href: '/' },
      { label: 'Analytics', onClick: () => console.log('Analytics') },
    ],
    showBack: true,
    onBack: () => console.log('Back clicked'),
    actions: (
      <>
        <Button icon={<DownloadOutlined />}>Export PDF</Button>
        <Button type="primary" icon={<PlusOutlined />}>
          New Report
        </Button>
      </>
    ),
  },
};

export const MinimalTitle: Story = {
  args: {
    title: 'Settings',
  },
};
