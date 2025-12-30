import React from 'react';
import { Row, Col, Card, Table, Progress, Typography, Space, Tag, Tooltip } from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import { MetricCard, tokens, formatCompactNumber } from '@lumina/design-system';
import { createLogger } from '../../utils/logger';

const { Text } = Typography;
const log = createLogger('ConformanceTab');

// Mock conformance data
const mockConformanceMetrics = {
  fitness: 87.5,
  precision: 92.3,
  generalization: 78.9,
  simplicity: 85.2,
};

const mockDeviations = [
  {
    caseId: 'CASE-1001',
    violationType: 'Missing Activity',
    activity: 'Quality Check',
    expectedAfter: 'Processing',
    frequency: 125,
    impact: 'high',
  },
  {
    caseId: 'CASE-1002',
    violationType: 'Wrong Order',
    activity: 'Payment',
    expectedAfter: 'Approval',
    frequency: 89,
    impact: 'medium',
  },
  {
    caseId: 'CASE-1003',
    violationType: 'Extra Activity',
    activity: 'Manual Review',
    expectedAfter: 'N/A',
    frequency: 67,
    impact: 'low',
  },
  {
    caseId: 'CASE-1004',
    violationType: 'Missing Activity',
    activity: 'Confirmation',
    expectedAfter: 'Delivery',
    frequency: 45,
    impact: 'medium',
  },
  {
    caseId: 'CASE-1005',
    violationType: 'Wrong Order',
    activity: 'Validation',
    expectedAfter: 'Order Received',
    frequency: 34,
    impact: 'high',
  },
];

const impactColors: Record<string, string> = {
  high: tokens.colors.error[500],
  medium: tokens.colors.warning[500],
  low: tokens.colors.success[500],
};

function FitnessGauge({ value, label }: { value: number; label: string }) {
  const getColor = (val: number) => {
    if (val >= 90) return tokens.colors.success[500];
    if (val >= 70) return tokens.colors.warning[500];
    return tokens.colors.error[500];
  };

  return (
    <div style={{ textAlign: 'center', padding: tokens.spacing[4] }}>
      <Progress
        type="circle"
        percent={value}
        strokeColor={getColor(value)}
        strokeWidth={8}
        size={120}
        format={(percent) => (
          <span style={{ fontSize: tokens.fontSize['2xl'], fontWeight: tokens.fontWeight.bold }}>
            {percent}%
          </span>
        )}
      />
      <div style={{ marginTop: tokens.spacing[3] }}>
        <Text strong style={{ fontSize: tokens.fontSize.base }}>{label}</Text>
      </div>
    </div>
  );
}

