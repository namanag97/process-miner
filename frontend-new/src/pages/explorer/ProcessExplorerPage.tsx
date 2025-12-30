/**
 * ProcessExplorerPage - World-Class Process Mining Explorer
 *
 * Features:
 * - Advanced DFG visualization with dagre layout
 * - Performance and frequency metrics
 * - KPI bar with key process metrics
 * - Advanced filtering (activity, sequence, duration, time, resource)
 * - Variant exploration with search and sorting
 * - Activity and edge detail panels
 * - Path highlighting from variant selection
 */

import React, { useState, useCallback, useMemo } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Button, Tabs, Spin, Space, Tooltip, Breadcrumb, Drawer, Alert, Tag, Dropdown } from 'antd';
import {
  ArrowLeftOutlined,
  DownloadOutlined,
  FilterOutlined,
  ExpandOutlined,
  CompressOutlined,
} from '@ant-design/icons';
import { tokens, toast, useSDK } from '@lumina/design-system';
import { createLogger } from '../../utils/logger';

// Import components
import { ProcessCanvas, DFGNodeData, DFGEdgeData } from './components/ProcessCanvas';
import { ProcessKPIBar, ProcessKPIs } from './components/ProcessKPIBar';
import { VariantPanel, Variant } from './components/VariantPanel';
import { ActivityDetailsPanel } from './components/ActivityDetailsPanel';
import { EdgeDetailsPanel, EdgeDetail } from './components/EdgeDetailsPanel';
import { FilterPanel, AppliedFilter, FilterOptions } from './components/FilterPanel';

// =============================================================================
// SDK RESPONSE TYPES
// =============================================================================

interface SDKDFGNode {
  name: string;
  frequency: number;
  isStart: boolean;
  isEnd: boolean;
}

interface SDKDFGEdge {
  source: string;
  target: string;
  frequency: number;
  probability: number;
  avgDurationSeconds?: number;
}

interface SDKVariant {
  key: string;
  activities: string[];
  caseCount: number;
  frequencyPercent: number;
  avgDuration: number | null;
  complexityScore?: number;
}

interface SDKActivityDetail {
  id: string;
  name: string;
  frequency: number;
  frequencyPercent: number;
  avgDuration: number | null;
  minDuration: number | null;
  maxDuration: number | null;
  isStart: boolean;
  isEnd: boolean;
  resources: string[];
}

const log = createLogger('ProcessExplorerPage');

