/**
 * PredictionModelCard - Display card for ML prediction models
 *
 * Shows model status, performance metrics, and drift indicators.
 * Used in the prediction model listing and model detail pages.
 *
 * @example
 * <PredictionModelCard
 *   model={predictionModel}
 *   onDeploy={() => deployModel(model.id)}
 *   onRetrain={() => retrainModel(model.id)}
 * />
 */

import {
  Card,
  Space,
  Typography,
  Progress,
  Tag,
  Button,
  Divider,
  Row,
  Col,
} from 'antd';
import {
  RobotOutlined,
  ThunderboltOutlined,
  ExperimentOutlined,
  RocketOutlined,
  SyncOutlined,
  WarningOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  LineChartOutlined,
} from '@ant-design/icons';
import { StatusBadge, type ObjectStatus } from './StatusBadge';
import { tokens } from '../theme';

const { Text, Title } = Typography;

// ============================================
// Types
// ============================================

export type ModelType =
  | 'next_activity'
  | 'remaining_time'
  | 'outcome'
  | 'next_timestamp'
  | 'resource'
  | 'custom';

export type DriftLevel = 'none' | 'low' | 'medium' | 'high' | 'critical';

export interface PredictionModel {
  id: string;
  name: string;
  type: ModelType;
  status: ObjectStatus;
  accuracy?: number;
  precision?: number;
  recall?: number;
  f1Score?: number;
  mae?: number; // Mean Absolute Error (for time predictions)
  driftLevel: DriftLevel;
  lastTrainedAt?: Date;
  lastPredictionAt?: Date;
  predictionCount?: number;
  eventLogId?: string;
  eventLogName?: string;
  version?: string;
}

export interface PredictionModelCardProps {
  /** Model data */
  model: PredictionModel;
  /** Click handler for card */
  onClick?: () => void;
  /** Deploy model handler */
  onDeploy?: () => void;
  /** Retrain model handler */
  onRetrain?: () => void;
  /** View predictions handler */
  onViewPredictions?: () => void;
  /** Loading state */
  loading?: boolean;
  /** Compact mode */
  compact?: boolean;
}

// ============================================
// Configuration
// ============================================

const MODEL_TYPE_LABELS: Record<ModelType, string> = {
  next_activity: 'Next Activity',
  remaining_time: 'Remaining Time',
  outcome: 'Outcome',
  next_timestamp: 'Next Timestamp',
  resource: 'Resource',
  custom: 'Custom',
};

const MODEL_TYPE_ICONS: Record<ModelType, React.ReactNode> = {
  next_activity: <ThunderboltOutlined />,
  remaining_time: <ClockCircleOutlined />,
  outcome: <CheckCircleOutlined />,
  next_timestamp: <ClockCircleOutlined />,
  resource: <RobotOutlined />,
  custom: <ExperimentOutlined />,
};

const DRIFT_CONFIG: Record<DriftLevel, { color: string; label: string; bgColor: string }> = {
  none: { color: tokens.colors.success[500], label: 'No Drift', bgColor: tokens.colors.success[50] },
  low: { color: tokens.colors.success[500], label: 'Low Drift', bgColor: tokens.colors.success[50] },
  medium: { color: tokens.colors.warning[500], label: 'Medium Drift', bgColor: tokens.colors.warning[50] },
  high: { color: tokens.colors.error[500], label: 'High Drift', bgColor: tokens.colors.error[50] },
  critical: { color: tokens.colors.severity.critical, label: 'Critical Drift', bgColor: tokens.colors.error[50] },
};

// ============================================
// Helpers
// ============================================

