/**
 * DashboardBuilder - Widget-based dashboard configuration
 *
 * Allows users to create custom dashboards by selecting and
 * arranging widgets in a grid layout.
 *
 * @example
 * <DashboardBuilder
 *   widgets={availableWidgets}
 *   layout={currentLayout}
 *   onLayoutChange={handleLayoutChange}
 *   onSave={saveDashboard}
 * />
 */

import React, { useState, useCallback, useMemo } from 'react';
import {
  Card,
  Button,
  Space,
  Typography,
  Row,
  Col,
  Drawer,
  List,
  Empty,
  Tooltip,
  Modal,
  Input,
  Select,
  Divider,
  Tag,
} from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  DragOutlined,
  SettingOutlined,
  SaveOutlined,
  EyeOutlined,
  AppstoreOutlined,
  LineChartOutlined,
  PieChartOutlined,
  TableOutlined,
  NumberOutlined,
  BellOutlined,
  ClockCircleOutlined,
  FullscreenOutlined,
  FullscreenExitOutlined,
} from '@ant-design/icons';
import { tokens } from '../theme';

const { Text, Title } = Typography;

// ============================================
// Types
// ============================================

export type WidgetType =
  | 'metric'
  | 'line_chart'
  | 'bar_chart'
  | 'pie_chart'
  | 'table'
  | 'alert_list'
  | 'bottleneck'
  | 'deviation'
  | 'process_map'
  | 'queue'
  | 'custom';

export interface WidgetConfig {
  id: string;
  type: WidgetType;
  title: string;
  description?: string;
  icon?: React.ReactNode;
  defaultSize: { w: number; h: number };
  minSize?: { w: number; h: number };
  maxSize?: { w: number; h: number };
  configurable?: boolean;
  settings?: Record<string, any>;
}

export interface LayoutItem {
  widgetId: string;
  x: number;
  y: number;
  w: number;
  h: number;
  settings?: Record<string, any>;
}

export interface DashboardLayout {
  id: string;
  name: string;
  items: LayoutItem[];
  columns?: number;
  createdAt?: Date;
  updatedAt?: Date;
}

export interface DashboardBuilderProps {
  /** Available widgets */
  widgets: WidgetConfig[];
  /** Current layout */
  layout: DashboardLayout;
  /** Layout change handler */
  onLayoutChange: (layout: DashboardLayout) => void;
  /** Save dashboard handler */
  onSave?: (layout: DashboardLayout) => void;
  /** Widget render function */
  renderWidget?: (widget: WidgetConfig, settings?: Record<string, any>) => React.ReactNode;
  /** Edit mode */
  editMode?: boolean;
  /** Toggle edit mode */
  onEditModeChange?: (editMode: boolean) => void;
  /** Grid columns */
  columns?: number;
  /** Row height in pixels */
  rowHeight?: number;
}

// ============================================
// Configuration
// ============================================

const WIDGET_TYPE_ICONS: Record<WidgetType, React.ReactNode> = {
  metric: <NumberOutlined />,
  line_chart: <LineChartOutlined />,
  bar_chart: <LineChartOutlined />,
  pie_chart: <PieChartOutlined />,
  table: <TableOutlined />,
  alert_list: <BellOutlined />,
  bottleneck: <ClockCircleOutlined />,
  deviation: <BellOutlined />,
  process_map: <AppstoreOutlined />,
  queue: <AppstoreOutlined />,
  custom: <SettingOutlined />,
};

const WIDGET_TYPE_LABELS: Record<WidgetType, string> = {
  metric: 'Metric Card',
  line_chart: 'Line Chart',
  bar_chart: 'Bar Chart',
  pie_chart: 'Pie Chart',
  table: 'Data Table',
  alert_list: 'Alert List',
  bottleneck: 'Bottleneck Panel',
  deviation: 'Deviation Viewer',
  process_map: 'Process Map',
  queue: 'Work Queue',
  custom: 'Custom Widget',
};

// ============================================
// DashboardBuilder Component
// ============================================