export function ConformanceTab() {
  log.debug('Rendering ConformanceTab');

  const deviationColumns = [
    {
      title: 'Case ID',
      dataIndex: 'caseId',
      key: 'caseId',
      render: (text: string) => <Text code>{text}</Text>,
    },
    {
      title: 'Violation Type',
      dataIndex: 'violationType',
      key: 'violationType',
      render: (type: string) => {
        const icon = type === 'Missing Activity' ? <CloseCircleOutlined /> :
                     type === 'Wrong Order' ? <ExclamationCircleOutlined /> :
                     <InfoCircleOutlined />;
        return (
          <Space>
            {icon}
            <span>{type}</span>
          </Space>
        );
      },
    },
    {
      title: 'Activity',
      dataIndex: 'activity',
      key: 'activity',
      render: (text: string) => <Text strong>{text}</Text>,
    },
    {
      title: 'Expected After',
      dataIndex: 'expectedAfter',
      key: 'expectedAfter',
      render: (text: string) => <Text type="secondary">{text}</Text>,
    },
    {
      title: 'Frequency',
      dataIndex: 'frequency',
      key: 'frequency',
      render: (val: number) => formatCompactNumber(val),
    },
    {
      title: 'Impact',
      dataIndex: 'impact',
      key: 'impact',
      render: (impact: string) => (
        <Tag color={impact === 'high' ? 'error' : impact === 'medium' ? 'warning' : 'success'}>
          {impact.toUpperCase()}
        </Tag>
      ),
    },
  ];

  const conformantCases = Math.round(5340 * (mockConformanceMetrics.fitness / 100));
  const deviatingCases = 5340 - conformantCases;

  return (
    <div>
      {/* Summary Stats */}
      <Row gutter={16} style={{ marginBottom: tokens.spacing[6] }}>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Overall Fitness"
            value={`${mockConformanceMetrics.fitness}%`}
            status={mockConformanceMetrics.fitness >= 85 ? 'success' : mockConformanceMetrics.fitness >= 70 ? 'warning' : 'error'}
          />
        </Col>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Conformant Cases"
            value={formatCompactNumber(conformantCases)}
            prefix={<CheckCircleOutlined style={{ color: tokens.colors.success[500], marginRight: 8 }} />}
            status="success"
          />
        </Col>
        <Col xs={24} sm={8}>
          <MetricCard
            title="Deviating Cases"
            value={formatCompactNumber(deviatingCases)}
            prefix={<ExclamationCircleOutlined style={{ color: tokens.colors.warning[500], marginRight: 8 }} />}
            status="warning"
          />
        </Col>
      </Row>

      <Row gutter={24}>
        {/* Conformance Metrics Gauges */}
        <Col xs={24} lg={10}>
          <Card
            title={
              <Space>
                <CheckCircleOutlined style={{ color: tokens.colors.success[500] }} />
                <span>Conformance Metrics</span>
                <Tooltip title="Measures how well your process follows the expected model">
                  <InfoCircleOutlined style={{ color: tokens.colors.neutral[400] }} />
                </Tooltip>
              </Space>
            }
            style={{ marginBottom: tokens.spacing[6] }}
          >
            <Row>
              <Col xs={12}>
                <FitnessGauge value={mockConformanceMetrics.fitness} label="Fitness" />
              </Col>
              <Col xs={12}>
                <FitnessGauge value={mockConformanceMetrics.precision} label="Precision" />
              </Col>
            </Row>
            <Row style={{ marginTop: tokens.spacing[4] }}>
              <Col xs={12}>
                <FitnessGauge value={mockConformanceMetrics.generalization} label="Generalization" />
              </Col>
              <Col xs={12}>
                <FitnessGauge value={mockConformanceMetrics.simplicity} label="Simplicity" />
              </Col>
            </Row>
          </Card>
        </Col>

        {/* Deviation Details */}
        <Col xs={24} lg={14}>
          <Card
            title={
              <Space>
                <ExclamationCircleOutlined style={{ color: tokens.colors.warning[500] }} />
                <span>Top Deviations</span>
              </Space>
            }
            style={{ marginBottom: tokens.spacing[6] }}
          >
            <Table
              dataSource={mockDeviations}
              columns={deviationColumns}
              rowKey="caseId"
              pagination={false}
              size="middle"
            />
          </Card>
        </Col>
      </Row>

      {/* Deviation Impact Summary */}
      <Card title="Deviation Impact Summary">
        <Row gutter={24}>
          <Col xs={24} sm={8}>
            <div style={{ textAlign: 'center', padding: tokens.spacing[4] }}>
              <div style={{
                width: 64,
                height: 64,
                borderRadius: '50%',
                backgroundColor: `${tokens.colors.error[500]}20`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto',
                marginBottom: tokens.spacing[3],
              }}>
                <Text style={{ fontSize: tokens.fontSize['2xl'], fontWeight: tokens.fontWeight.bold, color: tokens.colors.error[500] }}>
                  2
                </Text>
              </div>
              <Text strong>High Impact</Text>
              <div><Text type="secondary">Requires immediate attention</Text></div>
            </div>
          </Col>
          <Col xs={24} sm={8}>
            <div style={{ textAlign: 'center', padding: tokens.spacing[4] }}>
              <div style={{
                width: 64,
                height: 64,
                borderRadius: '50%',
                backgroundColor: `${tokens.colors.warning[500]}20`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto',
                marginBottom: tokens.spacing[3],
              }}>
                <Text style={{ fontSize: tokens.fontSize['2xl'], fontWeight: tokens.fontWeight.bold, color: tokens.colors.warning[500] }}>
                  2
                </Text>
              </div>
              <Text strong>Medium Impact</Text>
              <div><Text type="secondary">Should be reviewed</Text></div>
            </div>
          </Col>
          <Col xs={24} sm={8}>
            <div style={{ textAlign: 'center', padding: tokens.spacing[4] }}>
              <div style={{
                width: 64,
                height: 64,
                borderRadius: '50%',
                backgroundColor: `${tokens.colors.success[500]}20`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto',
                marginBottom: tokens.spacing[3],
              }}>
                <Text style={{ fontSize: tokens.fontSize['2xl'], fontWeight: tokens.fontWeight.bold, color: tokens.colors.success[500] }}>
                  1
                </Text>
              </div>
              <Text strong>Low Impact</Text>
              <div><Text type="secondary">Minor deviations</Text></div>
            </div>
          </Col>
        </Row>
      </Card>
    </div>
  );
}

export default ConformanceTab;
