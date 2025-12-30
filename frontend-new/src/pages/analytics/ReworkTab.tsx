import React from 'react';
import { Row, Col, Card, Table, Progress, Typography, Space, Tag, Tooltip } from 'antd';
import {
  ReloadOutlined,
  DollarOutlined,
  WarningOutlined,
  InfoCircleOutlined,
  ArrowRightOutlined,
} from '@ant-design/icons';
import { MetricCard, tokens, formatCompactNumber, formatDuration } from '@lumina/design-system';
import { createLogger } from '../../utils/logger';

const { Text, Title } = Typography;
const log = createLogger('ReworkTab');

// Mock rework data
const mockReworkStats = {
  casesWithRework: 1250,
  totalCases: 5340,
  reworkPercentage: 23.4,
  totalLoops: 3450,
  avgLoopsPerCase: 2.76,
  estimatedCost: 125000,
};

const mockLoopFrequency = [
  { from: 'Review', to: 'Revision', frequency: 890, avgDuration: 28800, reason: 'Incomplete documentation' },
  { from: 'Approval', to: 'Review', frequency: 650, avgDuration: 43200, reason: 'Missing signatures' },
  { from: 'Validation', to: 'Data Entry', frequency: 420, avgDuration: 14400, reason: 'Data errors' },
  { from: 'Quality Check', to: 'Processing', frequency: 380, avgDuration: 21600, reason: 'Quality issues' },
  { from: 'Delivery', to: 'Preparation', frequency: 210, avgDuration: 86400, reason: 'Wrong items' },
];

const mockCasesWithMostRework = [
  { caseId: 'CASE-2341', loops: 8, activities: 24, totalDuration: 604800, status: 'completed' },
  { caseId: 'CASE-1892', loops: 7, activities: 21, totalDuration: 518400, status: 'completed' },
  { caseId: 'CASE-3102', loops: 6, activities: 19, totalDuration: 432000, status: 'in-progress' },
  { caseId: 'CASE-2567', loops: 6, activities: 18, totalDuration: 345600, status: 'completed' },
  { caseId: 'CASE-1456', loops: 5, activities: 16, totalDuration: 259200, status: 'completed' },
];

