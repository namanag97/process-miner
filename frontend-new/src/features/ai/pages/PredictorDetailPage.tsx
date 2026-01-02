import React, { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Card, Row, Col, Typography, Tag, Space, Button, Descriptions, Input, Table, Modal, Skeleton, Statistic, Divider } from 'antd';
import {
  ArrowLeftOutlined,
  ExperimentOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  HistoryOutlined,
  ThunderboltOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import { PageHeader, MetricCard, tokens, toast } from '@lumina/design-system';
import { createLogger } from '../../../utils/logger';

const { Text, Title, Paragraph } = Typography;
const log = createLogger('PredictorDetailPage');

// Mock predictor data
const mockPredictor = {
  id: '1',
  name: 'Order Next Step',
  type: 'next_activity',
  typeLabel: 'Next Activity Prediction',
  logId: '1',
  logName: 'Orders_2024.csv',
  accuracy: 87.5,
  precision: 85.2,
  recall: 89.1,
  f1Score: 87.1,
  status: 'ready',
  createdAt: '2024-12-28T10:30:00Z',
  trainedOn: 5340,
  predictions: 456,
  avgLatency: '45ms',
  modelType: 'LSTM',
  features: ['activity_sequence', 'timestamp', 'resource'],
};

// Mock recent predictions
const mockRecentPredictions = [
  { id: '1', caseId: 'ORD-2024-001', input: 'Submit → Review', prediction: 'Approve', confidence: 92.3, timestamp: '2024-12-30T09:15:00Z' },
  { id: '2', caseId: 'ORD-2024-002', input: 'Submit → Review → Reject', prediction: 'Revise', confidence: 88.7, timestamp: '2024-12-30T09:12:00Z' },
  { id: '3', caseId: 'ORD-2024-003', input: 'Submit', prediction: 'Review', confidence: 95.1, timestamp: '2024-12-30T09:08:00Z' },
  { id: '4', caseId: 'ORD-2024-004', input: 'Submit → Review → Approve', prediction: 'Complete', confidence: 97.8, timestamp: '2024-12-30T09:05:00Z' },
];

// Mock possible activities for prediction
const possibleActivities = ['Submit', 'Review', 'Approve', 'Reject', 'Revise', 'Complete', 'Cancel'];

export function PredictorDetailPage() {
  const navigate = useNavigate();
  const { id, projectId } = useParams<{ id: string; projectId?: string }>();
  const [isLoading, setIsLoading] = useState(false);
  const [testInput, setTestInput] = useState('');
  const [testResult, setTestResult] = useState<{ prediction: string; confidence: number } | null>(null);
  const [isTesting, setIsTesting] = useState(false);

  const handleBack = () => {
    if (projectId) {
      navigate(`/workspace/${projectId}/ai/predictions`);
    } else {
      navigate('/ai/predictions');
    }
  };

  const handleDelete = () => {
    Modal.confirm({
      title: 'Delete Predictor',
      icon: <ExclamationCircleOutlined />,
      content: 'Are you sure you want to delete this predictor? This action cannot be undone.',
      okText: 'Delete',
      okType: 'danger',
      onOk: () => {
        log.info('Deleting predictor', { id });
        toast.success('Predictor deleted');
        if (projectId) {
          navigate(`/workspace/${projectId}/ai/predictions`);
        } else {
          navigate('/ai/predictions');
        }
      },
    });
  };

  const handleTestPrediction = () => {
    if (!testInput.trim()) {
      toast.error('Please enter a case prefix to test');
      return;
    }

    log.info('Testing prediction', { input: testInput });
    setIsTesting(true);
    setTestResult(null);

    setTimeout(() => {
      // Mock prediction result
      const randomActivity = possibleActivities[Math.floor(Math.random() * possibleActivities.length)];
      const confidence = Math.round(70 + Math.random() * 25);
      setTestResult({ prediction: randomActivity, confidence });
      setIsTesting(false);
    }, 800);
  };

  const recentColumns = [
    { title: 'Case ID', dataIndex: 'caseId', key: 'caseId' },
    { title: 'Input Sequence', dataIndex: 'input', key: 'input' },
    {
      title: 'Prediction',
      dataIndex: 'prediction',
      key: 'prediction',
      render: (pred: string) => <Tag color="blue">{pred}</Tag>,
    },
    {
      title: 'Confidence',
      dataIndex: 'confidence',
      key: 'confidence',
      render: (conf: number) => (
        <Text style={{ color: conf >= 90 ? tokens.colors.success[500] : tokens.colors.warning[500] }}>
          {conf}%
        </Text>
      ),
    },
    {
      title: 'Time',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (ts: string) => new Date(ts).toLocaleTimeString(),
    },
  ];

  // Build breadcrumbs based on context
  const getBreadcrumbs = () => {
    if (projectId) {
      return [
        { label: 'Workspace', href: '/workspace' },
        { label: 'Project', href: `/workspace/${projectId}` },
        { label: 'Predictions', href: `/workspace/${projectId}/ai/predictions` },
        { label: mockPredictor.name },
      ];
    }
    return [
      { label: 'AI', href: '/ai' },
      { label: 'Predictions', href: '/ai/predictions' },
      { label: mockPredictor.name },
    ];
  };

  if (isLoading) {
    return (
      <div>
        <PageHeader title="Predictor Details" breadcrumb={getBreadcrumbs()} />
        <Card>
          <Skeleton active paragraph={{ rows: 10 }} />
        </Card>
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title={mockPredictor.name}
        description={mockPredictor.typeLabel}
        breadcrumb={getBreadcrumbs()}
        actions={
          <Space>
            <Button icon={<ArrowLeftOutlined />} onClick={handleBack}>
              Back
            </Button>
            <Button danger icon={<DeleteOutlined />} onClick={handleDelete}>
              Delete
            </Button>
          </Space>
        }
      />

      {/* Summary Stats */}
      <Row gutter={16} style={{ marginBottom: tokens.spacing[6] }}>
        <Col xs={24} sm={6}>
          <MetricCard title="Accuracy" value={`${mockPredictor.accuracy}%`} status="success" />
        </Col>
        <Col xs={24} sm={6}>
          <MetricCard title="Predictions Made" value={mockPredictor.predictions} />
        </Col>
        <Col xs={24} sm={6}>
          <MetricCard title="Avg Latency" value={mockPredictor.avgLatency} />
        </Col>
        <Col xs={24} sm={6}>
          <MetricCard
            title="Status"
            value={mockPredictor.status === 'ready' ? 'Ready' : 'Training'}
            status={mockPredictor.status === 'ready' ? 'success' : 'warning'}
          />
        </Col>
      </Row>

      <Row gutter={16}>
        {/* Predictor Info */}
        <Col xs={24} lg={12}>
          <Card title="Predictor Information" style={{ marginBottom: tokens.spacing[4] }}>
            <Descriptions column={1} size="small">
              <Descriptions.Item label="Model Type">{mockPredictor.modelType}</Descriptions.Item>
              <Descriptions.Item label="Event Log">{mockPredictor.logName}</Descriptions.Item>
              <Descriptions.Item label="Trained On">{mockPredictor.trainedOn.toLocaleString()} cases</Descriptions.Item>
              <Descriptions.Item label="Created">
                {new Date(mockPredictor.createdAt).toLocaleDateString()}
              </Descriptions.Item>
              <Descriptions.Item label="Features">
                {mockPredictor.features.map((f) => (
                  <Tag key={f} style={{ marginRight: 4 }}>
                    {f}
                  </Tag>
                ))}
              </Descriptions.Item>
            </Descriptions>

            <Divider />

            <Title level={5}>Model Metrics</Title>
            <Row gutter={16}>
              <Col span={8}>
                <Statistic title="Precision" value={mockPredictor.precision} suffix="%" />
              </Col>
              <Col span={8}>
                <Statistic title="Recall" value={mockPredictor.recall} suffix="%" />
              </Col>
              <Col span={8}>
                <Statistic title="F1 Score" value={mockPredictor.f1Score} suffix="%" />
              </Col>
            </Row>
          </Card>
        </Col>

        {/* Test Prediction */}
        <Col xs={24} lg={12}>
          <Card
            title={
              <Space>
                <PlayCircleOutlined style={{ color: tokens.colors.primary[500] }} />
                Test Prediction
              </Space>
            }
            style={{ marginBottom: tokens.spacing[4] }}
          >
            <Paragraph type="secondary" style={{ marginBottom: tokens.spacing[4] }}>
              Enter a case prefix (sequence of activities) to test the prediction model.
            </Paragraph>

            <Space.Compact style={{ width: '100%', marginBottom: tokens.spacing[4] }}>
              <Input
                placeholder="e.g., Submit → Review → Approve"
                value={testInput}
                onChange={(e) => setTestInput(e.target.value)}
                onPressEnter={handleTestPrediction}
              />
              <Button type="primary" onClick={handleTestPrediction} loading={isTesting}>
                Predict
              </Button>
            </Space.Compact>

            {testResult && (
              <Card size="small" style={{ backgroundColor: tokens.colors.success[50] }}>
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Space>
                    <ThunderboltOutlined style={{ color: tokens.colors.success[500] }} />
                    <Text strong>Prediction Result</Text>
                  </Space>
                  <Row gutter={16}>
                    <Col span={12}>
                      <Text type="secondary">Next Activity:</Text>
                      <br />
                      <Tag color="success" style={{ fontSize: 16, padding: '4px 12px' }}>
                        {testResult.prediction}
                      </Tag>
                    </Col>
                    <Col span={12}>
                      <Text type="secondary">Confidence:</Text>
                      <br />
                      <Text strong style={{ fontSize: 24, color: tokens.colors.success[500] }}>
                        {testResult.confidence}%
                      </Text>
                    </Col>
                  </Row>
                </Space>
              </Card>
            )}
          </Card>
        </Col>
      </Row>

      {/* Recent Predictions */}
      <Card
        title={
          <Space>
            <HistoryOutlined />
            Recent Predictions
          </Space>
        }
      >
        <Table
          dataSource={mockRecentPredictions}
          columns={recentColumns}
          rowKey="id"
          pagination={{ pageSize: 5 }}
          size="small"
        />
      </Card>
    </div>
  );
}

export default PredictorDetailPage;
