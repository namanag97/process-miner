import React from 'react';
import { useParams } from 'react-router-dom';
import { Typography, Card, Row, Col, Progress } from 'antd';

const { Title, Text } = Typography;

const ConformancePage: React.FC = () => {
  const { logId } = useParams<{ logId: string }>();

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ marginBottom: 4 }}>Conformance Checking</Title>
        <Text type="secondary">Check compliance for log: {logId}</Text>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12}>
          <Card title="Fitness Score">
            <Progress
              type="circle"
              percent={82}
              format={(percent) => `${percent}%`}
              strokeColor="#0052CC"
            />
            <div style={{ marginTop: 16 }}>
              <Text>10,234 fitting cases</Text>
              <br />
              <Text type="secondary">2,198 deviating cases</Text>
            </div>
          </Card>
        </Col>
        <Col xs={24} sm={12}>
          <Card title="Precision Score">
            <Progress
              type="circle"
              percent={96}
              format={(percent) => `${percent}%`}
              strokeColor="#36B37E"
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24}>
          <Card title="Top Deviations" extra={<a href={`/conformance/${logId}/deviations`}>View All</a>}>
            <Text type="secondary">Deviation table will be rendered here</Text>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default ConformancePage;
