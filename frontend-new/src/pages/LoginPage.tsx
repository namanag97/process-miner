import React, { useState } from 'react';
import { Card, Input, Button, Typography, Divider, ConfigProvider } from 'antd';
import { MailOutlined, LockOutlined } from '@ant-design/icons';
import { useAuth } from '../context/AuthContext';
import { luminaTheme, tokens } from '@lumina/design-system';

const { Title, Text } = Typography;

export function LoginPage() {
  const { login, loginAsGuest } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ConfigProvider theme={luminaTheme}>
      <div
        style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: tokens.colors.neutral[100],
        }}
      >
        <Card
          style={{
            width: 400,
            borderRadius: tokens.radius.lg,
            boxShadow: tokens.shadow.lg,
          }}
        >
          <div style={{ textAlign: 'center', marginBottom: tokens.spacing[6] }}>
            <div
              style={{
                width: 48,
                height: 48,
                borderRadius: tokens.radius.lg,
                background: tokens.colors.primary[500],
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 16px',
              }}
            >
              <span style={{ color: 'white', fontWeight: 700, fontSize: 20 }}>PM</span>
            </div>
            <Title level={3} style={{ margin: 0 }}>
              Process Miner
            </Title>
            <Text type="secondary">Sign in to continue</Text>
          </div>

          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: tokens.spacing[4] }}>
              <Input
                size="large"
                placeholder="Email"
                prefix={<MailOutlined style={{ color: tokens.colors.neutral[400] }} />}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div style={{ marginBottom: tokens.spacing[6] }}>
              <Input.Password
                size="large"
                placeholder="Password"
                prefix={<LockOutlined style={{ color: tokens.colors.neutral[400] }} />}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <Button
              type="primary"
              size="large"
              block
              htmlType="submit"
              loading={loading}
            >
              Sign In
            </Button>
          </form>

          <Divider>or</Divider>

          <Button
            size="large"
            block
            onClick={loginAsGuest}
          >
            Continue as Guest
          </Button>

          <Text
            type="secondary"
            style={{
              display: 'block',
              textAlign: 'center',
              marginTop: tokens.spacing[4],
              fontSize: tokens.fontSize.xs,
            }}
          >
            Mock auth: any email/password works
          </Text>
        </Card>
      </div>
    </ConfigProvider>
  );
}

export default LoginPage;
