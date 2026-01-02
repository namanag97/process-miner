import React, { useState, useEffect, useCallback } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Steps,
  Button,
  Upload,
  Card,
  Table,
  Select,
  Spin,
  Result,
  Typography,
  Space,
  Alert,
  Form,
  Modal,
  Progress,
  Tag,
} from 'antd';
import type { UploadProps } from 'antd';
import {
  InboxOutlined,
  CheckCircleOutlined,
  ArrowLeftOutlined,
  WarningOutlined,
  CloseCircleOutlined,
  FileOutlined,
  ClockCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { PageHeader, tokens, toast, useSDK } from '@lumina/design-system';
import { createLogger } from '../../utils/logger';
import { useBeforeUnload } from '../../utils/useBeforeUnload';
import type { ColumnDetection } from '@lumina/design-system';

const log = createLogger('UploadWizard');
const { Dragger } = Upload;
const { Text, Title } = Typography;

const STEPS = [
  { title: 'Select File', description: 'Upload CSV or XES' },
  { title: 'Validate', description: 'Preview data' },
  { title: 'Configure', description: 'Map columns' },
  { title: 'Process', description: 'Complete' },
];

type ProcessingStage = 'idle' | 'uploading' | 'parsing' | 'analyzing' | 'complete' | 'error';

// Helper to format file size
function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// Helper to get unique values from sample data
function getUniqueValuesFromSample(sampleRows: Record<string, unknown>[], column: string): number {
  const values = new Set(sampleRows.map(row => row[column]));
  return values.size;
}

export function UploadWizardPage() {
  const navigate = useNavigate();
  const { projectId } = useParams<{ projectId: string }>();
  const sdk = useSDK();
  const queryClient = useQueryClient();
  
  const [currentStep, setCurrentStep] = useState(0);
  const [file, setFile] = useState<File | null>(null);
  const [previewData, setPreviewData] = useState<ColumnDetection | null>(null);
  const [columnMapping, setColumnMapping] = useState({
    caseId: '',
    activity: '',
    timestamp: '',
    resource: '',
  });
  const [uploadedLogId, setUploadedLogId] = useState<string | null>(null);
  
  // New state for improved UX
  const [processingStage, setProcessingStage] = useState<ProcessingStage>('idle');
  const [showCancelConfirm, setShowCancelConfirm] = useState(false);
  const [detectionStartTime, setDetectionStartTime] = useState<number | null>(null);
  const [showDetectionTimeout, setShowDetectionTimeout] = useState(false);
  const [processingStartTime, setProcessingStartTime] = useState<number | null>(null);
  const [showProcessingTimeout, setShowProcessingTimeout] = useState(false);
  const [uploadPercent, setUploadPercent] = useState(0);

  // Determine if wizard has unsaved state
  const hasUnsavedState = currentStep > 0 && !uploadedLogId;

  // Browser navigation blocking
  useBeforeUnload(hasUnsavedState, 'Your upload progress will be lost. Are you sure you want to leave?');

  // Note: useBlocker requires data router, so we only use browser beforeunload
  // plus manual confirmation modal for Cancel button clicks

  // Detection timeout tracker
  useEffect(() => {
    if (!detectionStartTime) {
      setShowDetectionTimeout(false);
      return;
    }

    const timer = setTimeout(() => {
      setShowDetectionTimeout(true);
    }, 30000); // 30 seconds

    return () => clearTimeout(timer);
  }, [detectionStartTime]);

  // Processing timeout tracker
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  useEffect(() => {
    if (!processingStartTime) {
      setShowProcessingTimeout(false);
      setElapsedSeconds(0);
      return;
    }

    // Update elapsed time every second
    const interval = setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - processingStartTime) / 1000));
    }, 1000);

    const timer = setTimeout(() => {
      setShowProcessingTimeout(true);
    }, 15000); // 15 seconds

    return () => {
      clearInterval(interval);
      clearTimeout(timer);
    };
  }, [processingStartTime]);

  // Detect columns mutation
  const detectColumnsMutation = useMutation({
    mutationFn: (file: File) => sdk.processes.detectColumns(file),
    onMutate: () => {
      setDetectionStartTime(Date.now());
      setShowDetectionTimeout(false);
    },
    onSuccess: (data) => {
      setDetectionStartTime(null);
      setPreviewData(data);
      // Apply suggestions
      if (data.suggestions) {
        setColumnMapping({
          caseId: data.suggestions.caseId ?? '',
          activity: data.suggestions.activity ?? '',
          timestamp: data.suggestions.timestamp ?? '',
          resource: data.suggestions.resource ?? '',
        });
      }
      setCurrentStep(1);
    },
    onError: (err) => {
      setDetectionStartTime(null);
      toast.error(`Failed to detect columns: ${(err as Error).message}`);
    },
  });

  // Ingest mutation with real upload progress
  const ingestMutation = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error('No file selected');

      // Reset and start uploading
      setUploadPercent(0);
      setProcessingStage('uploading');

      const result = await sdk.processes.ingestWithProgress(
        file,
        {
          name: file.name,
          projectId: projectId,
          caseIdColumn: columnMapping.caseId,
          activityColumn: columnMapping.activity,
          timestampColumn: columnMapping.timestamp,
          resourceColumn: columnMapping.resource || undefined,
        },
        (percent) => {
          setUploadPercent(percent);
          // Transition to parsing stage when upload is ~100%
          if (percent >= 100) {
            setProcessingStage('parsing');
          }
        }
      );

      // Associate with project if we came from a project context
      if (projectId) {
        setProcessingStage('analyzing');
        await sdk.projects.addFile(projectId, result.id);
      }

      // Stage 3: Complete
      setProcessingStage('complete');
      return result;
    },
    onMutate: () => {
      setProcessingStartTime(Date.now());
      setShowProcessingTimeout(false);
    },
    onSuccess: (data) => {
      setProcessingStartTime(null);
      queryClient.invalidateQueries({ queryKey: ['processes'] });
      queryClient.invalidateQueries({ queryKey: ['projects'] });
      // Explicitly invalidate the specific project detail to ensure immediate refresh
      if (projectId) {
        queryClient.invalidateQueries({ queryKey: ['projects', projectId] });
      }
      setUploadedLogId(data.id);
      toast.success('Event log processed successfully!');
    },
    onError: (err) => {
      setProcessingStartTime(null);
      setProcessingStage('error');
      toast.error(`Failed to upload: ${(err as Error).message}`);
    },
  });

  log.debug('Rendering UploadWizard', { step: currentStep, processingStage });

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
    
    // Detect columns
    detectColumnsMutation.mutate(uploadedFile);
  };

  const handleCancelDetection = useCallback(() => {
    detectColumnsMutation.reset();
    setDetectionStartTime(null);
    setShowDetectionTimeout(false);
    setFile(null);
    toast.info('Column detection cancelled');
  }, [detectColumnsMutation]);

  const handleNext = () => {
    log.debug('Moving to next step', { from: currentStep, to: currentStep + 1 });
    
    if (currentStep === 2) {
      // Start processing
      setCurrentStep(3);
      setProcessingStage('uploading');
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
    if (projectId) {
      navigate(`/workspace/${projectId}/data/${uploadedLogId}/questions`);
    } else {
      navigate(`/processes/${uploadedLogId}`);
    }
  };

  const handleExploreProcess = () => {
    log.info('Navigating to explorer for new log');
    if (projectId) {
      navigate(`/workspace/${projectId}/data/${uploadedLogId}/explorer`);
    } else {
      navigate(`/explorer/${uploadedLogId}`);
    }
  };

  const handleUploadAnother = () => {
    log.info('Resetting wizard');
    setCurrentStep(0);
    setFile(null);
    setPreviewData(null);
    setColumnMapping({ caseId: '', activity: '', timestamp: '', resource: '' });
    setUploadedLogId(null);
    setProcessingStage('idle');
    setShowProcessingTimeout(false);
    setShowDetectionTimeout(false);
    setUploadPercent(0);
  };

  const handleDone = () => {
    if (projectId) {
      navigate(`/workspace/${projectId}`);
    } else {
      navigate('/processes');
    }
  };

  const getBackPath = () => projectId ? `/workspace/${projectId}` : '/processes';

  const handleCancelClick = () => {
    if (hasUnsavedState) {
      setShowCancelConfirm(true);
    } else {
      navigate(getBackPath());
    }
  };

  const handleConfirmCancel = () => {
    setShowCancelConfirm(false);
    navigate(getBackPath());
  };

  const handleCancelStay = () => {
    setShowCancelConfirm(false);
  };

  // Step 1: File Upload
  const renderFileUpload = () => (
    <div className="animate-fade-in">
      <Card 
        className="glass-effect surface-noise"
        style={{ borderRadius: 16, border: 'none' }}
      >
        <div style={{ padding: tokens.spacing[4] }}>
          <Dragger
            name="file"
            multiple={false}
            customRequest={handleFileUpload}
            showUploadList={false}
            accept=".csv,.xes"
            disabled={detectColumnsMutation.isPending}
            style={{ 
              background: 'rgba(255,255,255,0.5)', 
              borderColor: tokens.colors.primary[200],
              borderRadius: 12,
              padding: tokens.spacing[4]
            }}
            className="card-hover-lift"
          >
            <p className="ant-upload-drag-icon">
              <InboxOutlined style={{ fontSize: 64, color: tokens.colors.primary[500], opacity: 0.8 }} />
            </p>
            <p className="ant-upload-text" style={{ fontSize: 20, fontWeight: 600, color: tokens.colors.neutral[800] }}>
              {detectColumnsMutation.isPending ? 'Analyzing File...' : 'Upload Event Log'}
            </p>
            <p className="ant-upload-hint" style={{ fontSize: 16, color: tokens.colors.neutral[500] }}>
              Drag & drop CSV or XES file
            </p>
            <Button 
              type="primary" 
              ghost 
              style={{ marginTop: tokens.spacing[6], borderRadius: 20 }}
            >
              Browse Files
            </Button>
            <p style={{ marginTop: tokens.spacing[4], color: tokens.colors.neutral[400], fontSize: 12 }}>
              Max size: 100MB • Secure processing
            </p>
          </Dragger>
        </div>

        {/* Detection in progress with cancel */}
        {detectColumnsMutation.isPending && (
          <div style={{ marginTop: tokens.spacing[6], textAlign: 'center' }} className="animate-fade-in-up">
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div>
                <Spin size="large" style={{ marginBottom: tokens.spacing[2] }} />
                <Title level={5} style={{ margin: 0 }}>Analyzing structure...</Title>
                <Text type="secondary">Reading {file?.name}</Text>
              </div>
              
              {showDetectionTimeout && (
                <Alert
                  type="warning"
                  message="Large file detected"
                  description="This is taking a bit longer than usual. Please hang tight."
                  icon={<ClockCircleOutlined />}
                  showIcon
                  style={{ maxWidth: 400, margin: '0 auto' }}
                />
              )}
              
              <Button 
                onClick={handleCancelDetection}
                type="text"
                danger
                icon={<CloseCircleOutlined />}
              >
                Cancel
              </Button>
            </Space>
          </div>
        )}

        {/* File selected indicator */}
        {file && !detectColumnsMutation.isPending && (
          <div className="animate-scale-in" style={{ marginTop: tokens.spacing[6] }}>
            <Alert
              type="info"
              message={
                <Space align="center" style={{ width: '100%', justifyContent: 'space-between' }}>
                  <Space>
                    <FileOutlined style={{ fontSize: 24, color: tokens.colors.primary[500] }} />
                    <Space direction="vertical" size={0}>
                      <Text strong style={{ fontSize: 16 }}>{file.name}</Text>
                      <Text type="secondary">{formatFileSize(file.size)}</Text>
                    </Space>
                  </Space>
                  <CheckCircleOutlined style={{ fontSize: 24, color: tokens.colors.success[500] }} />
                </Space>
              }
              style={{ 
                borderRadius: 12, 
                border: `1px solid ${tokens.colors.primary[200]}`,
                background: tokens.colors.primary[50]
              }}
            />
          </div>
        )}
      </Card>
    </div>
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
            <Text type="secondary">({formatFileSize(file?.size ?? 0)})</Text>
          </Space>
        }
        description={`${previewData?.rowCount?.toLocaleString() ?? 0} rows detected`}
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

      {previewData?.sampleRows && previewData.sampleRows.length > 0 && (
        <Card title="Sample Data (First 5 rows)">
          <Table
            dataSource={previewData.sampleRows.slice(0, 5)}
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

  // Column validation warnings
  const getColumnValidationWarnings = (): { type: 'warning' | 'error' | 'success'; message: string }[] => {
    const warnings: { type: 'warning' | 'error' | 'success'; message: string }[] = [];
    
    if (!previewData?.sampleRows || previewData.sampleRows.length === 0) return warnings;

    const sampleRows = previewData.sampleRows;
    
    // Check case ID
    if (columnMapping.caseId) {
      const uniqueCaseIds = getUniqueValuesFromSample(sampleRows, columnMapping.caseId);
      if (uniqueCaseIds <= 2) {
        warnings.push({ type: 'warning', message: `Very few unique Case IDs (${uniqueCaseIds}) in sample. Verify this is the correct column.` });
      } else if (uniqueCaseIds === sampleRows.length) {
        warnings.push({ type: 'success', message: `Case ID column looks good (${uniqueCaseIds} unique values in sample)` });
      }
    }
    
    // Check activity
    if (columnMapping.activity) {
      const uniqueActivities = getUniqueValuesFromSample(sampleRows, columnMapping.activity);
      if (uniqueActivities === sampleRows.length) {
        warnings.push({ type: 'warning', message: `Every row has a unique Activity. This is unusual for process data.` });
      } else if (uniqueActivities > 0) {
        warnings.push({ type: 'success', message: `Activity column has ${uniqueActivities} unique values in sample` });
      }
    }
    
    // Check timestamp format (simple validation)
    if (columnMapping.timestamp && sampleRows[0]) {
      const sampleTimestamp = String(sampleRows[0][columnMapping.timestamp] ?? '');
      if (sampleTimestamp && !isNaN(Date.parse(sampleTimestamp))) {
        warnings.push({ type: 'success', message: `Timestamp format detected: ${sampleTimestamp.slice(0, 19)}` });
      } else if (sampleTimestamp) {
        warnings.push({ type: 'warning', message: `Timestamp format may not parse correctly: "${sampleTimestamp}"` });
      }
    }
    
    return warnings;
  };

  // Step 3: Configure Column Mapping with Validation Summary
  const renderConfiguration = () => {
    const validationWarnings = getColumnValidationWarnings();
    const hasAllRequired = !!columnMapping.caseId && !!columnMapping.activity && !!columnMapping.timestamp;
    
    return (
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
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

        {/* Validation Summary */}
        {hasAllRequired && validationWarnings.length > 0 && (
          <Card title="Column Validation" size="small">
            <Space direction="vertical" style={{ width: '100%' }}>
              {validationWarnings.map((warning, idx) => (
                <Alert
                  key={idx}
                  type={warning.type === 'success' ? 'success' : warning.type}
                  message={warning.message}
                  showIcon
                  icon={
                    warning.type === 'warning' ? <WarningOutlined /> :
                    warning.type === 'success' ? <CheckCircleOutlined /> :
                    <ExclamationCircleOutlined />
                  }
                />
              ))}
            </Space>
          </Card>
        )}
      </Space>
    );
  };

  // Get processing stage info
  const getProcessingStageInfo = () => {
    switch (processingStage) {
      case 'uploading':
        return { percent: uploadPercent, text: `Uploading your file... ${uploadPercent}%`, status: 'active' as const };
      case 'parsing':
        return { percent: 100, text: 'Processing on server...', status: 'active' as const };
      case 'analyzing':
        return { percent: 100, text: 'Analyzing process structure...', status: 'active' as const };
      case 'complete':
        return { percent: 100, text: 'Complete!', status: 'success' as const };
      case 'error':
        return { percent: 0, text: 'Processing failed', status: 'exception' as const };
      default:
        return { percent: 0, text: 'Preparing...', status: 'normal' as const };
    }
  };

  // Step 4: Processing
  const renderProcessing = () => {
    if (uploadedLogId) {
      return (
        <Result
          status="success"
          title="Event Log Processed Successfully!"
          subTitle={
            <Space direction="vertical" size="small">
              <Text>{file?.name} has been processed and is ready for analysis.</Text>
              <Text type="secondary">{formatFileSize(file?.size ?? 0)}</Text>
            </Space>
          }
          extra={[
            <Button type="primary" size="large" key="done" onClick={handleDone}>
              Done
            </Button>,
            <Button key="explore" onClick={handleExploreProcess}>
              Explore Analysis
            </Button>,
            <Button key="another" onClick={handleUploadAnother}>
              Upload Another
            </Button>,
          ]}
        />
      );
    }

    if (ingestMutation.isError) {
      const errorMessage = (ingestMutation.error as Error).message;
      const isNetworkError = errorMessage.toLowerCase().includes('network') || 
                            errorMessage.toLowerCase().includes('unable to reach') ||
                            errorMessage.toLowerCase().includes('failed to fetch');
      
      return (
        <Result
          status="error"
          title={isNetworkError ? 'Cannot Connect to Server' : 'Upload Failed'}
          subTitle={
            <Space direction="vertical">
              <Text>{errorMessage}</Text>
              {isNetworkError && (
                <Text type="secondary">
                  Please check that the backend server is running and try again.
                </Text>
              )}
            </Space>
          }
          extra={[
            <Button type="primary" key="retry" onClick={() => {
              setUploadPercent(0);
              setProcessingStage('uploading');
              ingestMutation.mutate();
            }}>
              Try Again
            </Button>,
            <Button key="back" onClick={() => {
              setProcessingStage('idle');
              setCurrentStep(2);
            }}>
              Go Back to Configuration
            </Button>,
            <Button key="start-over" onClick={handleUploadAnother}>
              Start Over
            </Button>,
          ]}
        />
      );
    }

    const stageInfo = getProcessingStageInfo();

    return (
      <Card>
        <div style={{ textAlign: 'center', padding: tokens.spacing[8] }}>
          <Progress 
            type="circle" 
            percent={stageInfo.percent} 
            status={stageInfo.status}
            strokeColor={{
              '0%': tokens.colors.primary[400],
              '100%': tokens.colors.primary[600],
            }}
          />
          
          <Title level={4} style={{ marginTop: tokens.spacing[6] }}>
            {stageInfo.text}
          </Title>
          
          <Space direction="vertical" style={{ marginTop: tokens.spacing[4] }}>
            <Text type="secondary">
              Processing {file?.name}
            </Text>
            
            {/* Processing stages indicator */}
            <Space style={{ marginTop: tokens.spacing[4] }}>
              <Tag color={processingStage === 'uploading' ? 'processing' : processingStage !== 'idle' ? 'success' : 'default'}>
                1. Upload
              </Tag>
              <Tag color={processingStage === 'parsing' ? 'processing' : ['analyzing', 'complete'].includes(processingStage) ? 'success' : 'default'}>
                2. Parse
              </Tag>
              <Tag color={processingStage === 'analyzing' ? 'processing' : processingStage === 'complete' ? 'success' : 'default'}>
                3. Analyze
              </Tag>
            </Space>
          </Space>

          {/* Elapsed time for long operations */}
          {elapsedSeconds > 0 && !uploadedLogId && (
            <Text type="secondary" style={{ display: 'block', marginTop: tokens.spacing[4] }}>
              Elapsed: {elapsedSeconds}s
            </Text>
          )}

          {/* Timeout warning */}
          {showProcessingTimeout && (
            <Alert
              type="info"
              message="Still processing your data..."
              description="Large files may take several minutes. Please don't close this page."
              icon={<ClockCircleOutlined />}
              showIcon
              style={{ marginTop: tokens.spacing[6], textAlign: 'left' }}
            />
          )}
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
        breadcrumb={
          projectId
            ? [
                { label: 'Projects', href: '/workspace' },
                { label: 'Project', href: `/workspace/${projectId}` },
                { label: 'Upload' },
              ]
            : [
                { label: 'Event Logs', href: '/processes' },
                { label: 'Upload' },
              ]
        }
        actions={
          <Button
            icon={<ArrowLeftOutlined />}
            onClick={handleCancelClick}
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

      {/* Cancel Confirmation Modal */}
      <Modal
        title="Discard Upload Progress?"
        open={showCancelConfirm}
        onOk={handleConfirmCancel}
        onCancel={handleCancelStay}
        okText="Discard"
        cancelText="Stay"
        okButtonProps={{ danger: true }}
      >
        <p>
          You have unsaved upload progress. If you leave now, your file selection and column 
          configuration will be lost.
        </p>
        <p>Are you sure you want to discard your progress?</p>
      </Modal>
    </div>
  );
}

export default UploadWizardPage;
