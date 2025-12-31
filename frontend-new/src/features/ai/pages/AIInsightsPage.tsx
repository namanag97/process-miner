import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Row, Col, Card, Select, Space, Typography, Input, Tag, Skeleton, Alert, Collapse, List, Progress } from 'antd';
import {
  BulbOutlined,
  ThunderboltOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  SearchOutlined,
  ClockCircleOutlined,
  RiseOutlined,
  NodeIndexOutlined,
  ReloadOutlined,
  SendOutlined,
} from '@ant-design/icons';
import { PageHeader, MetricCard, EmptyState, tokens } from '@lumina/design-system';
import { createLogger } from '../../../utils/logger';

const { Text, Title, Paragraph } = Typography;
const { Panel } = Collapse;
const log = createLogger('AIInsightsPage');

// Mock available logs
const mockLogs = [
  { id: '1', name: 'Orders_2024.csv', cases: 5340 },
  { id: '2', name: 'Claims_Process.xes', cases: 2890 },
  { id: '3', name: 'Purchase_Orders.csv', cases: 8200 },
];

// Mock insights data
const mockInsights = {
  performance: [
    {
      id: 'p1',
      type: 'bottleneck',
      severity: 'high',
      title: 'Critical Bottleneck Detected',
      description: '"Approval Review" activity has an average waiting time of 4.2 days, significantly higher than the process average of 0.8 days.',
      impact: '23% of total cycle time',
      recommendation: 'Consider adding parallel approval paths or automating initial reviews.',
    },
    {
      id: 'p2',
      type: 'slow_activity',
      severity: 'medium',
      title: 'Slow Processing Activity',
      description: '"Document Verification" takes 2.1 days on average. This is 40% slower than similar processes.',
      impact: '12% of total cycle time',
      recommendation: 'Implement document pre-screening or automated verification tools.',
    },
  ],
  patterns: [
    {
      id: 'pt1',
      type: 'frequent_pattern',
      severity: 'info',
      title: 'Dominant Process Path',
      description: 'The sequence "Submit → Review → Approve → Complete" appears in 67% of all cases.',
      impact: 'Happy path identified',
      recommendation: 'Optimize this path further as it handles the majority of cases.',
    },
    {
      id: 'pt2',
      type: 'rework',
      severity: 'warning',
      title: 'High Rework Rate',
      description: '"Request Revision" activity is repeated 2.3 times on average per case.',
      impact: '18% additional cycle time',
      recommendation: 'Improve initial submission quality with validation rules.',
    },
  ],
  anomalies: [
    {
      id: 'a1',
      type: 'anomaly',
      severity: 'warning',
      title: 'Unusual Activity Sequence',
      description: '5% of cases skip "Quality Check" before "Final Approval", which may indicate process violations.',
      impact: 'Potential compliance risk',
      recommendation: 'Enforce mandatory quality checks in the workflow system.',
    },
  ],
};

// Severity colors
const severityConfig = {
  high: { color: tokens.colors.error[500], icon: <WarningOutlined /> },
  medium: { color: tokens.colors.warning[500], icon: <ClockCircleOutlined /> },
  info: { color: tokens.colors.primary[500], icon: <BulbOutlined /> },
  warning: { color: tokens.colors.warning[500], icon: <WarningOutlined /> },
};

interface InsightCardProps {
  insight: {
    id: string;
    type: string;
    severity: string;
    title: string;
    description: string;
    impact: string;
    recommendation: string;
  };
}

function InsightCard({ insight }: InsightCardProps) {
  const config = severityConfig[insight.severity as keyof typeof severityConfig] || severityConfig.info;

  return (
    <Card
      size="small"
      style={{ marginBottom: tokens.spacing[3] }}
      title={
        <Space>
          <span style={{ color: config.color }}>{config.icon}</span>
          <Text strong>{insight.title}</Text>
          <Tag color={insight.severity === 'high' ? 'error' : insight.severity === 'warning' ? 'warning' : 'blue'}>
            {insight.type.replace('_', ' ')}
          </Tag>
        </Space>
      }
    >
      <Paragraph style={{ marginBottom: tokens.spacing[2] }}>{insight.description}</Paragraph>
      <Space direction="vertical" size={4} style={{ width: '100%' }}>
        <Text type="secondary">
          <RiseOutlined style={{ marginRight: 4 }} />
          Impact: {insight.impact}
        </Text>
        <Alert
          type="info"
          showIcon
          icon={<CheckCircleOutlined />}
          message={
            <Text style={{ fontSize: tokens.fontSize.sm }}>
              <strong>Recommendation:</strong> {insight.recommendation}
            </Text>
          }
          style={{ padding: '8px 12px' }}
        />
      </Space>
    </Card>
  );
}

