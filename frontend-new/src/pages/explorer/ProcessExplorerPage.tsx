import React, { useState, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button, Tabs, Spin, Space, Tooltip, Breadcrumb, Drawer } from 'antd';
import {
  ArrowLeftOutlined,
  DownloadOutlined,
  FilterOutlined,
  ExpandOutlined,
  CompressOutlined,
} from '@ant-design/icons';
import { tokens, toast } from '@lumina/design-system';
import { createLogger } from '../../utils/logger';
import { ProcessCanvas } from './components/ProcessCanvas';
import { VariantPanel } from './components/VariantPanel';
import { ActivityDetailsPanel } from './components/ActivityDetailsPanel';
import { FilterPanel, AppliedFilter } from './components/FilterPanel';
import {
  mockDFGNodes,
  mockDFGEdges,
  mockVariants,
  mockFilterOptions,
  getActivityDetail,
  MockActivityDetail,
} from './mockExplorerData';

const log = createLogger('ProcessExplorerPage');

// Mock log data
const mockLogInfo = {
  '1': { name: 'Orders_2024.csv', totalCases: 1250 },
  '2': { name: 'Claims_Process.xes', totalCases: 890 },
  '3': { name: 'Purchase_Orders.csv', totalCases: 3200 },
  '4': { name: 'Support_Tickets.csv', totalCases: 560 },
};

