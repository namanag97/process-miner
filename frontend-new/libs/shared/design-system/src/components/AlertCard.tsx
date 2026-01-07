/**
 * AlertCard - Component for displaying process alerts and notifications
 *
 * Shows real-time alerts with severity, context, and actions.
 * Used in dashboards and notification panels.
 *
 * @example
 * <AlertCard
 *   alert={alertData}
 *   onAcknowledge={() => acknowledgeAlert(alert.id)}
 *   onDismiss={() => dismissAlert(alert.id)}
 * />
 */

import React, { memo, useMemo } from 'react';
import {
  Card,
  Space,
  Typography,
  Tag,
  Button,
  Badge,
} from 'antd';
import {
  BellOutlined,
  WarningOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  ClockCircleOutlined,
  EyeOutlined,
  CloseOutlined,
  RightOutlined,
} from '@ant-design/icons';
import { SeverityBadge, type SeverityLevel } from './StatusBadge';
import { tokens } from '../theme';
import { formatTimeAgo } from '../utils/date';

const { Text, Title, Paragraph } = Typography;

// ============================================
// Types
// ============================================

export type AlertType =
  | 'sla_breach'
  | 'bottleneck'
  | 'deviation'
  | 'prediction'
  | 'threshold'
  | 'anomaly'
  | 'custom';

export type AlertStatus = 'active' | 'acknowledged' | 'resolved' | 'dismissed';

export interface Alert {
  id: string;
  type: AlertType;
  severity: SeverityLevel;
  status: AlertStatus;
  title: string;
  message: string;
  caseId?: string;
  activityName?: string;
  triggeredAt: Date;
  acknowledgedAt?: Date;
  resolvedAt?: Date;
  metadata?: Record<string, any>;
}

export interface AlertCardProps {
  /** Alert data */
  alert: Alert;
  /** Click handler for the card */
  onClick?: () => void;
  /** Acknowledge alert handler */
  onAcknowledge?: () => void;
  /** Dismiss alert handler */
  onDismiss?: () => void;
  /** Navigate to case handler */
  onNavigateToCase?: () => void;
  /** Compact mode for lists */
  compact?: boolean;
  /** Show timestamp */
  showTimestamp?: boolean;
}

// ============================================
// Configuration
// ============================================

const ALERT_TYPE_LABELS: Record<AlertType, string> = {
  sla_breach: 'SLA Breach',
  bottleneck: 'Bottleneck Detected',
  deviation: 'Process Deviation',
  prediction: 'Prediction Alert',
  threshold: 'Threshold Exceeded',
  anomaly: 'Anomaly Detected',
  custom: 'Custom Alert',
};

const ALERT_TYPE_ICONS: Record<AlertType, React.ReactNode> = {
  sla_breach: <ClockCircleOutlined />,
  bottleneck: <WarningOutlined />,
  deviation: <ExclamationCircleOutlined />,
  prediction: <BellOutlined />,
  threshold: <ExclamationCircleOutlined />,
  anomaly: <WarningOutlined />,
  custom: <InfoCircleOutlined />,
};

const SEVERITY_BORDER_COLORS: Record<SeverityLevel, string> = {
  critical: tokens.colors.severity.critical,
  high: tokens.colors.severity.high,
  medium: tokens.colors.severity.medium,
  low: tokens.colors.severity.low,
  info: tokens.colors.neutral[300],
};

const STATUS_CONFIG: Record<AlertStatus, { color: string; label: string }> = {
  active: { color: tokens.colors.error[500], label: 'Active' },
  acknowledged: { color: tokens.colors.warning[500], label: 'Acknowledged' },
  resolved: { color: tokens.colors.success[500], label: 'Resolved' },
  dismissed: { color: tokens.colors.neutral[400], label: 'Dismissed' },
};

// ============================================
// Style Factories (extracted for memo optimization)
// ============================================

const getCompactContainerStyle = (
  severity: SeverityLevel,
  isActive: boolean,
  isResolved: boolean,
  hasOnClick: boolean
) => ({
  display: 'flex' as const,
  alignItems: 'center' as const,
  gap: tokens.spacing[3],
  padding: tokens.spacing[3],
  borderLeft: `3px solid ${SEVERITY_BORDER_COLORS[severity]}`,
  backgroundColor: isActive ? tokens.colors.error[50] : tokens.colors.neutral[50],
  borderRadius: `0 ${tokens.radius.sm}px ${tokens.radius.sm}px 0`,
  cursor: hasOnClick ? 'pointer' : 'default',
  opacity: isResolved ? 0.6 : 1,
});

const getIconContainerStyle = (severity: SeverityLevel, size: number) => ({
  width: size,
  height: size,
  borderRadius: tokens.radius.sm,
  backgroundColor: SEVERITY_BORDER_COLORS[severity] + '20',
  display: 'flex' as const,
  alignItems: 'center' as const,
  justifyContent: 'center' as const,
  color: SEVERITY_BORDER_COLORS[severity],
});

const getCardStyle = (severity: SeverityLevel, isActive: boolean, isResolved: boolean) => ({
  borderLeft: `4px solid ${SEVERITY_BORDER_COLORS[severity]}`,
  borderRadius: tokens.radius.lg,
  backgroundColor: isActive ? tokens.colors.error[50] : undefined,
  opacity: isResolved ? 0.7 : 1,
});

// ============================================
// Helpers
// ============================================

// formatTimeAgo imported from ../utils/date

// ============================================
// AlertCard Component
// ============================================