export function AIInsightsPage() {
  const navigate = useNavigate();
  const [selectedLogId, setSelectedLogId] = useState<string>(mockLogs[0].id);
  const [isLoading, setIsLoading] = useState(false);
  const [nlQuery, setNlQuery] = useState('');

  const handleLogChange = (logId: string) => {
    log.info('Log selection changed', { logId });
    setSelectedLogId(logId);
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 800);
  };

  const handleNLQuery = () => {
    if (!nlQuery.trim()) return;
    log.info('Natural language query submitted', { query: nlQuery });
    // Mock - just show a toast or feedback
    setNlQuery('');
  };

  const handleRefresh = () => {
    log.info('Refreshing insights');
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 1000);
  };

  const totalInsights =
    mockInsights.performance.length + mockInsights.patterns.length + mockInsights.anomalies.length;

  const highSeverityCount = [...mockInsights.performance, ...mockInsights.patterns, ...mockInsights.anomalies].filter(
    (i) => i.severity === 'high'
  ).length;

  if (mockLogs.length === 0) {
    return (
      <div>
        <PageHeader
          title="AI Insights"
          description="Auto-generated insights from your process data"
        />
        <EmptyState
          icon={<BulbOutlined />}
          title="No event logs available"
          description="Upload an event log to generate AI insights"
          actionLabel="Upload Event Log"
          onAction={() => navigate('/processes/upload')}
        />
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title="AI Insights"
        description="Auto-generated insights from your process data"
        actions={
          <Space>
            <Text type="secondary">Analyzing:</Text>
            <Select
              value={selectedLogId}
              onChange={handleLogChange}
              style={{ width: 200 }}
              options={mockLogs.map((log) => ({
                value: log.id,
                label: log.name,
              }))}
            />
          </Space>
        }
      />

      {/* Summary Stats */}
      <Row gutter={16} style={{ marginBottom: tokens.spacing[6] }}>
        <Col xs={24} sm={6}>
          <MetricCard title="Total Insights" value={totalInsights} loading={isLoading} />
        </Col>
        <Col xs={24} sm={6}>
          <MetricCard
            title="High Priority"
            value={highSeverityCount}
            status={highSeverityCount > 0 ? 'error' : 'success'}
            loading={isLoading}
          />
        </Col>
        <Col xs={24} sm={6}>
          <MetricCard title="Patterns Found" value={mockInsights.patterns.length} loading={isLoading} />
        </Col>
        <Col xs={24} sm={6}>
          <MetricCard
            title="Anomalies"
            value={mockInsights.anomalies.length}
            status={mockInsights.anomalies.length > 0 ? 'warning' : 'success'}
            loading={isLoading}
          />
        </Col>
      </Row>

      {/* Natural Language Query (Mock) */}
      <Card style={{ marginBottom: tokens.spacing[6] }}>
        <Title level={5} style={{ marginBottom: tokens.spacing[3] }}>
          <SearchOutlined style={{ marginRight: 8 }} />
          Ask a Question
        </Title>
        <Space.Compact style={{ width: '100%' }}>
          <Input
            placeholder="Ask about your process in natural language, e.g., 'What causes delays in the approval stage?'"
            value={nlQuery}
            onChange={(e) => setNlQuery(e.target.value)}
            onPressEnter={handleNLQuery}
            style={{ flex: 1 }}
          />
          <button
            onClick={handleNLQuery}
            style={{
              padding: '4px 16px',
              backgroundColor: tokens.colors.primary[500],
              color: 'white',
              border: 'none',
              borderRadius: '0 6px 6px 0',
              cursor: 'pointer',
            }}
          >
            <SendOutlined />
          </button>
        </Space.Compact>
        <Text type="secondary" style={{ fontSize: tokens.fontSize.xs, display: 'block', marginTop: 8 }}>
          Natural language queries are coming soon. This is a preview of the interface.
        </Text>
      </Card>

      {/* Insights by Category */}
      {isLoading ? (
        <Card>
          <Skeleton active paragraph={{ rows: 8 }} />
        </Card>
      ) : (
        <Collapse
          defaultActiveKey={['performance', 'patterns', 'anomalies']}
          style={{ marginBottom: tokens.spacing[4] }}
        >
          <Panel
            header={
              <Space>
                <ThunderboltOutlined style={{ color: tokens.colors.error[500] }} />
                <Text strong>Performance Insights</Text>
                <Tag color="red">{mockInsights.performance.length}</Tag>
              </Space>
            }
            key="performance"
          >
            {mockInsights.performance.map((insight) => (
              <InsightCard key={insight.id} insight={insight} />
            ))}
          </Panel>

          <Panel
            header={
              <Space>
                <NodeIndexOutlined style={{ color: tokens.colors.primary[500] }} />
                <Text strong>Pattern Insights</Text>
                <Tag color="blue">{mockInsights.patterns.length}</Tag>
              </Space>
            }
            key="patterns"
          >
            {mockInsights.patterns.map((insight) => (
              <InsightCard key={insight.id} insight={insight} />
            ))}
          </Panel>

          <Panel
            header={
              <Space>
                <WarningOutlined style={{ color: tokens.colors.warning[500] }} />
                <Text strong>Anomalies</Text>
                <Tag color="warning">{mockInsights.anomalies.length}</Tag>
              </Space>
            }
            key="anomalies"
          >
            {mockInsights.anomalies.map((insight) => (
              <InsightCard key={insight.id} insight={insight} />
            ))}
          </Panel>
        </Collapse>
      )}
    </div>
  );
}

export default AIInsightsPage;