export function ProcessExplorerPage() {
  const { logId } = useParams<{ logId: string }>();
  const navigate = useNavigate();
  
  // UI State
  const [loading, setLoading] = useState(false);
  const [rightPanelOpen, setRightPanelOpen] = useState(true);
  const [rightPanelTab, setRightPanelTab] = useState('variants');
  const [filterDrawerOpen, setFilterDrawerOpen] = useState(false);
  
  // Selection State
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedVariantKey, setSelectedVariantKey] = useState<string | null>(null);
  
  // Filter State
  const [appliedFilters, setAppliedFilters] = useState<AppliedFilter[]>([]);

  const logInfo = mockLogInfo[logId as keyof typeof mockLogInfo] || { name: 'Unknown Log', totalCases: 0 };

  log.debug('Rendering ProcessExplorerPage', { logId, selectedNodeId, selectedVariantKey });

  // Get activity detail for selected node
  const selectedActivity: MockActivityDetail | null = useMemo(() => {
    if (!selectedNodeId) return null;
    return getActivityDetail(selectedNodeId);
  }, [selectedNodeId]);

  // Get highlighted path from selected variant
  const highlightedPath = useMemo(() => {
    if (!selectedVariantKey) return [];
    const variant = mockVariants.find((v) => v.key === selectedVariantKey);
    if (!variant) return [];
    // Map activity names to node IDs
    return variant.activities.map((name) => {
      const node = mockDFGNodes.find((n) => n.label === name);
      return node?.id || '';
    }).filter(Boolean);
  }, [selectedVariantKey]);

  // Handlers
  const handleNodeClick = useCallback((nodeId: string) => {
    log.debug('Node clicked', { nodeId });
    setSelectedNodeId((prev) => (prev === nodeId ? null : nodeId));
    setRightPanelTab('activity');
  }, []);

  const handleSelectVariant = useCallback((variantKey: string | null) => {
    log.debug('Variant selected', { variantKey });
    setSelectedVariantKey(variantKey);
  }, []);

  const handleFilterToVariant = useCallback((variantKey: string) => {
    log.info('Filter to variant', { variantKey });
    toast.info('Filtering to variant (mock)');
  }, []);

  const handleFilterWithActivity = useCallback((activityId: string) => {
    const activity = getActivityDetail(activityId);
    if (activity) {
      const filter: AppliedFilter = {
        id: `with-${activityId}-${Date.now()}`,
        type: 'activity',
        label: `With: ${activity.name}`,
        value: { include: [activityId] },
      };
      setAppliedFilters((prev) => [...prev, filter]);
      toast.success(`Filtering cases with "${activity.name}"`);
    }
  }, []);

  const handleFilterWithoutActivity = useCallback((activityId: string) => {
    const activity = getActivityDetail(activityId);
    if (activity) {
      const filter: AppliedFilter = {
        id: `without-${activityId}-${Date.now()}`,
        type: 'activity',
        label: `Without: ${activity.name}`,
        value: { exclude: [activityId] },
      };
      setAppliedFilters((prev) => [...prev, filter]);
      toast.success(`Filtering cases without "${activity.name}"`);
    }
  }, []);

  const handleApplyFilter = useCallback((filter: AppliedFilter) => {
    setAppliedFilters((prev) => [...prev, filter]);
    toast.success('Filter applied');
  }, []);

  const handleRemoveFilter = useCallback((filterId: string) => {
    setAppliedFilters((prev) => prev.filter((f) => f.id !== filterId));
    toast.info('Filter removed');
  }, []);

  const handleClearAllFilters = useCallback(() => {
    setAppliedFilters([]);
    toast.info('All filters cleared');
  }, []);

  const handleExportSVG = useCallback(() => {
    log.info('Exporting SVG');
    toast.info('SVG export coming soon');
  }, []);

  const handleExportPNG = useCallback(() => {
    log.info('Exporting PNG');
    toast.info('PNG export coming soon');
  }, []);

  const tabItems = [
    {
      key: 'variants',
      label: 'Variants',
      children: (
        <VariantPanel
          variants={mockVariants}
          selectedVariantKey={selectedVariantKey}
          onSelectVariant={handleSelectVariant}
          onFilterToVariant={handleFilterToVariant}
        />
      ),
    },
    {
      key: 'activity',
      label: 'Activity',
      children: (
        <ActivityDetailsPanel
          activity={selectedActivity}
          onClose={() => setSelectedNodeId(null)}
          onFilterWith={handleFilterWithActivity}
          onFilterWithout={handleFilterWithoutActivity}
        />
      ),
    },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', margin: -24 }}>
      {/* Toolbar */}
      <div
        style={{
          height: 56,
          backgroundColor: tokens.colors.neutral[0],
          borderBottom: `1px solid ${tokens.colors.neutral[200]}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: `0 ${tokens.spacing[4]}`,
          flexShrink: 0,
        }}
      >
        {/* Left: Back + Breadcrumb */}
        <Space size="middle">
          <Button
            type="text"
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/explorer')}
          >
            Back
          </Button>
          <Breadcrumb
            items={[
              { title: 'Event Logs', onClick: () => navigate('/logs') },
              { title: logInfo.name },
              { title: 'Explorer' },
            ]}
          />
        </Space>

        {/* Right: Actions */}
        <Space>
          <Tooltip title="Filters">
            <Button
              icon={<FilterOutlined />}
              onClick={() => setFilterDrawerOpen(true)}
              type={appliedFilters.length > 0 ? 'primary' : 'default'}
            >
              Filters {appliedFilters.length > 0 && `(${appliedFilters.length})`}
            </Button>
          </Tooltip>
          <Tooltip title="Export SVG">
            <Button icon={<DownloadOutlined />} onClick={handleExportSVG}>
              Export
            </Button>
          </Tooltip>
          <Tooltip title={rightPanelOpen ? 'Collapse panel' : 'Expand panel'}>
            <Button
              type="text"
              icon={rightPanelOpen ? <CompressOutlined /> : <ExpandOutlined />}
              onClick={() => setRightPanelOpen(!rightPanelOpen)}
            />
          </Tooltip>
        </Space>
      </div>

      {/* Main Content */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Canvas Area */}
        <div
          style={{
            flex: 1,
            position: 'relative',
            overflow: 'hidden',
          }}
        >
          {loading ? (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                height: '100%',
              }}
            >
              <Spin size="large" tip="Loading process map..." />
            </div>
          ) : (
            <ProcessCanvas
              dfgNodes={mockDFGNodes}
              dfgEdges={mockDFGEdges}
              selectedNodeId={selectedNodeId}
              highlightedPath={highlightedPath}
              onNodeClick={handleNodeClick}
            />
          )}
        </div>

        {/* Right Panel */}
        {rightPanelOpen && (
          <div
            style={{
              width: 320,
              backgroundColor: tokens.colors.neutral[0],
              borderLeft: `1px solid ${tokens.colors.neutral[200]}`,
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
            }}
          >
            <Tabs
              activeKey={rightPanelTab}
              onChange={setRightPanelTab}
              items={tabItems}
              size="small"
              style={{ height: '100%' }}
              tabBarStyle={{ margin: 0, padding: `0 ${tokens.spacing[3]}` }}
            />
          </div>
        )}
      </div>

      {/* Filter Drawer */}
      <Drawer
        title="Filters"
        placement="right"
        width={340}
        open={filterDrawerOpen}
        onClose={() => setFilterDrawerOpen(false)}
        styles={{ body: { padding: 0 } }}
      >
        <FilterPanel
          filterOptions={mockFilterOptions}
          appliedFilters={appliedFilters}
          onApplyFilter={handleApplyFilter}
          onRemoveFilter={handleRemoveFilter}
          onClearAllFilters={handleClearAllFilters}
        />
      </Drawer>
    </div>
  );
}

export default ProcessExplorerPage;
