import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Table, Button, Space, Typography, Tag, Modal, Form, Select, Card, Skeleton } from 'antd';
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
import { PageHeader, EmptyState, tokens } from '@lumina/design-system';
import { createLogger } from '../../../utils/logger';
import { useAIProcesses, useAIPredictors/*, useTrainPredictor, useDeletePredictor*/ } from '../hooks';

const { Text } = Typography;
const log = createLogger('PredictionsPage');

// Predictor types
const predictorTypes = [
  { value: 'next_activity', label: 'Next Activity Prediction' },
  { value: 'remaining_time', label: 'Remaining Time Prediction' },
  { value: 'outcome', label: 'Outcome Prediction' },
];

// Status config
const statusConfig = {
  ready: { color: 'success', icon: <CheckCircleOutlined />, text: 'Ready' },
  training: { color: 'processing', icon: <ClockCircleOutlined />, text: 'Training' },
  failed: { color: 'error', icon: <ExclamationCircleOutlined />, text: 'Failed' },
};

export function PredictionsPage() {
  const navigate = useNavigate();
  const { projectId } = useParams<{ projectId?: string }>();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();

  // Data Fetching
  const { data: processesData } = useAIProcesses({});
  const processes = processesData?.items || [];

  const [selectedLogId, setSelectedLogId] = useState<string>('');

  // Auto-select first log
  useEffect(() => {
    if (!selectedLogId && processes.length > 0) {
      setSelectedLogId(processes[0].id);
    }
  }, [processes, selectedLogId]);

  const { data: predictors = [], isLoading: isPredictorsLoading } = useAIPredictors(selectedLogId);
  // const trainPredictor = useTrainPredictor();
  // const deletePredictor = useDeletePredictor();

  const handleTrainNew = () => {
    log.debug('Opening train predictor modal');
    form.setFieldsValue({ logId: selectedLogId });
    setIsModalOpen(true);
  };

  const handleModalCancel = () => {
    setIsModalOpen(false);
    form.resetFields();
  };

  const handleTrain = async (values: { name: string; logId: string; type: string }) => {
    log.info('Training new predictor', values);

    // trainPredictor.mutate(
    //   {
    //     logId: values.logId,
    //     request: {
    //       targetType: values.type,
    //       // Default algorithm for now, could add to form
    //       algorithm: 'random_forest'
    //     }
    //   },
    //   {
    //     onSuccess: () => {
    //       setIsModalOpen(false);
    //       form.resetFields();
    //       // Ideally we'd switch view to the log we just trained on
    //       if (values.logId !== selectedLogId) {
    //         setSelectedLogId(values.logId);
    //       }
    //     }
    //   }
    // );
    console.warn('Training not implemented yet due to missing hooks');
    setIsModalOpen(false);
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
        // deletePredictor.mutate(id);
        console.warn('Deletion not implemented yet due to missing hooks');
      },
    });
  };

  const handleView = (id: string) => {
    log.debug('Viewing predictor', { id });
    if (projectId) {
      navigate(`/workspace/${projectId}/ai/predictions/${id}`);
    } else {
      navigate(`/ai/predictions/${id}`);
    }
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'id', // PredictorResponse might not have 'name' yet, check schema? Schema has no name.
      key: 'name',
      render: (id: string, record: any) => (
        <Space>
          <ExperimentOutlined style={{ color: tokens.colors.primary[500] }} />
          <Text strong>{record.target_type} Model ({record.algorithm})</Text>
        </Space>
      ),
    },
    {
      title: 'Type',
      dataIndex: 'target_type',
      key: 'type',
      render: (type: string) => (
        <Tag color="blue">{predictorTypes.find((t) => t.value === type)?.label || type}</Tag>
      ),
    },
    {
      title: 'Event Log',
      dataIndex: 'log_id',
      key: 'logName',
      render: (logId: string) => {
        const logName = processes.find(p => p.id === logId)?.name || logId;
        return <Text type="secondary">{logName}</Text>;
      },
    },
    {
      title: 'Accuracy',
      dataIndex: 'metrics',
      key: 'accuracy',
      render: (metrics: any) => {
        const accuracy = metrics?.accuracy ? Math.round(metrics.accuracy * 100) : 0;
        return (
          <Text style={{ color: accuracy >= 85 ? tokens.colors.success[500] : tokens.colors.warning[500] }}>
            {accuracy}%
          </Text>
        );
      },
    },
    {
      title: 'Status',
      key: 'status',
      render: () => {
        // Backend doesn't return status yet in PredictorResponse (it's sync for now or async job separate)
        // Assuming 'ready' if it exists in list
        const config = statusConfig['ready'];
        return (
          <Tag icon={config.icon} color={config.color}>
            {config.text}
          </Tag>
        );
      },
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: unknown, record: any) => (
        <Space>
          <Button
            type="text"
            icon={<EyeOutlined />}
            onClick={() => handleView(record.id)}
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

  if (processes.length === 0 && !processesData) {
    // Loading processes
    return <Skeleton active />;
  }

  // Build breadcrumbs based on context
  const getBreadcrumbs = () => {
    if (projectId) {
      return [
        { label: 'Workspace', href: '/workspace' },
        { label: 'Project', href: `/workspace/${projectId}` },
        { label: 'AI Predictions' },
      ];
    }
    return [
      { label: 'AI', href: '/ai' },
      { label: 'Predictions' },
    ];
  };

  if (processes.length === 0) {
    return (
      <div>
        <PageHeader
          title="Predictions"
          description="Train ML models to predict process outcomes"
          breadcrumb={getBreadcrumbs()}
        />
        <EmptyState
          icon={<ExperimentOutlined />}
          title="No event logs available"
          description="Upload an event log to train prediction models"
          actionLabel="Upload Event Log"
          onAction={() => navigate(projectId ? `/workspace/${projectId}` : '/workspace')}
        />
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title="Predictions"
        description="Train ML models to predict next activities, remaining time, and process outcomes"
        breadcrumb={getBreadcrumbs()}
        actions={
          <Space>
            <Select
              style={{ width: 250 }}
              placeholder="Select Event Log"
              value={selectedLogId}
              onChange={setSelectedLogId}
              options={processes.map(p => ({ label: p.name, value: p.id }))}
            />
            <Button type="primary" icon={<PlusOutlined />} onClick={handleTrainNew}>
              Train New Predictor
            </Button>
          </Space>
        }
      />

      {isPredictorsLoading ? (
        <Card>
          <Skeleton active paragraph={{ rows: 6 }} />
        </Card>
      ) : predictors.length === 0 ? (
        <EmptyState
          icon={<ExperimentOutlined />}
          title="No predictors found"
          description={`No prediction models trained for this log.`}
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
        <Form form={form} layout="vertical" onFinish={handleTrain}>
          <Form.Item
            name="logId"
            label="Event Log"
            rules={[{ required: true, message: 'Please select an event log' }]}
          >
            <Select
              placeholder="Select event log"
              options={processes.map((p) => ({ value: p.id, label: p.name }))}
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
              <Button
                type="primary"
                htmlType="submit"
                icon={<PlayCircleOutlined />}
                loading={false /*trainPredictor.isPending*/}
              >
                Start Training
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}

export default PredictionsPage;
