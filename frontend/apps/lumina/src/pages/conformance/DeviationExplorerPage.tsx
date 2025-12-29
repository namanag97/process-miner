import React from 'react';
import { useParams } from 'react-router-dom';
import { Typography, Card } from 'antd';

const { Title, Text } = Typography;

const DeviationExplorerPage: React.FC = () => {
  const { logId } = useParams<{ logId: string }>();

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ marginBottom: 4 }}>Deviation Explorer</Title>
        <Text type="secondary">Explore conformance deviations for log: {logId}</Text>
      </div>

      <Card style={{ minHeight: 400 }}>
        <Text type="secondary">Deviation details and case alignment will be rendered here</Text>
      </Card>
    </div>
  );
};

export default DeviationExplorerPage;