export const AlertCard = memo(function AlertCard({
  alert,
  onClick,
  onAcknowledge,
  onDismiss,
  onNavigateToCase,
  compact = false,
  showTimestamp = true,
}: AlertCardProps) {
  const isActive = alert.status === 'active';
  const isResolved = alert.status === 'resolved' || alert.status === 'dismissed';
  const statusConfig = STATUS_CONFIG[alert.status];

  // Memoize styles to prevent object recreation on every render
  const compactContainerStyle = useMemo(
    () => getCompactContainerStyle(alert.severity, isActive, isResolved, !!onClick),
    [alert.severity, isActive, isResolved, onClick]
  );

  const compactIconStyle = useMemo(
    () => getIconContainerStyle(alert.severity, 32),
    [alert.severity]
  );

  const cardStyle = useMemo(
    () => getCardStyle(alert.severity, isActive, isResolved),
    [alert.severity, isActive, isResolved]
  );

  const fullIconStyle = useMemo(
    () => ({ ...getIconContainerStyle(alert.severity, 40), fontSize: 20, borderRadius: tokens.radius.md }),
    [alert.severity]
  );

  if (compact) {
    return (
      <div onClick={onClick} style={compactContainerStyle}>
        <Badge dot={isActive} color={statusConfig.color}>
          <div style={compactIconStyle}>
            {ALERT_TYPE_ICONS[alert.type]}
          </div>
        </Badge>
        <div style={{ flex: 1, minWidth: 0 }}>
          <Text strong ellipsis style={{ display: 'block' }}>
            {alert.title}
          </Text>
          <Text type="secondary" style={{ fontSize: tokens.fontSize.xs }}>
            {formatTimeAgo(alert.triggeredAt)}
          </Text>
        </div>
        <SeverityBadge severity={alert.severity} size="small" showLabel={false} />
      </div>
    );
  }

  return (
    <Card
      hoverable={!!onClick}
      onClick={onClick}
      className={onClick ? 'card-hover-lift' : ''}
      style={cardStyle}
    >
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          marginBottom: tokens.spacing[3],
        }}
      >
        <Space>
          <Badge dot={isActive} color={statusConfig.color}>
            <div style={fullIconStyle}>
              {ALERT_TYPE_ICONS[alert.type]}
            </div>
          </Badge>
          <div>
            <Title level={5} style={{ margin: 0 }}>
              {alert.title}
            </Title>
            <Text type="secondary" style={{ fontSize: tokens.fontSize.xs }}>
              {ALERT_TYPE_LABELS[alert.type]}
            </Text>
          </div>
        </Space>
        <SeverityBadge severity={alert.severity} />
      </div>

      {/* Message */}
      <Paragraph
        type="secondary"
        style={{ marginBottom: tokens.spacing[3] }}
        ellipsis={{ rows: 2 }}
      >
        {alert.message}
      </Paragraph>

      {/* Context */}
      <Space wrap style={{ marginBottom: tokens.spacing[3] }}>
        {alert.caseId && (
          <Tag
            icon={<RightOutlined />}
            style={{ cursor: onNavigateToCase ? 'pointer' : 'default' }}
            onClick={(e) => {
              e.stopPropagation();
              onNavigateToCase?.();
            }}
          >
            Case: {alert.caseId}
          </Tag>
        )}
        {alert.activityName && <Tag>Activity: {alert.activityName}</Tag>}
        <Tag color={statusConfig.color}>{statusConfig.label}</Tag>
      </Space>

      {/* Timestamp */}
      {showTimestamp && (
        <Text type="secondary" style={{ fontSize: tokens.fontSize.xs, display: 'block', marginBottom: tokens.spacing[3] }}>
          <ClockCircleOutlined style={{ marginRight: 4 }} />
          Triggered {formatTimeAgo(alert.triggeredAt)}
          {alert.acknowledgedAt && ` • Acknowledged ${formatTimeAgo(alert.acknowledgedAt)}`}
        </Text>
      )}

      {/* Actions */}
      {(onAcknowledge || onDismiss) && isActive && (
        <div
          style={{ display: 'flex', gap: tokens.spacing[2] }}
          onClick={(e) => e.stopPropagation()}
        >
          {onAcknowledge && (
            <Button icon={<EyeOutlined />} size="small" onClick={onAcknowledge}>
              Acknowledge
            </Button>
          )}
          {onDismiss && (
            <Button icon={<CloseOutlined />} size="small" onClick={onDismiss}>
              Dismiss
            </Button>
          )}
        </div>
      )}
    </Card>
  );
});

// ============================================
// AlertList - Helper for rendering multiple alerts
// ============================================

export interface AlertListProps {
  alerts: Alert[];
  onAlertClick?: (alert: Alert) => void;
  onAcknowledge?: (alertId: string) => void;
  onDismiss?: (alertId: string) => void;
  compact?: boolean;
  maxItems?: number;
}

export function AlertList({
  alerts,
  onAlertClick,
  onAcknowledge,
  onDismiss,
  compact = false,
  maxItems,
}: AlertListProps) {
  const displayAlerts = maxItems ? alerts.slice(0, maxItems) : alerts;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: tokens.spacing[3] }}>
      {displayAlerts.map((alert) => (
        <AlertCard
          key={alert.id}
          alert={alert}
          onClick={onAlertClick ? () => onAlertClick(alert) : undefined}
          onAcknowledge={onAcknowledge ? () => onAcknowledge(alert.id) : undefined}
          onDismiss={onDismiss ? () => onDismiss(alert.id) : undefined}
          compact={compact}
        />
      ))}
    </div>
  );
}

export default AlertCard;
