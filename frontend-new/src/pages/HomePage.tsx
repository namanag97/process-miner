import React from 'react';
import { Row, Col, Card, Button, List, Typography } from 'antd';
import {
  UploadOutlined,
  SearchOutlined,
  SettingOutlined,
  FileOutlined,
  FolderOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { PageHeader, MetricCard, EmptyState, tokens } from '@lumina/design-system';
import { useAuth } from '../context/AuthContext';

const { Text } = Typography;

// Mock data for demo
const mockRecentLogs = [
  { id: '1', name: 'Orders_2024.csv', cases: 1250, events: 45000, uploaded: '2 hours ago' },
  { id: '2', name: 'Claims_Process.xes', cases: 890, events: 23400, uploaded: 'Yesterday' },
  { id: '3', name: 'Purchase_Orders.csv', cases: 3200, events: 98000, uploaded: '3 days ago' },
];

export function HomePage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  
  const hasLogs = mockRecentLogs.length > 0;

  return (
    <div>
      <PageHeader
        title={`Welcome back, ${user?.name || 'User'}`}
        description="Here's an overview of your process mining activity"
      />

      {/* Stats Row */}
      {hasLogs && (
        <Row gutter={16} style={{ marginBottom: tokens.spacing[6] }}>
          <Col xs={24} sm={8}>
            <MetricCard
              title="Event Logs"
              value={3}
              trend={{ value: 50, isPositive: true, label: 'this week' }}
            />
          </Col>
          <Col xs={24} sm={8}>
            <MetricCard
              title="Total Cases"
              value="5.3K"
              status="success"
            />
          </Col>
          <Col xs={24} sm={8}>
            <MetricCard
              title="Last Activity"
              value="2h ago"
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
              <Button type="link" onClick={() => navigate('/logs')}>
                View all
              </Button>
            }
            style={{ marginBottom: tokens.spacing[6] }}
          >
            {hasLogs ? (
              <List
                dataSource={mockRecentLogs}
                renderItem={(item) => (
                  <List.Item
                    actions={[
                      <Button
                        key="view"
                        type="link"
                        onClick={() => navigate(`/logs/${item.id}`)}
                      >
                        View
                      </Button>,
                    ]}
                    style={{ cursor: 'pointer' }}
                    onClick={() => navigate(`/logs/${item.id}`)}
                  >
                    <List.Item.Meta
                      avatar={<FileOutlined style={{ fontSize: 24, color: tokens.colors.primary[500] }} />}
                      title={item.name}
                      description={
                        <Text type="secondary">
                          {item.cases.toLocaleString()} cases • {item.events.toLocaleString()} events • {item.uploaded}
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
                onAction={() => navigate('/logs/upload')}
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
                onClick={() => navigate('/logs/upload')}
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
