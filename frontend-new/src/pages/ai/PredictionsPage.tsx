import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Table, Button, Space, Typography, Tag, Modal, Form, Input, Select, Card, Progress, Skeleton } from 'antd';
import {
  PlusOutlined,
  ExperimentOutlined,
  DeleteOutlined,
  EyeOutlined,
  PlayCircleOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import { PageHeader, EmptyState, tokens, toast } from '@lumina/design-system';
import { createLogger } from '../../utils/logger';

const { Text } = Typography;
const log = createLogger('PredictionsPage');

// Mock logs for selector
const mockLogs = [
  { id: '1', name: 'Orders_2024.csv' },
  { id: '2', name: 'Claims_Process.xes' },
  { id: '3', name: 'Purchase_Orders.csv' },
];

// Predictor types
const predictorTypes = [
  { value: 'next_activity', label: 'Next Activity Prediction' },
  { value: 'remaining_time', label: 'Remaining Time Prediction' },
  { value: 'outcome', label: 'Outcome Prediction' },
];

// Mock predictors data
const mockPredictors = [
  {
    id: '1',
    name: 'Order Next Step',
    type: 'next_activity',
    logId: '1',
    logName: 'Orders_2024.csv',
    accuracy: 87.5,
    status: 'ready',
    createdAt: '2024-12-28T10:30:00Z',
    predictions: 456,
  },
  {
    id: '2',
    name: 'Claims Duration',
    type: 'remaining_time',
    logId: '2',
    logName: 'Claims_Process.xes',
    accuracy: 82.3,
    status: 'ready',
    createdAt: '2024-12-27T14:20:00Z',
    predictions: 234,
  },
  {
    id: '3',
    name: 'PO Outcome',
    type: 'outcome',
    logId: '3',
    logName: 'Purchase_Orders.csv',
    accuracy: 91.2,
    status: 'training',
    createdAt: '2024-12-30T08:00:00Z',
    predictions: 0,
  },
];

// Status config
const statusConfig = {
  ready: { color: 'success', icon: <CheckCircleOutlined />, text: 'Ready' },
  training: { color: 'processing', icon: <ClockCircleOutlined />, text: 'Training' },
  failed: { color: 'error', icon: <ExclamationCircleOutlined />, text: 'Failed' },
};

export function PredictionsPage() {
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isTraining, setIsTraining] = useState(false);
  const [trainingProgress, setTrainingProgress] = useState(0);
  const [form] = Form.useForm();
  const [predictors, setPredictors] = useState(mockPredictors);
  const [isLoading, setIsLoading] = useState(false);

  const handleTrainNew = () => {
    log.debug('Opening train predictor modal');
    setIsModalOpen(true);
  };

  const handleModalCancel = () => {
    setIsModalOpen(false);
    setIsTraining(false);
    setTrainingProgress(0);
    form.resetFields();
  };

  const handleTrain = async (values: { name: string; logId: string; type: string }) => {
    log.info('Training new predictor', values);
    setIsTraining(true);
    setTrainingProgress(0);

    // Simulate training progress
    const interval = setInterval(() => {
      setTrainingProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 10;
      });
    }, 300);

    setTimeout(() => {
      clearInterval(interval);
      setIsTraining(false);
      setIsModalOpen(false);
      form.resetFields();
      setTrainingProgress(0);

      // Add new predictor to list
      const newPredictor = {
        id: String(Date.now()),
        name: values.name,
        type: values.type,
        logId: values.logId,
        logName: mockLogs.find((l) => l.id === values.logId)?.name || 'Unknown',
        accuracy: Math.round(75 + Math.random() * 20),
        status: 'ready' as const,
        createdAt: new Date().toISOString(),
        predictions: 0,
      };
      setPredictors([newPredictor, ...predictors]);
      toast.success('Predictor trained successfully!');
    }, 3500);
  };

  const handleDelete = (id: string) => {
    Modal.confirm({
      title: 'Delete Predictor',
      icon: <ExclamationCircleOutlined />,
      content: 'Are you sure you want to delete this predictor? This action cannot be undone.',
      okText: 'Delete',
      okType: 'danger',
      onOk: () => {
        log.info('Deleting predictor', { id });
        setPredictors(predictors.filter((p) => p.id !== id));
        toast.success('Predictor deleted');
      },
    });
  };

  const handleView = (id: string) => {
    log.debug('Viewing predictor', { id });
    navigate(`/ai/predictions/${id}`);
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: typeof mockPredictors[0]) => (
        <Space>
          <ExperimentOutlined style={{ color: tokens.colors.primary[500] }} />
          <Text strong>{name}</Text>
        </Space>
      ),
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      render: (type: string) => (
        <Tag color="blue">{predictorTypes.find((t) => t.value === type)?.label || type}</Tag>
      ),
    },
    {
      title: 'Event Log',
      dataIndex: 'logName',
      key: 'logName',
      render: (name: string) => <Text type="secondary">{name}</Text>,
    },
    {
      title: 'Accuracy',
      dataIndex: 'accuracy',
      key: 'accuracy',
      render: (accuracy: number, record: typeof mockPredictors[0]) =>
        record.status === 'training' ? (
          <Text type="secondary">Training...</Text>
        ) : (
          <Text style={{ color: accuracy >= 85 ? tokens.colors.success[500] : tokens.colors.warning[500] }}>
            {accuracy}%
          </Text>
        ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: keyof typeof statusConfig) => {
        const config = statusConfig[status];
        return (
          <Tag icon={config.icon} color={config.color}>
            {config.text}
          </Tag>
        );
      },
    },
    {
      title: 'Predictions',
      dataIndex: 'predictions',
      key: 'predictions',
      render: (count: number) => count.toLocaleString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: unknown, record: typeof mockPredictors[0]) => (
        <Space>
          <Button
            type="text"
            icon={<EyeOutlined />}
            onClick={() => handleView(record.id)}
            disabled={record.status !== 'ready'}
          >
            View
          </Button>
          <Button
            type="text"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          />
        </Space>
      ),
    },
  ];

  if (mockLogs.length === 0) {
    return (
      <div>
        <PageHeader
          title="Predictions"
          description="Train ML models to predict process outcomes"
        />
        <EmptyState
          icon={<ExperimentOutlined />}
          title="No event logs available"
          description="Upload an event log to train prediction models"
          actionLabel="Upload Event Log"
          onAction={() => navigate('/logs/upload')}
        />
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title="Predictions"
        description="Train ML models to predict next activities, remaining time, and process outcomes"
        actions={
          <Button type="primary" icon={<PlusOutlined />} onClick={handleTrainNew}>
            Train New Predictor
          </Button>
        }
      />

      {isLoading ? (
        <Card>
          <Skeleton active paragraph={{ rows: 6 }} />
        </Card>
      ) : predictors.length === 0 ? (
        <EmptyState
          icon={<ExperimentOutlined />}
          title="No predictors trained"
          description="Train your first prediction model to start making predictions"
          actionLabel="Train New Predictor"
          onAction={handleTrainNew}
        />
      ) : (
        <Card>
          <Table
            dataSource={predictors}
            columns={columns}
            rowKey="id"
            pagination={{ pageSize: 10 }}
          />
        </Card>
      )}

      {/* Train Predictor Modal */}
      <Modal
        title="Train New Predictor"
        open={isModalOpen}
        onCancel={handleModalCancel}
        footer={null}
        width={480}
      >
        {isTraining ? (
          <div style={{ textAlign: 'center', padding: tokens.spacing[6] }}>
            <ExperimentOutlined style={{ fontSize: 48, color: tokens.colors.primary[500], marginBottom: tokens.spacing[4] }} />
            <Text style={{ display: 'block', marginBottom: tokens.spacing[4] }}>Training predictor...</Text>
            <Progress percent={trainingProgress} status="active" />
            <Text type="secondary" style={{ display: 'block', marginTop: tokens.spacing[2] }}>
              This may take a few moments
            </Text>
          </div>
        ) : (
          <Form form={form} layout="vertical" onFinish={handleTrain}>
            <Form.Item
              name="name"
              label="Predictor Name"
              rules={[{ required: true, message: 'Please enter a name' }]}
            >
              <Input placeholder="e.g., Order Next Step Predictor" />
            </Form.Item>

            <Form.Item
              name="logId"
              label="Event Log"
              rules={[{ required: true, message: 'Please select an event log' }]}
            >
              <Select
                placeholder="Select event log"
                options={mockLogs.map((log) => ({ value: log.id, label: log.name }))}
              />
            </Form.Item>

            <Form.Item
              name="type"
              label="Prediction Type"
              rules={[{ required: true, message: 'Please select a type' }]}
            >
              <Select placeholder="Select prediction type" options={predictorTypes} />
            </Form.Item>

            <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
              <Space>
                <Button onClick={handleModalCancel}>Cancel</Button>
                <Button type="primary" htmlType="submit" icon={<PlayCircleOutlined />}>
                  Start Training
                </Button>
              </Space>
            </Form.Item>
          </Form>
        )}
      </Modal>
    </div>
  );
}

export default PredictionsPage;
