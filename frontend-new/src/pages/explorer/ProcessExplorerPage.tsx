import React, { useState, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Button, Tabs, Spin, Space, Tooltip, Breadcrumb, Drawer, Alert } from 'antd';
import {
  ArrowLeftOutlined,
  DownloadOutlined,
  FilterOutlined,
  ExpandOutlined,
  CompressOutlined,
} from '@ant-design/icons';
import { tokens, toast, useSDK, type DFGNode, type DFGEdge, type Variant, type ActivityDetail } from '@lumina/design-system';
import { createLogger } from '../../utils/logger';
import { ProcessCanvas } from './components/ProcessCanvas';
import { VariantPanel } from './components/VariantPanel';
import { ActivityDetailsPanel } from './components/ActivityDetailsPanel';
import { FilterPanel, AppliedFilter } from './components/FilterPanel';

const log = createLogger('ProcessExplorerPage');

export function ProcessExplorerPage() {
  const { logId } = useParams<{ logId: string }>();
  const navigate = useNavigate();
  const sdk = useSDK();
  
  // UI State
  const [rightPanelOpen, setRightPanelOpen] = useState(true);
  const [rightPanelTab, setRightPanelTab] = useState('variants');
  const [filterDrawerOpen, setFilterDrawerOpen] = useState(false);
  
  // Selection State
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedVariantKey, setSelectedVariantKey] = useState<string | null>(null);
  
  // Filter State
  const [appliedFilters, setAppliedFilters] = useState<AppliedFilter[]>([]);

  // Fetch log details
  const { data: logInfo, isLoading: logLoading } = useQuery({
    queryKey: ['logs', logId],
    queryFn: () => sdk.logs.get(logId!),
    enabled: !!logId,
  });

  // Fetch DFG data
  const { data: dfgData, isLoading: dfgLoading, error: dfgError } = useQuery({
    queryKey: ['dfg', logId],
    queryFn: () => sdk.discovery.buildDFG(logId!, { includePerformance: true }),
    enabled: !!logId,
  });

  // Fetch variants
  const { data: variants, isLoading: variantsLoading } = useQuery({
    queryKey: ['variants', logId],
    queryFn: () => sdk.discovery.getVariants(logId!, { topN: 20, includeComplexity: true }),
    enabled: !!logId,
  });

  // Fetch activities
  const { data: activities, isLoading: activitiesLoading } = useQuery({
    queryKey: ['activities', logId],
    queryFn: () => sdk.discovery.getActivities(logId!),
    enabled: !!logId,
  });

  const loading = logLoading || dfgLoading || variantsLoading || activitiesLoading;

  log.debug('Rendering ProcessExplorerPage', { logId, selectedNodeId, selectedVariantKey, loading });

  // Convert SDK types to component-compatible format
  const dfgNodes = useMemo(() => {
    if (!dfgData?.nodes) return [];
    return dfgData.nodes.map((node: DFGNode) => ({
      id: node.id,
      label: node.label,
      frequency: node.frequency,
    }));
  }, [dfgData]);

  const dfgEdges = useMemo(() => {
    if (!dfgData?.edges) return [];
    return dfgData.edges.map((edge: DFGEdge) => ({
      source: edge.source,
      target: edge.target,
      frequency: edge.frequency,
      performance: edge.avgDuration,
    }));
  }, [dfgData]);

  const mockVariants = useMemo(() => {
    if (!variants) return [];
    return variants.map((v: Variant) => ({
      key: v.key,
      activities: v.activities,
      caseCount: v.caseCount,
      frequencyPercent: v.frequencyPercent,
      avgDurationSeconds: v.avgDuration ?? 0,
    }));
  }, [variants]);

  // Get activity detail for selected node
  const selectedActivity = useMemo(() => {
    if (!selectedNodeId || !activities) return null;
    const activity = activities.find((a: ActivityDetail) => a.id === selectedNodeId);
    if (!activity) return null;
    return {
      id: activity.id,
      name: activity.name,
      totalOccurrences: activity.frequency,
      casePercentage: activity.frequencyPercent,
      avgDurationSeconds: activity.avgDuration ?? 0,
      minDurationSeconds: activity.minDuration ?? 0,
      maxDurationSeconds: activity.maxDuration ?? 0,
      resources: activity.resources,
    };
  }, [selectedNodeId, activities]);

  // Get highlighted path from selected variant
  const highlightedPath = useMemo(() => {
    if (!selectedVariantKey || !mockVariants.length) return [];
    const variant = mockVariants.find((v: { key: string }) => v.key === selectedVariantKey);
    if (!variant) return [];
    // Map activity names to node IDs
    return variant.activities.map((name: string) => {
      const node = dfgNodes.find((n: { label: string }) => n.label === name);
      return node?.id || '';
    }).filter(Boolean);
  }, [selectedVariantKey, mockVariants, dfgNodes]);

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
    toast.info('Filtering to variant (coming soon)');
  }, []);

  const handleFilterWithActivity = useCallback((activityId: string) => {
    const activity = activities?.find((a: ActivityDetail) => a.id === activityId);
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
  }, [activities]);

  const handleFilterWithoutActivity = useCallback((activityId: string) => {
    const activity = activities?.find((a: ActivityDetail) => a.id === activityId);
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
  }, [activities]);

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

  // Mock filter options (will be fetched from API in future)
  const mockFilterOptions = useMemo(() => ({
    activities: activities?.map((a: ActivityDetail) => a.name) ?? [],
    resources: [],
    timeRange: { start: '', end: '' },
    caseDuration: { min: 0, max: 0, mean: 0 },
  }), [activities]);

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

  // Error state
  if (dfgError) {
    return (
      <div style={{ padding: 24 }}>
        <Alert
          message="Failed to load process map"
          description={(dfgError as Error).message}
          type="error"
          showIcon
          action={
            <Button onClick={() => navigate('/explorer')}>
              Go Back
            </Button>
          }
        />
      </div>
    );
  }

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
              { title: logInfo?.name ?? 'Loading...' },
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
              dfgNodes={dfgNodes}
              dfgEdges={dfgEdges}
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
