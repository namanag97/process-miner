import React from 'react';
import { useParams, useSearchParams, Link } from 'react-router-dom';
import { Typography, Row, Col, Breadcrumb, Space, Button, Alert, Tabs } from 'antd';
import {
  HomeOutlined,
  BarChartOutlined,
  ArrowLeftOutlined,
  ClockCircleOutlined,
  ThunderboltOutlined,
  WarningOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import {
  KPIDashboard,
  BottleneckTable,
  CycleTimeChart,
  ThroughputChart,
  ReworkAnalysis,
} from '@lumina/analytics';

const { Title, Text } = Typography;

const AnalyticsPage: React.FC = () => {
  const { logId } = useParams<{ logId: string }>();
  const [searchParams] = useSearchParams();
  const logName = searchParams.get('name') || logId;

  if (!logId) {
    return (
      <Alert
        type="error"
        message="No log selected"
        description="Please select an event log to view analytics."
      />
    );
  }

  const tabItems = [
    {
      key: 'overview',
      label: (
        <Space>
          <BarChartOutlined />
          Overview
        </Space>
      ),
      children: (
        <Row gutter={[16, 16]}>
          {/* KPI Dashboard at the top */}
          <Col span={24}>
            <KPIDashboard logId={logId} />
          </Col>

          {/* Cycle Time and Throughput side by side */}
          <Col xs={24} lg={12}>
            <CycleTimeChart logId={logId} />
          </Col>
          <Col xs={24} lg={12}>
            <ThroughputChart logId={logId} />
          </Col>
        </Row>
      ),
    },
    {
      key: 'bottlenecks',
      label: (
        <Space>
          <WarningOutlined />
          Bottlenecks
        </Space>
      ),
      children: (
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <BottleneckTable logId={logId} />
          </Col>
        </Row>
      ),
    },
    {
      key: 'cycle-time',
      label: (
        <Space>
          <ClockCircleOutlined />
          Cycle Time
        </Space>
      ),
      children: (
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <CycleTimeChart logId={logId} />
          </Col>
        </Row>
      ),
    },
    {
      key: 'throughput',
      label: (
        <Space>
          <ThunderboltOutlined />
          Throughput
        </Space>
      ),
      children: (
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <ThroughputChart logId={logId} />
          </Col>
        </Row>
      ),
    },
    {
      key: 'rework',
      label: (
        <Space>
          <ReloadOutlined />
          Rework
        </Space>
      ),
      children: (
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <ReworkAnalysis logId={logId} />
          </Col>
        </Row>
      ),
    },
  ];

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
              <Space>
                <BarChartOutlined />
                Analytics
              </Space>
            ),
          },
        ]}
      />

      {/* Page Header */}
      <div style={{ marginBottom: 24 }}>
        <Space align="center" style={{ marginBottom: 8 }}>
          <Link to={`/explorer/${logId}?name=${encodeURIComponent(logName || '')}`}>
            <Button icon={<ArrowLeftOutlined />} type="text">
              Back to Explorer
            </Button>
          </Link>
        </Space>
        <Title level={3} style={{ marginBottom: 4 }}>
          <BarChartOutlined style={{ marginRight: 8 }} />
          Performance Analytics
        </Title>
        <Text type="secondary">
          Analyze performance metrics for: <strong>{logName}</strong>
        </Text>
      </div>

      {/* Tabbed Content */}
      <Tabs
        defaultActiveKey="overview"
        items={tabItems}
        size="large"
        style={{ marginTop: -8 }}
      />
    </div>
  );
};

export default AnalyticsPage;
