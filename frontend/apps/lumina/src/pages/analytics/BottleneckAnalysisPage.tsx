import React, { useState } from 'react';
import { useParams, useSearchParams, Link } from 'react-router-dom';
import { Typography, Row, Col, Breadcrumb, Space, Button, Alert, Card, Drawer } from 'antd';
import {
  HomeOutlined,
  WarningOutlined,
  ArrowLeftOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons';
import {
  BottleneckTable,
  KPIDashboard,
  useBottlenecks,
} from '@lumina/analytics';

const { Title, Text, Paragraph } = Typography;

const BottleneckAnalysisPage: React.FC = () => {
  const { logId } = useParams<{ logId: string }>();
  const [searchParams] = useSearchParams();
  const logName = searchParams.get('name') || logId;
  const [selectedActivity, setSelectedActivity] = useState<string | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const { data: bottleneckData } = useBottlenecks(logId || '');

  if (!logId) {
    return (
      <Alert
        type="error"
        message="No log selected"
        description="Please select an event log to analyze bottlenecks."
      />
    );
  }

  const handleActivityClick = (activity: string) => {
    setSelectedActivity(activity);
    setDrawerOpen(true);
  };

  const selectedBottleneck = bottleneckData?.bottlenecks?.find(
    (b) => b.activity === selectedActivity
  );

  return (
    <div>
      {/* Breadcrumb Navigation */}
      <Breadcrumb
        style={{ marginBottom: 16 }}
        items={[
          {
            title: (
              <Link to="/data-hub">
                <HomeOutlined /> Data Hub
              </Link>
            ),
          },
          {
            title: (
              <Link to={`/explorer/${logId}`}>
                Process Explorer
              </Link>
            ),
          },
          {
            title: (
              <Link to={`/analytics/${logId}`}>
                Analytics
              </Link>
            ),
          },
          {
            title: (
              <Space>
                <WarningOutlined />
                Bottlenecks
              </Space>
            ),
          },
        ]}
      />

      {/* Page Header */}
      <div style={{ marginBottom: 24 }}>
        <Space align="center" style={{ marginBottom: 8 }}>
          <Link to={`/analytics/${logId}?name=${encodeURIComponent(logName || '')}`}>
            <Button icon={<ArrowLeftOutlined />} type="text">
              Back to Analytics
            </Button>
          </Link>
        </Space>
        <Title level={3} style={{ marginBottom: 4 }}>
          <WarningOutlined style={{ marginRight: 8, color: '#faad14' }} />
          Bottleneck Analysis
        </Title>
        <Text type="secondary">
          Deep-dive into process bottlenecks for: <strong>{logName}</strong>
        </Text>
      </div>

      {/* KPI Summary */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={24}>
          <KPIDashboard logId={logId} compact />
        </Col>
      </Row>

      {/* Main Content */}
      <Row gutter={[16, 16]}>
        {/* Bottleneck Explanation */}
        <Col xs={24} lg={8}>
          <Card
            title={
              <Space>
                <InfoCircleOutlined style={{ color: '#0052cc' }} />
                Understanding Bottlenecks
              </Space>
            }
          >
            <Space direction="vertical" size="middle">
              <Paragraph style={{ margin: 0 }}>
                <Text strong>What is a bottleneck?</Text>
                <br />
                A bottleneck is an activity where work accumulates due to high
                waiting times. Cases spend more time waiting before this activity
                than at other points in the process.
              </Paragraph>

              <Paragraph style={{ margin: 0 }}>
                <Text strong>Severity Levels:</Text>
              </Paragraph>
              <ul style={{ margin: 0, paddingLeft: 20 }}>
                <li>
                  <Text type="danger">Critical:</Text> Highest waiting times,
                  immediate attention needed
                </li>
                <li>
                  <Text style={{ color: '#fa8c16' }}>High:</Text> Significant
                  delays, should be addressed
                </li>
                <li>
                  <Text style={{ color: '#faad14' }}>Medium:</Text> Notable delays,
                  monitor closely
                </li>
                <li>
                  <Text type="success">Low:</Text> Minor delays, acceptable
                </li>
              </ul>

              <Paragraph style={{ margin: 0 }}>
                <Text strong>Recommendations:</Text>
                <br />
                Click on any activity to see detailed recommendations for
                reducing wait times.
              </Paragraph>
            </Space>
          </Card>
        </Col>

        {/* Bottleneck Table */}
        <Col xs={24} lg={16}>
          <BottleneckTable
            logId={logId}
            onActivityClick={handleActivityClick}
          />
        </Col>
      </Row>

      {/* Activity Detail Drawer */}
      <Drawer
        title={
          <Space>
            <WarningOutlined style={{ color: '#faad14' }} />
            Activity: {selectedActivity}
          </Space>
        }
        placement="right"
        width={400}
        onClose={() => setDrawerOpen(false)}
        open={drawerOpen}
      >
        {selectedBottleneck && (
          <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <Card size="small" title="Metrics">
              <Space direction="vertical">
                <Text>
                  <strong>Waiting Time:</strong>{' '}
                  {(selectedBottleneck.waitingTime / 3600).toFixed(1)} hours
                </Text>
                <Text>
                  <strong>Frequency:</strong>{' '}
                  {selectedBottleneck.frequency.toLocaleString()} occurrences
                </Text>
              </Space>
            </Card>

            <Card size="small" title="Recommendations">
              <Space direction="vertical">
                <Paragraph>
                  <Text strong>1. Resource Allocation</Text>
                  <br />
                  Consider adding more resources to handle this activity during
                  peak times.
                </Paragraph>
                <Paragraph>
                  <Text strong>2. Process Automation</Text>
                  <br />
                  Evaluate if parts of this activity can be automated to reduce
                  processing time.
                </Paragraph>
                <Paragraph>
                  <Text strong>3. Workload Balancing</Text>
                  <br />
                  Distribute cases more evenly to prevent bottlenecks during
                  high-volume periods.
                </Paragraph>
              </Space>
            </Card>
          </Space>
        )}
      </Drawer>
    </div>
  );
};

export default BottleneckAnalysisPage;
