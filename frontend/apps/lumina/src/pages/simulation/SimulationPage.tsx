import React from 'react';
import { useParams } from 'react-router-dom';
import { Typography, Card, Row, Col } from 'antd';

const { Title, Text } = Typography;

const SimulationPage: React.FC = () => {
  const { logId } = useParams<{ logId: string }>();

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ marginBottom: 4 }}>Simulation Lab</Title>
        <Text type="secondary">What-if analysis for log: {logId}</Text>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="Scenario Builder" style={{ minHeight: 300 }}>
            <Text type="secondary">Scenario configuration will be rendered here</Text>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Simulation Results" style={{ minHeight: 300 }}>
            <Text type="secondary">Comparison results will be displayed here</Text>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default SimulationPage;
