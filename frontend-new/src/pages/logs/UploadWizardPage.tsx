import React, { useState } from 'react';
import {
  Steps,
  Button,
  Upload,
  Card,
  Table,
  Select,
  Progress,
  Result,
  Typography,
  Space,
  Alert,
  Form,
} from 'antd';
import type { UploadProps } from 'antd';
import {
  InboxOutlined,
  FileOutlined,
  CheckCircleOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { PageHeader, tokens, toast } from '@lumina/design-system';
import { createLogger } from '../../utils/logger';

const log = createLogger('UploadWizard');
const { Dragger } = Upload;
const { Text, Title } = Typography;

// Mock detected columns and sample data
const mockPreviewData = {
  columns: ['case_id', 'activity', 'timestamp', 'resource', 'cost'],
  suggestions: {
    caseId: 'case_id',
    activity: 'activity',
    timestamp: 'timestamp',
    resource: 'resource',
  },
  sampleRows: [
    { case_id: 'C001', activity: 'Register Order', timestamp: '2024-01-15 09:00:00', resource: 'John', cost: 150 },
    { case_id: 'C001', activity: 'Check Inventory', timestamp: '2024-01-15 09:30:00', resource: 'Sarah', cost: 50 },
    { case_id: 'C001', activity: 'Ship Order', timestamp: '2024-01-15 14:00:00', resource: 'Mike', cost: 75 },
    { case_id: 'C002', activity: 'Register Order', timestamp: '2024-01-15 10:00:00', resource: 'John', cost: 200 },
    { case_id: 'C002', activity: 'Check Inventory', timestamp: '2024-01-15 10:45:00', resource: 'Sarah', cost: 50 },
  ],
  rowCount: 45000,
  estimatedCaseCount: 1250,
};

const STEPS = [
  { title: 'Select File', description: 'Upload CSV or XES' },
  { title: 'Validate', description: 'Preview data' },
  { title: 'Configure', description: 'Map columns' },
  { title: 'Process', description: 'Complete' },
];

export function UploadWizardPage() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [file, setFile] = useState<File | null>(null);
  const [columnMapping, setColumnMapping] = useState({
    caseId: 'case_id',
    activity: 'activity',
    timestamp: 'timestamp',
    resource: 'resource',
  });
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [uploadComplete, setUploadComplete] = useState(false);

  log.debug('Rendering UploadWizard', { step: currentStep });

  const handleFileUpload: UploadProps['customRequest'] = (options) => {
    const uploadedFile = options.file as File;
    log.info('File selected', { name: uploadedFile.name, size: uploadedFile.size });
    
    // Validate file type
    const validExtensions = ['.csv', '.xes'];
    const ext = uploadedFile.name.toLowerCase().slice(uploadedFile.name.lastIndexOf('.'));
    
    if (!validExtensions.includes(ext)) {
      log.warn('Invalid file type', { extension: ext });
      toast.error('Please upload a CSV or XES file');
      options.onError?.(new Error('Invalid file type'));
      return;
    }
    
    // Validate file size (100MB limit)
    const maxSize = 100 * 1024 * 1024;
    if (uploadedFile.size > maxSize) {
      log.warn('File too large', { size: uploadedFile.size, maxSize });
      toast.error('File size must be less than 100MB');
      options.onError?.(new Error('File too large'));
      return;
    }
    
    setFile(uploadedFile);
    options.onSuccess?.({});
    toast.success('File uploaded successfully');
    
    // Auto-advance to next step
    setTimeout(() => setCurrentStep(1), 500);
  };

  const handleNext = () => {
    log.debug('Moving to next step', { from: currentStep, to: currentStep + 1 });
    
    if (currentStep === 2) {
      // Start processing
      startProcessing();
    } else {
      setCurrentStep((prev) => prev + 1);
    }
  };

  const handleBack = () => {
    log.debug('Moving to previous step', { from: currentStep, to: currentStep - 1 });
    setCurrentStep((prev) => prev - 1);
  };

  const startProcessing = () => {
    log.info('Starting file processing', { fileName: file?.name });
    setCurrentStep(3);
    setProcessing(true);
    setProgress(0);

    // Simulate processing progress
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setProcessing(false);
          setUploadComplete(true);
          log.info('Processing complete');
          toast.success('Event log processed successfully!');
          return 100;
        }
        return prev + 10;
      });
    }, 300);
  };

  const handleViewLog = () => {
    log.info('Navigating to new log');
    navigate('/logs/1'); // Would use actual log ID in real app
  };

  const handleUploadAnother = () => {
    log.info('Resetting wizard');
    setCurrentStep(0);
    setFile(null);
    setProcessing(false);
    setProgress(0);
    setUploadComplete(false);
  };

  // Step 1: File Upload
  const renderFileUpload = () => (
    <Card>
      <Dragger
        name="file"
        multiple={false}
        customRequest={handleFileUpload}
        showUploadList={false}
        accept=".csv,.xes"
      >
        <p className="ant-upload-drag-icon">
          <InboxOutlined style={{ fontSize: 48, color: tokens.colors.primary[500] }} />
        </p>
        <p className="ant-upload-text" style={{ fontSize: 16, fontWeight: 500 }}>
          Drag & drop your file here
        </p>
        <p className="ant-upload-hint">
          or click to browse
        </p>
        <p style={{ marginTop: tokens.spacing[4], color: tokens.colors.neutral[400] }}>
          Supports CSV and XES files up to 100MB
        </p>
      </Dragger>
    </Card>
  );

  // Step 2: Validate & Preview
  const renderValidation = () => (
    <div>
      <Alert
        type="success"
        message={
          <Space>
            <CheckCircleOutlined />
            <Text strong>File validated: {file?.name}</Text>
          </Space>
        }
        description={`${mockPreviewData.rowCount.toLocaleString()} rows detected • ~${mockPreviewData.estimatedCaseCount.toLocaleString()} cases estimated`}
        style={{ marginBottom: tokens.spacing[6] }}
      />

      <Card title="Detected Columns" style={{ marginBottom: tokens.spacing[4] }}>
        <Space wrap>
          {mockPreviewData.columns.map((col) => (
            <Text
              key={col}
              code
              style={{
                padding: '4px 8px',
                background: tokens.colors.neutral[100],
                borderRadius: 4,
              }}
            >
              {col}
            </Text>
          ))}
        </Space>
      </Card>

      <Card title="Sample Data (First 5 rows)">
        <Table
          dataSource={mockPreviewData.sampleRows}
          columns={mockPreviewData.columns.map((col) => ({
            title: col,
            dataIndex: col,
            key: col,
          }))}
          rowKey={(_, index) => String(index)}
          pagination={false}
          size="small"
          scroll={{ x: true }}
        />
      </Card>
    </div>
  );

  // Step 3: Configure Column Mapping
  const renderConfiguration = () => (
    <Card title="Map Your Columns">
      <Text type="secondary" style={{ display: 'block', marginBottom: tokens.spacing[6] }}>
        Select which columns correspond to the required event log fields.
      </Text>

      <Form layout="vertical" style={{ maxWidth: 400 }}>
        <Form.Item label="Case ID" required>
          <Select
            value={columnMapping.caseId}
            onChange={(value) => setColumnMapping((prev) => ({ ...prev, caseId: value }))}
            options={mockPreviewData.columns.map((c) => ({ label: c, value: c }))}
          />
        </Form.Item>

        <Form.Item label="Activity" required>
          <Select
            value={columnMapping.activity}
            onChange={(value) => setColumnMapping((prev) => ({ ...prev, activity: value }))}
            options={mockPreviewData.columns.map((c) => ({ label: c, value: c }))}
          />
        </Form.Item>

        <Form.Item label="Timestamp" required>
          <Select
            value={columnMapping.timestamp}
            onChange={(value) => setColumnMapping((prev) => ({ ...prev, timestamp: value }))}
            options={mockPreviewData.columns.map((c) => ({ label: c, value: c }))}
          />
        </Form.Item>

        <Form.Item label="Resource (optional)">
          <Select
            value={columnMapping.resource}
            onChange={(value) => setColumnMapping((prev) => ({ ...prev, resource: value }))}
            options={[
              { label: '— None —', value: '' },
              ...mockPreviewData.columns.map((c) => ({ label: c, value: c })),
            ]}
            allowClear
          />
        </Form.Item>
      </Form>
    </Card>
  );

  // Step 4: Processing
  const renderProcessing = () => {
    if (uploadComplete) {
      return (
        <Result
          status="success"
          title="Event Log Processed Successfully!"
          subTitle={`${file?.name} has been processed and is ready for analysis.`}
          extra={[
            <Button type="primary" key="view" onClick={handleViewLog}>
              View Event Log
            </Button>,
            <Button key="another" onClick={handleUploadAnother}>
              Upload Another
            </Button>,
          ]}
        />
      );
    }

    return (
      <Card>
        <div style={{ textAlign: 'center', padding: tokens.spacing[8] }}>
          <Title level={4}>Processing your data...</Title>
          <Progress
            percent={progress}
            status="active"
            style={{ maxWidth: 400, margin: '0 auto' }}
          />
          <div style={{ marginTop: tokens.spacing[6] }}>
            {progress < 30 && <Text type="secondary">• Validating rows...</Text>}
            {progress >= 30 && progress < 60 && <Text type="secondary">✓ Validating rows... Creating event log...</Text>}
            {progress >= 60 && progress < 100 && <Text type="secondary">✓ Validating rows... ✓ Creating event log... Generating statistics...</Text>}
          </div>
        </div>
      </Card>
    );
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return renderFileUpload();
      case 1:
        return renderValidation();
      case 2:
        return renderConfiguration();
      case 3:
        return renderProcessing();
      default:
        return null;
    }
  };

  const canProceed = () => {
    switch (currentStep) {
      case 0:
        return !!file;
      case 1:
        return true;
      case 2:
        return !!columnMapping.caseId && !!columnMapping.activity && !!columnMapping.timestamp;
      default:
        return false;
    }
  };

  return (
    <div>
      <PageHeader
        title="Upload Event Log"
        description="Import your process data to start analyzing"
        breadcrumb={[
          { label: 'Event Logs', href: '/logs' },
          { label: 'Upload' },
        ]}
        actions={
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/logs')}
          >
            Cancel
          </Button>
        }
      />

      {/* Steps Indicator */}
      <Steps
        current={currentStep}
        items={STEPS}
        style={{ marginBottom: tokens.spacing[8] }}
      />

      {/* Step Content */}
      <div style={{ marginBottom: tokens.spacing[6] }}>
        {renderStepContent()}
      </div>

      {/* Navigation Buttons */}
      {currentStep < 3 && (
        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
          <Button
            onClick={handleBack}
            disabled={currentStep === 0}
          >
            Back
          </Button>
          <Button
            type="primary"
            onClick={handleNext}
            disabled={!canProceed()}
          >
            {currentStep === 2 ? 'Process' : 'Next'}
          </Button>
        </div>
      )}
    </div>
  );
}

export default UploadWizardPage;
