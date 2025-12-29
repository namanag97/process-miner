import React, { useState } from 'react';
import { Button, Drawer, Space, Typography, Divider, Tag, Switch, message } from 'antd';
import {
  BugOutlined,
  ClearOutlined,
  ReloadOutlined,
  ApiOutlined,
  DatabaseOutlined,
} from '@ant-design/icons';
import { useQueryClient } from '@tanstack/react-query';
import { devLog } from './logger';

const { Text, Title } = Typography;

// Only show in development
const isDev = import.meta.env.DEV || import.meta.env.VITE_DEV_PANEL === 'true';

export const DevPanel: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [mockMode, setMockMode] = useState(import.meta.env.VITE_MOCK === 'true');
  const queryClient = useQueryClient();

  if (!isDev) {
    return null;
  }

  const handleClearCache = () => {
    queryClient.clear();
    devLog.info('DevPanel', 'Query cache cleared');
    message.success('Cache cleared');
  };

  const handleRefreshAll = () => {
    queryClient.invalidateQueries();
    devLog.info('DevPanel', 'All queries invalidated');
    message.success('Queries refreshed');
  };

  const handleToggleMock = (checked: boolean) => {
    setMockMode(checked);
    devLog.info('DevPanel', `Mock mode ${checked ? 'enabled' : 'disabled'}`);
    message.info(`Mock mode ${checked ? 'enabled' : 'disabled'}. Refresh page to apply.`);
  };

  const handleTriggerError = () => {
    devLog.error('DevPanel', 'Test error triggered');
    throw new Error('Test error from DevPanel');
  };

  return (
    <>
      {/* Floating trigger button */}
      <Button
        type="primary"
        icon={<BugOutlined />}
        onClick={() => setOpen(true)}
        style={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          zIndex: 1000,
          boxShadow: '0 4px 12px rgba(0, 82, 204, 0.4)',
        }}
      />

      {/* Dev tools drawer */}
      <Drawer
        title={
          <Space>
            <BugOutlined />
            <span>Dev Tools</span>
            <Tag color="blue">DEV</Tag>
          </Space>
        }
        placement="right"
        onClose={() => setOpen(false)}
        open={open}
        width={360}
      >
        {/* Environment Info */}
        <div>
          <Title level={5}>Environment</Title>
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Text type="secondary">API URL</Text>
              <Text code>{import.meta.env.VITE_API_URL || 'localhost:8001'}</Text>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Text type="secondary">Mode</Text>
              <Tag color={import.meta.env.DEV ? 'green' : 'blue'}>
                {import.meta.env.DEV ? 'Development' : 'Production'}
              </Tag>
            </div>
          </Space>
        </div>

        <Divider />

        {/* Cache Controls */}
        <div>
          <Title level={5}>
            <DatabaseOutlined /> Query Cache
          </Title>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Button
              icon={<ClearOutlined />}
              onClick={handleClearCache}
              block
            >
              Clear Cache
            </Button>
            <Button
              icon={<ReloadOutlined />}
              onClick={handleRefreshAll}
              block
            >
              Refresh All Queries
            </Button>
          </Space>
        </div>

        <Divider />

        {/* Mock Mode */}
        <div>
          <Title level={5}>
            <ApiOutlined /> API Settings
          </Title>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Text>Mock Mode</Text>
            <Switch checked={mockMode} onChange={handleToggleMock} />
          </div>
          <Text type="secondary" style={{ fontSize: 12, marginTop: 8, display: 'block' }}>
            Enable mock mode for offline development
          </Text>
        </div>

        <Divider />

        {/* Testing */}
        <div>
          <Title level={5}>Testing</Title>
          <Button
            danger
            icon={<BugOutlined />}
            onClick={handleTriggerError}
            block
          >
            Trigger Test Error
          </Button>
        </div>

        <Divider />

        {/* Logs Info */}
        <div>
          <Title level={5}>Logging</Title>
          <Text type="secondary" style={{ fontSize: 12 }}>
            Logs are written to:
          </Text>
          <Text code style={{ display: 'block', marginTop: 4, fontSize: 11 }}>
            frontend/dev-logs/YYYY-MM-DD.log
          </Text>
        </div>
      </Drawer>
    </>
  );
};

export default DevPanel;
