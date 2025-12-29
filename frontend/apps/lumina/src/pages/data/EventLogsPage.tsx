import React from 'react';
import { Typography, Button, Card } from 'antd';
import { UploadOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { LogList } from '@lumina/data-hub';

const { Title, Text } = Typography;

const EventLogsPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <Title level={3} style={{ marginBottom: 4 }}>Event Logs</Title>
          <Text type="secondary">Manage your event log data</Text>
        </div>
        <Button
          type="primary"
          icon={<UploadOutlined />}
          onClick={() => navigate('/data/upload')}
        >
          Upload Log
        </Button>
      </div>

      <Card>
        <LogList />
      </Card>
    </div>
  );
};

export default EventLogsPage;
