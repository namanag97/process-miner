import React from 'react';
import { useParams } from 'react-router-dom';
import { Typography, Card, Row, Col } from 'antd';

const { Title, Text } = Typography;

const ResourcesPage: React.FC = () => {
  const { logId } = useParams<{ logId: string }>();

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ marginBottom: 4 }}>Resource Network</Title>
        <Text type="secondary">Organizational mining for log: {logId}</Text>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <Card title="Social Network Analysis" style={{ minHeight: 400 }}>
            <Text type="secondary">SNA graph visualization will be rendered here</Text>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="Resource Summary" extra={<a href={`/resources/${logId}/profiles`}>View Profiles</a>}>
            <Text type="secondary">Resource statistics will be displayed here</Text>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default ResourcesPage;
