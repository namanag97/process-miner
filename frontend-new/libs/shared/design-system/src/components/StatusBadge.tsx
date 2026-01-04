/**
 * StatusBadge - Consistent status indicator across domain objects
 *
 * Provides standardized status display for object lifecycle states.
 * Uses semantic color tokens from theme.ts.
 *
 * @example
 * <StatusBadge status="running" showLabel />
 * <StatusBadge status="completed" size="small" />
 * <StatusBadge status="failed" pulse />
 */
import { Tag, Tooltip } from 'antd';
import {
  ClockCircleOutlined,
  SyncOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ExclamationCircleOutlined,
  InboxOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import { tokens } from '../theme';

// ============================================
// Types
// ============================================

export type ObjectStatus =
  | 'pending'
  | 'running'
  | 'completed'
  | 'failed'
  | 'stale'
  | 'active'
  | 'archived'
  | 'draft';

export type SeverityLevel =
  | 'critical'
  | 'high'
  | 'medium'
  | 'low'
  | 'info';

export interface StatusBadgeProps {
  /** Object lifecycle status */
  status: ObjectStatus;
  /** Badge size */
  size?: 'small' | 'default' | 'large';
  /** Show status label text */
  showLabel?: boolean;
  /** Custom label override */
  label?: string;
  /** Animate for running states */
  pulse?: boolean;
  /** Show as dot only (minimal) */
  dotOnly?: boolean;
  /** Tooltip text */
  tooltip?: string;
}

export interface SeverityBadgeProps {
  /** Severity level */
  severity: SeverityLevel;
  /** Badge size */
  size?: 'small' | 'default' | 'large';
  /** Show severity label text */
  showLabel?: boolean;
  /** Custom label override */
  label?: string;
}

// ============================================
// Configuration
// ============================================

interface StatusConfig {
  color: string;
  bgColor: string;
  icon: React.ReactNode;
  label: string;
}

const STATUS_CONFIG: Record<ObjectStatus, StatusConfig> = {
  pending: {
    color: tokens.colors.status.pending,
    bgColor: '#FFFBEB',
    icon: <ClockCircleOutlined />,
    label: 'Pending',
  },
  running: {
    color: tokens.colors.status.running,
    bgColor: '#EFF6FF',
    icon: <SyncOutlined spin />,
    label: 'Running',
  },
  completed: {
    color: tokens.colors.status.completed,
    bgColor: '#ECFDF5',
    icon: <CheckCircleOutlined />,
    label: 'Completed',
  },
  failed: {
    color: tokens.colors.status.failed,
    bgColor: '#FEF2F2',
    icon: <CloseCircleOutlined />,
    label: 'Failed',
  },
  stale: {
    color: tokens.colors.status.stale,
    bgColor: '#F3F4F6',
    icon: <ExclamationCircleOutlined />,
    label: 'Stale',
  },
  active: {
    color: tokens.colors.status.active,
    bgColor: '#ECFDF5',
    icon: <CheckCircleOutlined />,
    label: 'Active',
  },
  archived: {
    color: tokens.colors.status.archived,
    bgColor: '#F3F4F6',
    icon: <InboxOutlined />,
    label: 'Archived',
  },
  draft: {
    color: tokens.colors.status.draft,
    bgColor: '#F5F3FF',
    icon: <FileTextOutlined />,
    label: 'Draft',
  },
};

const SEVERITY_CONFIG: Record<SeverityLevel, { color: string; bgColor: string; label: string }> = {
  critical: {
    color: tokens.colors.severity.critical,
    bgColor: '#FEF2F2',
    label: 'Critical',
  },
  high: {
    color: tokens.colors.severity.high,
    bgColor: '#FFFBEB',
    label: 'High',
  },
  medium: {
    color: tokens.colors.severity.medium,
    bgColor: '#EFF6FF',
    label: 'Medium',
  },
  low: {
    color: tokens.colors.severity.low,
    bgColor: '#ECFDF5',
    label: 'Low',
  },
  info: {
    color: tokens.colors.severity.info,
    bgColor: '#F3F4F6',
    label: 'Info',
  },
};

// ============================================
// Size Mapping
// ============================================

const SIZE_STYLES = {
  small: {
    fontSize: tokens.fontSize.xs,
    padding: '0 6px',
    height: 20,
    dotSize: 6,
  },
  default: {
    fontSize: tokens.fontSize.sm,
    padding: '0 8px',
    height: 24,
    dotSize: 8,
  },
  large: {
    fontSize: tokens.fontSize.base,
    padding: '0 12px',
    height: 28,
    dotSize: 10,
  },
};

// ============================================
// StatusBadge Component
// ============================================

export function StatusBadge({
  status,
  size = 'default',
  showLabel = true,
  label,
  pulse = false,
  dotOnly = false,
  tooltip,
}: StatusBadgeProps) {
  const config = STATUS_CONFIG[status];
  const sizeStyle = SIZE_STYLES[size];
  const displayLabel = label || config.label;

  // Dot-only variant
  if (dotOnly) {
    const dot = (
      <span
        style={{
          display: 'inline-block',
          width: sizeStyle.dotSize,
          height: sizeStyle.dotSize,
          borderRadius: '50%',
          backgroundColor: config.color,
          animation: pulse || status === 'running' ? 'pulse 2s ease-in-out infinite' : undefined,
        }}
        aria-label={displayLabel}
        role="status"
      />
    );

    return tooltip ? <Tooltip title={tooltip}>{dot}</Tooltip> : dot;
  }

  // Full badge variant
  const badge = (
    <Tag
      icon={showLabel ? config.icon : undefined}
      style={{
        color: config.color,
        backgroundColor: config.bgColor,
        border: `1px solid ${config.color}20`,
        borderRadius: tokens.radius.sm,
        fontSize: sizeStyle.fontSize,
        padding: sizeStyle.padding,
        height: sizeStyle.height,
        lineHeight: `${sizeStyle.height - 2}px`,
        display: 'inline-flex',
        alignItems: 'center',
        gap: 4,
        margin: 0,
        animation: pulse && status === 'running' ? 'pulse 2s ease-in-out infinite' : undefined,
      }}
    >
      {!showLabel && config.icon}
      {showLabel && displayLabel}
    </Tag>
  );

  return tooltip ? <Tooltip title={tooltip}>{badge}</Tooltip> : badge;
}

// ============================================
// SeverityBadge Component
// ============================================

export function SeverityBadge({
  severity,
  size = 'default',
  showLabel = true,
  label,
}: SeverityBadgeProps) {
  const config = SEVERITY_CONFIG[severity];
  const sizeStyle = SIZE_STYLES[size];
  const displayLabel = label || config.label;

  return (
    <Tag
      style={{
        color: config.color,
        backgroundColor: config.bgColor,
        border: `1px solid ${config.color}20`,
        borderRadius: tokens.radius.sm,
        fontSize: sizeStyle.fontSize,
        padding: sizeStyle.padding,
        height: sizeStyle.height,
        lineHeight: `${sizeStyle.height - 2}px`,
        display: 'inline-flex',
        alignItems: 'center',
        margin: 0,
        fontWeight: tokens.fontWeight.medium,
      }}
    >
      {showLabel ? displayLabel : severity.charAt(0).toUpperCase()}
    </Tag>
  );
}

// ============================================
// Utility: Get status from object state
// ============================================

export function getStatusFromState(state: string): ObjectStatus {
  const stateMap: Record<string, ObjectStatus> = {
    // Event Log states
    'CREATED': 'pending',
    'UPLOADING': 'running',
    'VALIDATING': 'running',
    'MAPPING': 'pending',
    'PROCESSING': 'running',
    'REPROCESSING': 'running',
    'READY': 'completed',
    'ERROR': 'failed',
    'ARCHIVED': 'archived',
    'DELETED': 'archived',

    // Process Model states
    'QUEUED': 'pending',
    'DISCOVERING': 'running',
    'STALE': 'stale',

    // Prediction Model states
    'TRAINING': 'running',
    'TRAINED': 'completed',
    'DEPLOYED': 'active',
    'RETIRED': 'archived',

    // Connection states
    'TESTING': 'running',
    'CONNECTED': 'active',
    'FAILED': 'failed',
    'SYNCING': 'running',

    // Generic states
    'ACTIVE': 'active',
    'INACTIVE': 'archived',
    'PENDING': 'pending',
    'RUNNING': 'running',
    'COMPLETED': 'completed',
    'DRAFT': 'draft',
  };

  return stateMap[state.toUpperCase()] || 'pending';
}

export default StatusBadge;
