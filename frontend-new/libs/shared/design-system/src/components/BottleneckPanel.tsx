/**
 * BottleneckPanel - Component for displaying process bottleneck insights
 *
 * Visualizes bottleneck activities with wait times, impact scores,
 * and actionable recommendations.
 *
 * @example
 * <BottleneckPanel
 *   bottlenecks={bottleneckData}
 *   onActivityClick={(activity) => filterByActivity(activity)}
 * />
 */

import { memo, useMemo, useState } from 'react';
import {
  Card,
  List,
  Progress,
  Space,
  Typography,
  Tag,
  Button,
  Tooltip,
  Statistic,
  Row,
  Col,
} from 'antd';
import { EmptyState } from './EmptyState';
import {
  ClockCircleOutlined,
  WarningOutlined,
  ThunderboltOutlined,
  ArrowRightOutlined,
  FireOutlined,
} from '@ant-design/icons';
import { tokens } from '../theme';

const { Text } = Typography;

// ============================================
// Types
// ============================================

export interface Bottleneck {
  id: string;
  activity: string;
  averageWaitTime: number; // in seconds
  medianWaitTime: number;
  maxWaitTime: number;
  caseCount: number;
  impactScore: number; // 1-100
  percentile: number; // What percentile of activities this represents
  previousActivity?: string;
  recommendations?: string[];
}

export interface BottleneckPanelProps {
  /** List of bottlenecks (should be sorted by impact) */
  bottlenecks: Bottleneck[];
  /** Activity click handler */
  onActivityClick?: (activity: string) => void;
  /** Loading state */
  loading?: boolean;
  /** Maximum items to show initially */
  maxItems?: number;
  /** Title override */
  title?: string;
  /** Show impact progress bars */
  showImpact?: boolean;
}

// ============================================
// Helpers
// ============================================

function formatDuration(seconds: number): string {
  if (seconds < 60) return `${Math.round(seconds)}s`;
  if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
  if (seconds < 86400) return `${(seconds / 3600).toFixed(1)}h`;
  return `${(seconds / 86400).toFixed(1)}d`;
}

function getImpactColor(score: number): string {
  if (score >= 80) return tokens.colors.severity.critical;
  if (score >= 60) return tokens.colors.severity.high;
  if (score >= 40) return tokens.colors.severity.medium;
  return tokens.colors.severity.low;
}

function getImpactLabel(score: number): string {
  if (score >= 80) return 'Critical';
  if (score >= 60) return 'High';
  if (score >= 40) return 'Medium';
  return 'Low';
}

// ============================================
// BottleneckPanel Component
// ============================================

