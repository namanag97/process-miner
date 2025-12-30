import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Row, Col, Card, Button, List, Typography, Spin } from 'antd';
import {
  UploadOutlined,
  SearchOutlined,
  SettingOutlined,
  FileOutlined,
  FolderOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { PageHeader, MetricCard, EmptyState, tokens, useSDK, type EventLog } from '@lumina/design-system';
import { useAuth } from '../context/AuthContext';

const { Text } = Typography;

function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffHours / 24);

  if (diffHours < 1) return 'Just now';
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  if (diffDays === 1) return 'Yesterday';
  return `${diffDays} days ago`;
}

export function HomePage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const sdk = useSDK();

  // Fetch real logs from SDK
  const { data, isLoading } = useQuery({
    queryKey: ['processes'],
    queryFn: () => sdk.processes.list({ pageSize: 5 }),
  });

  const logs = Array.isArray(data?.items) ? data.items : [];
  const hasLogs = logs.length > 0;

  // Calculate stats from real data
  const totalCases = logs.reduce((sum, log) => sum + log.totalCases, 0);
  const lastActivity = logs.length > 0 ? formatRelativeTime(logs[0].createdAt) : 'N/A';

  return (
    <div>
      <PageHeader
        title={`Welcome back, ${user?.name || 'User'}`}
        description="Here's an overview of your process mining activity"
      />

      {/* Stats Row */}
      {hasLogs && (
        <Row gutter={16} style={{ marginBottom: tokens.spacing[6] }}>
          <Col xs={24} sm={8} className="animate-fade-in-up stagger-1">
            <MetricCard
              title="Event Logs"
              value={logs.length}
            />
          </Col>
          <Col xs={24} sm={8} className="animate-fade-in-up stagger-2">
            <MetricCard
              title="Total Cases"
              value={totalCases >= 1000 ? `${(totalCases / 1000).toFixed(1)}K` : totalCases}
              status="success"
            />
          </Col>
          <Col xs={24} sm={8} className="animate-fade-in-up stagger-3">
            <MetricCard
              title="Last Activity"
              value={lastActivity}
            />
          </Col>
        </Row>
      )}

      <Row gutter={24}>
        {/* Recent Logs */}
        <Col xs={24} lg={16}>
          <Card
            title="Recent Event Logs"
            extra={
              <Button type="link" onClick={() => navigate('/processes')}>
                View all
              </Button>
            }
            style={{ marginBottom: tokens.spacing[6] }}
          >
            {isLoading ? (
              <div style={{ display: 'flex', justifyContent: 'center', padding: 24 }}>
                <Spin />
              </div>
            ) : hasLogs ? (
              <List
                dataSource={logs}
                renderItem={(item: EventLog) => (
                  <List.Item
                    actions={[
                      <Button
                        key="view"
                        type="link"
                        onClick={() => navigate(`/processes/${item.id}`)}
                      >
                        View
                      </Button>,
                    ]}
                    style={{ cursor: 'pointer' }}
                    onClick={() => navigate(`/processes/${item.id}`)}
                  >
                    <List.Item.Meta
                      avatar={<FileOutlined style={{ fontSize: 24, color: tokens.colors.primary[500] }} />}
                      title={item.name}
                      description={
                        <Text type="secondary">
                          {item.totalCases.toLocaleString()} cases • {item.totalEvents.toLocaleString()} events • {formatRelativeTime(item.createdAt)}
                        </Text>
                      }
                    />
                  </List.Item>
                )}
              />
            ) : (
              <EmptyState
                icon={<FolderOutlined />}
                title="No event logs yet"
                description="Upload your first event log to start analyzing your process"
                actionLabel="Upload File"
                onAction={() => navigate('/processes/upload')}
              />
            )}
          </Card>
        </Col>

        {/* Quick Actions */}
        <Col xs={24} lg={8}>
          <Card title="Quick Actions">
            <div style={{ display: 'flex', flexDirection: 'column', gap: tokens.spacing[3] }}>
              <Button
                type="primary"
                icon={<UploadOutlined />}
                size="large"
                block
                onClick={() => navigate('/processes/upload')}
              >
                Upload Event Log
              </Button>
              <Button
                icon={<SearchOutlined />}
                size="large"
                block
                onClick={() => navigate('/explorer')}
              >
                Explore Processes
              </Button>
              <Button
                icon={<SettingOutlined />}
                size="large"
                block
                onClick={() => navigate('/settings')}
              >
                Settings
              </Button>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default HomePage;
