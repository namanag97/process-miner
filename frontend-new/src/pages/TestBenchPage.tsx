import React, { useState, useEffect } from 'react';
import { Tabs, Card, Row, Col, Button, Typography, Space, Alert, Input, message, Divider, Collapse, Select, Descriptions, Table, Progress, Tag, Tooltip, Switch } from 'antd';
import {
  FolderOutlined,
  InboxOutlined,
  ThunderboltOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  LoadingOutlined,
  PlayCircleOutlined,
  DeleteOutlined,
  UploadOutlined,
  BarChartOutlined,
  TeamOutlined,
  ExperimentOutlined,
  NodeIndexOutlined,
  ClockCircleOutlined,
  ReloadOutlined,
  ApiOutlined,
} from '@ant-design/icons';
import {
  PageHeader,
  MetricCard,
  EmptyState,
  SkeletonCard,
  useSDK,
  tokens,
} from '@lumina/design-system';

const { Title, Text, Paragraph } = Typography;
const { Panel } = Collapse;

type RequestStatus = 'idle' | 'loading' | 'success' | 'error';

interface ApiTestResult {
  status: RequestStatus;
  data?: unknown;
  error?: string;
  duration?: number;
}

/**
 * TestBenchPage - Comprehensive testing environment for FE components and BE API endpoints
 * 
 * Features:
 * - All design-system components with various states
 * - All SDK API endpoints with interactive testing
 * - Real-time response display with timing
 */
