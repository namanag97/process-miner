/**
 * LoginPage - Authentication page for the MVP
 *
 * Supports login with email/password.
 * Stores JWT token in localStorage for subsequent API calls.
 */

import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Form, Input, Button, Card, Typography, Alert, Space, Divider } from 'antd';
import { UserOutlined, LockOutlined, LoginOutlined } from '@ant-design/icons';
import { sdk } from '@/api/sdk';

const { Title, Text, Link } = Typography;

interface LoginFormValues {
  email: string;
  password: string;
}

interface LocationState {
  from?: { pathname: string };
}

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Get redirect path from location state or default to workspace
  const from = (location.state as LocationState)?.from?.pathname || '/workspace';

  const handleLogin = async (values: LoginFormValues) => {
    setLoading(true);
    setError(null);

    try {
      // Call login API
      const response = await sdk.auth.login(values.email, values.password);

      // Store token in localStorage
      if (response.access_token) {
        localStorage.setItem('auth_token', response.access_token);
        if (response.refresh_token) {
          localStorage.setItem('refresh_token', response.refresh_token);
        }
      }

      // Navigate to the intended destination
      navigate(from, { replace: true });
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Login failed. Please check your credentials.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = () => {
    // Pre-fill form with demo credentials
    handleLogin({ email: 'analyst@example.com', password: 'TestPass123' });
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: 24,
      }}
    >
      <Card
        style={{
          width: '100%',
          maxWidth: 420,
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
          borderRadius: 12,
        }}
      >
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          {/* Header */}
          <div style={{ textAlign: 'center' }}>
            <Title level={2} style={{ marginBottom: 8 }}>
              ProcessMind
            </Title>
            <Text type="secondary">
              Sign in to your account to continue
            </Text>
          </div>

          {/* Error Alert */}
          {error && (
            <Alert
              message="Login Failed"
              description={error}
              type="error"
              showIcon
              closable
              onClose={() => setError(null)}
            />
          )}

          {/* Login Form */}
          <Form
            name="login"
            layout="vertical"
            onFinish={handleLogin}
            autoComplete="off"
            size="large"
            initialValues={{
              email: 'analyst@example.com',
              password: 'TestPass123',
            }}
          >
            <Form.Item
              name="email"
              label="Email"
              rules={[
                { required: true, message: 'Please enter your email' },
                { type: 'email', message: 'Please enter a valid email' },
              ]}
            >
              <Input
                prefix={<UserOutlined style={{ color: 'rgba(0,0,0,.25)' }} />}
                placeholder="analyst@example.com"
              />
            </Form.Item>

            <Form.Item
              name="password"
              label="Password"
              rules={[
                { required: true, message: 'Please enter your password' },
                { min: 6, message: 'Password must be at least 6 characters' },
              ]}
            >
              <Input.Password
                prefix={<LockOutlined style={{ color: 'rgba(0,0,0,.25)' }} />}
                placeholder="Enter your password"
              />
            </Form.Item>

            <Form.Item style={{ marginBottom: 12 }}>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                icon={<LoginOutlined />}
                block
              >
                Sign In
              </Button>
            </Form.Item>
          </Form>

          <Divider plain>
            <Text type="secondary">or</Text>
          </Divider>

          {/* Demo Login Button */}
          <Button
            onClick={handleDemoLogin}
            loading={loading}
            block
            style={{ marginBottom: 16 }}
          >
            Continue with Demo Account
          </Button>

          {/* Help Text */}
          <div style={{ textAlign: 'center' }}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              Demo credentials: analyst@example.com / TestPass123
            </Text>
          </div>

          {/* Footer Links */}
          <div style={{ textAlign: 'center' }}>
            <Space split={<span style={{ color: '#d9d9d9' }}>|</span>}>
              <Link href="#" style={{ fontSize: 12 }}>
                Forgot Password?
              </Link>
              <Link href="#" style={{ fontSize: 12 }}>
                Create Account
              </Link>
            </Space>
          </div>
        </Space>
      </Card>
    </div>
  );
}

export default LoginPage;