export function ReworkTab() {
  log.debug('Rendering ReworkTab');

  const loopColumns = [
    {
      title: 'Loop Pattern',
      key: 'pattern',
      render: (_: unknown, record: typeof mockLoopFrequency[0]) => (
        <Space>
          <Tag color="blue">{record.from}</Tag>
          <ArrowRightOutlined style={{ color: tokens.colors.neutral[400] }} />
          <Tag color="orange">{record.to}</Tag>
        </Space>
      ),
    },
    {
      title: 'Frequency',
      dataIndex: 'frequency',
      key: 'frequency',
      render: (val: number) => (
        <Text strong style={{ color: val > 500 ? tokens.colors.error[500] : tokens.colors.neutral[800] }}>
          {formatCompactNumber(val)}
        </Text>
      ),
    },
    {
      title: 'Avg Time Lost',
      dataIndex: 'avgDuration',
      key: 'avgDuration',
      render: (seconds: number) => formatDuration(seconds),
    },
    {
      title: 'Common Reason',
      dataIndex: 'reason',
      key: 'reason',
      render: (text: string) => <Text type="secondary">{text}</Text>,
    },
  ];

  const casesColumns = [
    {
      title: 'Case ID',
      dataIndex: 'caseId',
      key: 'caseId',
      render: (text: string) => <Text code>{text}</Text>,
    },
    {
      title: 'Loops',
      dataIndex: 'loops',
      key: 'loops',
      render: (val: number) => (
        <Tag color={val > 6 ? 'error' : val > 4 ? 'warning' : 'default'}>
          {val} loops
        </Tag>
      ),
    },
    {
      title: 'Activities',
      dataIndex: 'activities',
      key: 'activities',
      render: (val: number) => formatCompactNumber(val),
    },
    {
      title: 'Total Duration',
      dataIndex: 'totalDuration',
      key: 'totalDuration',
      render: (seconds: number) => formatDuration(seconds),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'completed' ? 'success' : 'processing'}>
          {status.toUpperCase()}
        </Tag>
      ),
    },
  ];

  const reworkPercentage = mockReworkStats.reworkPercentage;

  return (
    <div>
      {/* KPI Row */}
      <Row gutter={16} style={{ marginBottom: tokens.spacing[6] }}>
        <Col xs={24} sm={6}>
          <MetricCard
            title="Rework Rate"
            value={`${reworkPercentage}%`}
            status={reworkPercentage > 25 ? 'error' : reworkPercentage > 15 ? 'warning' : 'success'}
          />
        </Col>
        <Col xs={24} sm={6}>
          <MetricCard
            title="Cases with Rework"
            value={formatCompactNumber(mockReworkStats.casesWithRework)}
            suffix={`/ ${formatCompactNumber(mockReworkStats.totalCases)}`}
          />
        </Col>
        <Col xs={24} sm={6}>
          <MetricCard
            title="Total Loops"
            value={formatCompactNumber(mockReworkStats.totalLoops)}
          />
        </Col>
        <Col xs={24} sm={6}>
          <MetricCard
            title="Estimated Cost"
            value={`$${formatCompactNumber(mockReworkStats.estimatedCost)}`}
            status="warning"
          />
        </Col>
      </Row>

      {/* Rework Summary Visual */}
      <Card style={{ marginBottom: tokens.spacing[6] }}>
        <Row gutter={24} align="middle">
          <Col xs={24} sm={8}>
            <div style={{ textAlign: 'center' }}>
              <Progress
                type="circle"
                percent={reworkPercentage}
                strokeColor={reworkPercentage > 25 ? tokens.colors.error[500] : reworkPercentage > 15 ? tokens.colors.warning[500] : tokens.colors.success[500]}
                strokeWidth={10}
                size={140}
                format={(percent) => (
                  <div>
                    <div style={{ fontSize: tokens.fontSize['3xl'], fontWeight: tokens.fontWeight.bold }}>
                      {percent}%
                    </div>
                    <div style={{ fontSize: tokens.fontSize.sm, color: tokens.colors.neutral[500] }}>
                      Rework Rate
                    </div>
                  </div>
                )}
              />
            </div>
          </Col>
          <Col xs={24} sm={16}>
            <Space direction="vertical" size={16} style={{ width: '100%' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <Text>Cases without rework</Text>
                  <Text strong>{formatCompactNumber(mockReworkStats.totalCases - mockReworkStats.casesWithRework)}</Text>
                </div>
                <Progress
                  percent={100 - reworkPercentage}
                  strokeColor={tokens.colors.success[500]}
                  trailColor={tokens.colors.neutral[200]}
                  showInfo={false}
                />
              </div>
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                  <Text>Cases with rework</Text>
                  <Text strong>{formatCompactNumber(mockReworkStats.casesWithRework)}</Text>
                </div>
                <Progress
                  percent={reworkPercentage}
                  strokeColor={reworkPercentage > 25 ? tokens.colors.error[500] : tokens.colors.warning[500]}
                  trailColor={tokens.colors.neutral[200]}
                  showInfo={false}
                />
              </div>
            </Space>
          </Col>
        </Row>
      </Card>

      <Row gutter={24}>
        {/* Loop Frequency */}
        <Col xs={24} lg={14}>
          <Card
            title={
              <Space>
                <ReloadOutlined style={{ color: tokens.colors.warning[500] }} />
                <span>Top Loop Patterns</span>
                <Tooltip title="Most frequent activity loops causing rework">
                  <InfoCircleOutlined style={{ color: tokens.colors.neutral[400] }} />
                </Tooltip>
              </Space>
            }
            style={{ marginBottom: tokens.spacing[6] }}
          >
            <Table
              dataSource={mockLoopFrequency}
              columns={loopColumns}
              rowKey={(record) => `${record.from}-${record.to}`}
              pagination={false}
              size="middle"
            />
          </Card>
        </Col>

        {/* Cases with Most Rework */}
        <Col xs={24} lg={10}>
          <Card
            title={
              <Space>
                <WarningOutlined style={{ color: tokens.colors.error[500] }} />
                <span>Cases with Most Rework</span>
              </Space>
            }
            style={{ marginBottom: tokens.spacing[6] }}
          >
            <Table
              dataSource={mockCasesWithMostRework}
              columns={casesColumns}
              rowKey="caseId"
              pagination={false}
              size="small"
            />
          </Card>
        </Col>
      </Row>

      {/* Cost Analysis */}
      <Card
        title={
          <Space>
            <DollarOutlined style={{ color: tokens.colors.success[500] }} />
            <span>Rework Cost Analysis</span>
          </Space>
        }
      >
        <Row gutter={24}>
          <Col xs={24} sm={8}>
            <div style={{ textAlign: 'center', padding: tokens.spacing[4] }}>
              <Title level={2} style={{ marginBottom: 0, color: tokens.colors.error[500] }}>
                ${formatCompactNumber(mockReworkStats.estimatedCost)}
              </Title>
              <Text type="secondary">Estimated Total Cost</Text>
              <div style={{ marginTop: tokens.spacing[2] }}>
                <Text style={{ fontSize: tokens.fontSize.xs, color: tokens.colors.neutral[400] }}>
                  Based on avg. hourly cost of $45
                </Text>
              </div>
            </div>
          </Col>
          <Col xs={24} sm={8}>
            <div style={{ textAlign: 'center', padding: tokens.spacing[4] }}>
              <Title level={2} style={{ marginBottom: 0, color: tokens.colors.warning[500] }}>
                {mockReworkStats.avgLoopsPerCase.toFixed(1)}
              </Title>
              <Text type="secondary">Avg Loops per Rework Case</Text>
            </div>
          </Col>
          <Col xs={24} sm={8}>
            <div style={{ textAlign: 'center', padding: tokens.spacing[4] }}>
              <Title level={2} style={{ marginBottom: 0, color: tokens.colors.primary[500] }}>
                ${Math.round(mockReworkStats.estimatedCost / mockReworkStats.casesWithRework)}
              </Title>
              <Text type="secondary">Avg Cost per Rework Case</Text>
            </div>
          </Col>
        </Row>
      </Card>
    </div>
  );
}

export default ReworkTab;
