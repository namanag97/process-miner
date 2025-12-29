import React from 'react';
import { useParams } from 'react-router-dom';
import { Typography, Card, Row, Col, Statistic, Tag } from 'antd';
import { BulbOutlined, ThunderboltOutlined, AlertOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

const PredictionsPage: React.FC = () => {
  const { logId } = useParams<{ logId: string }>();

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ marginBottom: 4 }}>Predictive Monitoring</Title>
        <Text type="secondary">ML-powered predictions for log: {logId}</Text>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic
              title="Active Models"
              value={3}
              prefix={<BulbOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic
              title="Running Cases"
              value={42}
              prefix={<ThunderboltOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic
              title="At-Risk Cases"
              value={5}
              prefix={<AlertOutlined />}
              valueStyle={{ color: '#DE350B' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24}>
          <Card title="Case Predictions" extra={<a href="/predictions/studio">Open Studio</a>}>
            <Text type="secondary">Running case predictions will be displayed here</Text>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default PredictionsPage;
