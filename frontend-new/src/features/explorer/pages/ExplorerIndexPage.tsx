/**
 * ExplorerIndexPage - Process Selection for Exploration
 *
 * Lists available event logs for the user to select and explore.
 */

import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Input, Typography, Row, Col, Tag, Space, Button, Alert } from 'antd';
import { SearchOutlined, FolderOpenOutlined, PlayCircleOutlined, ReloadOutlined } from '@ant-design/icons';
import { PageHeader, EmptyState, tokens, logAction } from '@lumina/design-system';
import { FeaturePage } from '../../../core/components/FeaturePage';
import { useEventLogsList } from '../hooks';
import { createLogger } from '../../../utils/logger';

const log = createLogger('ExplorerIndexPage');
const { Text, Title } = Typography;

export function ExplorerIndexPage() {
  const navigate = useNavigate();
  const [searchText, setSearchText] = useState('');

  // Fetch logs using feature hook
  const { data, isLoading, error, refetch } = useEventLogsList({ pageSize: 50 });

  const logs = Array.isArray(data?.items) ? data.items : [];

  log.debug('Rendering ExplorerIndexPage', { logCount: logs.length, isLoading });

  const filteredLogs = useMemo(() => {
    if (!searchText) return logs;
    const lower = searchText.toLowerCase();
    return logs.filter((logItem) => logItem.name.toLowerCase().includes(lower));
  }, [logs, searchText]);

  const handleExplore = (logItem: { id: string; name: string }) => {
    logAction('ExplorerIndexPage', 'explore_clicked', { logId: logItem.id, name: logItem.name });
    log.info('Exploring log', { logId: logItem.id, name: logItem.name });
    navigate(`/explorer/${logItem.id}`);
  };

  return (
    <FeaturePage
      title="Process Explorer"
      breadcrumb={[
        { label: 'Workspace', href: '/workspace' },
        { label: 'Process Explorer' },
      ]}
      isLoading={isLoading}
      error={error}
      onRetry={() => { refetch(); }}
      isEmpty={!isLoading && logs.length === 0}
      emptyState={{
        icon: <FolderOpenOutlined />,
        title: 'No event logs available',
        description: 'Upload an event log first to start exploring your process',
        actionLabel: 'Upload File',
        onAction: () => navigate('/workspace'),
      }}
    >
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
        {filteredLogs.map((logItem, index) => (
          <Col
            xs={24}
            sm={12}
            lg={8}
            xl={6}
            key={logItem.id}
            className={`animate-fade-in-up stagger-${Math.min(index + 1, 6)}`}
          >
            <Card
              hoverable
              onClick={() => handleExplore(logItem)}
              className="card-hover-lift"
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

      {filteredLogs.length === 0 && searchText && (
        <EmptyState
          icon={<SearchOutlined />}
          title="No logs found"
          description={`No event logs match "${searchText}"`}
          actionLabel="Clear Search"
          onAction={() => setSearchText('')}
        />
      )}
    </FeaturePage>
  );
}

export default ExplorerIndexPage;
