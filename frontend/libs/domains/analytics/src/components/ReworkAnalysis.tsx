import React, { useMemo } from 'react';
import {
  Card,
  Table,
  Progress,
  Tag,
  Typography,
  Space,
  Alert,
  Spin,
  Empty,
  Row,
  Col,
  Statistic,
  Tooltip,
} from 'antd';
import {
  ReloadOutlined,
  WarningOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { useRework } from '../hooks';

const { Text } = Typography;

interface ReworkAnalysisProps {
  logId: string;
  onActivityClick?: (activity: string) => void;
  maxRows?: number;
  showSummary?: boolean;
}

interface ReworkRow {
  activity: string;
  reworkCount: number;
  caseCount: number;
  percentOfMax: number;
  severity: 'critical' | 'high' | 'medium' | 'low';
}

function getSeverity(percentOfMax: number): 'critical' | 'high' | 'medium' | 'low' {
  if (percentOfMax >= 80) return 'critical';
  if (percentOfMax >= 50) return 'high';
  if (percentOfMax >= 25) return 'medium';
  return 'low';
}

function getSeverityColor(severity: string): string {
  switch (severity) {
    case 'critical':
      return '#ff4d4f';
    case 'high':
      return '#fa8c16';
    case 'medium':
      return '#faad14';
    default:
      return '#52c41a';
  }
}

export const ReworkAnalysis: React.FC<ReworkAnalysisProps> = ({
  logId,
  onActivityClick,
  maxRows,
  showSummary = true,
}) => {
  const { data, isLoading, error } = useRework(logId);

  const tableData = useMemo<ReworkRow[]>(() => {
    if (!data?.rework || data.rework.length === 0) return [];

    const maxRework = Math.max(...data.rework.map((r: { reworkCount: number }) => r.reworkCount));
    const rows = data.rework.map((r: { activity: string; reworkCount: number; cases: string[] }) => {
      const percentOfMax = maxRework > 0 ? (r.reworkCount / maxRework) * 100 : 0;
      return {
        activity: r.activity,
        reworkCount: r.reworkCount,
        caseCount: r.cases.length,
        percentOfMax,
        severity: getSeverity(percentOfMax),
      };
    });

    return maxRows ? rows.slice(0, maxRows) : rows;
  }, [data, maxRows]);

  const columns: ColumnsType<ReworkRow> = [
    {
      title: '#',
      key: 'rank',
      width: 50,
      render: (_, __, index) => (
        <Text type="secondary">{index + 1}</Text>
      ),
    },
    {
      title: 'Activity',
      dataIndex: 'activity',
      key: 'activity',
      render: (activity: string, record) => (
        <Space>
          {record.severity === 'critical' && (
            <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />
          )}
          <Text
            strong
            style={{
              cursor: onActivityClick ? 'pointer' : 'default',
              color: onActivityClick ? '#0052cc' : undefined,
            }}
            onClick={() => onActivityClick?.(activity)}
          >
            {activity}
          </Text>
        </Space>
      ),
    },
    {
      title: (
        <Tooltip title="Number of times this activity was repeated">
          <Space>
            <ReloadOutlined />
            Rework Count
          </Space>
        </Tooltip>
      ),
      dataIndex: 'reworkCount',
      key: 'reworkCount',
      width: 150,
      sorter: (a, b) => a.reworkCount - b.reworkCount,
      defaultSortOrder: 'descend',
      render: (count: number, record) => (
        <Space direction="vertical" size={2} style={{ width: '100%' }}>
          <Text strong>{count.toLocaleString()}</Text>
          <Progress
            percent={record.percentOfMax}
            size="small"
            showInfo={false}
            strokeColor={getSeverityColor(record.severity)}
            style={{ margin: 0, width: 80 }}
          />
        </Space>
      ),
    },
    {
      title: 'Severity',
      dataIndex: 'severity',
      key: 'severity',
      width: 100,
      filters: [
        { text: 'Critical', value: 'critical' },
        { text: 'High', value: 'high' },
        { text: 'Medium', value: 'medium' },
        { text: 'Low', value: 'low' },
      ],
      onFilter: (value, record) => record.severity === value,
      render: (severity: string) => {
        const colors: Record<string, string> = {
          critical: 'error',
          high: 'warning',
          medium: 'gold',
          low: 'success',
        };
        return (
          <Tag color={colors[severity]}>
            {severity.charAt(0).toUpperCase() + severity.slice(1)}
          </Tag>
        );
      },
    },
    {
      title: 'Affected Cases',
      dataIndex: 'caseCount',
      key: 'caseCount',
      width: 120,
      sorter: (a, b) => a.caseCount - b.caseCount,
      render: (count: number) => (
        <Text>{count.toLocaleString()} cases</Text>
      ),
    },
  ];

  if (error) {
    return (
      <Alert
        type="error"
        message="Failed to load rework analysis"
        description="Could not retrieve rework data."
      />
    );
  }

  return (
    <Card
      title={
        <Space>
          <ReloadOutlined style={{ color: '#722ed1' }} />
          Rework Analysis
          {data && (
            <Tag color="default">
              {data.activitiesWithRework || 0} activities
            </Tag>
          )}
        </Space>
      }
      styles={{ body: { padding: 0 } }}
    >
      <Spin spinning={isLoading}>
        {/* Summary Section */}
        {showSummary && data && (
          <div style={{ padding: 16, background: '#fafafa', borderBottom: '1px solid #f0f0f0' }}>
            <Row gutter={[16, 16]}>
              <Col xs={12} sm={8}>
                <Statistic
                  title="Total Rework Instances"
                  value={data.totalRework || 0}
                  prefix={<ReloadOutlined />}
                  valueStyle={{ color: '#722ed1' }}
                />
              </Col>
              <Col xs={12} sm={8}>
                <Statistic
                  title="Activities with Rework"
                  value={data.activitiesWithRework || 0}
                  prefix={<WarningOutlined />}
                  valueStyle={{ color: '#faad14' }}
                />
              </Col>
              <Col xs={24} sm={8}>
                <Text type="secondary" style={{ fontSize: 12 }}>
                  Rework indicates repeated activities within cases, often
                  signaling process inefficiencies or errors requiring
                  correction.
                </Text>
              </Col>
            </Row>
          </div>
        )}

        {/* Table */}
        {tableData.length === 0 && !isLoading ? (
          <Empty
            description="No rework detected"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            style={{ padding: 40 }}
          />
        ) : (
          <Table
            columns={columns}
            dataSource={tableData}
            rowKey="activity"
            size="small"
            pagination={
              tableData.length > 10
                ? { pageSize: 10, showSizeChanger: false }
                : false
            }
          />
        )}
      </Spin>
    </Card>
  );
};
