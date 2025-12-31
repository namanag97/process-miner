/**
 * DeviationViewer - Component for displaying process conformance deviations
 *
 * Shows deviations between actual process execution and reference model,
 * with severity indicators and detailed deviation information.
 *
 * @example
 * <DeviationViewer
 *   deviations={deviationData}
 *   onCaseClick={(caseId) => navigateToCase(caseId)}
 * />
 */

import React, { useState, useMemo } from 'react';
import {
  Card,
  Table,
  Tag,
  Space,
  Typography,
  Segmented,
  Input,
  Empty,
  Tooltip,
  Button,
  Statistic,
  Row,
  Col,
} from 'antd';
import {
  WarningOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  SearchOutlined,
  FilterOutlined,
  ExportOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { SeverityBadge, type SeverityLevel } from './StatusBadge';
import { tokens } from '../theme';

const { Text, Title } = Typography;

// ============================================
// Types
// ============================================

export type DeviationType =
  | 'missing_activity'
  | 'extra_activity'
  | 'wrong_order'
  | 'skipped_activity'
  | 'repeated_activity'
  | 'timing_violation'
  | 'resource_violation';

export interface Deviation {
  id: string;
  caseId: string;
  type: DeviationType;
  severity: SeverityLevel;
  activity?: string;
  expectedActivity?: string;
  actualActivity?: string;
  description: string;
  timestamp?: Date;
  impact?: number; // Business impact score 1-100
}

export interface DeviationViewerProps {
  /** List of deviations to display */
  deviations: Deviation[];
  /** Click handler for case navigation */
  onCaseClick?: (caseId: string) => void;
  /** Export handler */
  onExport?: () => void;
  /** Loading state */
  loading?: boolean;
  /** Title override */
  title?: string;
  /** Show summary stats */
  showSummary?: boolean;
}

// ============================================
// Configuration
// ============================================

const DEVIATION_TYPE_LABELS: Record<DeviationType, string> = {
  missing_activity: 'Missing Activity',
  extra_activity: 'Extra Activity',
  wrong_order: 'Wrong Order',
  skipped_activity: 'Skipped Activity',
  repeated_activity: 'Repeated Activity',
  timing_violation: 'Timing Violation',
  resource_violation: 'Resource Violation',
};

const DEVIATION_TYPE_ICONS: Record<DeviationType, React.ReactNode> = {
  missing_activity: <ExclamationCircleOutlined />,
  extra_activity: <WarningOutlined />,
  wrong_order: <WarningOutlined />,
  skipped_activity: <ExclamationCircleOutlined />,
  repeated_activity: <InfoCircleOutlined />,
  timing_violation: <ExclamationCircleOutlined />,
  resource_violation: <InfoCircleOutlined />,
};

// ============================================
// DeviationViewer Component
// ============================================

export function DeviationViewer({
  deviations,
  onCaseClick,
  onExport,
  loading = false,
  title = 'Process Deviations',
  showSummary = true,
}: DeviationViewerProps) {
  const [viewMode, setViewMode] = useState<'table' | 'grouped'>('table');
  const [searchText, setSearchText] = useState('');
  const [severityFilter, setSeverityFilter] = useState<SeverityLevel | 'all'>('all');

  // Filter deviations
  const filteredDeviations = useMemo(() => {
    return deviations.filter((d) => {
      const matchesSearch =
        !searchText ||
        d.caseId.toLowerCase().includes(searchText.toLowerCase()) ||
        d.description.toLowerCase().includes(searchText.toLowerCase()) ||
        d.activity?.toLowerCase().includes(searchText.toLowerCase());
      
      const matchesSeverity = severityFilter === 'all' || d.severity === severityFilter;
      
      return matchesSearch && matchesSeverity;
    });
  }, [deviations, searchText, severityFilter]);

  // Summary statistics
  const summary = useMemo(() => {
    const byType: Record<DeviationType, number> = {} as any;
    const bySeverity: Record<SeverityLevel, number> = { critical: 0, high: 0, medium: 0, low: 0, info: 0 };
    
    deviations.forEach((d) => {
      byType[d.type] = (byType[d.type] || 0) + 1;
      bySeverity[d.severity]++;
    });

    return {
      total: deviations.length,
      byType,
      bySeverity,
      affectedCases: new Set(deviations.map((d) => d.caseId)).size,
    };
  }, [deviations]);

  // Table columns - memoized to prevent recreation on every render
  const columns = useMemo<ColumnsType<Deviation>>(() => [
    {
      title: 'Severity',
      dataIndex: 'severity',
      key: 'severity',
      width: 100,
      render: (severity: SeverityLevel) => <SeverityBadge severity={severity} size="small" />,
      sorter: (a, b) => {
        const order = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };
        return order[a.severity] - order[b.severity];
      },
    },
    {
      title: 'Case ID',
      dataIndex: 'caseId',
      key: 'caseId',
      width: 120,
      render: (caseId: string) => (
        <Button
          type="link"
          size="small"
          onClick={() => onCaseClick?.(caseId)}
          style={{ padding: 0 }}
        >
          {caseId}
        </Button>
      ),
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      width: 150,
      render: (type: DeviationType) => (
        <Tag icon={DEVIATION_TYPE_ICONS[type]}>
          {DEVIATION_TYPE_LABELS[type]}
        </Tag>
      ),
      filters: Object.entries(DEVIATION_TYPE_LABELS).map(([value, text]) => ({ text, value })),
      onFilter: (value, record) => record.type === value,
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (text: string) => (
        <Tooltip title={text}>
          <Text>{text}</Text>
        </Tooltip>
      ),
    },
    {
      title: 'Activity',
      dataIndex: 'activity',
      key: 'activity',
      width: 180,
      ellipsis: true,
      render: (activity: string | undefined) => activity || '-',
    },
  ], [onCaseClick]);

  if (deviations.length === 0 && !loading) {
    return (
      <Card>
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="No deviations detected"
        />
      </Card>
    );
  }

  return (
    <div className="animate-fade-in">
      {/* Summary Stats */}
      {showSummary && (
        <Row gutter={[16, 16]} style={{ marginBottom: tokens.spacing[6] }}>
          <Col xs={12} sm={6}>
            <Card size="small">
              <Statistic
                title="Total Deviations"
                value={summary.total}
                valueStyle={{ color: tokens.colors.error[500] }}
              />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card size="small">
              <Statistic
                title="Affected Cases"
                value={summary.affectedCases}
              />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card size="small">
              <Statistic
                title="Critical"
                value={summary.bySeverity.critical}
                valueStyle={{ color: tokens.colors.severity.critical }}
              />
            </Card>
          </Col>
          <Col xs={12} sm={6}>
            <Card size="small">
              <Statistic
                title="High Priority"
                value={summary.bySeverity.high}
                valueStyle={{ color: tokens.colors.severity.high }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* Main Card */}
      <Card
        title={
          <Space>
            <WarningOutlined style={{ color: tokens.colors.warning[500] }} />
            <span>{title}</span>
            <Tag>{filteredDeviations.length}</Tag>
          </Space>
        }
        extra={
          <Space>
            <Input
              placeholder="Search..."
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              style={{ width: 200 }}
              allowClear
            />
            <Segmented
              options={[
                { label: 'All', value: 'all' },
                { label: 'Critical', value: 'critical' },
                { label: 'High', value: 'high' },
              ]}
              value={severityFilter}
              onChange={(val) => setSeverityFilter(val as SeverityLevel | 'all')}
            />
            {onExport && (
              <Button icon={<ExportOutlined />} onClick={onExport}>
                Export
              </Button>
            )}
          </Space>
        }
      >
        <Table
          dataSource={filteredDeviations}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
            showTotal: (total) => `${total} deviations`,
          }}
          size="small"
        />
      </Card>
    </div>
  );
}

export default DeviationViewer;
