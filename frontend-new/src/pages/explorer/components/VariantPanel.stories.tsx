import type { Meta, StoryObj } from '@storybook/react';
import { VariantPanel } from './VariantPanel';

const meta: Meta<typeof VariantPanel> = {
  title: 'Explorer/VariantPanel',
  component: VariantPanel,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof VariantPanel>;

const sampleVariants = [
  {
    key: 'var-1',
    activities: ['Receive Order', 'Check Credit', 'Approve Order', 'Ship Goods', 'Order Complete'],
    caseCount: 4500,
    frequencyPercent: 45.2,
    avgDurationSeconds: 432000,
    isHappyPath: true,
    complexityScore: 1.2,
    hasRework: false,
    conformanceScore: 100,
  },
  {
    key: 'var-2',
    activities: ['Receive Order', 'Check Credit', 'Reject Order', 'Order Complete'],
    caseCount: 1500,
    frequencyPercent: 15.1,
    avgDurationSeconds: 86400,
    isHappyPath: false,
    complexityScore: 1.0,
    hasRework: false,
    conformanceScore: 100,
  },
  {
    key: 'var-3',
    activities: [
      'Receive Order',
      'Check Credit',
      'Request More Info',
      'Check Credit',
      'Approve Order',
      'Ship Goods',
      'Order Complete',
    ],
    caseCount: 1200,
    frequencyPercent: 12.0,
    avgDurationSeconds: 864000,
    isHappyPath: false,
    complexityScore: 2.5,
    hasRework: true,
    conformanceScore: 85,
  },
  {
    key: 'var-4',
    activities: ['Receive Order', 'Check Credit', 'Manual Review', 'Approve Order', 'Ship Goods', 'Order Complete'],
    caseCount: 800,
    frequencyPercent: 8.0,
    avgDurationSeconds: 604800,
    isHappyPath: false,
    complexityScore: 1.8,
    hasRework: false,
    conformanceScore: 92,
  },
];

export const Default: Story = {
  args: {
    variants: sampleVariants,
    selectedVariantKey: null,
  },
  render: (args) => (
    <div style={{ width: '300px', height: '800px', border: '1px solid #eee' }}>
      <VariantPanel {...args} />
    </div>
  ),
};

export const WithSelection: Story = {
  args: {
    variants: sampleVariants,
    selectedVariantKey: 'var-1',
  },
  render: (args) => (
    <div style={{ width: '300px', height: '800px', border: '1px solid #eee' }}>
      <VariantPanel {...args} />
    </div>
  ),
};

export const Loading: Story = {
  args: {
    variants: [],
    loading: true,
  },
  render: (args) => (
    <div style={{ width: '300px', height: '800px', border: '1px solid #eee' }}>
      <VariantPanel {...args} />
    </div>
  ),
};
