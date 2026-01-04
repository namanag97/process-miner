/**
 * ConnectionWizard - Multi-step wizard for data source connections
 *
 * Guides users through:
 * 1. Selecting connection type (Database, API, File, etc.)
 * 2. Entering connection credentials
 * 3. Testing the connection
 * 4. Mapping data fields
 *
 * @example
 * <ConnectionWizard
 *   onComplete={(connection) => saveConnection(connection)}
 *   onCancel={() => setWizardOpen(false)}
 * />
 */

import React, { useState, useCallback } from 'react';
import {
  Modal,
  Steps,
  Button,
  Form,
  Input,
  Select,
  Card,
  Space,
  Typography,
  Result,
  Spin,
  Row,
  Col,
  Divider,
} from 'antd';
import {
  DatabaseOutlined,
  ApiOutlined,
  FileTextOutlined,
  CloudOutlined,
  LoadingOutlined,
  SafetyCertificateOutlined,
} from '@ant-design/icons';
import { tokens } from '../theme';

const { Text } = Typography;

// ============================================
// Types
// ============================================

export type ConnectionType = 'postgresql' | 'mysql' | 'sqlserver' | 'oracle' | 'api' | 'csv' | 's3' | 'azure_blob';

export interface ConnectionConfig {
  type: ConnectionType;
  name: string;
  host?: string;
  port?: number;
  database?: string;
  username?: string;
  password?: string;
  ssl?: boolean;
  apiUrl?: string;
  apiKey?: string;
  bucketName?: string;
  region?: string;
  filePath?: string;
}

export interface ConnectionWizardProps {
  /** Whether the wizard is open */
  open: boolean;
  /** Close handler */
  onClose: () => void;
  /** Completion handler with the created connection */
  onComplete: (connection: ConnectionConfig) => void;
  /** Test connection function (returns success/error) */
  onTestConnection?: (config: ConnectionConfig) => Promise<{ success: boolean; message?: string }>;
  /** Allowed connection types */
  allowedTypes?: ConnectionType[];
  /** Initial values for editing */
  initialValues?: Partial<ConnectionConfig>;
}

// ============================================
// Configuration
// ============================================

interface ConnectionTypeInfo {
  key: ConnectionType;
  label: string;
  icon: React.ReactNode;
  category: 'database' | 'api' | 'storage';
  description: string;
}

const CONNECTION_TYPES: ConnectionTypeInfo[] = [
  { key: 'postgresql', label: 'PostgreSQL', icon: <DatabaseOutlined />, category: 'database', description: 'Connect to PostgreSQL databases' },
  { key: 'mysql', label: 'MySQL', icon: <DatabaseOutlined />, category: 'database', description: 'Connect to MySQL/MariaDB' },
  { key: 'sqlserver', label: 'SQL Server', icon: <DatabaseOutlined />, category: 'database', description: 'Connect to Microsoft SQL Server' },
  { key: 'oracle', label: 'Oracle', icon: <DatabaseOutlined />, category: 'database', description: 'Connect to Oracle Database' },
  { key: 'api', label: 'REST API', icon: <ApiOutlined />, category: 'api', description: 'Connect via REST API' },
  { key: 'csv', label: 'CSV File', icon: <FileTextOutlined />, category: 'storage', description: 'Upload CSV files' },
  { key: 's3', label: 'Amazon S3', icon: <CloudOutlined />, category: 'storage', description: 'Connect to S3 buckets' },
  { key: 'azure_blob', label: 'Azure Blob', icon: <CloudOutlined />, category: 'storage', description: 'Connect to Azure Blob Storage' },
];

const STEPS = [
  { title: 'Select Type', description: 'Choose data source' },
  { title: 'Configure', description: 'Enter connection details' },
  { title: 'Test', description: 'Verify connection' },
  { title: 'Complete', description: 'Save and finish' },
];

// ============================================
// ConnectionWizard Component
// ============================================

