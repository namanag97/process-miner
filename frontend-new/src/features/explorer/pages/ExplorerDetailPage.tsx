/**
 * ExplorerDetailPage - World-Class Process Mining Explorer
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

import { useState, useCallback, useMemo, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button, Tabs, Spin, Space, Tooltip, Breadcrumb, Drawer, Alert, Tag, Dropdown, Empty, Result, Typography } from 'antd';
import {
  ArrowLeftOutlined,
  DownloadOutlined,
  FilterOutlined,
  ExpandOutlined,
  CompressOutlined,
  ShareAltOutlined,
  PlusOutlined,
  QuestionCircleOutlined,
} from '@ant-design/icons';
import { tokens, toast, logAction, logError, ErrorBoundary, type ActivityDetail } from '@lumina/design-system';
import { createLogger } from '../../../shared/lib/logger';

// Import components
import { CytoscapeCanvas, type ProcessNode, type ProcessEdge } from '../components/CytoscapeCanvas';
import { ProcessKPIBar } from '../components/ProcessKPIBar';
import { VariantPanel } from '../components/VariantPanel';
import { ActivityDetailsPanel } from '../components/ActivityDetailsPanel';
import { EdgeDetailsPanel } from '../components/EdgeDetailsPanel';
import { FilterPanel } from '../components/FilterPanel';
import { CaseCoverageGauge } from '../components/CaseCoverageGauge';
import { ActivitiesPanel, type ActivityItem } from '../components/ActivitiesPanel';

// Import hooks - using unified useExplorerData for optimal performance
import { useExplorerData, useLogDetail } from '../hooks';

// Import types
import {
  hasReworkInVariant,
  type DFGNodeData,
  type DFGEdgeData,
  type ProcessedVariant,
  type ProcessKPIs,
  type FilterOptions,
  type AppliedFilter,
  type EdgeDetail,
  type ActivityData,
} from '../types';

// Import mock data and fallback utilities
import {
  mockOrderToCashDFG,
  mockOrderToCashVariants,
  mockOrderToCashActivities,
  mockOrderToCashLogInfo,
} from '../mocks/orderToCash';
import {
  useFallbackData,
  extractErrorMessages,
  getFallbackStatus,
} from '../utils/fallbackData';

const { Text } = Typography;

const log = createLogger('ExplorerDetailPage');

export function ExplorerDetailPage() {
  // IMPORTANT: Route uses :datasetId (standard naming)
  // Alias as datasetId for backwards compatibility with hooks
  const { datasetId, projectId } = useParams<{ datasetId: string; projectId: string }>();
  const navigate = useNavigate();

  // Navigate back to project
  const getBackPath = () => `/workspace/${projectId}`;

  // UI State
  const [leftPanelOpen] = useState(true);
  const [rightPanelOpen, setRightPanelOpen] = useState(true);
  const [rightPanelTab, setRightPanelTab] = useState('filter');
  const [filterDrawerOpen, setFilterDrawerOpen] = useState(false);

  // Log page mount
  useEffect(() => {
    logAction('ExplorerDetailPage', 'page_mounted', { datasetId, projectId });
  }, [datasetId, projectId]);

  // Selection State
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [selectedEdgeId, setSelectedEdgeId] = useState<string | null>(null);
  const [selectedVariantKey, setSelectedVariantKey] = useState<string | null>(null);

  // Filter State
  const [appliedFilters, setAppliedFilters] = useState<AppliedFilter[]>([]);

  // =============================================================================
  // DATA FETCHING
  // =============================================================================

  const { data: logInfo, isLoading: logLoading } = useLogDetail(datasetId || '');

  // Use unified explorer data hook for better performance (replaces 3 separate API calls)
  const {
    data: explorerData,
    isLoading: explorerLoading,
    error: explorerError,
  } = useExplorerData({
    datasetId: datasetId || '',
    options: { includePerformance: true, topVariants: 50 }
  });

  // Extract individual data from unified response
  const dfgData = explorerData?.dfg;
  const variants = explorerData?.variants;
  const activities = explorerData?.activities;

  // Combine errors (prefer explorerError, but keep individual names for backward compat)
  const dfgError = explorerError;
  const variantsError = explorerError;
  const activitiesError = explorerError;

  const loading = logLoading || explorerLoading;

  // Apply fallbacks - Re-enabled for graceful degradation when backend is unavailable
  const logInfoWithFallback = useFallbackData(
    logInfo,
    null,
    mockOrderToCashLogInfo,
    { source: 'ExplorerDetailPage', hookType: 'useLogDetail', datasetId: datasetId || '', disableFallback: false }
  );

  const dfgDataWithFallback = useFallbackData(
    dfgData,
    dfgError,
    mockOrderToCashDFG,
    { source: 'ExplorerDetailPage', hookType: 'useDFG', datasetId: datasetId || '', endpoint: '/api/visualization/dfg', disableFallback: false }
  );

  const variantsWithFallback = useFallbackData(
    variants,
    variantsError,
    mockOrderToCashVariants,
    { source: 'ExplorerDetailPage', hookType: 'useVariants', datasetId: datasetId || '', endpoint: '/api/datasets/variants', disableFallback: false }
  );

  const activitiesWithFallback = useFallbackData<ActivityDetail[]>(
    activities,
    activitiesError,
    mockOrderToCashActivities,
    { source: 'ExplorerDetailPage', hookType: 'useActivities', datasetId: datasetId || '', endpoint: '/api/discovery/activities', disableFallback: false }
  );

  // Determine if we're using fallback data
  const usingFallbackData = getFallbackStatus(dfgError).usingFallback ||
    getFallbackStatus(variantsError).usingFallback ||
    getFallbackStatus(activitiesError).usingFallback;

  log.debug('Rendering ExplorerDetailPage', {
    datasetId,
    selectedNodeId,
    selectedEdgeId,
    selectedVariantKey,
    loading,
    usingFallbackData,
  });

  // =============================================================================
  // DATA TRANSFORMATIONS
  // =============================================================================

  // Transform DFG nodes for ProcessCanvas
  const dfgNodes = useMemo((): DFGNodeData[] => {
    if (!dfgDataWithFallback?.nodes || !Array.isArray(dfgDataWithFallback.nodes)) {
      return [];
    }

    const activityList = Array.isArray(activitiesWithFallback) ? activitiesWithFallback : [];
    const activityMap = new Map(activityList.map((a) => [a.name, a]));

    return dfgDataWithFallback.nodes.map((node) => {
      const activityDetail = activityMap.get(node.label);
      return {
        id: node.id,
        label: node.label,
        frequency: node.frequency ?? 0,
        isStart: node.isStart ?? false,
        isEnd: node.isEnd ?? false,
        avgDuration: activityDetail?.avgDuration ?? undefined,
        minDuration: activityDetail?.minDuration ?? undefined,
        maxDuration: activityDetail?.maxDuration ?? undefined,
      };
    });
  }, [dfgDataWithFallback, activitiesWithFallback]);

  // Transform DFG edges for ProcessCanvas
  const dfgEdges = useMemo((): DFGEdgeData[] => {
    if (!dfgDataWithFallback?.edges || !Array.isArray(dfgDataWithFallback.edges)) {
      return [];
    }

    return dfgDataWithFallback.edges.map((edge) => ({
      source: edge.source,
      target: edge.target,
      frequency: edge.frequency ?? 0,
      performance: edge.avgDuration,
    }));
  }, [dfgDataWithFallback]);

  // Transform variants for VariantPanel
  const processedVariants = useMemo((): ProcessedVariant[] => {
    if (!variantsWithFallback || !Array.isArray(variantsWithFallback)) {
      return [];
    }

    const sortedVariants = [...variantsWithFallback].sort((a, b) =>
      (b.frequencyPercent ?? 0) - (a.frequencyPercent ?? 0)
    );

    return sortedVariants.map((v, index) => ({
      key: v.key,
      activities: Array.isArray(v.activities) ? v.activities : [],
      caseCount: v.caseCount ?? 0,
      frequencyPercent: v.frequencyPercent ?? 0,
      avgDuration: v.avgDuration ?? null,
      avgDurationSeconds: v.avgDuration ?? 0,
      isHappyPath: index === 0 && (v.frequencyPercent ?? 0) > 50,
      complexityScore: v.complexityScore,
      hasRework: hasReworkInVariant(Array.isArray(v.activities) ? v.activities : []),
    }));
  }, [variantsWithFallback]);

  // Calculate KPIs
  const kpis = useMemo((): ProcessKPIs => {
    const totalCases = processedVariants.reduce((sum, v) => sum + v.caseCount, 0);
    const uniqueVariants = processedVariants.length;
    const uniqueActivities = dfgNodes.length;

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
  }, [processedVariants, dfgNodes]);

  // Build filter options
  const filterOptions = useMemo((): FilterOptions => {
    const activityList = Array.isArray(activitiesWithFallback) ? activitiesWithFallback : [];
    const activityNames = activityList.map((a) => a.name);
    const allResources = new Set<string>();
    activityList.forEach((a) => {
      if (Array.isArray(a.resources)) {
        a.resources.forEach((r: string) => allResources.add(r));
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
  }, [activitiesWithFallback, processedVariants]);

  // Get activity detail for selected node
  const selectedActivity = useMemo((): ActivityData | null => {
    if (!selectedNodeId || !Array.isArray(activitiesWithFallback)) return null;

    const activity = activitiesWithFallback.find(
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
  }, [selectedNodeId, activitiesWithFallback]);

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

  // Note: Path highlighting removed during CytoscapeCanvas migration
  // TODO: Re-implement when adding path highlighting feature to CytoscapeCanvas

  // Transform activities for ActivitiesPanel
  const activitiesPanelData: ActivityItem[] = useMemo(() => {
    if (!Array.isArray(activitiesWithFallback)) return [];
    return activitiesWithFallback.map((a) => ({
      id: a.id || a.name,
      name: a.name,
      frequency: a.frequency ?? 0,
      casePercent: a.frequencyPercent ?? 0,
      avgDuration: a.avgDuration ?? undefined,
    }));
  }, [activitiesWithFallback]);

  // =============================================================================
  // HANDLERS
  // =============================================================================

  const handleNodeClick = useCallback((nodeId: string) => {
    log.debug('Node clicked', { nodeId });
    setSelectedNodeId((prev) => (prev === nodeId ? null : nodeId));
    setSelectedEdgeId(null);
    setRightPanelTab('activity');
  }, []);

  // Handler for CytoscapeCanvas node clicks
  const handleCytoscapeNodeClick = useCallback((node: ProcessNode) => {
    handleNodeClick(node.id);
  }, [handleNodeClick]);

  const handleEdgeClick = useCallback((edgeId: string, source: string, target: string) => {
    log.debug('Edge clicked', { edgeId, source, target });
    setSelectedEdgeId((prev) => (prev === edgeId ? null : edgeId));
    setSelectedNodeId(null);
    setRightPanelTab('edge');
  }, []);

  // Handler for CytoscapeCanvas edge clicks
  const handleCytoscapeEdgeClick = useCallback((edge: ProcessEdge) => {
    handleEdgeClick(edge.id, edge.source, edge.target);
  }, [handleEdgeClick]);

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
        label: `Variant: ${variant.activities.slice(0, 2).join(' \u2192 ')}...`,
        value: { variantKey, activities: variant.activities },
      };
      setAppliedFilters((prev) => [...prev, filter]);
      toast.success('Filtering to variant');
    }
  }, [processedVariants]);

  const handleFilterWithActivity = useCallback(
    (activityId: string) => {
      if (!Array.isArray(activitiesWithFallback)) return;

      const activity = activitiesWithFallback.find(
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
    [activitiesWithFallback]
  );

  const handleFilterWithoutActivity = useCallback(
    (activityId: string) => {
      if (!Array.isArray(activitiesWithFallback)) return;

      const activity = activitiesWithFallback.find(
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
    [activitiesWithFallback]
  );

  const handleApplyFilter = useCallback((filter: AppliedFilter) => {
    logAction('ExplorerDetailPage', 'filter_applied', { filterType: filter.type, filterLabel: filter.label });
    setAppliedFilters((prev) => [...prev, filter]);
    toast.success('Filter applied');
  }, []);

  const handleRemoveFilter = useCallback((filterId: string) => {
    setAppliedFilters((prev) => prev.filter((f) => f.id !== filterId));
    toast.info('Filter removed');
  }, []);

  const handleClearAllFilters = useCallback(() => {
    logAction('ExplorerDetailPage', 'filters_cleared', { count: appliedFilters.length });
    setAppliedFilters([]);
    toast.info('All filters cleared');
  }, [appliedFilters.length]);

  const handleCompareVariants = useCallback((variantKeys: string[]) => {
    toast.info(`Comparing ${variantKeys.length} variants - feature coming soon`);
    logAction('ExplorerDetailPage', 'compare_variants', { count: variantKeys.length, keys: variantKeys });
  }, []);

  const handleExportPNG = useCallback(() => {
    log.info('Exporting PNG');

    // Find the Cytoscape canvas wrapper
    const canvasWrapper = document.querySelector('.cytoscape-canvas-wrapper') as HTMLElement;
    if (!canvasWrapper) {
      toast.error('Unable to export: Canvas not found');
      return;
    }

    // Try to find the actual canvas element inside Cytoscape
    const canvas = canvasWrapper.querySelector('canvas') as HTMLCanvasElement;
    if (canvas) {
      // Direct canvas export (faster, better quality)
      try {
        const dataUrl = canvas.toDataURL('image/png');
        const link = document.createElement('a');
        link.download = `${logInfoWithFallback?.name ?? 'process'}-dfg.png`;
        link.href = dataUrl;
        link.click();
        toast.success('Process map exported as PNG');
        return;
      } catch (err) {
        log.warn('Direct canvas export failed, falling back to html-to-image', err);
      }
    }

    // Fallback to html-to-image for the wrapper
    import('html-to-image').then(({ toPng }) => {
      toPng(canvasWrapper, {
        backgroundColor: '#ffffff',
        quality: 1,
      }).then((dataUrl: string) => {
        const link = document.createElement('a');
        link.download = `${logInfoWithFallback?.name ?? 'process'}-dfg.png`;
        link.href = dataUrl;
        link.click();
        toast.success('Process map exported as PNG');
      }).catch((err: Error) => {
        log.error('PNG export failed', err);
        toast.error('Failed to export PNG');
      });
    }).catch(() => {
      toast.info('Image export not available. Use CSV export to download process data.');
    });
  }, [logInfoWithFallback]);

  const handleExportCSV = useCallback(() => {
    log.info('Exporting CSV');

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
          `"${v.activities.join(' \u2192 ')}"`,
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
    link.download = `${logInfoWithFallback?.name ?? 'process'}-data.csv`;
    link.click();
    URL.revokeObjectURL(link.href);
    toast.success('Process data exported as CSV');
  }, [dfgNodes, dfgEdges, processedVariants, logInfoWithFallback]);

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
      key: 'filter',
      label: 'Filter',
      children: (
        <div style={{ padding: tokens.spacing[3], display: 'flex', flexDirection: 'column', gap: tokens.spacing[4] }}>
          {/* TODO: Replace with real filtered case count when filter backend is implemented
              See Task 2.1 in bug fix task list for backend filter endpoint spec */}
          <CaseCoverageGauge
            percent={appliedFilters.length === 0 ? 100 : Math.max(10, 100 - appliedFilters.length * 15)}
            visibleCases={kpis.totalCases}
            totalCases={kpis.totalCases}
            size={90}
          />
          <div style={{ flex: 1 }}>
            <FilterPanel
              filterOptions={filterOptions}
              appliedFilters={appliedFilters}
              onApplyFilter={handleApplyFilter}
              onRemoveFilter={handleRemoveFilter}
              onClearAllFilters={handleClearAllFilters}
            />
          </div>
        </div>
      ),
    },
    {
      key: 'variants',
      label: 'Variants',
      children: (
        <ErrorBoundary
          fallback={
            <Empty
              description="Variant panel failed to load. Check DevConsole for details."
              style={{ padding: 40 }}
            />
          }
          onError={(_error) => {
            logError('VariantPanel', { datasetId: datasetId || '', componentCrash: true });
          }}
        >
          <VariantPanel
            variants={processedVariants}
            selectedVariantKey={selectedVariantKey}
            onSelectVariant={handleSelectVariant}
            onFilterToVariant={handleFilterToVariant}
            onCompareVariants={handleCompareVariants}
          />
        </ErrorBoundary>
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

  // Check logInfo loading FIRST - we need to know the status before proceeding
  if (logLoading) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '100vh',
          margin: -24,
        }}
      >
        <Spin size="large" />
      </div>
    );
  }

  // Dataset status validation - check if ready for analysis BEFORE checking DFG errors
  // This prevents showing DFG errors for datasets that haven't been analyzed yet
  const datasetStatus = logInfo?.status;

  // If we have no logInfo or status, something is wrong
  if (!logInfo) {
    return (
      <div style={{ padding: 24 }}>
        <Alert
          message="Dataset Not Found"
          description="This dataset may have been deleted or does not exist."
          type="warning"
          showIcon
          action={
            <Button type="primary" onClick={() => navigate(getBackPath())}>
              Go Back
            </Button>
          }
        />
      </div>
    );
  }

  // UNSTRUCTURED: Dataset needs column mapping
  if (datasetStatus === 'unstructured') {
    return (
      <div style={{ padding: tokens.spacing[8], maxWidth: 640, margin: '0 auto' }}>
        <Alert
          message="Column Mapping Required"
          description="Before exploring your process, you need to map the columns in your dataset. This tells us which columns contain the Case ID, Activity, and Timestamp."
          type="info"
          showIcon
          action={
            <Button type="primary" onClick={() => navigate(getBackPath())}>
              Go to Project to Analyze
            </Button>
          }
        />
      </div>
    );
  }

  // ANALYZING: Dataset is being processed
  if (datasetStatus === 'analyzing') {
    return (
      <div style={{ padding: tokens.spacing[8], maxWidth: 640, margin: '0 auto' }}>
        <Alert
          message="Processing Your Data..."
          description="Your dataset is being analyzed. This may take a few moments depending on the file size."
          type="info"
          showIcon
          icon={<Spin />}
          action={
            <Button onClick={() => window.location.reload()}>
              Check Status
            </Button>
          }
        />
      </div>
    );
  }

  // ERROR: Analysis failed
  if (datasetStatus === 'error') {
    return (
      <div style={{ padding: tokens.spacing[8], maxWidth: 640, margin: '0 auto' }}>
        <Alert
          message="Analysis Failed"
          description="There was an error processing your dataset. Please go back and try again."
          type="error"
          showIcon
          action={
            <Button type="primary" onClick={() => navigate(getBackPath())}>
              Go to Project to Retry
            </Button>
          }
        />
      </div>
    );
  }

  // No longer blocking entire page on errors - we use fallback data instead
  // Error banner will be shown inline below

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
            onClick={() => navigate(getBackPath())}
          >
            Back
          </Button>
          <Breadcrumb
            items={[
              { title: 'Projects', onClick: () => navigate('/workspace') },
              { title: 'Project', onClick: () => navigate(`/workspace/${projectId}`) },
              { title: logInfoWithFallback?.name ?? 'Loading...' },
              { title: 'Explorer' },
            ]}
          />
        </Space>

        {/* Right: Actions */}
        <Space size="small">
          <Tooltip title="Share exploration">
            <Button
              type="text"
              icon={<ShareAltOutlined />}
              onClick={() => {
                navigator.clipboard.writeText(window.location.href);
                toast.success('Link copied to clipboard');
              }}
            >
              Share
            </Button>
          </Tooltip>
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
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              logAction('ExplorerDetailPage', 'create_exploration_clicked', { datasetId });
              toast.info('New exploration feature coming soon!');
            }}
          >
            Create Exploration
          </Button>
          <Tooltip title="Help & Documentation">
            <Button
              type="text"
              icon={<QuestionCircleOutlined />}
              onClick={() => {
                logAction('ExplorerDetailPage', 'help_clicked', { datasetId });
                toast.info('Documentation coming soon!');
              }}
            />
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

      {/* Error Banner - show when using fallback data */}
      {usingFallbackData && (
        <Alert
          type="error"
          message="Backend Error - Using Mock Data"
          description={
            <Space direction="vertical" style={{ width: '100%' }}>
              <Text strong>Technical Details:</Text>
              <Text>{extractErrorMessages([dfgError, variantsError, activitiesError])}</Text>
              <Text type="secondary">
                A mock Order-to-Cash process is displayed below for demonstration purposes.
                All functionality is available but data is not real.
              </Text>
            </Space>
          }
          action={
            <Button onClick={() => window.location.reload()}>
              Retry Connection
            </Button>
          }
          showIcon
          closable={false}
          banner
          style={{ borderRadius: 0 }}
        />
      )}

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
        {/* Left Panel - Activities */}
        {leftPanelOpen && (
          <div
            style={{
              width: 260,
              backgroundColor: tokens.colors.neutral[0],
              borderRight: `1px solid ${tokens.colors.neutral[200]}`,
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
            }}
          >
            <ActivitiesPanel
              activities={activitiesPanelData}
              selectedActivityId={selectedNodeId}
              onActivityClick={handleNodeClick}
              onFilterWithActivity={handleFilterWithActivity}
              totalActivities={dfgNodes.length}
            />
          </div>
        )}

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
            <ErrorBoundary
              fallback={
                <Result
                  status="error"
                  title="Graph Rendering Failed"
                  subTitle="The process map could not be rendered. Detailed error logged to DevConsole."
                  extra={
                    <Button type="primary" onClick={() => window.location.reload()}>
                      Reload Page
                    </Button>
                  }
                />
              }
              onError={(_error) => {
                logError('CytoscapeCanvas', { datasetId: datasetId || '', componentCrash: true });
              }}
            >
              <CytoscapeCanvas
                data={{
                  nodes: dfgNodes.map(n => ({
                    id: n.id,
                    label: n.label,
                    frequency: n.frequency,
                    isStart: n.isStart,
                    isEnd: n.isEnd,
                  })),
                  edges: dfgEdges.map((e, i) => ({
                    id: `edge-${e.source}-${e.target}-${i}`,
                    source: e.source,
                    target: e.target,
                    frequency: e.frequency,
                  })),
                }}
                onNodeClick={handleCytoscapeNodeClick}
                onEdgeClick={handleCytoscapeEdgeClick}
              />
            </ErrorBoundary>
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

export default ExplorerDetailPage;
