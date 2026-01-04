import type { Meta, StoryObj } from '@storybook/react-vite';

import TestBenchPage from '../pages/TestBenchPage';

const meta = {
    component: TestBenchPage,
} satisfies Meta<typeof TestBenchPage>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {
    args: {},
};
