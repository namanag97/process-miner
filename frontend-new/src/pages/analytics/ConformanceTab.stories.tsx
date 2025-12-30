import type { Meta, StoryObj } from '@storybook/react';
import { ConformanceTab } from './ConformanceTab';

const meta: Meta<typeof ConformanceTab> = {
  title: 'Analytics/ConformanceTab',
  component: ConformanceTab,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof ConformanceTab>;

export const Default: Story = {
  args: {
    logId: 'test-log-id',
  },
};