export function TestBenchPage() {
  const sdk = useSDK();
  const [activeTab, setActiveTab] = useState('components');
  const [logIdInput, setLogIdInput] = useState('');
  const [modelIdInput, setModelIdInput] = useState('');
  const [predictorIdInput, setPredictorIdInput] = useState('');
  const [resourceInput, setResourceInput] = useState('');
  const [apiResults, setApiResults] = useState<Record<string, ApiTestResult>>({});
  const [logs, setLogs] = useState<Array<{ id: string; name: string }>>([]);
  const [expandResults, setExpandResults] = useState(true);

  // Fetch logs on mount for selector
  useEffect(() => {
    sdk.processes.list({ pageSize: 20 }).then(res => {
      setLogs(res.items.map(i => ({ id: i.id, name: i.name })));
      if (res.items.length > 0 && !logIdInput) {
        setLogIdInput(res.items[0].id);
      }
    }).catch(() => {});
  }, []);

  // Helper to run API tests
  const runApiTest = async (key: string, apiFn: () => Promise<unknown>) => {
    setApiResults((prev) => ({ ...prev, [key]: { status: 'loading' } }));
    const startTime = Date.now();
    try {
      const data = await apiFn();
      setApiResults((prev) => ({
        ...prev,
        [key]: { status: 'success', data, duration: Date.now() - startTime },
      }));
      message.success(`${key} — ${Date.now() - startTime}ms`);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setApiResults((prev) => ({
        ...prev,
        [key]: { status: 'error', error: errorMessage, duration: Date.now() - startTime },
      }));
      message.error(`${key} failed`);
    }
  };

  const getStatusIcon = (status: RequestStatus) => {
    switch (status) {
      case 'loading':
        return <LoadingOutlined spin style={{ color: '#1890ff' }} />;
      case 'success':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'error':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
      default:
        return <ApiOutlined style={{ color: '#d9d9d9' }} />;
    }
  };

  const renderResult = (key: string) => {
    const result = apiResults[key];
    if (!result || result.status === 'idle') return null;

    const renderData = () => {
      if (result.status !== 'success' || result.data === undefined) return null;
      if (!expandResults) return <Text type="secondary">Result hidden. Toggle to show.</Text>;
      return (
        <pre
          style={{
            background: '#f5f5f5',
            padding: 12,
            borderRadius: 8,
            marginTop: 8,
            maxHeight: 250,
            overflow: 'auto',
            fontSize: 11,
          }}
        >
          {JSON.stringify(result.data, null, 2)}
        </pre>
      );
    };

    return (
      <div style={{ marginTop: 8 }}>
        <Space>
          {getStatusIcon(result.status)}
          {result.duration && <Tag>{result.duration}ms</Tag>}
        </Space>
        {renderData()}
        {result.status === 'error' && result.error && (
          <Alert message={result.error} type="error" style={{ marginTop: 8 }} showIcon />
        )}
      </div>
    );
  };

  // === COMPONENTS TAB ===
  const componentsTab = (
    <div>
      <Title level={4}>Design System Components</Title>
      <Paragraph type="secondary">
        Interactive showcase of all reusable UI components with various states.
      </Paragraph>

      {/* MetricCard Section */}
      <Divider orientation="left">MetricCard (6 variants)</Divider>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={6}>
          <MetricCard title="Default" value="1,234" suffix="items" />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <MetricCard
            title="Success + Trend Up"
            value="89.5"
            suffix="%"
            status="success"
            trend={{ value: 12.5, isPositive: true, label: 'vs last month' }}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <MetricCard
            title="Warning + Trend Down"
            value="3.2"
            suffix="hrs"
            status="warning"
            trend={{ value: 5.3, isPositive: false }}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <MetricCard
            title="Error Status"
            value="15"
            status="error"
            trend={{ value: 28, isPositive: false, label: 'critical' }}
          />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <MetricCard title="Loading State" value="—" loading />
        </Col>
        <Col xs={24} sm={12} md={6}>
          <MetricCard
            title="Clickable"
            value="Click Me!"
            onClick={() => message.info('MetricCard clicked!')}
          />
        </Col>
      </Row>

      {/* EmptyState Section */}
      <Divider orientation="left">EmptyState</Divider>
      <Card>
        <EmptyState
          icon={<InboxOutlined />}
          title="No Data Found"
          description="Upload your first event log to start exploring process insights."
          actionLabel="Upload File"
          onAction={() => message.info('Upload action triggered!')}
        />
      </Card>

      {/* PageHeader Section */}
      <Divider orientation="left">PageHeader</Divider>
      <Card>
        <PageHeader
          title="Sample Page Title"
          description="This is a sample page header with breadcrumb and actions."
          breadcrumb={[
            { label: 'Home', onClick: () => message.info('Home clicked') },
            { label: 'Section', onClick: () => message.info('Section clicked') },
            { label: 'Current Page' },
          ]}
          showBack
          onBack={() => message.info('Back clicked!')}
          actions={
            <Space>
              <Button>Secondary</Button>
              <Button type="primary">Primary</Button>
            </Space>
          }
        />
      </Card>

      {/* SkeletonCard Section */}
      <Divider orientation="left">SkeletonCard (3 variants)</Divider>
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={8}>
          <SkeletonCard lines={2} />
        </Col>
        <Col xs={24} sm={12} md={8}>
          <SkeletonCard lines={4} avatar />
        </Col>
        <Col xs={24} sm={12} md={8}>
          <SkeletonCard lines={3} height={180} />
        </Col>
      </Row>

      {/* Tables Section */}
      <Divider orientation="left">Ant Design Table</Divider>
      <Card>
        <Table
          dataSource={[
            { key: '1', activity: 'Order Received', frequency: 1250, avgDuration: '2.5 hrs' },
            { key: '2', activity: 'Processing', frequency: 1180, avgDuration: '4.2 hrs' },
            { key: '3', activity: 'Quality Check', frequency: 980, avgDuration: '1.8 hrs' },
          ]}
          columns={[
            { title: 'Activity', dataIndex: 'activity', key: 'activity' },
            { title: 'Frequency', dataIndex: 'frequency', key: 'frequency', render: (v: number) => <Tag color="blue">{v}</Tag> },
            { title: 'Avg Duration', dataIndex: 'avgDuration', key: 'avgDuration' },
          ]}
          pagination={false}
          size="small"
        />
      </Card>

      {/* Progress Indicators */}
      <Divider orientation="left">Progress Indicators</Divider>
      <Card>
        <Space direction="vertical" style={{ width: '100%' }} size={16}>
          <div>
            <Text>Linear Progress</Text>
            <Progress percent={75} status="active" />
          </div>
          <Row gutter={24}>
            <Col span={8}>
              <Progress type="circle" percent={87} strokeColor={tokens.colors.success[500]} />
              <Text style={{ display: 'block', textAlign: 'center', marginTop: 8 }}>Fitness</Text>
            </Col>
            <Col span={8}>
              <Progress type="circle" percent={92} strokeColor={tokens.colors.primary[500]} />
              <Text style={{ display: 'block', textAlign: 'center', marginTop: 8 }}>Precision</Text>
            </Col>
            <Col span={8}>
              <Progress type="circle" percent={78} strokeColor={tokens.colors.warning[500]} />
              <Text style={{ display: 'block', textAlign: 'center', marginTop: 8 }}>Generalization</Text>
            </Col>
          </Row>
        </Space>
      </Card>

      {/* Tags & Badges */}
      <Divider orientation="left">Tags & Status Indicators</Divider>
      <Card>
        <Space wrap size={12}>
          <Tag color="success">Completed</Tag>
          <Tag color="processing">In Progress</Tag>
          <Tag color="warning">Pending</Tag>
          <Tag color="error">Failed</Tag>
          <Tag color="default">Default</Tag>
          <Tag icon={<CheckCircleOutlined />} color="success">Conformant</Tag>
          <Tag icon={<CloseCircleOutlined />} color="error">Deviation</Tag>
        </Space>
      </Card>
    </div>
  );

  // === API ENDPOINTS TAB ===
  const apiEndpointsTab = (
    <div>
      <Title level={4}>API Endpoint Tester</Title>
      <Paragraph type="secondary">
        Test all {8} SDK modules against the live backend. Select a log to use for endpoint testing.
      </Paragraph>

      {/* Configuration Card */}
      <Card style={{ marginBottom: 16 }}>
        <Row gutter={16}>
          <Col xs={24} md={8}>
            <Text strong>Log ID:</Text>
            <Select
              style={{ width: '100%', marginTop: 4 }}
              placeholder="Select a log"
              value={logIdInput || undefined}
              onChange={setLogIdInput}
              options={logs.map(l => ({ value: l.id, label: `${l.name} (${l.id.slice(0, 8)}...)` }))}
              notFoundContent="No logs found. Run List Processes first."
            />
          </Col>
          <Col xs={24} md={8}>
            <Text strong>Model ID (for conformance/sim):</Text>
            <Input
              style={{ marginTop: 4 }}
              placeholder="Model ID"
              value={modelIdInput}
              onChange={(e) => setModelIdInput(e.target.value)}
            />
          </Col>
          <Col xs={24} md={8}>
            <Text strong>Predictor ID:</Text>
            <Input
              style={{ marginTop: 4 }}
              placeholder="Predictor ID"
              value={predictorIdInput}
              onChange={(e) => setPredictorIdInput(e.target.value)}
            />
          </Col>
        </Row>
        <div style={{ marginTop: 12 }}>
          <Space>
            <Text>Show Results:</Text>
            <Switch checked={expandResults} onChange={setExpandResults} />
          </Space>
        </div>
      </Card>

      <Collapse defaultActiveKey={['processes', 'discovery']}>
        {/* PROCESSES MODULE */}
        <Panel header={<><FolderOutlined /> <strong>Processes</strong> — 6 endpoints</>} key="processes">
          <Space wrap style={{ marginBottom: 12 }}>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('processes.list', () => sdk.processes.list())} loading={apiResults['processes.list']?.status === 'loading'}>
              list()
            </Button>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('processes.get', () => sdk.processes.get(logIdInput))} loading={apiResults['processes.get']?.status === 'loading'} disabled={!logIdInput}>
              get(logId)
            </Button>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('processes.analyze', () => sdk.processes.analyze(logIdInput))} loading={apiResults['processes.analyze']?.status === 'loading'} disabled={!logIdInput}>
              analyze(logId)
            </Button>
            <Button icon={<DeleteOutlined />} danger onClick={() => { if (window.confirm('Delete this log?')) runApiTest('processes.delete', () => sdk.processes.delete(logIdInput)); }} loading={apiResults['processes.delete']?.status === 'loading'} disabled={!logIdInput}>
              delete(logId)
            </Button>
          </Space>
          <Alert message="ingest() and detectColumns() require file upload — test via Upload Wizard" type="info" showIcon style={{ marginBottom: 8 }} />
          {renderResult('processes.list')}
          {renderResult('processes.get')}
          {renderResult('processes.analyze')}
          {renderResult('processes.delete')}
        </Panel>

        {/* DISCOVERY MODULE */}
        <Panel header={<><ThunderboltOutlined /> <strong>Discovery</strong> — 4 endpoints</>} key="discovery">
          <Space wrap style={{ marginBottom: 12 }}>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('discovery.buildDFG', () => sdk.discovery.buildDFG(logIdInput))} loading={apiResults['discovery.buildDFG']?.status === 'loading'} disabled={!logIdInput}>
              buildDFG(logId)
            </Button>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('discovery.getVariants', () => sdk.discovery.getVariants(logIdInput))} loading={apiResults['discovery.getVariants']?.status === 'loading'} disabled={!logIdInput}>
              getVariants(logId)
            </Button>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('discovery.getActivities', () => sdk.discovery.getActivities(logIdInput))} loading={apiResults['discovery.getActivities']?.status === 'loading'} disabled={!logIdInput}>
              getActivities(logId)
            </Button>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('discovery.discover', () => sdk.discovery.discover({ logId: logIdInput }))} loading={apiResults['discovery.discover']?.status === 'loading'} disabled={!logIdInput}>
              discover(logId)
            </Button>
          </Space>
          {renderResult('discovery.buildDFG')}
          {renderResult('discovery.getVariants')}
          {renderResult('discovery.getActivities')}
          {renderResult('discovery.discover')}
        </Panel>

        {/* ANALYTICS MODULE */}
        <Panel header={<><BarChartOutlined /> <strong>Analytics</strong> — 4 endpoints</>} key="analytics">
          <Space wrap style={{ marginBottom: 12 }}>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('analytics.getPerformance', () => sdk.analytics.getPerformance(logIdInput))} loading={apiResults['analytics.getPerformance']?.status === 'loading'} disabled={!logIdInput}>
              getPerformance(logId)
            </Button>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('analytics.getRework', () => sdk.analytics.getRework(logIdInput))} loading={apiResults['analytics.getRework']?.status === 'loading'} disabled={!logIdInput}>
              getRework(logId)
            </Button>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('analytics.getBottlenecks', () => sdk.analytics.getBottlenecks(logIdInput))} loading={apiResults['analytics.getBottlenecks']?.status === 'loading'} disabled={!logIdInput}>
              getBottlenecks(logId)
            </Button>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('analytics.getCycleTime', () => sdk.analytics.getCycleTime(logIdInput))} loading={apiResults['analytics.getCycleTime']?.status === 'loading'} disabled={!logIdInput}>
              getCycleTime(logId)
            </Button>
          </Space>
          {renderResult('analytics.getPerformance')}
          {renderResult('analytics.getRework')}
          {renderResult('analytics.getBottlenecks')}
          {renderResult('analytics.getCycleTime')}
        </Panel>

        {/* CONFORMANCE MODULE */}
        <Panel header={<><CheckCircleOutlined /> <strong>Conformance</strong> — 2 endpoints</>} key="conformance">
          <Space wrap style={{ marginBottom: 12 }}>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('conformance.check', () => sdk.conformance.check({ logId: logIdInput, modelId: modelIdInput }))} loading={apiResults['conformance.check']?.status === 'loading'} disabled={!logIdInput || !modelIdInput}>
              check(logId, modelId)
            </Button>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('conformance.getDiagnostics', () => sdk.conformance.getDiagnostics(logIdInput, modelIdInput))} loading={apiResults['conformance.getDiagnostics']?.status === 'loading'} disabled={!logIdInput || !modelIdInput}>
              getDiagnostics(logId, modelId)
            </Button>
          </Space>
          <Alert message="Requires a Model ID — run discovery.discover() first to get one" type="info" showIcon style={{ marginBottom: 8 }} />
          {renderResult('conformance.check')}
          {renderResult('conformance.getDiagnostics')}
        </Panel>

        {/* AI MODULE */}
        <Panel header={<><ExperimentOutlined /> <strong>AI</strong> — 3 endpoints</>} key="ai">
          <Space wrap style={{ marginBottom: 12 }}>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('ai.listPredictors', () => sdk.ai.listPredictors())} loading={apiResults['ai.listPredictors']?.status === 'loading'}>
              listPredictors()
            </Button>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('ai.getInsights', () => sdk.ai.getInsights(logIdInput))} loading={apiResults['ai.getInsights']?.status === 'loading'} disabled={!logIdInput}>
              getInsights(logId)
            </Button>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('ai.getPredictorDetail', () => sdk.ai.getPredictorDetail(predictorIdInput))} loading={apiResults['ai.getPredictorDetail']?.status === 'loading'} disabled={!predictorIdInput}>
              getPredictorDetail(predictorId)
            </Button>
          </Space>
          {renderResult('ai.listPredictors')}
          {renderResult('ai.getInsights')}
          {renderResult('ai.getPredictorDetail')}
        </Panel>

        {/* PREDICTIONS MODULE */}
        <Panel header={<><NodeIndexOutlined /> <strong>Predictions</strong> — 7 endpoints</>} key="predictions">
          <Space wrap style={{ marginBottom: 12 }}>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('predictions.listPredictors', () => sdk.predictions.listPredictors(logIdInput))} loading={apiResults['predictions.listPredictors']?.status === 'loading'} disabled={!logIdInput}>
              listPredictors(logId)
            </Button>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('predictions.trainPredictor', () => sdk.predictions.trainPredictor(logIdInput, { targetType: 'next_activity' }))} loading={apiResults['predictions.trainPredictor']?.status === 'loading'} disabled={!logIdInput}>
              trainPredictor(logId, next_activity)
            </Button>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('predictions.getPredictor', () => sdk.predictions.getPredictor(predictorIdInput))} loading={apiResults['predictions.getPredictor']?.status === 'loading'} disabled={!predictorIdInput}>
              getPredictor(predictorId)
            </Button>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('predictions.predict', () => sdk.predictions.predict(predictorIdInput, ['Activity A', 'Activity B']))} loading={apiResults['predictions.predict']?.status === 'loading'} disabled={!predictorIdInput}>
              predict(predictorId, [A, B])
            </Button>
            <Button icon={<DeleteOutlined />} danger onClick={() => { if (window.confirm('Delete this predictor?')) runApiTest('predictions.deletePredictor', () => sdk.predictions.deletePredictor(predictorIdInput)); }} loading={apiResults['predictions.deletePredictor']?.status === 'loading'} disabled={!predictorIdInput}>
              deletePredictor(predictorId)
            </Button>
          </Space>
          {renderResult('predictions.listPredictors')}
          {renderResult('predictions.trainPredictor')}
          {renderResult('predictions.getPredictor')}
          {renderResult('predictions.predict')}
          {renderResult('predictions.deletePredictor')}
        </Panel>

        {/* ORGANIZATIONAL MODULE */}
        <Panel header={<><TeamOutlined /> <strong>Organizational</strong> — 6 endpoints</>} key="organizational">
          <div style={{ marginBottom: 8 }}>
            <Text strong>Resource Name (for profile):</Text>
            <Input placeholder="e.g., John Smith" value={resourceInput} onChange={(e) => setResourceInput(e.target.value)} style={{ width: 200, marginLeft: 8 }} />
          </div>
          <Space wrap style={{ marginBottom: 12 }}>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('organizational.getHandoverNetwork', () => sdk.organizational.getHandoverNetwork(logIdInput))} loading={apiResults['organizational.getHandoverNetwork']?.status === 'loading'} disabled={!logIdInput}>
              getHandoverNetwork(logId)
            </Button>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('organizational.getCollaborationNetwork', () => sdk.organizational.getCollaborationNetwork(logIdInput))} loading={apiResults['organizational.getCollaborationNetwork']?.status === 'loading'} disabled={!logIdInput}>
              getCollaborationNetwork(logId)
            </Button>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('organizational.getResourceSimilarity', () => sdk.organizational.getResourceSimilarity(logIdInput))} loading={apiResults['organizational.getResourceSimilarity']?.status === 'loading'} disabled={!logIdInput}>
              getResourceSimilarity(logId)
            </Button>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('organizational.getRoles', () => sdk.organizational.getRoles(logIdInput))} loading={apiResults['organizational.getRoles']?.status === 'loading'} disabled={!logIdInput}>
              getRoles(logId)
            </Button>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('organizational.getResourceProfile', () => sdk.organizational.getResourceProfile(logIdInput, resourceInput))} loading={apiResults['organizational.getResourceProfile']?.status === 'loading'} disabled={!logIdInput || !resourceInput}>
              getResourceProfile(logId, resource)
            </Button>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('organizational.getWorkload', () => sdk.organizational.getWorkload(logIdInput))} loading={apiResults['organizational.getWorkload']?.status === 'loading'} disabled={!logIdInput}>
              getWorkload(logId)
            </Button>
          </Space>
          {renderResult('organizational.getHandoverNetwork')}
          {renderResult('organizational.getCollaborationNetwork')}
          {renderResult('organizational.getResourceSimilarity')}
          {renderResult('organizational.getRoles')}
          {renderResult('organizational.getResourceProfile')}
          {renderResult('organizational.getWorkload')}
        </Panel>

        {/* SIMULATION MODULE */}
        <Panel header={<><ClockCircleOutlined /> <strong>Simulation</strong> — 3 endpoints</>} key="simulation">
          <Space wrap style={{ marginBottom: 12 }}>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('simulation.playOut', () => sdk.simulation.playOut(modelIdInput, { numTraces: 100 }))} loading={apiResults['simulation.playOut']?.status === 'loading'} disabled={!modelIdInput}>
              playOut(modelId, 100 traces)
            </Button>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('simulation.simulate', () => sdk.simulation.simulate(logIdInput, [{ type: 'remove_activity', activity: 'Test' }]))} loading={apiResults['simulation.simulate']?.status === 'loading'} disabled={!logIdInput}>
              simulate(logId, modifications)
            </Button>
            <Button icon={<PlayCircleOutlined />} onClick={() => runApiTest('simulation.estimateCapacity', () => sdk.simulation.estimateCapacity(logIdInput, 100))} loading={apiResults['simulation.estimateCapacity']?.status === 'loading'} disabled={!logIdInput}>
              estimateCapacity(logId, 100)
            </Button>
          </Space>
          <Alert message="playOut requires a Model ID — run discovery.discover() first" type="info" showIcon style={{ marginBottom: 8 }} />
          {renderResult('simulation.playOut')}
          {renderResult('simulation.simulate')}
          {renderResult('simulation.estimateCapacity')}
        </Panel>
      </Collapse>

      {/* Summary */}
      <Card style={{ marginTop: 16 }}>
        <Descriptions title="API Summary" bordered size="small">
          <Descriptions.Item label="Total Modules">8</Descriptions.Item>
          <Descriptions.Item label="Total Endpoints">35</Descriptions.Item>
          <Descriptions.Item label="Selected Log">{logIdInput ? `${logIdInput.slice(0, 12)}...` : 'None'}</Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  );

  const items = [
    { key: 'components', label: 'Components', children: componentsTab },
    { key: 'api', label: 'API Endpoints', children: apiEndpointsTab },
  ];

  return (
    <div>
      <PageHeader
        title="Test Bench"
        description="Comprehensive testing environment for all frontend components and backend API endpoints"
        actions={
          <Button icon={<ReloadOutlined />} onClick={() => window.location.reload()}>
            Reset
          </Button>
        }
      />
      <Tabs activeKey={activeTab} onChange={setActiveTab} items={items} size="large" />
    </div>
  );
}

export default TestBenchPage;
