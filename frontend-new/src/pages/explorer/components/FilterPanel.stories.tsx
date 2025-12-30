import type { Meta, StoryObj } from '@storybook/react';
import { FilterPanel } from './FilterPanel';

const meta: Meta<typeof FilterPanel> = {
  title: 'Explorer/FilterPanel',
  component: FilterPanel,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof FilterPanel>;

const sampleFilterOptions = {
  activities: [
    'Receive Order',
    'Check Credit',
    'Approve Order',
    'Reject Order',
    'Ship Goods',
    'Order Complete',
    'Manual Review',
    'Request More Info',
  ],
  resources: ['System', 'John Doe', 'Jane Smith', 'AI Agent'],
  timeRange: {
    start: '2023-01-01T00:00:00Z',
    end: '2023-12-31T23:59:59Z',
  },
  caseDuration: {
    min: 3600,
    max: 2592000,
    mean: 432000,
    p90: 1209600,
  },
};

export const Default: Story = {
  args: {
    filterOptions: sampleFilterOptions,
    appliedFilters: [],
  },
  render: (args) => (
    <div style={{ width: '300px', height: '800px', border: '1px solid #eee' }}>
      <FilterPanel {...args} />
    </div>
  ),
};

export const WithAppliedFilters: Story = {
  args: {
    filterOptions: sampleFilterOptions,
    appliedFilters: [
      {
        id: '1',
        type: 'activity',
        label: 'With: Receive Order',
        value: { mode: 'include', activities: ['Receive Order'] },
        color: 'green',
      },
      {
        id: '2',
        type: 'performance',
        label: 'Duration: > 5 days',
        value: { min: 432000, max: 2592000 },
        color: 'orange',
      },
    ],
  },
  render: (args) => (
    <div style={{ width: '300px', height: '800px', border: '1px solid #eee' }}>
      <FilterPanel {...args} />
    </div>
  ),
};
