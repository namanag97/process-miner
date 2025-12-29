import React from 'react';
import { Typography, Row, Col, Card, Statistic } from 'antd';
import {
  FileTextOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  WarningOutlined,
} from '@ant-design/icons';

const { Title, Text } = Typography;

const DashboardPage: React.FC = () => {
  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ marginBottom: 4 }}>Dashboard</Title>
        <Text type="secondary">Overview of your process mining workspace</Text>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Cases"
              value={125432}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#0052CC' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Active Logs"
              value={12}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Avg Cycle Time"
              value="4.2 days"
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Conformance Score"
              value={94.2}
              suffix="%"
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#36B37E' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} lg={12}>
          <Card title="Recent Event Logs" extra={<a href="/data/logs">View All</a>}>
            <Text type="secondary">No event logs uploaded yet. Get started by uploading your first log.</Text>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Alerts & Notifications" extra={<a href="#">View All</a>}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <WarningOutlined style={{ color: '#FAAD14' }} />
              <Text>No active alerts</Text>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DashboardPage;
