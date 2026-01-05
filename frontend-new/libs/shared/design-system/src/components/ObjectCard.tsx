/**
 * ObjectCard - Generic card component for representing domain objects
 *
 * Base card component that can display any domain object (workspace, event log,
 * model, prediction, connection, alert, etc.) with consistent styling.
 *
 * @example
 * <ObjectCard
 *   type="event_log"
 *   title="sales_log.csv"
 *   subtitle="125,432 events"
 *   status="completed"
 *   metadata={[
 *     { label: 'Cases', value: '12,456' },
 *     { label: 'Activities', value: '47' },
 *   ]}
 *   onClick={() => navigate(`/datasets/${id}`)}
 * />
 */
import { useState } from 'react';
import { Card, Typography, Tooltip } from 'antd';
import {
  FolderOutlined,
  FileTextOutlined,
  ApartmentOutlined,
  RobotOutlined,
  ApiOutlined,
  BellOutlined,
  InboxOutlined,
} from '@ant-design/icons';
import { StatusBadge, type ObjectStatus } from './StatusBadge';
import { tokens } from '../theme';

const { Text, Title } = Typography;

// ============================================
// Types
// ============================================

export type ObjectType =
  | 'workspace'
  | 'event_log'
  | 'model'
  | 'prediction'
  | 'connection'
  | 'alert'
  | 'queue'
  | 'dashboard';

export interface ObjectMetadata {
  label: string;
  value: string | number;
  tooltip?: string;
}

export interface ObjectCardProps {
  /** Type of domain object */
  type: ObjectType;
  /** Card title */
  title: string;
  /** Optional subtitle */
  subtitle?: string;
  /** Object status */
  status?: ObjectStatus;
  /** Metadata items to display */
  metadata?: ObjectMetadata[];
  /** Action buttons/menu */
  actions?: React.ReactNode;
  /** Click handler */
  onClick?: () => void;
  /** Whether card is selected */
  selected?: boolean;
  /** Whether card is in loading state */
  loading?: boolean;
  /** Custom icon override */
  icon?: React.ReactNode;
  /** Additional CSS class */
  className?: string;
  /** Timestamp to display */
  timestamp?: string | Date;
  /** Timestamp label */
  timestampLabel?: string;
}

// ============================================
// Configuration
// ============================================

interface TypeConfig {
  icon: React.ReactNode;
  color: string;
  bgColor: string;
}

const TYPE_CONFIG: Record<ObjectType, TypeConfig> = {
  workspace: {
    icon: <FolderOutlined />,
    color: tokens.colors.primary[500],
    bgColor: tokens.colors.primary[50],
  },
  event_log: {
    icon: <FileTextOutlined />,
    color: tokens.colors.success[500],
    bgColor: tokens.colors.success[50],
  },
  model: {
    icon: <ApartmentOutlined />,
    color: tokens.colors.info[500],
    bgColor: tokens.colors.info[50],
  },
  prediction: {
    icon: <RobotOutlined />,
    color: '#8B5CF6', // Purple
    bgColor: '#F5F3FF',
  },
  connection: {
    icon: <ApiOutlined />,
    color: tokens.colors.warning[500],
    bgColor: tokens.colors.warning[50],
  },
  alert: {
    icon: <BellOutlined />,
    color: tokens.colors.error[500],
    bgColor: tokens.colors.error[50],
  },
  queue: {
    icon: <InboxOutlined />,
    color: tokens.colors.neutral[600],
    bgColor: tokens.colors.neutral[100],
  },
  dashboard: {
    icon: <ApartmentOutlined />,
    color: tokens.colors.primary[500],
    bgColor: tokens.colors.primary[50],
  },
};

// ============================================
// ObjectCard Component
// ============================================