function formatDate(date: Date | undefined): string {
  if (!date) return 'Never';
  return date.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

function getAccuracyColor(accuracy: number): string {
  if (accuracy >= 90) return tokens.colors.success[500];
  if (accuracy >= 75) return tokens.colors.warning[500];
  return tokens.colors.error[500];
}

// ============================================
// PredictionModelCard Component
// ============================================

export function PredictionModelCard({
  model,
  onClick,
  onDeploy,
  onRetrain,
  onViewPredictions,
  loading = false,
  compact = false,
}: PredictionModelCardProps) {
  const driftConfig = DRIFT_CONFIG[model.driftLevel];
  const isDeployed = model.status === 'active';
  const canDeploy = model.status === 'completed';
  const needsRetrain = model.driftLevel === 'high' || model.driftLevel === 'critical';

  return (
    <Card
      hoverable={!!onClick}
      onClick={onClick}
      loading={loading}
      className="card-hover-lift"
      style={{
        borderRadius: tokens.radius.lg,
        cursor: onClick ? 'pointer' : 'default',
      }}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: tokens.spacing[4],
        }}
      >
        <Space direction="vertical" size={4}>
          <Space>
            <div
              style={{
                width: 36,
                height: 36,
                borderRadius: tokens.radius.md,
                backgroundColor: tokens.colors.primary[50],
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: tokens.colors.primary[500],
                fontSize: 18,
              }}
            >
              {MODEL_TYPE_ICONS[model.type]}
            </div>
            <div>
              <Title level={5} style={{ margin: 0 }}>
                {model.name}
              </Title>
              <Text type="secondary" style={{ fontSize: tokens.fontSize.xs }}>
                {MODEL_TYPE_LABELS[model.type]} {model.version && `• v${model.version}`}
              </Text>
            </div>
          </Space>
        </Space>
        <StatusBadge status={model.status} size="small" />
      </div>

      {/* Metrics */}
      {!compact && (
        <>
          <Row gutter={[16, 8]} style={{ marginBottom: tokens.spacing[4] }}>
            {model.accuracy !== undefined && (
              <Col span={12}>
                <div style={{ textAlign: 'center' }}>
                  <Progress
                    type="circle"
                    percent={model.accuracy}
                    size={60}
                    strokeColor={getAccuracyColor(model.accuracy)}
                    format={(percent) => (
                      <span style={{ fontSize: tokens.fontSize.sm, fontWeight: tokens.fontWeight.semibold }}>
                        {percent}%
                      </span>
                    )}
                  />
                  <Text
                    type="secondary"
                    style={{ display: 'block', fontSize: tokens.fontSize.xs, marginTop: 4 }}
                  >
                    Accuracy
                  </Text>
                </div>
              </Col>
            )}
            {model.f1Score !== undefined && (
              <Col span={12}>
                <div style={{ textAlign: 'center' }}>
                  <Progress
                    type="circle"
                    percent={Math.round(model.f1Score * 100)}
                    size={60}
                    strokeColor={tokens.colors.info[500]}
                    format={(_percent) => (
                      <span style={{ fontSize: tokens.fontSize.sm, fontWeight: tokens.fontWeight.semibold }}>
                        {(model.f1Score! * 100).toFixed(0)}%
                      </span>
                    )}
                  />
                  <Text
                    type="secondary"
                    style={{ display: 'block', fontSize: tokens.fontSize.xs, marginTop: 4 }}
                  >
                    F1 Score
                  </Text>
                </div>
              </Col>
            )}
          </Row>

          {/* Drift Indicator */}
          <div
            style={{
              padding: tokens.spacing[3],
              backgroundColor: driftConfig.bgColor,
              borderRadius: tokens.radius.sm,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: tokens.spacing[4],
            }}
          >
            <Space>
              {model.driftLevel !== 'none' && model.driftLevel !== 'low' ? (
                <WarningOutlined style={{ color: driftConfig.color }} />
              ) : (
                <CheckCircleOutlined style={{ color: driftConfig.color }} />
              )}
              <Text style={{ color: driftConfig.color, fontWeight: tokens.fontWeight.medium }}>
                {driftConfig.label}
              </Text>
            </Space>
            {needsRetrain && (
              <Tag color="error" style={{ margin: 0 }}>
                Retrain Recommended
              </Tag>
            )}
          </div>

          {/* Metadata */}
          <Space split={<Divider type="vertical" />} style={{ fontSize: tokens.fontSize.xs }}>
            <Text type="secondary">
              Trained: {formatDate(model.lastTrainedAt)}
            </Text>
            {model.predictionCount !== undefined && (
              <Text type="secondary">
                {model.predictionCount.toLocaleString()} predictions
              </Text>
            )}
          </Space>
        </>
      )}

      {/* Actions */}
      {(onDeploy || onRetrain || onViewPredictions) && (
        <div
          style={{
            marginTop: tokens.spacing[4],
            display: 'flex',
            gap: tokens.spacing[2],
          }}
          onClick={(e) => e.stopPropagation()}
        >
          {canDeploy && onDeploy && (
            <Button type="primary" icon={<RocketOutlined />} size="small" onClick={onDeploy}>
              Deploy
            </Button>
          )}
          {needsRetrain && onRetrain && (
            <Button icon={<SyncOutlined />} size="small" onClick={onRetrain}>
              Retrain
            </Button>
          )}
          {isDeployed && onViewPredictions && (
            <Button icon={<LineChartOutlined />} size="small" onClick={onViewPredictions}>
              View Predictions
            </Button>
          )}
        </div>
      )}
    </Card>
  );
}

export default PredictionModelCard;