export const BottleneckPanel = memo(function BottleneckPanel({
  bottlenecks,
  onActivityClick,
  loading = false,
  maxItems = 5,
  title = 'Top Bottlenecks',
  showImpact = true,
}: BottleneckPanelProps) {
  const [showAll, setShowAll] = useState(false);

  const displayedBottlenecks = useMemo(() => {
    const sorted = [...bottlenecks].sort((a, b) => b.impactScore - a.impactScore);
    return showAll ? sorted : sorted.slice(0, maxItems);
  }, [bottlenecks, maxItems, showAll]);

  // Summary stats
  const summary = useMemo(() => {
    if (bottlenecks.length === 0) return null;

    const totalWaitTime = bottlenecks.reduce((sum, b) => sum + b.averageWaitTime * b.caseCount, 0);
    const totalCases = bottlenecks.reduce((sum, b) => sum + b.caseCount, 0);
    const criticalCount = bottlenecks.filter((b) => b.impactScore >= 80).length;

    return {
      totalWaitTime,
      avgWaitTime: totalCases > 0 ? totalWaitTime / totalCases : 0,
      criticalCount,
      worstBottleneck: bottlenecks[0],
    };
  }, [bottlenecks]);

  if (bottlenecks.length === 0 && !loading) {
    return (
      <Card>
        <EmptyState
          title="No bottlenecks detected"
          description="Your process is running smoothly with no significant delays."
        />
      </Card>
    );
  }

  return (
    <div className="animate-fade-in">
      <Card
        title={
          <Space>
            <FireOutlined style={{ color: tokens.colors.warning[500] }} />
            <span>{title}</span>
            <Tag color="orange">{bottlenecks.length}</Tag>
          </Space>
        }
        loading={loading}
      >
        {/* Summary Row */}
        {summary && (
          <Row gutter={[16, 16]} style={{ marginBottom: tokens.spacing[6] }}>
            <Col xs={12} sm={8}>
              <Statistic
                title="Avg Wait Time"
                value={formatDuration(summary.avgWaitTime)}
                prefix={<ClockCircleOutlined />}
              />
            </Col>
            <Col xs={12} sm={8}>
              <Statistic
                title="Critical Bottlenecks"
                value={summary.criticalCount}
                valueStyle={{ color: tokens.colors.severity.critical }}
                prefix={<WarningOutlined />}
              />
            </Col>
            <Col xs={24} sm={8}>
              <Statistic
                title="Worst: Wait Time"
                value={formatDuration(summary.worstBottleneck?.averageWaitTime || 0)}
                suffix={
                  <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
                    at {summary.worstBottleneck?.activity}
                  </Text>
                }
              />
            </Col>
          </Row>
        )}

        {/* Bottleneck List */}
        <List
          dataSource={displayedBottlenecks}
          renderItem={(item, index) => (
            <List.Item
              key={item.id}
              className={index === 0 ? 'is-top-bottleneck' : undefined}
              style={{
                padding: tokens.spacing[4],
                backgroundColor: index === 0 ? tokens.colors.error[50] : undefined,
                borderRadius: tokens.radius.md,
                marginBottom: tokens.spacing[2],
              }}
              actions={[
                onActivityClick && (
                  <Button
                    type="link"
                    size="small"
                    icon={<ArrowRightOutlined />}
                    onClick={() => onActivityClick(item.activity)}
                  >
                    Explore
                  </Button>
                ),
              ].filter(Boolean)}
            >
              <List.Item.Meta
                avatar={
                  <div
                    style={{
                      width: 40,
                      height: 40,
                      borderRadius: tokens.radius.md,
                      backgroundColor: getImpactColor(item.impactScore) + '20',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: getImpactColor(item.impactScore),
                      fontWeight: tokens.fontWeight.bold,
                      fontSize: tokens.fontSize.base,
                    }}
                  >
                    #{index + 1}
                  </div>
                }
                title={
                  <Space>
                    <Text strong>{item.activity}</Text>
                    <Tag color={getImpactColor(item.impactScore)}>
                      {getImpactLabel(item.impactScore)} Impact
                    </Tag>
                  </Space>
                }
                description={
                  <div>
                    <Space split="•" style={{ marginBottom: tokens.spacing[2] }}>
                      <Text type="secondary">
                        <ClockCircleOutlined style={{ marginRight: 4 }} />
                        Avg: {formatDuration(item.averageWaitTime)}
                      </Text>
                      <Text type="secondary">Max: {formatDuration(item.maxWaitTime)}</Text>
                      <Text type="secondary">{item.caseCount.toLocaleString()} cases</Text>
                    </Space>

                    {item.previousActivity && (
                      <div>
                        <Text type="secondary" style={{ fontSize: tokens.fontSize.xs }}>
                          After: {item.previousActivity}
                        </Text>
                      </div>
                    )}

                    {showImpact && (
                      <Progress
                        percent={item.impactScore}
                        size="small"
                        showInfo={false}
                        strokeColor={getImpactColor(item.impactScore)}
                        style={{ maxWidth: 200, marginTop: tokens.spacing[2] }}
                      />
                    )}

                    {item.recommendations && item.recommendations.length > 0 && (
                      <Tooltip
                        title={
                          <ul style={{ margin: 0, paddingLeft: 16 }}>
                            {item.recommendations.map((rec, i) => (
                              <li key={i}>{rec}</li>
                            ))}
                          </ul>
                        }
                      >
                        <Button
                          type="link"
                          size="small"
                          icon={<ThunderboltOutlined />}
                          style={{ padding: 0, marginTop: tokens.spacing[1] }}
                        >
                          {item.recommendations.length} recommendation(s)
                        </Button>
                      </Tooltip>
                    )}
                  </div>
                }
              />
            </List.Item>
          )}
        />

        {/* Show More */}
        {bottlenecks.length > maxItems && (
          <div style={{ textAlign: 'center', marginTop: tokens.spacing[4] }}>
            <Button type="link" onClick={() => setShowAll(!showAll)}>
              {showAll ? 'Show Less' : `Show All ${bottlenecks.length} Bottlenecks`}
            </Button>
          </div>
        )}
      </Card>
    </div>
  );
});

export default BottleneckPanel;
