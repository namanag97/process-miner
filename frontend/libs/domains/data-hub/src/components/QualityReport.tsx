import React from 'react';
import {
  Card,
  Row,
  Col,
  Progress,
  Typography,
  Table,
  Tag,
  Alert,
  Skeleton,
  Space,
  Tooltip,
} from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  WarningOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import { useLogQuality } from '../hooks';

const { Title, Text } = Typography;

interface QualityReportProps {
  logId: string;
}

interface QualityIssue {
  issueType: string;
  message: string;
  severity: 'error' | 'warning' | 'info';
  affectedRows: number;
  column?: string;
}

export const QualityReport: React.FC<QualityReportProps> = ({ logId }) => {
  const { data: quality, isLoading, error } = useLogQuality(logId);

  if (error) {
    return (
      <Alert
        type="error"
        message="Failed to load quality report"
        description="Could not retrieve the quality assessment for this log."
      />
    );
  }

  if (isLoading) {
    return (
      <Card>
        <Skeleton active />
      </Card>
    );
  }

  if (!quality) {
    return (
      <Alert
        type="info"
        message="Quality report not available"
        description="Run a quality assessment to see the results."
      />
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#52c41a';
    if (score >= 60) return '#faad14';
    return '#ff4d4f';
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'error':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
      case 'warning':
        return <WarningOutlined style={{ color: '#faad14' }} />;
      default:
        return <InfoCircleOutlined style={{ color: '#1890ff' }} />;
    }
  };

  const getSeverityTag = (severity: string) => {
    switch (severity) {
      case 'error':
        return <Tag color="error">Error</Tag>;
      case 'warning':
        return <Tag color="warning">Warning</Tag>;
      default:
        return <Tag color="blue">Info</Tag>;
    }
  };

  const issueColumns = [
    {
      title: '',
      key: 'icon',
      width: 40,
      render: (_: unknown, record: QualityIssue) => getSeverityIcon(record.severity),
    },
    {
      title: 'Issue Type',
      dataIndex: 'issueType',
      key: 'issueType',
      width: 150,
      render: (type: string) => (
        <Text strong style={{ textTransform: 'capitalize' }}>
          {type.replace(/_/g, ' ')}
        </Text>
      ),
    },
    {
      title: 'Description',
      dataIndex: 'message',
      key: 'message',
    },
    {
      title: 'Severity',
      dataIndex: 'severity',
      key: 'severity',
      width: 100,
      render: (severity: string) => getSeverityTag(severity),
    },
    {
      title: 'Affected Rows',
      dataIndex: 'affectedRows',
      key: 'affectedRows',
      width: 120,
      render: (rows: number) => rows.toLocaleString(),
    },
    {
      title: 'Column',
      dataIndex: 'column',
      key: 'column',
      width: 120,
      render: (column: string) => column || '-',
    },
  ];

  const errorCount = quality.issues.filter((i) => i.severity === 'error').length;
  const warningCount = quality.issues.filter((i) => i.severity === 'warning').length;
  const infoCount = quality.issues.filter((i) => i.severity === 'info').length;

  return (
    <div>
      {/* Overall Status */}
      <Card size="small" style={{ marginBottom: 16 }}>
        <Row align="middle" gutter={24}>
          <Col>
            {quality.isValid ? (
              <CheckCircleOutlined style={{ fontSize: 48, color: '#52c41a' }} />
            ) : (
              <CloseCircleOutlined style={{ fontSize: 48, color: '#ff4d4f' }} />
            )}
          </Col>
          <Col flex={1}>
            <Title level={4} style={{ marginBottom: 4 }}>
              {quality.isValid ? 'Data Quality: Good' : 'Data Quality: Issues Found'}
            </Title>
            <Text type="secondary">
              {quality.isValid
                ? 'Your event log meets quality standards and is ready for analysis.'
                : 'Some issues were found that may affect analysis quality.'}
            </Text>
          </Col>
          <Col>
            <Space size="large">
              {errorCount > 0 && (
                <Tooltip title="Errors">
                  <Tag color="error" icon={<CloseCircleOutlined />}>
                    {errorCount} Errors
                  </Tag>
                </Tooltip>
              )}
              {warningCount > 0 && (
                <Tooltip title="Warnings">
                  <Tag color="warning" icon={<WarningOutlined />}>
                    {warningCount} Warnings
                  </Tag>
                </Tooltip>
              )}
              {infoCount > 0 && (
                <Tooltip title="Info">
                  <Tag color="blue" icon={<InfoCircleOutlined />}>
                    {infoCount} Info
                  </Tag>
                </Tooltip>
              )}
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Score Cards */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={8}>
          <Card size="small">
            <div style={{ textAlign: 'center' }}>
              <Progress
                type="dashboard"
                percent={quality.overallScore}
                strokeColor={getScoreColor(quality.overallScore)}
                size={120}
              />
              <div style={{ marginTop: 8 }}>
                <Text strong>Overall Score</Text>
              </div>
            </div>
          </Card>
        </Col>
        <Col span={8}>
          <Card size="small">
            <div style={{ textAlign: 'center' }}>
              <Progress
                type="dashboard"
                percent={quality.completenessScore}
                strokeColor={getScoreColor(quality.completenessScore)}
                size={120}
              />
              <div style={{ marginTop: 8 }}>
                <Text strong>Completeness</Text>
                <br />
                <Text type="secondary" style={{ fontSize: 12 }}>
                  Missing values & required fields
                </Text>
              </div>
            </div>
          </Card>
        </Col>
        <Col span={8}>
          <Card size="small">
            <div style={{ textAlign: 'center' }}>
              <Progress
                type="dashboard"
                percent={quality.validityScore}
                strokeColor={getScoreColor(quality.validityScore)}
                size={120}
              />
              <div style={{ marginTop: 8 }}>
                <Text strong>Validity</Text>
                <br />
                <Text type="secondary" style={{ fontSize: 12 }}>
                  Data format & consistency
                </Text>
              </div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* Issues Table */}
      {quality.issues.length > 0 ? (
        <Card title="Quality Issues" size="small">
          <Table
            columns={issueColumns}
            dataSource={quality.issues.map((issue, i) => ({ ...issue, key: i }))}
            pagination={{ pageSize: 5 }}
            size="small"
          />
        </Card>
      ) : (
        <Card size="small">
          <Alert
            type="success"
            message="No Issues Found"
            description="Your event log passed all quality checks."
            showIcon
            icon={<CheckCircleOutlined />}
          />
        </Card>
      )}
    </div>
  );
};
