/**
 * WorkQueueList - Component for displaying action items and task queues
 *
 * Shows pending tasks, cases requiring attention, and automation recommendations.
 * Used in dashboards and operational views.
 *
 * @example
 * <WorkQueueList
 *   items={queueItems}
 *   onItemAction={(item) => handleAction(item)}
 * />
 */

import React, { useState, useMemo } from 'react';
import {
  Card,
  List,
  Space,
  Typography,
  Tag,
  Button,
  Tooltip,
  Empty,
  Segmented,
  Badge,
  Avatar,
  Progress,
} from 'antd';
import {
  InboxOutlined,
  ClockCircleOutlined,
  UserOutlined,
  RightOutlined,
  CheckOutlined,
  ThunderboltOutlined,
  ExclamationCircleOutlined,
  FilterOutlined,
} from '@ant-design/icons';
import { SeverityBadge, type SeverityLevel } from './StatusBadge';
import { tokens } from '../theme';

const { Text, Title } = Typography;

// ============================================
// Types
// ============================================

export type QueueItemType =
  | 'case_action'
  | 'approval'
  | 'review'
  | 'escalation'
  | 'automation_recommendation'
  | 'manual_intervention';

export type QueueItemStatus = 'pending' | 'in_progress' | 'completed' | 'overdue';

export interface QueueItem {
  id: string;
  type: QueueItemType;
  status: QueueItemStatus;
  priority: SeverityLevel;
  title: string;
  description?: string;
  caseId?: string;
  assignee?: {
    id: string;
    name: string;
    avatar?: string;
  };
  dueAt?: Date;
  createdAt: Date;
  estimatedDuration?: number; // in minutes
  metadata?: Record<string, any>;
}

export interface WorkQueueListProps {
  /** Queue items */
  items: QueueItem[];
  /** Item click handler */
  onItemClick?: (item: QueueItem) => void;
  /** Complete item handler */
  onCompleteItem?: (itemId: string) => void;
  /** Assign item handler */
  onAssignItem?: (itemId: string) => void;
  /** Loading state */
  loading?: boolean;
  /** Title */
  title?: string;
  /** Show statistics */
  showStats?: boolean;
  /** Filter by status */
  filterStatus?: QueueItemStatus | 'all';
  /** Max items to display */
  maxItems?: number;
}

// ============================================
// Configuration
// ============================================

const ITEM_TYPE_LABELS: Record<QueueItemType, string> = {
  case_action: 'Case Action',
  approval: 'Approval Required',
  review: 'Review Needed',
  escalation: 'Escalation',
  automation_recommendation: 'Automation Opportunity',
  manual_intervention: 'Manual Intervention',
};

const ITEM_TYPE_ICONS: Record<QueueItemType, React.ReactNode> = {
  case_action: <RightOutlined />,
  approval: <CheckOutlined />,
  review: <InboxOutlined />,
  escalation: <ExclamationCircleOutlined />,
  automation_recommendation: <ThunderboltOutlined />,
  manual_intervention: <UserOutlined />,
};

const STATUS_CONFIG: Record<QueueItemStatus, { color: string; label: string }> = {
  pending: { color: tokens.colors.warning[500], label: 'Pending' },
  in_progress: { color: tokens.colors.info[500], label: 'In Progress' },
  completed: { color: tokens.colors.success[500], label: 'Completed' },
  overdue: { color: tokens.colors.error[500], label: 'Overdue' },
};

// ============================================
// Helpers
// ============================================

function formatTimeRemaining(dueAt: Date | undefined): string | null {
  if (!dueAt) return null;
  const now = new Date();
  const diffMs = dueAt.getTime() - now.getTime();
  
  if (diffMs < 0) {
    const overdueMs = Math.abs(diffMs);
    const overdueHours = Math.floor(overdueMs / 3600000);
    if (overdueHours < 24) return `${overdueHours}h overdue`;
    return `${Math.floor(overdueHours / 24)}d overdue`;
  }
  
  const hoursRemaining = Math.floor(diffMs / 3600000);
  if (hoursRemaining < 1) return `${Math.floor(diffMs / 60000)}m remaining`;
  if (hoursRemaining < 24) return `${hoursRemaining}h remaining`;
  return `${Math.floor(hoursRemaining / 24)}d remaining`;
}

function isOverdue(dueAt: Date | undefined): boolean {
  if (!dueAt) return false;
  return new Date() > dueAt;
}

// ============================================
// WorkQueueList Component
// ============================================