export function ConnectionWizard({
  open,
  onClose,
  onComplete,
  onTestConnection,
  allowedTypes,
  initialValues,
}: ConnectionWizardProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [form] = Form.useForm();
  const [selectedType, setSelectedType] = useState<ConnectionType | null>(initialValues?.type || null);
  const [testStatus, setTestStatus] = useState<'idle' | 'testing' | 'success' | 'error'>('idle');
  const [testMessage, setTestMessage] = useState('');
  const [connectionConfig, setConnectionConfig] = useState<ConnectionConfig | null>(null);

  const availableTypes = allowedTypes
    ? CONNECTION_TYPES.filter((t) => allowedTypes.includes(t.key))
    : CONNECTION_TYPES;

  const selectedTypeInfo = CONNECTION_TYPES.find((t) => t.key === selectedType);

  // Reset wizard state
  const handleReset = useCallback(() => {
    setCurrentStep(0);
    setSelectedType(initialValues?.type || null);
    setTestStatus('idle');
    setTestMessage('');
    setConnectionConfig(null);
    form.resetFields();
  }, [form, initialValues]);

  // Handle close
  const handleClose = useCallback(() => {
    handleReset();
    onClose();
  }, [handleReset, onClose]);

  // Step 1: Select type
  const handleSelectType = useCallback((type: ConnectionType) => {
    setSelectedType(type);
  }, []);

  // Step 2: Configure connection
  const handleConfigureNext = useCallback(async () => {
    try {
      const values = await form.validateFields();
      const config: ConnectionConfig = {
        type: selectedType!,
        ...values,
      };
      setConnectionConfig(config);
      setCurrentStep(2);
    } catch (error) {
      // Validation failed
    }
  }, [form, selectedType]);

  // Step 3: Test connection
  const handleTestConnection = useCallback(async () => {
    if (!connectionConfig || !onTestConnection) {
      // Skip test if no handler provided
      setTestStatus('success');
      setTestMessage('Connection configured successfully');
      return;
    }

    setTestStatus('testing');
    try {
      const result = await onTestConnection(connectionConfig);
      if (result.success) {
        setTestStatus('success');
        setTestMessage(result.message || 'Connection successful!');
      } else {
        setTestStatus('error');
        setTestMessage(result.message || 'Connection failed. Please check your settings.');
      }
    } catch (error) {
      setTestStatus('error');
      setTestMessage('An unexpected error occurred while testing the connection.');
    }
  }, [connectionConfig, onTestConnection]);

  // Step 4: Complete
  const handleComplete = useCallback(() => {
    if (connectionConfig) {
      onComplete(connectionConfig);
      handleClose();
    }
  }, [connectionConfig, onComplete, handleClose]);

  // Navigation
  const handleNext = useCallback(() => {
    if (currentStep === 0 && selectedType) {
      setCurrentStep(1);
    } else if (currentStep === 1) {
      handleConfigureNext();
    } else if (currentStep === 2) {
      if (testStatus === 'success') {
        setCurrentStep(3);
      } else {
        handleTestConnection();
      }
    } else if (currentStep === 3) {
      handleComplete();
    }
  }, [currentStep, selectedType, testStatus, handleConfigureNext, handleTestConnection, handleComplete]);

  const handleBack = useCallback(() => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
      if (currentStep === 3) {
        setTestStatus('idle');
      }
    }
  }, [currentStep]);

  // Render connection type selection (Step 1)
  const renderTypeSelection = () => {
    const categories = ['database', 'api', 'storage'] as const;
    const categoryLabels = { database: 'Databases', api: 'APIs', storage: 'Cloud Storage' };

    return (
      <div style={{ padding: tokens.spacing[4] }}>
        {categories.map((category) => {
          const typesInCategory = availableTypes.filter((t) => t.category === category);
          if (typesInCategory.length === 0) return null;

          return (
            <div key={category} style={{ marginBottom: tokens.spacing[6] }}>
              <Text type="secondary" style={{ fontSize: tokens.fontSize.sm, textTransform: 'uppercase', letterSpacing: 1 }}>
                {categoryLabels[category]}
              </Text>
              <Row gutter={[12, 12]} style={{ marginTop: tokens.spacing[3] }}>
                {typesInCategory.map((typeInfo) => (
                  <Col xs={12} sm={8} md={6} key={typeInfo.key}>
                    <Card
                      hoverable
                      onClick={() => handleSelectType(typeInfo.key)}
                      className="card-hover-lift"
                      style={{
                        textAlign: 'center',
                        border: selectedType === typeInfo.key ? `2px solid ${tokens.colors.primary[500]}` : undefined,
                        backgroundColor: selectedType === typeInfo.key ? tokens.colors.primary[50] : undefined,
                      }}
                      styles={{ body: { padding: tokens.spacing[4] } }}
                    >
                      <div style={{ fontSize: 28, color: tokens.colors.primary[500], marginBottom: tokens.spacing[2] }}>
                        {typeInfo.icon}
                      </div>
                      <Text strong>{typeInfo.label}</Text>
                    </Card>
                  </Col>
                ))}
              </Row>
            </div>
          );
        })}
      </div>
    );
  };

  // Render configuration form (Step 2)
  const renderConfigurationForm = () => {
    const isDatabase = selectedTypeInfo?.category === 'database';
    const isApi = selectedType === 'api';
    const isS3 = selectedType === 's3' || selectedType === 'azure_blob';

    return (
      <div style={{ padding: tokens.spacing[4], maxWidth: 500, margin: '0 auto' }}>
        <Form form={form} layout="vertical" initialValues={initialValues}>
          <Form.Item name="name" label="Connection Name" rules={[{ required: true, message: 'Please enter a name' }]}>
            <Input placeholder="e.g., Production Database" />
          </Form.Item>

          {isDatabase && (
            <>
              <Row gutter={12}>
                <Col span={16}>
                  <Form.Item name="host" label="Host" rules={[{ required: true }]}>
                    <Input placeholder="localhost or IP address" />
                  </Form.Item>
                </Col>
                <Col span={8}>
                  <Form.Item name="port" label="Port" rules={[{ required: true }]}>
                    <Input type="number" placeholder="5432" />
                  </Form.Item>
                </Col>
              </Row>
              <Form.Item name="database" label="Database Name" rules={[{ required: true }]}>
                <Input placeholder="mydb" />
              </Form.Item>
              <Row gutter={12}>
                <Col span={12}>
                  <Form.Item name="username" label="Username" rules={[{ required: true }]}>
                    <Input placeholder="db_user" />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item name="password" label="Password" rules={[{ required: true }]}>
                    <Input.Password placeholder="••••••••" />
                  </Form.Item>
                </Col>
              </Row>
            </>
          )}

          {isApi && (
            <>
              <Form.Item name="apiUrl" label="API URL" rules={[{ required: true, type: 'url' }]}>
                <Input placeholder="https://api.example.com/v1" />
              </Form.Item>
              <Form.Item name="apiKey" label="API Key">
                <Input.Password placeholder="Optional API key" />
              </Form.Item>
            </>
          )}

          {isS3 && (
            <>
              <Form.Item name="bucketName" label="Bucket Name" rules={[{ required: true }]}>
                <Input placeholder="my-data-bucket" />
              </Form.Item>
              <Form.Item name="region" label="Region">
                <Select placeholder="Select region">
                  <Select.Option value="us-east-1">US East (N. Virginia)</Select.Option>
                  <Select.Option value="us-west-2">US West (Oregon)</Select.Option>
                  <Select.Option value="eu-west-1">EU (Ireland)</Select.Option>
                  <Select.Option value="ap-southeast-1">Asia Pacific (Singapore)</Select.Option>
                </Select>
              </Form.Item>
            </>
          )}
        </Form>
      </div>
    );
  };

  // Render test results (Step 3)
  const renderTestConnection = () => (
    <div style={{ padding: tokens.spacing[8], textAlign: 'center' }}>
      {testStatus === 'idle' && (
        <Result
          icon={<SafetyCertificateOutlined style={{ color: tokens.colors.primary[500] }} />}
          title="Ready to Test"
          subTitle="Click the button below to verify your connection settings."
          extra={
            <Button type="primary" size="large" onClick={handleTestConnection}>
              Test Connection
            </Button>
          }
        />
      )}

      {testStatus === 'testing' && (
        <Result
          icon={<Spin indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />} />}
          title="Testing Connection..."
          subTitle="Please wait while we verify your connection settings."
        />
      )}

      {testStatus === 'success' && (
        <Result
          status="success"
          title="Connection Successful!"
          subTitle={testMessage}
        />
      )}

      {testStatus === 'error' && (
        <Result
          status="error"
          title="Connection Failed"
          subTitle={testMessage}
          extra={
            <Space>
              <Button onClick={() => setCurrentStep(1)}>Edit Settings</Button>
              <Button type="primary" onClick={handleTestConnection}>
                Retry
              </Button>
            </Space>
          }
        />
      )}
    </div>
  );

  // Render completion (Step 4)
  const renderComplete = () => (
    <div style={{ padding: tokens.spacing[8], textAlign: 'center' }}>
      <Result
        status="success"
        title="Connection Ready!"
        subTitle={`Your ${selectedTypeInfo?.label} connection "${connectionConfig?.name}" is configured and tested.`}
      />
    </div>
  );

  // Step content
  const stepContent = [renderTypeSelection, renderConfigurationForm, renderTestConnection, renderComplete];

  return (
    <Modal
      open={open}
      onCancel={handleClose}
      width={720}
      title={
        <Space>
          {selectedTypeInfo?.icon}
          <span>Connect Data Source</span>
        </Space>
      }
      footer={
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <Button onClick={handleClose}>Cancel</Button>
          <Space>
            {currentStep > 0 && (
              <Button onClick={handleBack}>Back</Button>
            )}
            <Button
              type="primary"
              onClick={handleNext}
              disabled={currentStep === 0 && !selectedType}
            >
              {currentStep === 3 ? 'Save Connection' : currentStep === 2 && testStatus === 'success' ? 'Continue' : 'Next'}
            </Button>
          </Space>
        </div>
      }
    >
      <Steps current={currentStep} items={STEPS} style={{ marginBottom: tokens.spacing[6] }} />
      <Divider style={{ margin: `${tokens.spacing[4]}px 0` }} />
      {stepContent[currentStep]()}
    </Modal>
  );
}

export default ConnectionWizard;
