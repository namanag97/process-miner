import type { Meta, StoryObj } from '@storybook/react';
import { SkeletonCard } from './SkeletonCard';

const meta: Meta<typeof SkeletonCard> = {
  title: 'Design System/SkeletonCard',
  component: SkeletonCard,
  parameters: {
    layout: 'centered',
  },
  tags: ['autodocs'],
  decorators: [
    (Story) => (
      <div style={{ width: 400 }}>
        <Story />
      </div>
    ),
  ],
};

export default meta;
type Story = StoryObj<typeof SkeletonCard>;

export const Default: Story = {
  args: {},
};

export const WithAvatar: Story = {
  args: {
    avatar: true,
  },
};

export const SingleLine: Story = {
  args: {
    lines: 1,
  },
};

export const MultipleLines: Story = {
  args: {
    lines: 5,
  },
};

export const WithAvatarAndMultipleLines: Story = {
  args: {
    avatar: true,
    lines: 4,
  },
};

export const CustomHeight: Story = {
  args: {
    lines: 3,
    height: 200,
  },
};

export const Tall: Story = {
  args: {
    avatar: true,
    lines: 6,
    height: 300,
  },
};

export const Compact: Story = {
  args: {
    lines: 2,
    height: 100,
  },
};

export const Grid: Story = {
  decorators: [
    (Story) => (
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, width: 900 }}>
        <SkeletonCard lines={3} />
        <SkeletonCard lines={3} />
        <SkeletonCard lines={3} />
        <SkeletonCard avatar lines={4} />
        <SkeletonCard avatar lines={4} />
        <SkeletonCard avatar lines={4} />
      </div>
    ),
  ],
  args: {},
};
