import React from 'react';
import { Typography, Card, Tabs } from 'antd';

const { Title, Text } = Typography;

const PredictionStudioPage: React.FC = () => {
  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ marginBottom: 4 }}>Prediction Studio</Title>
        <Text type="secondary">Train and manage ML models</Text>
      </div>

      <Card>
        <Tabs
          items={[
            {
              key: 'train',
              label: 'Train Model',
              children: (
                <div style={{ minHeight: 300 }}>
                  <Text type="secondary">Model training wizard will be rendered here</Text>
                </div>
              ),
            },
            {
              key: 'models',
              label: 'My Models',
              children: (
                <div style={{ minHeight: 300 }}>
                  <Text type="secondary">Trained models list will be displayed here</Text>
                </div>
              ),
            },
            {
              key: 'predictions',
              label: 'Predictions',
              children: (
                <div style={{ minHeight: 300 }}>
                  <Text type="secondary">Prediction results will be shown here</Text>
                </div>
              ),
            },
          ]}
        />
      </Card>
    </div>
  );
};

export default PredictionStudioPage;