// =============================================================================
// MAIN COMPONENT
// =============================================================================

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
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);
  const [selectedVariantKey, setSelectedVariantKey] = useState<string | null>(null);

  // Filter State
  const [appliedFilters, setAppliedFilters] = useState<AppliedFilter[]>([]);

  // =============================================================================
  // DATA FETCHING
  // =============================================================================

  // Fetch log details
  const { data: logInfo, isLoading: logLoading } = useQuery({
    queryKey: ['processes', logId],
    queryFn: () => sdk.processes.get(logId!),
    enabled: !!logId,
  });

  // Fetch DFG data
  const {
    data: dfgData,
    isLoading: dfgLoading,
    error: dfgError,
  } = useQuery({
    queryKey: ['dfg', logId],
    queryFn: () => sdk.discovery.buildDFG(logId!, { includePerformance: true }),
    enabled: !!logId,
  });

  // Fetch variants
  const {
    data: variants,
    isLoading: variantsLoading,
    error: variantsError,
  } = useQuery({
    queryKey: ['variants', logId],
    queryFn: () => sdk.discovery.getVariants(logId!, { topN: 50, includeComplexity: true }),
    enabled: !!logId,
  });

  // Fetch activities
  const {
    data: activities,
    isLoading: activitiesLoading,
    error: activitiesError,
  } = useQuery({
    queryKey: ['activities', logId],
    queryFn: () => sdk.discovery.getActivities(logId!),
    enabled: !!logId,
  });

  const loading = logLoading || dfgLoading || variantsLoading || activitiesLoading;
  const error = dfgError || variantsError || activitiesError;

  log.debug('Rendering ProcessExplorerPage', {
    logId,
    selectedNodeId,
    selectedEdgeId,
    selectedVariantKey,
    loading,
  });

  // =============================================================================
  // DATA TRANSFORMATIONS
  // =============================================================================

  // Transform DFG nodes for ProcessCanvas
  const dfgNodes = useMemo((): DFGNodeData[] => {
    if (!dfgData?.nodes || !Array.isArray(dfgData.nodes)) {
      if (dfgData?.nodes) {
        console.error('[ProcessExplorer] Invalid DFG nodes data:', dfgData);
      }
      return [];
    }

    const activityList = Array.isArray(activities) ? activities : [];
    const activityMap = new Map(activityList.map((a) => [a.name, a]));

    return dfgData.nodes.map((node) => {
      const activityDetail = activityMap.get(node.label);
      return {
        id: node.id,
        label: node.label,
        frequency: node.frequency,
        isStart: node.isStart,
        isEnd: node.isEnd,
        avgDuration: activityDetail?.avgDuration ?? undefined,
        minDuration: activityDetail?.minDuration ?? undefined,
        maxDuration: activityDetail?.maxDuration ?? undefined,
      };
    });
  }, [dfgData, activities]);

  // Transform DFG edges for ProcessCanvas
  const dfgEdges = useMemo((): DFGEdgeData[] => {
    if (!dfgData?.edges || !Array.isArray(dfgData.edges)) {
      if (dfgData?.edges) {
        console.error('[ProcessExplorer] Invalid DFG edges data:', dfgData);
      }
      return [];
    }

    return dfgData.edges.map((edge) => ({
      source: edge.source,
      target: edge.target,
      frequency: edge.frequency,
      performance: edge.avgDuration,
    }));
  }, [dfgData]);

  // Transform variants for VariantPanel
  const processedVariants = useMemo((): Variant[] => {
    if (!variants || !Array.isArray(variants)) {
      if (variants) {
        console.error('[ProcessExplorer] Invalid variants data:', variants);
      }
      return [];
    }

    // Explicitly sort by frequency DESC to ensure happy path detection is correct
    const sortedVariants = [...variants].sort((a, b) =>
      (b.frequencyPercent ?? 0) - (a.frequencyPercent ?? 0)
    );

    return sortedVariants.map((v, index) => ({
      key: v.key,
      activities: Array.isArray(v.activities) ? v.activities : [],
      caseCount: v.caseCount ?? 0,
      frequencyPercent: v.frequencyPercent ?? 0,
      avgDurationSeconds: v.avgDuration ?? 0,
      isHappyPath: index === 0 && (v.frequencyPercent ?? 0) > 50,
      complexityScore: v.complexityScore,
      hasRework: hasReworkInVariant(Array.isArray(v.activities) ? v.activities : []),
    }));
  }, [variants]);

  // Calculate KPIs
  const kpis = useMemo((): ProcessKPIs => {
    // Calculate totalCases from variants (backend DFG doesn't include this field)
    const totalCases = processedVariants.reduce((sum, v) => sum + v.caseCount, 0);
    const uniqueVariants = processedVariants.length;
    const uniqueActivities = dfgNodes.length;

    // Calculate avg throughput from variants
    const variantsWithDuration = processedVariants.filter((v) => v.avgDurationSeconds > 0);
    const avgThroughputTime =
      variantsWithDuration.length > 0
        ? variantsWithDuration.reduce((sum, v) => sum + v.avgDurationSeconds * v.caseCount, 0) /
          variantsWithDuration.reduce((sum, v) => sum + v.caseCount, 0)
        : undefined;

    const happyPathPercent = processedVariants[0]?.frequencyPercent;
    const reworkVariants = processedVariants.filter((v) => v.hasRework);
    const reworkRate =
      reworkVariants.length > 0
        ? reworkVariants.reduce((sum, v) => sum + v.frequencyPercent, 0)
        : undefined;

    return {
      totalCases,
      uniqueVariants,
      uniqueActivities,
      avgThroughputTime,
      happyPathPercent,
      reworkRate,
    };
  }, [dfgData, processedVariants, dfgNodes]);

  // Build filter options
  const filterOptions = useMemo((): FilterOptions => {
    const activityList = Array.isArray(activities) ? activities : [];
    const activityNames = activityList.map((a) => a.name);
    const allResources = new Set<string>();
    activityList.forEach((a) => {
      if (Array.isArray(a.resources)) {
        a.resources.forEach((r) => allResources.add(r));
      }
    });

    const durations = processedVariants
      .filter((v) => v.avgDurationSeconds > 0)
      .map((v) => v.avgDurationSeconds);
    const minDuration = durations.length > 0 ? Math.min(...durations) : 0;
    const maxDuration = durations.length > 0 ? Math.max(...durations) : 0;
    const meanDuration =
      durations.length > 0 ? durations.reduce((a, b) => a + b, 0) / durations.length : 0;

    return {
      activities: activityNames,
      resources: Array.from(allResources),
      timeRange: { start: '', end: '' },
      caseDuration: { min: minDuration, max: maxDuration, mean: meanDuration },
    };
  }, [activities, processedVariants]);

  // Get activity detail for selected node
  const selectedActivity = useMemo(() => {
    if (!selectedNodeId || !Array.isArray(activities)) return null;

    const activity = activities.find(
      (a) => a.id === selectedNodeId || a.name === selectedNodeId
    );
    if (!activity) return null;
    return {
      id: activity.id,
      name: activity.name,
      totalOccurrences: activity.frequency ?? 0,
      casePercentage: activity.frequencyPercent ?? 0,
      avgDurationSeconds: activity.avgDuration ?? 0,
      minDurationSeconds: activity.minDuration ?? 0,
      maxDurationSeconds: activity.maxDuration ?? 0,
      resources: Array.isArray(activity.resources) ? activity.resources : [],
    };
  }, [selectedNodeId, activities]);

  // Get edge detail for selected edge
  const selectedEdge = useMemo((): EdgeDetail | null => {
    if (!selectedEdgeId || !dfgEdges.length) return null;
    const [, source, target] = selectedEdgeId.split('-');
    const edge = dfgEdges.find((e) => e.source === source && e.target === target);
    if (!edge) return null;

    const totalFrequency = dfgEdges.reduce((sum, e) => sum + e.frequency, 0);
    return {
      id: selectedEdgeId,
      source: edge.source,
      target: edge.target,
      frequency: edge.frequency,
      frequencyPercent: (edge.frequency / totalFrequency) * 100,
      avgDurationSeconds: edge.performance,
    };
  }, [selectedEdgeId, dfgEdges]);

  // Get highlighted path from selected variant
  const highlightedPath = useMemo(() => {
    if (!selectedVariantKey || !processedVariants.length) return [];
    const variant = processedVariants.find((v) => v.key === selectedVariantKey);
    return variant?.activities ?? [];
  }, [selectedVariantKey, processedVariants]);

  // =============================================================================
  // HANDLERS
  // =============================================================================

  const handleNodeClick = useCallback((nodeId: string) => {
    log.debug('Node clicked', { nodeId });
    setSelectedNodeId((prev) => (prev === nodeId ? null : nodeId));
    setSelectedEdgeId(null);
    setRightPanelTab('activity');
  }, []);

  const handleEdgeClick = useCallback((edgeId: string, source: string, target: string) => {
    log.debug('Edge clicked', { edgeId, source, target });
    setSelectedEdgeId((prev) => (prev === edgeId ? null : edgeId));
    setSelectedNodeId(null);
    setRightPanelTab('edge');
  }, []);

  const handleSelectVariant = useCallback((variantKey: string | null) => {
    log.debug('Variant selected', { variantKey });
    setSelectedVariantKey(variantKey);
  }, []);

  const handleFilterToVariant = useCallback((variantKey: string) => {
    log.info('Filter to variant', { variantKey });
    const variant = processedVariants.find((v) => v.key === variantKey);
    if (variant) {
      const filter: AppliedFilter = {
        id: `variant-${variantKey}-${Date.now()}`,
        type: 'variant',
        label: `Variant: ${variant.activities.slice(0, 2).join(' → ')}...`,
        value: { variantKey, activities: variant.activities },
      };
      setAppliedFilters((prev) => [...prev, filter]);
      toast.success('Filtering to variant');
    }
  }, [processedVariants]);

  const handleFilterWithActivity = useCallback(
    (activityId: string) => {
      if (!Array.isArray(activities)) return;

      const activity = activities.find(
        (a) => a.id === activityId || a.name === activityId
      );
      if (activity) {
        const filter: AppliedFilter = {
          id: `with-${activityId}-${Date.now()}`,
          type: 'activity',
          label: `With: ${activity.name}`,
          value: { mode: 'include', activities: [activity.name] },
        };
        setAppliedFilters((prev) => [...prev, filter]);
        toast.success(`Filtering cases with "${activity.name}"`);
      }
    },
    [activities]
  );

  const handleFilterWithoutActivity = useCallback(
    (activityId: string) => {
      if (!Array.isArray(activities)) return;

      const activity = activities.find(
        (a) => a.id === activityId || a.name === activityId
      );
      if (activity) {
        const filter: AppliedFilter = {
          id: `without-${activityId}-${Date.now()}`,
          type: 'activity',
          label: `Without: ${activity.name}`,
          value: { mode: 'exclude', activities: [activity.name] },
        };
        setAppliedFilters((prev) => [...prev, filter]);
        toast.success(`Filtering cases without "${activity.name}"`);
      }
    },
    [activities]
  );

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

  const handleExportPNG = useCallback(() => {
    log.info('Exporting PNG');
    // Find the React Flow viewport and export
    const viewport = document.querySelector('.react-flow__viewport') as HTMLElement;
    if (!viewport) {
      toast.error('Unable to export: Canvas not found');
      return;
    }
    
    // Use html2canvas approach (simple implementation)
    import('html-to-image').then(({ toPng }) => {
      const flowContainer = document.querySelector('.react-flow') as HTMLElement;
      if (flowContainer) {
        toPng(flowContainer, { 
          backgroundColor: '#ffffff',
          quality: 1,
        }).then((dataUrl: string) => {
          const link = document.createElement('a');
          link.download = `${logInfo?.name ?? 'process'}-dfg.png`;
          link.href = dataUrl;
          link.click();
          toast.success('Process map exported as PNG');
        }).catch((err: Error) => {
          log.error('PNG export failed', err);
          toast.error('Failed to export PNG');
        });
      }
    }).catch(() => {
      // html-to-image not installed, fallback to CSV-only message
      toast.info('Image export not available. Use CSV export to download process data.');
    });
  }, [logInfo]);

  const handleExportCSV = useCallback(() => {
    log.info('Exporting CSV');
    
    // Export nodes and edges as CSV
    const nodesCSV = [
      ['Activity', 'Frequency', 'Is Start', 'Is End'].join(','),
      ...dfgNodes.map(node => 
        [
          `"${node.label}"`,
          node.frequency,
          node.isStart,
          node.isEnd
        ].join(',')
      )
    ].join('\n');

    const edgesCSV = [
      ['Source', 'Target', 'Frequency', 'Avg Duration (s)'].join(','),
      ...dfgEdges.map(edge =>
        [
          `"${edge.source}"`,
          `"${edge.target}"`,
          edge.frequency,
          edge.performance ?? ''
        ].join(',')
      )
    ].join('\n');

    const variantsCSV = [
      ['Variant', 'Case Count', 'Frequency %', 'Avg Duration (s)', 'Has Rework'].join(','),
      ...processedVariants.map(v =>
        [
          `"${v.activities.join(' → ')}"`,
          v.caseCount,
          v.frequencyPercent.toFixed(2),
          v.avgDurationSeconds,
          v.hasRework
        ].join(',')
      )
    ].join('\n');

    const fullCSV = `=== ACTIVITIES ===\n${nodesCSV}\n\n=== TRANSITIONS ===\n${edgesCSV}\n\n=== VARIANTS ===\n${variantsCSV}`;

    const blob = new Blob([fullCSV], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${logInfo?.name ?? 'process'}-data.csv`;
    link.click();
    URL.revokeObjectURL(link.href);
    toast.success('Process data exported as CSV');
  }, [dfgNodes, dfgEdges, processedVariants, logInfo]);

  const exportMenuItems = [
    {
      key: 'png',
      label: 'Export as PNG',
      icon: <DownloadOutlined />,
      onClick: handleExportPNG,
    },
    {
      key: 'csv',
      label: 'Export as CSV',
      icon: <DownloadOutlined />,
      onClick: handleExportCSV,
    },
  ];

  // =============================================================================
  // TAB ITEMS
  // =============================================================================

  const tabItems = [
    {
      key: 'variants',
      label: 'Variants',
      children: (
        <VariantPanel
          variants={processedVariants}
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
    {
      key: 'edge',
      label: 'Transition',
      children: (
        <EdgeDetailsPanel
          edge={selectedEdge}
          onClose={() => setSelectedEdgeId(null)}
          totalCases={kpis.totalCases}
        />
      ),
    },
  ];

  // =============================================================================
  // RENDER
  // =============================================================================

  // Error state
  if (error) {
    const errorMessages = [
      dfgError && `DFG: ${(dfgError as Error).message}`,
      variantsError && `Variants: ${(variantsError as Error).message}`,
      activitiesError && `Activities: ${(activitiesError as Error).message}`,
    ].filter(Boolean).join(' | ');

    // Check if this is a 404 (log not found) error
    const is404 = errorMessages.toLowerCase().includes('not found') || 
                  errorMessages.includes('404');
    const isNetworkError = errorMessages.toLowerCase().includes('network') ||
                           errorMessages.toLowerCase().includes('unable to reach') ||
                           errorMessages.toLowerCase().includes('failed to fetch');

    if (is404) {
      return (
        <div style={{ padding: 24 }}>
          <Alert
            message="Event Log Not Found"
            description="This event log may have been deleted or does not exist."
            type="warning"
            showIcon
            action={
              <Space direction="vertical">
                <Button type="primary" onClick={() => navigate('/processes')}>
                  Go to Event Logs
                </Button>
                <Button onClick={() => navigate('/explorer')}>
                  Back to Explorer
                </Button>
              </Space>
            }
          />
        </div>
      );
    }

    if (isNetworkError) {
      return (
        <div style={{ padding: 24 }}>
          <Alert
            message="Server Unavailable"
            description="Unable to connect to the server. Please check that the backend is running and try again."
            type="error"
            showIcon
            action={
              <Button onClick={() => window.location.reload()}>
                Retry
              </Button>
            }
          />
        </div>
      );
    }

    return (
      <div style={{ padding: 24 }}>
        <Alert
          message="Failed to load process map"
          description={errorMessages}
          type="error"
          showIcon
          action={
            <Button onClick={() => navigate('/explorer')}>Go Back</Button>
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
              { title: 'Event Logs', onClick: () => navigate('/processes') },
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
          <Dropdown menu={{ items: exportMenuItems }} trigger={['click']}>
            <Button icon={<DownloadOutlined />}>
              Export
            </Button>
          </Dropdown>
          <Tooltip title={rightPanelOpen ? 'Collapse panel' : 'Expand panel'}>
            <Button
              type="text"
              icon={rightPanelOpen ? <CompressOutlined /> : <ExpandOutlined />}
              onClick={() => setRightPanelOpen(!rightPanelOpen)}
            />
          </Tooltip>
        </Space>
      </div>

      {/* KPI Bar */}
      {!loading && <ProcessKPIBar kpis={kpis} compact />}

      {/* Applied Filters Bar */}
      {appliedFilters.length > 0 && (
        <div
          style={{
            padding: `${tokens.spacing[2]} ${tokens.spacing[4]}`,
            backgroundColor: tokens.colors.neutral[50],
            borderBottom: `1px solid ${tokens.colors.neutral[200]}`,
            display: 'flex',
            alignItems: 'center',
            gap: 8,
            flexWrap: 'wrap',
          }}
        >
          <span style={{ fontSize: 12, color: tokens.colors.neutral[500] }}>
            Active filters:
          </span>
          {appliedFilters.map((filter) => (
            <Tag
              key={filter.id}
              closable
              onClose={() => handleRemoveFilter(filter.id)}
              color={filter.color}
            >
              {filter.label}
            </Tag>
          ))}
          <Button type="link" size="small" onClick={handleClearAllFilters}>
            Clear all
          </Button>
        </div>
      )}

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
              <Spin size="large" />
            </div>
          ) : (
            <ProcessCanvas
              dfgNodes={dfgNodes}
              dfgEdges={dfgEdges}
              selectedNodeId={selectedNodeId}
              selectedEdgeId={selectedEdgeId}
              highlightedPath={highlightedPath}
              onNodeClick={handleNodeClick}
              onEdgeClick={handleEdgeClick}
            />
          )}
        </div>

        {/* Right Panel */}
        {rightPanelOpen && (
          <div
            style={{
              width: 360,
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
        width={380}
        open={filterDrawerOpen}
        onClose={() => setFilterDrawerOpen(false)}
        styles={{ body: { padding: 0 } }}
      >
        <FilterPanel
          filterOptions={filterOptions}
          appliedFilters={appliedFilters}
          onApplyFilter={handleApplyFilter}
          onRemoveFilter={handleRemoveFilter}
          onClearAllFilters={handleClearAllFilters}
        />
      </Drawer>
    </div>
  );
}

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

function hasReworkInVariant(activities: string[]): boolean {
  const seen = new Set<string>();
  for (const activity of activities) {
    if (seen.has(activity)) return true;
    seen.add(activity);
  }
  return false;
}

export default ProcessExplorerPage;
