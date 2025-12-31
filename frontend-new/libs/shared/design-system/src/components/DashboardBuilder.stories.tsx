import React from 'react';
import type { Meta, StoryObj } from '@storybook/react';
import { DashboardBuilder } from './DashboardBuilder';
import type { WidgetConfig, DashboardLayout } from './DashboardBuilder';

const meta: Meta<typeof DashboardBuilder> = {
  title: 'Lumina/DashboardBuilder',
  component: DashboardBuilder,
  parameters: {
    layout: 'fullscreen',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof DashboardBuilder>;

const sampleWidgets: WidgetConfig[] = [
  { id: 'w1', type: 'metric', title: 'Total Cases', defaultSize: { w: 3, h: 1 } },
  { id: 'w2', type: 'metric', title: 'Active Cases', defaultSize: { w: 3, h: 1 } },
  { id: 'w3', type: 'metric', title: 'Avg Duration', defaultSize: { w: 3, h: 1 } },
  { id: 'w4', type: 'metric', title: 'SLA Compliance', defaultSize: { w: 3, h: 1 } },
  { id: 'w5', type: 'line_chart', title: 'Cases Over Time', defaultSize: { w: 6, h: 2 }, configurable: true },
  { id: 'w6', type: 'pie_chart', title: 'Cases by Status', defaultSize: { w: 6, h: 2 } },
  { id: 'w7', type: 'bottleneck', title: 'Top Bottlenecks', defaultSize: { w: 6, h: 3 } },
  { id: 'w8', type: 'alert_list', title: 'Recent Alerts', defaultSize: { w: 6, h: 3 } },
  { id: 'w9', type: 'table', title: 'Case Details', defaultSize: { w: 12, h: 3 } },
  { id: 'w10', type: 'process_map', title: 'Process Overview', defaultSize: { w: 12, h: 4 } },
];

const sampleLayout: DashboardLayout = {
  id: 'dashboard-1',
  name: 'Operations Dashboard',
  items: [
    { widgetId: 'w1', x: 0, y: 0, w: 3, h: 1 },
    { widgetId: 'w2', x: 3, y: 0, w: 3, h: 1 },
    { widgetId: 'w3', x: 6, y: 0, w: 3, h: 1 },
    { widgetId: 'w4', x: 9, y: 0, w: 3, h: 1 },
    { widgetId: 'w5', x: 0, y: 1, w: 6, h: 2 },
    { widgetId: 'w6', x: 6, y: 1, w: 6, h: 2 },
  ],
};

export const Default: Story = {
  render: () => {
    const [layout, setLayout] = React.useState(sampleLayout);
    return (
      <div style={{ padding: 24 }}>
        <DashboardBuilder
          widgets={sampleWidgets}
          layout={layout}
          onLayoutChange={setLayout}
          onSave={(l) => console.log('Save dashboard:', l)}
        />
      </div>
    );
  },
};

export const EditMode: Story = {
  render: () => {
    const [layout, setLayout] = React.useState(sampleLayout);
    return (
      <div style={{ padding: 24 }}>
        <DashboardBuilder
          widgets={sampleWidgets}
          layout={layout}
          onLayoutChange={setLayout}
          editMode={true}
          onSave={(l) => console.log('Save dashboard:', l)}
        />
      </div>
    );
  },
};

export const EmptyDashboard: Story = {
  render: () => {
    const [layout, setLayout] = React.useState<DashboardLayout>({
      id: 'new-dashboard',
      name: 'New Dashboard',
      items: [],
    });
    return (
      <div style={{ padding: 24 }}>
        <DashboardBuilder
          widgets={sampleWidgets}
          layout={layout}
          onLayoutChange={setLayout}
          editMode={true}
        />
      </div>
    );
  },
};
