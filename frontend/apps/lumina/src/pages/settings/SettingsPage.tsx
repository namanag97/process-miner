import React from 'react';
import { Typography, Card, Tabs, Form, Input, Button, Switch, Space } from 'antd';

const { Title, Text } = Typography;

const SettingsPage: React.FC = () => {
  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={3} style={{ marginBottom: 4 }}>Settings</Title>
        <Text type="secondary">Manage your workspace settings</Text>
      </div>

      <Card>
        <Tabs
          tabPosition="left"
          items={[
            {
              key: 'workspace',
              label: 'Workspace',
              children: (
                <div style={{ maxWidth: 500 }}>
                  <Form layout="vertical">
                    <Form.Item label="Workspace Name">
                      <Input defaultValue="My Workspace" />
                    </Form.Item>
                    <Form.Item label="Description">
                      <Input.TextArea rows={3} />
                    </Form.Item>
                    <Form.Item>
                      <Button type="primary">Save Changes</Button>
                    </Form.Item>
                  </Form>
                </div>
              ),
            },
            {
              key: 'users',
              label: 'Users',
              children: (
                <div>
                  <Text type="secondary">User management coming soon</Text>
                </div>
              ),
            },
            {
              key: 'api',
              label: 'API Keys',
              children: (
                <div>
                  <Text type="secondary">API key management coming soon</Text>
                </div>
              ),
            },
            {
              key: 'preferences',
              label: 'Preferences',
              children: (
                <div style={{ maxWidth: 500 }}>
                  <Form layout="vertical">
                    <Form.Item label="Dark Mode">
                      <Switch />
                    </Form.Item>
                    <Form.Item label="Email Notifications">
                      <Switch defaultChecked />
                    </Form.Item>
                  </Form>
                </div>
              ),
            },
          ]}
        />
      </Card>
    </div>
  );
};

export default SettingsPage;
