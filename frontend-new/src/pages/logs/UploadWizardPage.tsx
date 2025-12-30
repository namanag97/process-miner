import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
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
  CheckCircleOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { PageHeader, tokens, toast, useSDK } from '@lumina/design-system';
import { createLogger } from '../../utils/logger';
import type { ColumnDetectionResponse } from '@lumina/design-system';

const log = createLogger('UploadWizard');
const { Dragger } = Upload;
const { Text, Title } = Typography;

const STEPS = [
  { title: 'Select File', description: 'Upload CSV or XES' },
  { title: 'Validate', description: 'Preview data' },
  { title: 'Configure', description: 'Map columns' },
  { title: 'Process', description: 'Complete' },
];

export function UploadWizardPage() {
  const navigate = useNavigate();
  const sdk = useSDK();
  const queryClient = useQueryClient();
  
  const [currentStep, setCurrentStep] = useState(0);
  const [file, setFile] = useState<File | null>(null);
  const [previewData, setPreviewData] = useState<ColumnDetectionResponse | null>(null);
  const [columnMapping, setColumnMapping] = useState({
    caseId: '',
    activity: '',
    timestamp: '',
    resource: '',
  });
  const [uploadedLogId, setUploadedLogId] = useState<string | null>(null);

  // Detect columns mutation
  const detectColumnsMutation = useMutation({
    mutationFn: (file: File) => sdk.processes.detectColumns(file),
    onSuccess: (data) => {
      setPreviewData(data);
      // Apply suggestions
      if (data.suggestions) {
        setColumnMapping({
          caseId: data.suggestions.case_id ?? '',
          activity: data.suggestions.activity ?? '',
          timestamp: data.suggestions.timestamp ?? '',
          resource: data.suggestions.resource ?? '',
        });
      }
      setCurrentStep(1);
    },
    onError: (err) => {
      toast.error(`Failed to detect columns: ${(err as Error).message}`);
    },
  });

  // Ingest mutation
  const ingestMutation = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error('No file selected');
      return sdk.processes.ingest(file, {
        name: file.name,
        caseIdColumn: columnMapping.caseId,
        activityColumn: columnMapping.activity,
        timestampColumn: columnMapping.timestamp,
        resourceColumn: columnMapping.resource || undefined,
      });
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['processes'] });
      setUploadedLogId(data.id);
      toast.success('Event log processed successfully!');
    },
    onError: (err) => {
      toast.error(`Failed to upload: ${(err as Error).message}`);
      setCurrentStep(2); // Go back to configure step
    },
  });

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
    toast.success('File selected successfully');
    
    // Detect columns
    detectColumnsMutation.mutate(uploadedFile);
  };

  const handleNext = () => {
    log.debug('Moving to next step', { from: currentStep, to: currentStep + 1 });
    
    if (currentStep === 2) {
      // Start processing
      setCurrentStep(3);
      ingestMutation.mutate();
    } else {
      setCurrentStep((prev) => prev + 1);
    }
  };

  const handleBack = () => {
    log.debug('Moving to previous step', { from: currentStep, to: currentStep - 1 });
    setCurrentStep((prev) => prev - 1);
  };

  const handleViewLog = () => {
    log.info('Navigating to new log');
    navigate(`/processes/${uploadedLogId}`);
  };

  const handleUploadAnother = () => {
    log.info('Resetting wizard');
    setCurrentStep(0);
    setFile(null);
    setPreviewData(null);
    setColumnMapping({ caseId: '', activity: '', timestamp: '', resource: '' });
    setUploadedLogId(null);
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
        disabled={detectColumnsMutation.isPending}
      >
        <p className="ant-upload-drag-icon">
          <InboxOutlined style={{ fontSize: 48, color: tokens.colors.primary[500] }} />
        </p>
        <p className="ant-upload-text" style={{ fontSize: 16, fontWeight: 500 }}>
          {detectColumnsMutation.isPending ? 'Detecting columns...' : 'Drag & drop your file here'}
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
        description={`${previewData?.row_count?.toLocaleString() ?? 0} rows detected`}
        style={{ marginBottom: tokens.spacing[6] }}
      />

      <Card title="Detected Columns" style={{ marginBottom: tokens.spacing[4] }}>
        <Space wrap>
          {previewData?.columns.map((col) => (
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

      {previewData?.sample_rows && previewData.sample_rows.length > 0 && (
        <Card title="Sample Data (First 5 rows)">
          <Table
            dataSource={previewData.sample_rows.slice(0, 5)}
            columns={(previewData.columns || []).map((col) => ({
              title: col,
              dataIndex: col,
              key: col,
              render: (val) => String(val ?? ''),
            }))}
            rowKey={(_, index) => String(index)}
            pagination={false}
            size="small"
            scroll={{ x: true }}
          />
        </Card>
      )}
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
            options={(previewData?.columns || []).map((c) => ({ label: c, value: c }))}
            placeholder="Select case ID column"
          />
        </Form.Item>

        <Form.Item label="Activity" required>
          <Select
            value={columnMapping.activity}
            onChange={(value) => setColumnMapping((prev) => ({ ...prev, activity: value }))}
            options={(previewData?.columns || []).map((c) => ({ label: c, value: c }))}
            placeholder="Select activity column"
          />
        </Form.Item>

        <Form.Item label="Timestamp" required>
          <Select
            value={columnMapping.timestamp}
            onChange={(value) => setColumnMapping((prev) => ({ ...prev, timestamp: value }))}
            options={(previewData?.columns || []).map((c) => ({ label: c, value: c }))}
            placeholder="Select timestamp column"
          />
        </Form.Item>

        <Form.Item label="Resource (optional)">
          <Select
            value={columnMapping.resource}
            onChange={(value) => setColumnMapping((prev) => ({ ...prev, resource: value }))}
            options={[
              { label: '— None —', value: '' },
              ...(previewData?.columns || []).map((c) => ({ label: c, value: c })),
            ]}
            allowClear
            placeholder="Select resource column"
          />
        </Form.Item>
      </Form>
    </Card>
  );

  // Step 4: Processing
  const renderProcessing = () => {
    if (uploadedLogId) {
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

    if (ingestMutation.isError) {
      return (
        <Result
          status="error"
          title="Upload Failed"
          subTitle={(ingestMutation.error as Error).message}
          extra={[
            <Button type="primary" key="retry" onClick={() => ingestMutation.mutate()}>
              Retry
            </Button>,
            <Button key="back" onClick={() => setCurrentStep(2)}>
              Go Back
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
            percent={ingestMutation.isPending ? 50 : 100}
            status={ingestMutation.isPending ? 'active' : 'success'}
            style={{ maxWidth: 400, margin: '0 auto' }}
          />
          <div style={{ marginTop: tokens.spacing[6] }}>
            <Text type="secondary">Uploading and analyzing your event log...</Text>
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
        return !!file && !detectColumnsMutation.isPending;
      case 1:
        return !!previewData;
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
          { label: 'Event Logs', href: '/processes' },
          { label: 'Upload' },
        ]}
        actions={
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={() => navigate('/processes')}
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
