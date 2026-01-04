import { Row, Col, Card, Table, Progress, Typography, Space, Tag, Tooltip, Skeleton, Empty, Button } from 'antd';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  FileSearchOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { MetricCard, tokens, formatCompactNumber, useSDK, queryKeys, EmptyState } from '@lumina/design-system';
import { createLogger } from '../../../utils/logger';

const { Text } = Typography;
const log = createLogger('ConformanceTab');

// Impact color mapping
const impactColors: Record<string, string> = {
  high: tokens.colors.error[500],
  medium: tokens.colors.warning[500],
  low: tokens.colors.success[500],
};

function FitnessGauge({ value, label }: { value: number; label: string }) {
  const getColor = (val: number) => {
    if (val >= 90) return tokens.colors.success[500];
    if (val >= 70) return tokens.colors.warning[500];
    return tokens.colors.error[500];
  };

  return (
    <div style={{ textAlign: 'center', padding: tokens.spacing[4] }}>
      <Progress
        type="circle"
        percent={value}
        strokeColor={getColor(value)}
        strokeWidth={8}
        size={120}
        format={(percent) => (
          <span style={{ fontSize: tokens.fontSize['2xl'], fontWeight: tokens.fontWeight.bold }}>
            {percent}%
          </span>
        )}
      />
      <div style={{ marginTop: tokens.spacing[3] }}>
        <Text strong style={{ fontSize: tokens.fontSize.base }}>{label}</Text>
      </div>
    </div>
  );
}

interface ConformanceTabProps {
  logId: string | null;
}

export function ConformanceTab({ logId }: ConformanceTabProps) {
  const navigate = useNavigate();
  const sdk = useSDK();

  // Try to fetch conformance data from the backend
  // Note: This requires a model to be discovered first
  const { data: conformanceData, isLoading, error } = useQuery({
    queryKey: queryKeys.conformance.check(logId ?? '', undefined),
    queryFn: async () => {
      if (!logId) return null;
      try {
        // Attempt to get conformance data - this may fail if no model exists
        const result = await sdk.conformance.check({
          logId,
          modelId: 'default', // Use default model if exists
          method: 'token_replay',
        });
        return result;
      } catch (e) {
        // If conformance check fails (no model), return null and show placeholder
        log.warn('Conformance check not available', { logId, error: e });
        return null;
      }
    },
    enabled: !!logId,
    retry: false, // Don't retry if model doesn't exist
    staleTime: 5 * 60 * 1000,
  });

  log.debug('Rendering ConformanceTab', { logId, hasData: !!conformanceData });

  // Loading state
  if (isLoading) {
    return (
      <Card>
        <Skeleton active paragraph={{ rows: 8 }} />
      </Card>
    );
  }

  // No logId selected
  if (!logId) {
    return (
      <Card>
        <Empty
          image={<FileSearchOutlined style={{ fontSize: 64, color: tokens.colors.neutral[300] }} />}
          description="Select an event log to view conformance analysis"
        />
      </Card>
    );
  }

  // Conformance data available - show real metrics
  if (conformanceData) {
    const metrics = {
      fitness: conformanceData.fitness * 100,
      precision: (conformanceData.precision ?? 0) * 100,
      generalization: (conformanceData.generalization ?? 0) * 100,
      simplicity: (conformanceData.simplicity ?? 0) * 100,
    };

    const conformantCases = conformanceData.fittingTraces;
    const deviatingCases = conformanceData.totalTraces - conformanceData.fittingTraces;

    return (
      <div>
        {/* Summary Stats */}
        <Row gutter={16} style={{ marginBottom: tokens.spacing[6] }}>
          <Col xs={24} sm={8}>
            <MetricCard
              title="Overall Fitness"
              value={`${metrics.fitness.toFixed(1)}%`}
              status={metrics.fitness >= 85 ? 'success' : metrics.fitness >= 70 ? 'warning' : 'error'}
            />
          </Col>
          <Col xs={24} sm={8}>
            <MetricCard
              title="Conformant Cases"
              value={formatCompactNumber(conformantCases)}
              prefix={<CheckCircleOutlined style={{ color: tokens.colors.success[500], marginRight: 8 }} />}
              status="success"
            />
          </Col>
          <Col xs={24} sm={8}>
            <MetricCard
              title="Deviating Cases"
              value={formatCompactNumber(deviatingCases)}
              prefix={<ExclamationCircleOutlined style={{ color: tokens.colors.warning[500], marginRight: 8 }} />}
              status="warning"
            />
          </Col>
        </Row>

        {/* Conformance Metrics Gauges */}
        <Card
          title={
            <Space>
              <CheckCircleOutlined style={{ color: tokens.colors.success[500] }} />
              <span>Conformance Metrics</span>
              <Tooltip title="Measures how well your process follows the expected model">
                <InfoCircleOutlined style={{ color: tokens.colors.neutral[400] }} />
              </Tooltip>
            </Space>
          }
          style={{ marginBottom: tokens.spacing[6] }}
        >
          <Row>
            <Col xs={12} sm={6}>
              <FitnessGauge value={metrics.fitness} label="Fitness" />
            </Col>
            <Col xs={12} sm={6}>
              <FitnessGauge value={metrics.precision} label="Precision" />
            </Col>
            <Col xs={12} sm={6}>
              <FitnessGauge value={metrics.generalization} label="Generalization" />
            </Col>
            <Col xs={12} sm={6}>
              <FitnessGauge value={metrics.simplicity} label="Simplicity" />
            </Col>
          </Row>
        </Card>

        {/* Conformance Status */}
        <Card>
          <div style={{ textAlign: 'center', padding: tokens.spacing[6] }}>
            {conformanceData.isConformant ? (
              <>
                <CheckCircleOutlined style={{ fontSize: 48, color: tokens.colors.success[500], marginBottom: 16 }} />
                <div>
                  <Text strong style={{ fontSize: tokens.fontSize.lg }}>Process is Conformant</Text>
                </div>
                <Text type="secondary">
                  {conformantCases} out of {conformanceData.totalTraces} traces fit the expected model
                </Text>
              </>
            ) : (
              <>
                <ExclamationCircleOutlined style={{ fontSize: 48, color: tokens.colors.warning[500], marginBottom: 16 }} />
                <div>
                  <Text strong style={{ fontSize: tokens.fontSize.lg }}>Deviations Detected</Text>
                </div>
                <Text type="secondary">
                  {deviatingCases} out of {conformanceData.totalTraces} traces deviate from the expected model
                </Text>
              </>
            )}
          </div>
        </Card>
      </div>
    );
  }

  // No conformance data - show placeholder with instructions
  return (
    <Card>
      <EmptyState
        icon={<FileSearchOutlined />}
        title="Conformance Analysis Not Available"
        description="Conformance checking requires a process model. Discover a model from the Process Explorer to enable conformance analysis."
        actionLabel="Go to Explorer"
        onAction={() => navigate(`/explorer/${logId}`)}
      />
    </Card>
  );
}

export default ConformanceTab;
