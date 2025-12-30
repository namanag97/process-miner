import type { Meta, StoryObj } from '@storybook/react';
import {
  InboxOutlined,
  FileTextOutlined,
  SearchOutlined,
  FolderOpenOutlined,
  DatabaseOutlined,
  CloudUploadOutlined,
} from '@ant-design/icons';
import { EmptyState } from './EmptyState';

const meta: Meta<typeof EmptyState> = {
  title: 'Design System/EmptyState',
  component: EmptyState,
  parameters: {
    layout: 'centered',
    docs: {
      description: {
        component: `
A flexible empty state component for displaying when no data is available.
Used to guide users toward the next action when content areas are empty.

### Usage
\`\`\`tsx
import { EmptyState } from '@shared/design-system';

<EmptyState
  icon={<InboxOutlined />}
  title="No items found"
  description="Get started by creating your first item."
  actionLabel="Create Item"
  onAction={() => console.log('Create clicked')}
/>
\`\`\`
        `,
      },
    },
  },
  tags: ['autodocs'],
  argTypes: {
    icon: {
      description: 'Icon displayed above the title. Use Ant Design icons.',
      control: false,
    },
    title: {
      description: 'Primary message explaining the empty state',
      control: 'text',
    },
    description: {
      description: 'Secondary text providing context or next steps',
      control: 'text',
    },
    actionLabel: {
      description: 'Label for the call-to-action button',
      control: 'text',
    },
    onAction: {
      description: 'Callback when the action button is clicked',
      action: 'clicked',
    },
  },
};

export default meta;
type Story = StoryObj<typeof EmptyState>;

export const Default: Story = {
  args: {
    title: 'No data available',
  },
};

export const WithDescription: Story = {
  args: {
    icon: <InboxOutlined />,
    title: 'No items found',
    description: 'Start by adding your first item to get started.',
  },
};

export const WithAction: Story = {
  args: {
    icon: <FileTextOutlined />,
    title: 'No event logs uploaded',
    description: 'Upload your first event log to start analyzing your processes.',
    actionLabel: 'Upload Event Log',
    onAction: () => alert('Upload clicked!'),
  },
};

export const NoSearchResults: Story = {
  args: {
    icon: <SearchOutlined />,
    title: 'No results found',
    description: 'Try adjusting your search criteria or filters.',
    actionLabel: 'Clear Filters',
    onAction: () => console.log('Clear filters'),
  },
};

export const EmptyFolder: Story = {
  args: {
    icon: <FolderOpenOutlined />,
    title: 'This folder is empty',
    description: 'Add files to this folder to see them here.',
    actionLabel: 'Add Files',
    onAction: () => console.log('Add files'),
  },
};

export const NoDataSource: Story = {
  args: {
    icon: <DatabaseOutlined />,
    title: 'No data source connected',
    description:
      'Connect a data source to start analyzing your process mining data.',
    actionLabel: 'Connect Data Source',
    onAction: () => console.log('Connect'),
  },
};

export const MinimalNoIcon: Story = {
  args: {
    title: 'Nothing to display',
    description: 'There are no items to show at the moment.',
  },
};

export const WithoutAction: Story = {
  args: {
    icon: <InboxOutlined />,
    title: 'Coming soon',
    description: 'This feature is currently under development.',
  },
};

export const FileUpload: Story = {
  name: 'File Upload Empty State',
  args: {
    icon: <CloudUploadOutlined />,
    title: 'Drop your files here',
    description: 'Drag and drop CSV or XES files, or click to browse.',
    actionLabel: 'Browse Files',
    onAction: () => console.log('Browse'),
  },
};
