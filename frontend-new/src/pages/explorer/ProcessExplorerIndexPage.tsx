import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Input, Typography, Row, Col, Tag, Space } from 'antd';
import { SearchOutlined, FolderOpenOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { PageHeader, EmptyState, tokens } from '@lumina/design-system';
import { createLogger } from '../../utils/logger';

const log = createLogger('ProcessExplorerIndexPage');
const { Text, Title } = Typography;

// Mock event logs - same as EventLogsPage
const mockEventLogs = [
  {
    id: '1',
    name: 'Orders_2024.csv',
    totalCases: 1250,
    totalEvents: 45000,
    createdAt: '2024-12-28T10:30:00Z',
  },
  {
    id: '2',
    name: 'Claims_Process.xes',
    totalCases: 890,
    totalEvents: 23400,
    createdAt: '2024-12-27T14:15:00Z',
  },
  {
    id: '3',
    name: 'Purchase_Orders.csv',
    totalCases: 3200,
    totalEvents: 98000,
    createdAt: '2024-12-25T09:00:00Z',
  },
  {
    id: '4',
    name: 'Support_Tickets.csv',
    totalCases: 560,
    totalEvents: 8900,
    createdAt: '2024-12-20T16:45:00Z',
  },
];

interface EventLogSummary {
  id: string;
  name: string;
  totalCases: number;
  totalEvents: number;
  createdAt: string;
}

export function ProcessExplorerIndexPage() {
  const navigate = useNavigate();
  const [searchText, setSearchText] = useState('');

  log.debug('Rendering ProcessExplorerIndexPage');

  const filteredLogs = useMemo(() => {
    if (!searchText) return mockEventLogs;
    const lower = searchText.toLowerCase();
    return mockEventLogs.filter((log) => log.name.toLowerCase().includes(lower));
  }, [searchText]);

  const handleExplore = (logItem: EventLogSummary) => {
    log.info('Exploring log', { logId: logItem.id, name: logItem.name });
    navigate(`/explorer/${logItem.id}`);
  };

  return (
    <div>
      <PageHeader
        title="Process Explorer"
        description="Select an event log to visualize and explore your process"
      />

      {mockEventLogs.length > 0 ? (
        <>
          {/* Search Bar */}
          <div style={{ marginBottom: tokens.spacing[6] }}>
            <Input
              placeholder="Search event logs..."
              prefix={<SearchOutlined />}
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              allowClear
              style={{ maxWidth: 320 }}
            />
          </div>

          {/* Log Cards Grid */}
          <Row gutter={[16, 16]}>
            {filteredLogs.map((logItem) => (
              <Col xs={24} sm={12} lg={8} xl={6} key={logItem.id}>
                <Card
                  hoverable
                  onClick={() => handleExplore(logItem)}
                  style={{
                    borderRadius: tokens.radius.lg,
                    height: '100%',
                  }}
                  styles={{
                    body: {
                      display: 'flex',
                      flexDirection: 'column',
                      height: '100%',
                    },
                  }}
                >
                  <Space direction="vertical" size="small" style={{ width: '100%', flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <PlayCircleOutlined style={{ fontSize: 20, color: tokens.colors.primary[500] }} />
                      <Title level={5} style={{ margin: 0, flex: 1 }} ellipsis>
                        {logItem.name}
                      </Title>
                    </div>
                    
                    <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginTop: 8 }}>
                      <Tag color="blue">{logItem.totalCases.toLocaleString()} cases</Tag>
                      <Tag>{logItem.totalEvents.toLocaleString()} events</Tag>
                    </div>

                    <Text
                      type="secondary"
                      style={{ fontSize: tokens.fontSize.sm, marginTop: 'auto' }}
                    >
                      Click to explore process
                    </Text>
                  </Space>
                </Card>
              </Col>
            ))}
          </Row>

          {filteredLogs.length === 0 && (
            <EmptyState
              icon={<SearchOutlined />}
              title="No logs found"
              description={`No event logs match "${searchText}"`}
              actionLabel="Clear Search"
              onAction={() => setSearchText('')}
            />
          )}
        </>
      ) : (
        <EmptyState
          icon={<FolderOpenOutlined />}
          title="No event logs available"
          description="Upload an event log first to start exploring your process"
          actionLabel="Upload File"
          onAction={() => navigate('/processes/upload')}
        />
      )}
    </div>
  );
}

export default ProcessExplorerIndexPage;