export function WorkQueueList({
  items,
  onItemClick,
  onCompleteItem,
  onAssignItem,
  loading = false,
  title = 'Work Queue',
  showStats = true,
  filterStatus = 'all',
  maxItems,
}: WorkQueueListProps) {
  const [selectedFilter, setSelectedFilter] = useState<QueueItemStatus | 'all'>(filterStatus);

  // Filter and sort items
  const filteredItems = useMemo(() => {
    let result = [...items];
    
    // Apply status filter
    if (selectedFilter !== 'all') {
      result = result.filter((item) => item.status === selectedFilter);
    }
    
    // Sort by priority and due date
    result.sort((a, b) => {
      const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3, info: 4 };
      if (priorityOrder[a.priority] !== priorityOrder[b.priority]) {
        return priorityOrder[a.priority] - priorityOrder[b.priority];
      }
      if (a.dueAt && b.dueAt) {
        return a.dueAt.getTime() - b.dueAt.getTime();
      }
      return 0;
    });
    
    return maxItems ? result.slice(0, maxItems) : result;
  }, [items, selectedFilter, maxItems]);

  // Statistics
  const stats = useMemo(() => {
    const pending = items.filter((i) => i.status === 'pending').length;
    const overdue = items.filter((i) => i.status === 'overdue' || isOverdue(i.dueAt)).length;
    const inProgress = items.filter((i) => i.status === 'in_progress').length;
    
    return { total: items.length, pending, overdue, inProgress };
  }, [items]);

  if (items.length === 0 && !loading) {
    return (
      <Card>
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description="No items in queue"
        />
      </Card>
    );
  }

  return (
    <Card
      title={
        <Space>
          <InboxOutlined style={{ color: tokens.colors.primary[500] }} />
          <span>{title}</span>
          <Badge count={stats.pending} style={{ backgroundColor: tokens.colors.warning[500] }} />
        </Space>
      }
      extra={
        <Segmented
          options={[
            { label: 'All', value: 'all' },
            { label: `Pending (${stats.pending})`, value: 'pending' },
            { label: 'Overdue', value: 'overdue' },
          ]}
          value={selectedFilter}
          onChange={(val) => setSelectedFilter(val as QueueItemStatus | 'all')}
          size="small"
        />
      }
      loading={loading}
    >
      {/* Stats Row */}
      {showStats && (
        <div
          style={{
            display: 'flex',
            gap: tokens.spacing[4],
            marginBottom: tokens.spacing[4],
            padding: tokens.spacing[3],
            backgroundColor: tokens.colors.neutral[50],
            borderRadius: tokens.radius.md,
          }}
        >
          <div style={{ flex: 1, textAlign: 'center' }}>
            <Text type="secondary" style={{ fontSize: tokens.fontSize.xs, display: 'block' }}>
              Total
            </Text>
            <Text strong style={{ fontSize: tokens.fontSize.lg }}>
              {stats.total}
            </Text>
          </div>
          <div style={{ flex: 1, textAlign: 'center' }}>
            <Text type="secondary" style={{ fontSize: tokens.fontSize.xs, display: 'block' }}>
              Pending
            </Text>
            <Text strong style={{ fontSize: tokens.fontSize.lg, color: tokens.colors.warning[500] }}>
              {stats.pending}
            </Text>
          </div>
          <div style={{ flex: 1, textAlign: 'center' }}>
            <Text type="secondary" style={{ fontSize: tokens.fontSize.xs, display: 'block' }}>
              Overdue
            </Text>
            <Text strong style={{ fontSize: tokens.fontSize.lg, color: tokens.colors.error[500] }}>
              {stats.overdue}
            </Text>
          </div>
          <div style={{ flex: 1, textAlign: 'center' }}>
            <Text type="secondary" style={{ fontSize: tokens.fontSize.xs, display: 'block' }}>
              In Progress
            </Text>
            <Text strong style={{ fontSize: tokens.fontSize.lg, color: tokens.colors.info[500] }}>
              {stats.inProgress}
            </Text>
          </div>
        </div>
      )}

      {/* Queue List */}
      <List
        dataSource={filteredItems}
        renderItem={(item) => {
          const itemIsOverdue = isOverdue(item.dueAt) || item.status === 'overdue';
          const timeRemaining = formatTimeRemaining(item.dueAt);
          const statusConfig = STATUS_CONFIG[itemIsOverdue ? 'overdue' : item.status];

          return (
            <List.Item
              key={item.id}
              onClick={() => onItemClick?.(item)}
              style={{
                cursor: onItemClick ? 'pointer' : 'default',
                padding: tokens.spacing[3],
                borderLeft: `3px solid ${itemIsOverdue ? tokens.colors.error[500] : tokens.colors.neutral[200]}`,
                backgroundColor: itemIsOverdue ? tokens.colors.error[50] : undefined,
                borderRadius: `0 ${tokens.radius.sm}px ${tokens.radius.sm}px 0`,
                marginBottom: tokens.spacing[2],
              }}
              actions={[
                onCompleteItem && item.status !== 'completed' && (
                  <Button
                    type="link"
                    size="small"
                    icon={<CheckOutlined />}
                    onClick={(e) => {
                      e.stopPropagation();
                      onCompleteItem(item.id);
                    }}
                  >
                    Complete
                  </Button>
                ),
              ].filter(Boolean)}
            >
              <List.Item.Meta
                avatar={
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
                    }}
                  >
                    {ITEM_TYPE_ICONS[item.type]}
                  </div>
                }
                title={
                  <Space>
                    <Text strong>{item.title}</Text>
                    <SeverityBadge severity={item.priority} size="small" showLabel={false} />
                    <Tag color={statusConfig.color} style={{ margin: 0 }}>
                      {statusConfig.label}
                    </Tag>
                  </Space>
                }
                description={
                  <Space direction="vertical" size={2}>
                    {item.description && (
                      <Text type="secondary" ellipsis style={{ maxWidth: 400 }}>
                        {item.description}
                      </Text>
                    )}
                    <Space split="•" style={{ fontSize: tokens.fontSize.xs }}>
                      <Text type="secondary">{ITEM_TYPE_LABELS[item.type]}</Text>
                      {item.caseId && <Text type="secondary">Case: {item.caseId}</Text>}
                      {timeRemaining && (
                        <Text style={{ color: itemIsOverdue ? tokens.colors.error[500] : tokens.colors.neutral[500] }}>
                          <ClockCircleOutlined style={{ marginRight: 4 }} />
                          {timeRemaining}
                        </Text>
                      )}
                    </Space>
                    {item.assignee && (
                      <Space size={4}>
                        <Avatar size="small" src={item.assignee.avatar} icon={<UserOutlined />} />
                        <Text type="secondary" style={{ fontSize: tokens.fontSize.xs }}>
                          {item.assignee.name}
                        </Text>
                      </Space>
                    )}
                  </Space>
                }
              />
            </List.Item>
          );
        }}
      />
    </Card>
  );
}

export default WorkQueueList;
