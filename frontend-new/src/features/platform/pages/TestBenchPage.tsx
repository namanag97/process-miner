/**
 * AnalysisShowcasePage - On-Demand Process Mining Analysis
 * 
 * Key features:
 * - Each analysis runs on-demand when user clicks "Run Analysis"
 * - Single shared Cytoscape graph for all graph-based analyses
 * - Highlights what's unique about each analysis type
 * - Calls real backend APIs
 */

import { useState, useCallback } from 'react';
import { Tabs, Typography, Space, Alert, Card, Row, Col, Button, Spin, Empty, Tag, Tooltip } from 'antd';
import {
  SearchOutlined,
  BranchesOutlined,
  BarChartOutlined,
  ThunderboltOutlined,
  TeamOutlined,
  CheckCircleOutlined,
  FileTextOutlined as _FileTextOutlined,
  ExperimentOutlined,
  PlayCircleOutlined,
  InfoCircleOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { PageHeader, useSDK, tokens } from '@lumina/design-system';
import { CytoscapeCanvas, type ProcessGraphData } from '../../explorer/components/CytoscapeCanvas';

const { Text } = Typography;

// =============================================================================
// Types
// =============================================================================

type AnalysisCategory = 'Discovery' | 'Variants' | 'Statistics' | 'Performance' | 'Organizational' | 'Conformance';

interface AnalysisType {
  id: string;
  name: string;
  category: AnalysisCategory;
  description: string;
  uniqueFeature: string; // What makes this analysis unique
  resultType: 'graph' | 'table' | 'metrics' | 'json';
  apiMethod: string;
  requiresModel?: boolean;
}

interface AnalysisState {
  status: 'idle' | 'loading' | 'success' | 'error';
  data?: unknown;
  error?: string;
  duration?: number;
}

// =============================================================================
// Analysis Definitions - What makes each unique
// =============================================================================

const ANALYSIS_TYPES: AnalysisType[] = [
  // Discovery
  {
    id: 'dfg',
    name: 'Directly-Follows Graph',
    category: 'Discovery',
    description: 'Shows direct transitions between activities',
    uniqueFeature: '📊 Frequency-based: Edge thickness = transition count',
    resultType: 'graph',
    apiMethod: 'discovery.buildDFG',
  },
  {
    id: 'alpha',
    name: 'Alpha Miner',
    category: 'Discovery',
    description: 'Classic Petri net discovery algorithm',
    uniqueFeature: '🔬 Formal: Guarantees footprint-related correctness',
    resultType: 'graph',
    apiMethod: 'discovery.discover',
  },
  {
    id: 'inductive',
    name: 'Inductive Miner',
    category: 'Discovery',
    description: 'Block-structured process tree discovery',
    uniqueFeature: '✅ Sound: Guarantees deadlock-free, terminating models',
    resultType: 'graph',
    apiMethod: 'discovery.discover',
  },
  {
    id: 'heuristic',
    name: 'Heuristics Miner',
    category: 'Discovery',
    description: 'Handles noisy and incomplete logs',
    uniqueFeature: '🔇 Noise-tolerant: Statistical thresholds filter outliers',
    resultType: 'graph',
    apiMethod: 'discovery.discover',
  },

  // Variants
  {
    id: 'variants',
    name: 'Process Variants',
    category: 'Variants',
    description: 'Unique execution paths through the process',
    uniqueFeature: '🔀 Coverage analysis: See which paths are most/least common',
    resultType: 'table',
    apiMethod: 'discovery.getVariants',
  },

  // Statistics  
  {
    id: 'statistics',
    name: 'Basic Statistics',
    category: 'Statistics',
    description: 'Key process metrics and distributions',
    uniqueFeature: '📈 Overview: Cases, events, activities, durations at a glance',
    resultType: 'metrics',
    apiMethod: 'processes.analyze',
  },

  // Performance
  {
    id: 'bottlenecks',
    name: 'Bottleneck Analysis',
    category: 'Performance',
    description: 'Identify activities causing delays',
    uniqueFeature: '⏱️ Time-based: Ranks activities by waiting time impact',
    resultType: 'table',
    apiMethod: 'analytics.getBottlenecks',
  },

  // Organizational
  {
    id: 'handover',
    name: 'Handover of Work',
    category: 'Organizational',
    description: 'Work handover patterns between resources',
    uniqueFeature: '👥 Social network: Who passes work to whom',
    resultType: 'graph',
    apiMethod: 'organizational.getHandoverNetwork',
  },
  {
    id: 'resource_util',
    name: 'Resource Utilization',
    category: 'Organizational',
    description: 'Workload distribution across resources',
    uniqueFeature: '📊 Workload: Events per resource, activity assignments',
    resultType: 'table',
    apiMethod: 'organizational.getWorkload',
  },

  // Conformance
  {
    id: 'token_replay',
    name: 'Token Replay',
    category: 'Conformance',
    description: 'Check conformance using token-based replay',
    uniqueFeature: '🎯 Fitness: How well does the log fit the model',
    resultType: 'metrics',
    apiMethod: 'conformance.check',
    requiresModel: true,
  },
];

const CATEGORY_ORDER: AnalysisCategory[] = ['Discovery', 'Variants', 'Statistics', 'Performance', 'Organizational', 'Conformance'];

const CATEGORY_ICONS: Record<AnalysisCategory, React.ReactNode> = {
  Discovery: <SearchOutlined />,
  Variants: <BranchesOutlined />,
  Statistics: <BarChartOutlined />,
  Performance: <ThunderboltOutlined />,
  Organizational: <TeamOutlined />,
  Conformance: <CheckCircleOutlined />,
};

const CATEGORY_COLORS: Record<AnalysisCategory, string> = {
  Discovery: 'blue',
  Variants: 'purple',
  Statistics: 'cyan',
  Performance: 'orange',
  Organizational: 'green',
  Conformance: 'gold',
};

// =============================================================================
// Components
// =============================================================================

/**
 * Single shared graph visualization panel
 */
function SharedGraphPanel({ data, title }: { data: ProcessGraphData | null; title: string }) {
  if (!data) {
    return (
      <Card style={{ height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Empty description="Run an analysis to see results" />
      </Card>
    );
  }

  return (
    <Card
      title={<Space><SearchOutlined /> {title}</Space>}
      size="small"
      style={{ height: 400 }}
      bodyStyle={{ height: 'calc(100% - 40px)', padding: 0 }}
    >
      <CytoscapeCanvas data={data} layout="dagre" showLabels colorByFrequency />
    </Card>
  );
}

/**
 * Analysis Card with Run button
 */
function AnalysisTypeCard({
  analysis,
  state,
  onRun,
  datasetId,
}: {
  analysis: AnalysisType;
  state: AnalysisState;
  onRun: () => void;
  datasetId: string | null;
}) {
  const isDisabled = !datasetId || (analysis.requiresModel && !datasetId);
  const isLoading = state.status === 'loading';

  return (
    <Card
      size="small"
      style={{ marginBottom: 12 }}
      bodyStyle={{ padding: 12 }}
    >
      <Row justify="space-between" align="middle">
        <Col flex="auto">
          <Space direction="vertical" size={4} style={{ width: '100%' }}>
            <Space>
              <Text strong>{analysis.name}</Text>
              <Tag color={CATEGORY_COLORS[analysis.category]}>{analysis.category}</Tag>
              {state.status === 'success' && (
                <Tag color="success" icon={<CheckCircleOutlined />}>
                  {state.duration}ms
                </Tag>
              )}
              {state.status === 'error' && (
                <Tag color="error">Failed</Tag>
              )}
            </Space>
            <Text type="secondary" style={{ fontSize: 12 }}>{analysis.description}</Text>
            <Tooltip title="What makes this analysis unique">
              <Text style={{ fontSize: 11, color: tokens.colors.primary[500] }}>
                <InfoCircleOutlined style={{ marginRight: 4 }} />
                {analysis.uniqueFeature}
              </Text>
            </Tooltip>
          </Space>
        </Col>
        <Col>
          <Button
            type={state.status === 'success' ? 'default' : 'primary'}
            icon={state.status === 'success' ? <ReloadOutlined /> : <PlayCircleOutlined />}
            loading={isLoading}
            disabled={isDisabled}
            onClick={onRun}
          >
            {state.status === 'success' ? 'Rerun' : 'Run'}
          </Button>
        </Col>
      </Row>

      {state.status === 'error' && (
        <Alert
          message={state.error}
          type="error"
          showIcon
          style={{ marginTop: 8 }}
          closable
        />
      )}
    </Card>
  );
}

/**
 * Results Panel - Shows results based on type
 */
function ResultsPanel({
  analysis,
  state
}: {
  analysis: AnalysisType | null;
  state: AnalysisState;
}) {
  if (!analysis || state.status === 'idle') {
    return (
      <Card style={{ minHeight: 300 }}>
        <Empty description="Select and run an analysis to see results" />
      </Card>
    );
  }

  if (state.status === 'loading') {
    return (
      <Card style={{ minHeight: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Spin size="large" tip={`Running ${analysis.name}...`} />
      </Card>
    );
  }

  if (state.status === 'error') {
    return (
      <Card style={{ minHeight: 300 }}>
        <Empty description={`Failed to run ${analysis.name}`} />
      </Card>
    );
  }

  // Render based on result type
  if (analysis.resultType === 'graph' && state.data) {
    return <SharedGraphPanel data={state.data as ProcessGraphData} title={analysis.name} />;
  }

  // For other types, show JSON for now
  return (
    <Card title={analysis.name} size="small">
      <pre style={{
        background: '#f5f5f5',
        padding: 12,
        borderRadius: 8,
        maxHeight: 400,
        overflow: 'auto',
        fontSize: 11,
      }}>
        {JSON.stringify(state.data, null, 2)}
      </pre>
    </Card>
  );
}

// =============================================================================
// Main Page
// =============================================================================

export function TestBenchPage() {
  const sdk = useSDK();
  const [activeCategory, setActiveCategory] = useState<AnalysisCategory>('Discovery');
  const [selectedDatasetId, setSelectedDatasetId] = useState<string | null>(null);
  const [datasets, setDatasets] = useState<Array<{ id: string; name: string }>>([]);
  const [analysisStates, setAnalysisStates] = useState<Record<string, AnalysisState>>({});
  const [lastRunAnalysis, setLastRunAnalysis] = useState<AnalysisType | null>(null);

  // Load datasets on mount
  useState(() => {
    sdk.processes.list({ pageSize: 20 }).then(res => {
      const items = res.items.map(i => ({ id: i.id, name: i.name }));
      setDatasets(items);
      if (items.length > 0) {
        setSelectedDatasetId(items[0].id);
      }
    }).catch(() => { });
  });

  // Run an analysis
  const runAnalysis = useCallback(async (analysis: AnalysisType) => {
    if (!selectedDatasetId) return;

    setAnalysisStates(prev => ({
      ...prev,
      [analysis.id]: { status: 'loading' },
    }));
    setLastRunAnalysis(analysis);

    const startTime = Date.now();

    try {
      let data: unknown;

      // Call appropriate API based on analysis type
      switch (analysis.id) {
        case 'dfg':
          data = await sdk.discovery.buildDFG(selectedDatasetId);
          // Transform to graph format
          data = transformToGraphData(data);
          break;
        case 'variants':
          data = await sdk.discovery.getVariants(selectedDatasetId, { topN: 20 });
          break;
        case 'statistics':
          data = await sdk.processes.analyze(selectedDatasetId);
          break;
        case 'bottlenecks':
          data = await sdk.analytics.getBottlenecks(selectedDatasetId);
          break;
        case 'handover':
          data = await sdk.organizational.getHandoverNetwork(selectedDatasetId);
          data = transformToGraphData(data);
          break;
        case 'resource_util':
          data = await sdk.organizational.getWorkload(selectedDatasetId);
          break;
        case 'alpha':
        case 'inductive':
        case 'heuristic':
          // These return a model ID, then we'd need to visualize
          const result = await sdk.discovery.discover({
            datasetId: selectedDatasetId,
            minerType: analysis.id === 'heuristic' ? 'heuristics' : analysis.id,
          });
          data = { modelId: result.modelId, message: `Model created: ${result.modelId}` };
          break;
        default:
          throw new Error(`Unknown analysis type: ${analysis.id}`);
      }

      setAnalysisStates(prev => ({
        ...prev,
        [analysis.id]: {
          status: 'success',
          data,
          duration: Date.now() - startTime,
        },
      }));
    } catch (err) {
      setAnalysisStates(prev => ({
        ...prev,
        [analysis.id]: {
          status: 'error',
          error: err instanceof Error ? err.message : 'Unknown error',
          duration: Date.now() - startTime,
        },
      }));
    }
  }, [sdk, selectedDatasetId]);

  const tabItems = CATEGORY_ORDER.map(category => {
    const analyses = ANALYSIS_TYPES.filter(a => a.category === category);
    return {
      key: category,
      label: (
        <Space>
          {CATEGORY_ICONS[category]}
          <span>{category}</span>
          <Text type="secondary" style={{ fontSize: 12 }}>({analyses.length})</Text>
        </Space>
      ),
      children: (
        <Row gutter={24}>
          {/* Left: Analysis list */}
          <Col xs={24} lg={10}>
            {analyses.map(analysis => (
              <AnalysisTypeCard
                key={analysis.id}
                analysis={analysis}
                state={analysisStates[analysis.id] || { status: 'idle' }}
                datasetId={selectedDatasetId}
                onRun={() => runAnalysis(analysis)}
              />
            ))}
          </Col>

          {/* Right: Results panel */}
          <Col xs={24} lg={14}>
            <ResultsPanel
              analysis={lastRunAnalysis?.category === category ? lastRunAnalysis : null}
              state={lastRunAnalysis?.category === category ? (analysisStates[lastRunAnalysis.id] || { status: 'idle' }) : { status: 'idle' }}
            />
          </Col>
        </Row>
      ),
    };
  });

  return (
    <div>
      <PageHeader
        title="Process Mining Analysis Showcase"
        description="Run analyses on-demand against your uploaded datasets"
        actions={
          <Space>
            <ExperimentOutlined style={{ fontSize: 20, color: tokens.colors.primary[500] }} />
          </Space>
        }
      />

      {/* Dataset Selector */}
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={16} align="middle">
          <Col>
            <Text strong>Dataset:</Text>
          </Col>
          <Col flex="auto">
            <select
              value={selectedDatasetId || ''}
              onChange={e => setSelectedDatasetId(e.target.value)}
              style={{
                width: '100%',
                maxWidth: 400,
                padding: '8px 12px',
                borderRadius: 6,
                border: '1px solid #d9d9d9',
              }}
            >
              <option value="" disabled>Select a dataset...</option>
              {datasets.map(d => (
                <option key={d.id} value={d.id}>{d.name} ({d.id.slice(0, 8)}...)</option>
              ))}
            </select>
          </Col>
          <Col>
            {!selectedDatasetId && (
              <Text type="secondary">Upload a dataset first to run analyses</Text>
            )}
          </Col>
        </Row>
      </Card>

      {/* Sample Dataset Info */}
      {datasets.length === 0 && (
        <Alert
          message="Need a Test Dataset?"
          description={
            <span>
              Download our sample <a href="/sample-data/order-to-cash-event-log.csv" download>Order-to-Cash Event Log</a> (25 cases, 10 activities, 8 resources) —
              designed to work with all analysis types. Upload it via the Upload Wizard first.
            </span>
          }
          type="warning"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {/* Info Alert */}
      <Alert
        message="On-Demand Analysis"
        description="Click 'Run' on any analysis to execute it against the selected dataset. Results will appear on the right."
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />

      {/* Category Tabs */}
      <Tabs
        activeKey={activeCategory}
        onChange={(k) => setActiveCategory(k as AnalysisCategory)}
        items={tabItems}
        size="large"
      />
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function transformToGraphData(data: unknown): ProcessGraphData {
  // Transform SDK response to Cytoscape format
  const dfgData = data as {
    nodes?: Array<{ id: string; label: string; frequency?: number }>;
    edges?: Array<{ source: string; target: string; frequency?: number }>;
  };

  if (!dfgData.nodes || !dfgData.edges) {
    // If data doesn't have expected structure, create placeholder
    return {
      nodes: [{ id: 'placeholder', label: 'No graph data', frequency: 1 }],
      edges: [],
    };
  }

  return {
    nodes: dfgData.nodes.map(n => ({
      id: n.id,
      label: n.label || n.id,
      frequency: n.frequency || 1,
    })),
    edges: dfgData.edges.map((e, i) => ({
      id: `e${i}`,
      source: e.source,
      target: e.target,
      frequency: e.frequency || 1,
    })),
  };
}

export default TestBenchPage;