export function DashboardBuilder({
  widgets,
  layout,
  onLayoutChange,
  onSave,
  renderWidget,
  editMode: controlledEditMode,
  onEditModeChange,
  columns = 12,
  rowHeight = 100,
}: DashboardBuilderProps) {
  const [internalEditMode, setInternalEditMode] = useState(false);
  const [widgetDrawerOpen, setWidgetDrawerOpen] = useState(false);
  const [configModalOpen, setConfigModalOpen] = useState(false);
  const [selectedItemIndex, setSelectedItemIndex] = useState<number | null>(null);

  const editMode = controlledEditMode !== undefined ? controlledEditMode : internalEditMode;
  const setEditMode = onEditModeChange || setInternalEditMode;

  // Widget map for quick lookup
  const widgetMap = useMemo(() => {
    return new Map(widgets.map((w) => [w.id, w]));
  }, [widgets]);

  // Add widget to layout
  const handleAddWidget = useCallback(
    (widget: WidgetConfig) => {
      const newItem: LayoutItem = {
        widgetId: widget.id,
        x: 0,
        y: layout.items.length > 0 ? Math.max(...layout.items.map((i) => i.y + i.h)) : 0,
        w: widget.defaultSize.w,
        h: widget.defaultSize.h,
      };

      onLayoutChange({
        ...layout,
        items: [...layout.items, newItem],
      });
      setWidgetDrawerOpen(false);
    },
    [layout, onLayoutChange]
  );

  // Remove widget from layout
  const handleRemoveWidget = useCallback(
    (index: number) => {
      const newItems = [...layout.items];
      newItems.splice(index, 1);
      onLayoutChange({
        ...layout,
        items: newItems,
      });
    },
    [layout, onLayoutChange]
  );

  // Configure widget
  const handleConfigureWidget = useCallback((index: number) => {
    setSelectedItemIndex(index);
    setConfigModalOpen(true);
  }, []);

  // Update widget settings
  const handleUpdateSettings = useCallback(
    (settings: Record<string, any>) => {
      if (selectedItemIndex === null) return;
      const newItems = [...layout.items];
      newItems[selectedItemIndex] = {
        ...newItems[selectedItemIndex],
        settings,
      };
      onLayoutChange({
        ...layout,
        items: newItems,
      });
      setConfigModalOpen(false);
    },
    [layout, onLayoutChange, selectedItemIndex]
  );

  // Resize widget
  const handleResizeWidget = useCallback(
    (index: number, direction: 'grow' | 'shrink') => {
      const newItems = [...layout.items];
      const item = newItems[index];
      const widget = widgetMap.get(item.widgetId);
      
      if (direction === 'grow') {
        const maxW = widget?.maxSize?.w || columns;
        const maxH = widget?.maxSize?.h || 4;
        item.w = Math.min(item.w + 1, maxW);
        item.h = Math.min(item.h + 1, maxH);
      } else {
        const minW = widget?.minSize?.w || 2;
        const minH = widget?.minSize?.h || 1;
        item.w = Math.max(item.w - 1, minW);
        item.h = Math.max(item.h - 1, minH);
      }
      
      onLayoutChange({ ...layout, items: newItems });
    },
    [layout, onLayoutChange, widgetMap, columns]
  );

  // Default widget renderer
  const defaultRenderWidget = (widget: WidgetConfig, settings?: Record<string, any>) => (
    <div
      style={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: tokens.colors.neutral[50],
        borderRadius: tokens.radius.md,
        border: `1px dashed ${tokens.colors.neutral[300]}`,
      }}
    >
      <div style={{ fontSize: 32, color: tokens.colors.neutral[400], marginBottom: tokens.spacing[2] }}>
        {widget.icon || WIDGET_TYPE_ICONS[widget.type]}
      </div>
      <Text type="secondary">{widget.title}</Text>
      <Text type="secondary" style={{ fontSize: tokens.fontSize.xs }}>
        {WIDGET_TYPE_LABELS[widget.type]}
      </Text>
    </div>
  );

  const widgetRenderer = renderWidget || defaultRenderWidget;

  return (
    <div className="animate-fade-in">
      {/* Toolbar */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: tokens.spacing[4],
          padding: tokens.spacing[3],
          backgroundColor: tokens.colors.neutral[50],
          borderRadius: tokens.radius.md,
        }}
      >
        <Space>
          <Title level={5} style={{ margin: 0 }}>
            {layout.name}
          </Title>
          <Tag>{layout.items.length} widgets</Tag>
        </Space>

        <Space>
          {editMode && (
            <Button icon={<PlusOutlined />} onClick={() => setWidgetDrawerOpen(true)}>
              Add Widget
            </Button>
          )}
          <Button
            icon={editMode ? <EyeOutlined /> : <SettingOutlined />}
            onClick={() => setEditMode(!editMode)}
          >
            {editMode ? 'Preview' : 'Edit'}
          </Button>
          {onSave && (
            <Button type="primary" icon={<SaveOutlined />} onClick={() => onSave(layout)}>
              Save
            </Button>
          )}
        </Space>
      </div>

      {/* Dashboard Grid */}
      {layout.items.length === 0 ? (
        <Card>
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description="No widgets added yet"
          >
            {editMode && (
              <Button type="primary" icon={<PlusOutlined />} onClick={() => setWidgetDrawerOpen(true)}>
                Add Your First Widget
              </Button>
            )}
          </Empty>
        </Card>
      ) : (
        <Row gutter={[16, 16]}>
          {layout.items.map((item, index) => {
            const widget = widgetMap.get(item.widgetId);
            if (!widget) return null;

            // Calculate column span (assuming 12-column grid)
            const colSpan = Math.min(24, Math.round((item.w / columns) * 24));

            return (
              <Col key={`${item.widgetId}-${index}`} span={colSpan}>
                <Card
                  title={
                    <Space>
                      {widget.icon || WIDGET_TYPE_ICONS[widget.type]}
                      <span>{widget.title}</span>
                    </Space>
                  }
                  extra={
                    editMode && (
                      <Space size={4}>
                        <Tooltip title="Shrink">
                          <Button
                            type="text"
                            size="small"
                            icon={<FullscreenExitOutlined />}
                            onClick={() => handleResizeWidget(index, 'shrink')}
                          />
                        </Tooltip>
                        <Tooltip title="Grow">
                          <Button
                            type="text"
                            size="small"
                            icon={<FullscreenOutlined />}
                            onClick={() => handleResizeWidget(index, 'grow')}
                          />
                        </Tooltip>
                        {widget.configurable && (
                          <Tooltip title="Configure">
                            <Button
                              type="text"
                              size="small"
                              icon={<SettingOutlined />}
                              onClick={() => handleConfigureWidget(index)}
                            />
                          </Tooltip>
                        )}
                        <Tooltip title="Remove">
                          <Button
                            type="text"
                            size="small"
                            danger
                            icon={<DeleteOutlined />}
                            onClick={() => handleRemoveWidget(index)}
                          />
                        </Tooltip>
                      </Space>
                    )
                  }
                  style={{
                    height: item.h * rowHeight,
                    border: editMode ? `2px dashed ${tokens.colors.primary[200]}` : undefined,
                  }}
                  styles={{
                    body: {
                      height: 'calc(100% - 57px)',
                      overflow: 'auto',
                    },
                  }}
                >
                  {widgetRenderer(widget, item.settings)}
                </Card>
              </Col>
            );
          })}
        </Row>
      )}

      {/* Widget Selection Drawer */}
      <Drawer
        title="Add Widget"
        placement="right"
        open={widgetDrawerOpen}
        onClose={() => setWidgetDrawerOpen(false)}
        width={360}
      >
        <List
          dataSource={widgets}
          renderItem={(widget) => (
            <List.Item
              key={widget.id}
              onClick={() => handleAddWidget(widget)}
              style={{
                cursor: 'pointer',
                padding: tokens.spacing[3],
                borderRadius: tokens.radius.md,
                marginBottom: tokens.spacing[2],
              }}
              className="card-hover-lift"
            >
              <List.Item.Meta
                avatar={
                  <div
                    style={{
                      width: 40,
                      height: 40,
                      borderRadius: tokens.radius.md,
                      backgroundColor: tokens.colors.primary[50],
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: tokens.colors.primary[500],
                      fontSize: 18,
                    }}
                  >
                    {widget.icon || WIDGET_TYPE_ICONS[widget.type]}
                  </div>
                }
                title={widget.title}
                description={widget.description || WIDGET_TYPE_LABELS[widget.type]}
              />
            </List.Item>
          )}
        />
      </Drawer>

      {/* Configuration Modal */}
      <Modal
        title="Configure Widget"
        open={configModalOpen}
        onCancel={() => setConfigModalOpen(false)}
        onOk={() => {
          if (selectedItemIndex !== null) {
            const currentSettings = layout.items[selectedItemIndex]?.settings || {};
            handleUpdateSettings(currentSettings);
          }
        }}
      >
        {selectedItemIndex !== null && (
          <div>
            <Text type="secondary">
              Widget configuration options will appear here based on the widget type.
            </Text>
            {/* Add dynamic configuration form based on widget type */}
          </div>
        )}
      </Modal>
    </div>
  );
}

export default DashboardBuilder;
