import React from 'react';
import type { Meta, StoryObj } from '@storybook/react';
import { FilterPresetManager } from './FilterPresetManager';
import type { FilterValue, FilterPreset } from './FilterPresetManager';
import { Card } from 'antd';

const meta: Meta<typeof FilterPresetManager> = {
  title: 'Lumina/FilterPresetManager',
  component: FilterPresetManager,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof FilterPresetManager>;

const sampleFilters: FilterValue[] = [
  { key: 'status', label: 'Status', value: 'active' },
  { key: 'duration', label: 'Duration', value: '> 24h', operator: 'gt' },
];

const samplePresets: FilterPreset[] = [
  { id: '1', name: 'Active Cases', filters: [{ key: 'status', label: 'Status', value: 'active' }], isDefault: true },
  { id: '2', name: 'Long Running', filters: [{ key: 'duration', label: 'Duration', value: '> 48h', operator: 'gt' }] },
  { id: '3', name: 'High Priority', filters: [{ key: 'priority', label: 'Priority', value: 'high' }] },
];

export const Default: Story = {
  render: () => {
    const [filters, setFilters] = React.useState<FilterValue[]>([]);
    return (
      <Card>
        <FilterPresetManager
          filters={filters}
          onChange={setFilters}
          presets={samplePresets}
          onSavePreset={(preset) => console.log('Save preset:', preset)}
        />
      </Card>
    );
  },
};

export const WithActiveFilters: Story = {
  render: () => {
    const [filters, setFilters] = React.useState<FilterValue[]>(sampleFilters);
    return (
      <Card>
        <FilterPresetManager
          filters={filters}
          onChange={setFilters}
          presets={samplePresets}
          onSavePreset={(preset) => console.log('Save preset:', preset)}
          onDeletePreset={(id) => console.log('Delete preset:', id)}
          onSetDefault={(id) => console.log('Set default:', id)}
        />
      </Card>
    );
  },
};

export const Compact: Story = {
  render: () => {
    const [filters, setFilters] = React.useState<FilterValue[]>(sampleFilters);
    return (
      <Card>
        <FilterPresetManager
          filters={filters}
          onChange={setFilters}
          presets={samplePresets}
          compact
        />
      </Card>
    );
  },
};
