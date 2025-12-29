import React from 'react';
import { Typography } from 'antd';
import { UploadWizard } from '@lumina/data-hub';

const { Title, Text } = Typography;

const UploadPage: React.FC = () => {
  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ marginBottom: 4 }}>Upload Event Log</Title>
        <Text type="secondary">Import your event log data</Text>
      </div>

      <UploadWizard />
    </div>
  );
};

export default UploadPage;