export function ObjectCard({
  type,
  title,
  subtitle,
  status,
  metadata = [],
  actions,
  onClick,
  selected = false,
  loading = false,
  icon,
  className,
  timestamp,
  timestampLabel = 'Updated',
}: ObjectCardProps) {
  const [isHovered, setIsHovered] = useState(false);
  const config = TYPE_CONFIG[type];
  const displayIcon = icon || config.icon;

  const formattedTimestamp = timestamp
    ? typeof timestamp === 'string'
      ? timestamp
      : timestamp.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      })
    : null;

  return (
    <Card
      hoverable={!!onClick}
      loading={loading}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`card-hover-lift ${className || ''}`}
      style={{
        cursor: onClick ? 'pointer' : 'default',
        border: selected
          ? `2px solid ${tokens.colors.primary[500]}`
          : `1px solid ${tokens.colors.neutral[200]}`,
        borderRadius: tokens.radius.lg,
        transition: `all ${tokens.duration.normal}ms ${tokens.easing.out}`,
        boxShadow: isHovered ? tokens.shadow.lg : tokens.shadow.sm,
      }}
      styles={{
        body: {
          padding: tokens.spacing[4],
        },
      }}
    >
      {/* Header Row: Status + Actions */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: tokens.spacing[3],
        }}
      >
        {status && <StatusBadge status={status} size="small" />}
        {!status && <div />}
        {actions && (
          <div onClick={(e) => e.stopPropagation()}>
            {actions}
          </div>
        )}
      </div>

      {/* Title Row: Icon + Title */}
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          gap: tokens.spacing[3],
          marginBottom: tokens.spacing[3],
        }}
      >
        {/* Type Icon */}
        <div
          style={{
            width: 40,
            height: 40,
            borderRadius: tokens.radius.md,
            backgroundColor: config.bgColor,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: config.color,
            fontSize: 18,
            flexShrink: 0,
          }}
        >
          {displayIcon}
        </div>

        {/* Title & Subtitle */}
        <div style={{ minWidth: 0, flex: 1 }}>
          <Title
            level={5}
            style={{
              margin: 0,
              fontSize: tokens.fontSize.base,
              fontWeight: tokens.fontWeight.semibold,
              lineHeight: 1.3,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {title}
          </Title>
          {subtitle && (
            <Text
              type="secondary"
              style={{
                fontSize: tokens.fontSize.sm,
                display: 'block',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                whiteSpace: 'nowrap',
              }}
            >
              {subtitle}
            </Text>
          )}
        </div>
      </div>

      {/* Metadata Grid */}
      {metadata.length > 0 && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: `repeat(${Math.min(metadata.length, 3)}, 1fr)`,
            gap: tokens.spacing[2],
            padding: tokens.spacing[3],
            backgroundColor: tokens.colors.neutral[50],
            borderRadius: tokens.radius.sm,
            marginBottom: formattedTimestamp ? tokens.spacing[3] : 0,
          }}
        >
          {metadata.slice(0, 3).map((item, index) => (
            <div key={index} style={{ textAlign: 'center' }}>
              <Text
                type="secondary"
                style={{
                  fontSize: tokens.fontSize.xs,
                  display: 'block',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                }}
              >
                {item.label}
              </Text>
              {item.tooltip ? (
                <Tooltip title={item.tooltip}>
                  <Text
                    strong
                    style={{
                      fontSize: tokens.fontSize.sm,
                      color: tokens.colors.neutral[800],
                    }}
                  >
                    {item.value}
                  </Text>
                </Tooltip>
              ) : (
                <Text
                  strong
                  style={{
                    fontSize: tokens.fontSize.sm,
                    color: tokens.colors.neutral[800],
                  }}
                >
                  {item.value}
                </Text>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Timestamp Footer */}
      {formattedTimestamp && (
        <Text
          type="secondary"
          style={{
            fontSize: tokens.fontSize.xs,
            display: 'block',
          }}
        >
          {timestampLabel}: {formattedTimestamp}
        </Text>
      )}
    </Card>
  );
}

// ============================================
// ObjectCardGrid - Layout helper
// ============================================

export interface ObjectCardGridProps {
  children: React.ReactNode;
  columns?: number;
  gap?: number;
}

export function ObjectCardGrid({
  children,
  columns: _columns = 3,
  gap = tokens.spacing[4],
}: ObjectCardGridProps) {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: `repeat(auto-fill, minmax(280px, 1fr))`,
        gap,
      }}
    >
      {children}
    </div>
  );
}

export default ObjectCard;
