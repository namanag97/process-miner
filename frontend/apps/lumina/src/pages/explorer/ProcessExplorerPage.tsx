import React, { useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Typography, Card, Row, Col, Tabs, Button, Space, Skeleton, Alert } from 'antd';
import { SettingOutlined, DownloadOutlined, FullscreenOutlined } from '@ant-design/icons';
import {
  ProcessMap,
  FilterPanel,
  ActivityDetails,
  useDFG,
  type FilterState,
} from '@lumina/process-explorer';
import { useLog } from '@lumina/data-hub';
import type { DFGNode, DFGEdge } from 'process-mining-sdk';

const { Title, Text } = Typography;

const ProcessExplorerPage: React.FC = () => {
  const { logId } = useParams<{ logId: string }>();
  const navigate = useNavigate();

  const { data: log, isLoading: logLoading } = useLog(logId || '');
  const { data: dfgData } = useDFG(logId || '');

  const [selectedActivity, setSelectedActivity] = useState<DFGNode | null>(null);
  const [filters, setFilters] = useState<FilterState>({
    activities: [],
    timeRange: null,
    variants: [],
    durationRange: null,
  });

  // Find edges for selected activity
  const incomingEdges = dfgData?.edges.filter((e) => e.target === selectedActivity?.id) || [];
  const outgoingEdges = dfgData?.edges.filter((e) => e.source === selectedActivity?.id) || [];

  const handleNodeClick = useCallback((nodeId: string, data: DFGNode) => {
    setSelectedActivity(data);
  }, []);

  const handleEdgeClick = useCallback((edge: DFGEdge) => {
    // Could show edge details in the future
    console.log('Edge clicked:', edge);
  }, []);

  const handleActivityNavigation = useCallback((activityId: string) => {
    if (dfgData) {
      const activity = dfgData.nodes.find((n) => n.id === activityId);
      if (activity) {
        setSelectedActivity(activity);
      }
    }
  }, [dfgData]);

  const handleFilterChange = useCallback((newFilters: FilterState) => {
    setFilters(newFilters);
  }, []);

  if (!logId) {
    return (
      <Alert
        type="error"
        message="No log selected"
        description="Please select an event log to explore."
        action={<Button onClick={() => navigate('/data/logs')}>Go to Logs</Button>}
      />
    );
  }

  const tabItems = [
    {
      key: 'dfg',
      label: 'Directly-Follows Graph',
      children: (
        <Row gutter={16}>
          {/* Filter Panel */}
          <Col flex="280px">
            <Space direction="vertical" size={16} style={{ width: '100%' }}>
              <FilterPanel
                logId={logId}
                value={filters}
                onChange={handleFilterChange}
              />

              <ActivityDetails
                activity={selectedActivity}
                incomingEdges={incomingEdges}
                outgoingEdges={outgoingEdges}
                totalCases={dfgData?.total_cases || 0}
                onClose={() => setSelectedActivity(null)}
                onNavigateToActivity={handleActivityNavigation}
              />
            </Space>
          </Col>

          {/* Process Map */}
          <Col flex="1">
            <ProcessMap
              logId={logId}
              onNodeClick={handleNodeClick}
              onEdgeClick={handleEdgeClick}
              selectedActivities={filters.activities}
              style={{ height: 600 }}
            />
          </Col>
        </Row>
      ),
    },
    {
      key: 'variants',
      label: 'Variants',
      children: (
        <Card>
          <Text type="secondary">Variant analysis view - Coming soon</Text>
        </Card>
      ),
    },
    {
      key: 'petri',
      label: 'Petri Net',
      children: (
        <Card>
          <Text type="secondary">Petri Net visualization - Coming soon</Text>
        </Card>
      ),
    },
  ];

  return (
    <div>
      {/* Header */}
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          {logLoading ? (
            <Skeleton.Input active style={{ width: 200 }} />
          ) : (
            <>
              <Title level={3} style={{ marginBottom: 4 }}>Process Explorer</Title>
              <Text type="secondary">
                {log?.name || `Log: ${logId}`}
                {dfgData && (
                  <span style={{ marginLeft: 16 }}>
                    {dfgData.nodes.length} activities &bull; {dfgData.edges.length} transitions &bull;{' '}
                    {dfgData.total_cases.toLocaleString()} cases
                  </span>
                )}
              </Text>
            </>
          )}
        </div>
        <Space>
          <Button icon={<DownloadOutlined />}>Export</Button>
          <Button icon={<FullscreenOutlined />}>Fullscreen</Button>
          <Button icon={<SettingOutlined />}>Settings</Button>
        </Space>
      </div>

      {/* Tabs */}
      <Tabs items={tabItems} defaultActiveKey="dfg" />
    </div>
  );
};

export default ProcessExplorerPage;
