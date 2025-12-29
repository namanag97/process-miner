import React from 'react';
import { useParams } from 'react-router-dom';
import { Typography, Card } from 'antd';

const { Title, Text } = Typography;

const ResourceProfilesPage: React.FC = () => {
  const { logId } = useParams<{ logId: string }>();

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ marginBottom: 4 }}>Resource Profiles</Title>
        <Text type="secondary">Individual resource analysis for log: {logId}</Text>
      </div>

      <Card style={{ minHeight: 400 }}>
        <Text type="secondary">Resource profile cards will be displayed here</Text>
      </Card>
    </div>
  );
};

export default ResourceProfilesPage;
