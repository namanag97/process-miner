import React, { useState } from 'react';
import {
  Steps,
  Upload,
  Card,
  Button,
  Select,
  Table,
  Alert,
  Form,
  Input,
  Space,
  Typography,
  Row,
  Col,
  Statistic,
  Result,
  Spin,
} from 'antd';
import {
  InboxOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  WarningOutlined,
  ArrowLeftOutlined,
  ArrowRightOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useUploadWizard } from '../hooks';

const { Dragger } = Upload;
const { Title, Text } = Typography;

export const UploadWizard: React.FC = () => {
  const navigate = useNavigate();
  const {
    state,
    setFile,
    setColumnMapping,
    validateMapping,
    goToConfirm,
    goBack,
    submit,
    reset,
    isPreviewLoading,
    isIngestLoading,
    previewError,
    ingestError,
    ingestResult,
  } = useUploadWizard();

  const [logName, setLogName] = useState('');

  const stepItems = [
    { title: 'Upload File' },
    { title: 'Map Columns' },
    { title: 'Validate' },
    { title: 'Confirm' },
  ];

  const currentStepIndex = ['upload', 'mapping', 'validate', 'confirm'].indexOf(state.step);

  // Step 1: File Upload
  const renderUploadStep = () => (
    <Card>
      <Dragger
        name="file"
        multiple={false}
        accept=".csv,.xes,.xlsx"
        beforeUpload={(file) => {
          setFile(file);
          return false; // Prevent auto upload
        }}
        showUploadList={false}
        disabled={isPreviewLoading}
      >
        {isPreviewLoading ? (
          <div style={{ padding: 40 }}>
            <Spin size="large" />
            <p style={{ marginTop: 16 }}>Analyzing file...</p>
          </div>
        ) : (
          <>
            <p className="ant-upload-drag-icon">
              <InboxOutlined />
            </p>
            <p className="ant-upload-text">Click or drag file to upload</p>
            <p className="ant-upload-hint">
              Supports CSV, XES, or Excel files. Maximum file size: 500MB.
            </p>
          </>
        )}
      </Dragger>

      {previewError && (
        <Alert
          type="error"
          message="Failed to analyze file"
          description={String(previewError)}
          style={{ marginTop: 16 }}
        />
      )}
    </Card>
  );

  // Step 2: Column Mapping
  const renderMappingStep = () => {
    if (!state.preview) return null;

    const columnOptions = state.preview.columns.map((col) => ({
      value: col,
      label: col,
    }));

    return (
      <Card>
        <Title level={5}>Map Columns</Title>
        <Text type="secondary" style={{ display: 'block', marginBottom: 24 }}>
          Select which columns contain the required event log fields.
        </Text>

        <Form layout="vertical">
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="Case ID Column"
                required
                tooltip="Unique identifier for each process instance"
              >
                <Select
                  placeholder="Select case ID column"
                  options={columnOptions}
                  value={state.columnMapping.caseIdColumn || undefined}
                  onChange={(value) => setColumnMapping({ caseIdColumn: value })}
                  showSearch
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="Activity Column"
                required
                tooltip="The activity or event name"
              >
                <Select
                  placeholder="Select activity column"
                  options={columnOptions}
                  value={state.columnMapping.activityColumn || undefined}
                  onChange={(value) => setColumnMapping({ activityColumn: value })}
                  showSearch
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                label="Timestamp Column"
                required
                tooltip="When the event occurred"
              >
                <Select
                  placeholder="Select timestamp column"
                  options={columnOptions}
                  value={state.columnMapping.timestampColumn || undefined}
                  onChange={(value) => setColumnMapping({ timestampColumn: value })}
                  showSearch
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                label="Resource Column"
                tooltip="Who performed the activity (optional)"
              >
                <Select
                  placeholder="Select resource column (optional)"
                  options={columnOptions}
                  value={state.columnMapping.resourceColumn || undefined}
                  onChange={(value) => setColumnMapping({ resourceColumn: value })}
                  allowClear
                  showSearch
                />
              </Form.Item>
            </Col>
          </Row>
        </Form>

        <Title level={5} style={{ marginTop: 24 }}>Data Preview</Title>
        <Table
          dataSource={state.preview.sampleRows.map((row, i) => ({ key: i, ...row }))}
          columns={state.preview.columns.map((col) => ({
            title: col,
            dataIndex: col,
            key: col,
            ellipsis: true,
            width: 150,
          }))}
          scroll={{ x: 'max-content' }}
          pagination={false}
          size="small"
          style={{ marginTop: 8 }}
        />

        <div style={{ marginTop: 24, display: 'flex', justifyContent: 'space-between' }}>
          <Button icon={<ArrowLeftOutlined />} onClick={goBack}>
            Back
          </Button>
          <Button
            type="primary"
            icon={<ArrowRightOutlined />}
            onClick={validateMapping}
            disabled={
              !state.columnMapping.caseIdColumn ||
              !state.columnMapping.activityColumn ||
              !state.columnMapping.timestampColumn
            }
          >
            Validate
          </Button>
        </div>
      </Card>
    );
  };

  // Step 3: Validation
  const renderValidateStep = () => {
    if (!state.validationResult) return null;

    const { isValid, errors, warnings, estimatedCases, estimatedEvents } = state.validationResult;

    return (
      <Card>
        <Result
          status={isValid ? 'success' : 'error'}
          title={isValid ? 'Validation Passed' : 'Validation Failed'}
          subTitle={
            isValid
              ? 'Your data is ready to be imported'
              : 'Please fix the errors before proceeding'
          }
        />

        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={8}>
            <Card size="small">
              <Statistic title="Estimated Cases" value={estimatedCases} />
            </Card>
          </Col>
          <Col span={8}>
            <Card size="small">
              <Statistic title="Estimated Events" value={estimatedEvents} />
            </Card>
          </Col>
          <Col span={8}>
            <Card size="small">
              <Statistic
                title="File"
                value={state.file?.name || 'Unknown'}
                valueStyle={{ fontSize: 14 }}
              />
            </Card>
          </Col>
        </Row>

        {errors.length > 0 && (
          <Alert
            type="error"
            message="Errors"
            description={
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                {errors.map((err, i) => (
                  <li key={i}>{err}</li>
                ))}
              </ul>
            }
            style={{ marginBottom: 16 }}
            icon={<CloseCircleOutlined />}
            showIcon
          />
        )}

        {warnings.length > 0 && (
          <Alert
            type="warning"
            message="Warnings"
            description={
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                {warnings.map((warn, i) => (
                  <li key={i}>{warn}</li>
                ))}
              </ul>
            }
            style={{ marginBottom: 16 }}
            icon={<WarningOutlined />}
            showIcon
          />
        )}

        <div style={{ marginTop: 24, display: 'flex', justifyContent: 'space-between' }}>
          <Button icon={<ArrowLeftOutlined />} onClick={goBack}>
            Back
          </Button>
          <Button
            type="primary"
            icon={<ArrowRightOutlined />}
            onClick={goToConfirm}
            disabled={!isValid}
          >
            Continue
          </Button>
        </div>
      </Card>
    );
  };

  // Step 4: Confirm & Import
  const renderConfirmStep = () => {
    if (ingestResult) {
      return (
        <Card>
          <Result
            status="success"
            title="Import Successful!"
            subTitle={`Log "${ingestResult.name}" has been created with ${ingestResult.totalCases.toLocaleString()} cases and ${ingestResult.totalEvents.toLocaleString()} events.`}
            extra={[
              <Button
                key="explore"
                type="primary"
                onClick={() => navigate(`/explorer/${ingestResult.id}`)}
              >
                Explore Process
              </Button>,
              <Button key="list" onClick={() => navigate('/data/logs')}>
                View All Logs
              </Button>,
              <Button key="another" onClick={reset}>
                Upload Another
              </Button>,
            ]}
          />
        </Card>
      );
    }

    return (
      <Card>
        <Title level={5}>Confirm Import</Title>
        <Text type="secondary" style={{ display: 'block', marginBottom: 24 }}>
          Review your configuration and provide a name for the event log.
        </Text>

        <Form layout="vertical">
          <Form.Item label="Log Name" required>
            <Input
              placeholder="Enter a name for this event log"
              value={logName}
              onChange={(e) => setLogName(e.target.value)}
              maxLength={100}
            />
          </Form.Item>
        </Form>

        <Card size="small" style={{ marginBottom: 16, background: '#fafafa' }}>
          <Row gutter={16}>
            <Col span={6}>
              <Text type="secondary">File:</Text>
              <br />
              <Text strong>{state.file?.name}</Text>
            </Col>
            <Col span={6}>
              <Text type="secondary">Case ID:</Text>
              <br />
              <Text strong>{state.columnMapping.caseIdColumn}</Text>
            </Col>
            <Col span={6}>
              <Text type="secondary">Activity:</Text>
              <br />
              <Text strong>{state.columnMapping.activityColumn}</Text>
            </Col>
            <Col span={6}>
              <Text type="secondary">Timestamp:</Text>
              <br />
              <Text strong>{state.columnMapping.timestampColumn}</Text>
            </Col>
          </Row>
        </Card>

        {ingestError && (
          <Alert
            type="error"
            message="Import Failed"
            description={String(ingestError)}
            style={{ marginBottom: 16 }}
          />
        )}

        <div style={{ marginTop: 24, display: 'flex', justifyContent: 'space-between' }}>
          <Button icon={<ArrowLeftOutlined />} onClick={goBack} disabled={isIngestLoading}>
            Back
          </Button>
          <Button
            type="primary"
            icon={<CheckCircleOutlined />}
            onClick={() => submit(logName || undefined)}
            loading={isIngestLoading}
            disabled={!logName}
          >
            Import Event Log
          </Button>
        </div>
      </Card>
    );
  };

  const renderStep = () => {
    switch (state.step) {
      case 'upload':
        return renderUploadStep();
      case 'mapping':
        return renderMappingStep();
      case 'validate':
        return renderValidateStep();
      case 'confirm':
        return renderConfirmStep();
      default:
        return null;
    }
  };

  return (
    <div>
      <Steps current={currentStepIndex} items={stepItems} style={{ marginBottom: 24 }} />
      {renderStep()}
    </div>
  );
};
