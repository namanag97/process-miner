import { useState, useEffect } from 'react';
import { Card, Form, Input, Button, Avatar, Space, Typography, message } from 'antd';
import { UserOutlined, CameraOutlined } from '@ant-design/icons';
import { tokens, toast } from '@/src/shared/design-system';
import { useUser } from '../../../../shared/context/UserContext';
import { createLogger } from '../../../../shared/lib/logger';

const log = createLogger('Settings');
const { Text } = Typography;

interface ProfileFormValues {
  name: string;
  email: string;
}

export function ProfileTab() {
  const { user } = useUser();
  const [form] = Form.useForm<ProfileFormValues>();
  const [isDirty, setIsDirty] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (user) {
      form.setFieldsValue({
        name: user.name,
        email: user.email,
      });
      log.debug('Profile form initialized', { name: user.name, email: user.email });
    }
  }, [user, form]);

  const handleValuesChange = () => {
    setIsDirty(true);
  };

  const handleCancel = () => {
    form.setFieldsValue({
      name: user?.name || '',
      email: user?.email || '',
    });
    setIsDirty(false);
    log.info('Profile changes cancelled');
  };

  const handleSave = async () => {
    setIsSaving(true);
    log.info('Saving profile changes', form.getFieldsValue());

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 500));

    toast.success('Profile updated successfully');
    setIsDirty(false);
    setIsSaving(false);
    log.info('Profile saved successfully');
  };

  const handleAvatarChange = () => {
    message.info('Avatar upload is a demo feature');
    log.info('Avatar change attempted (mock)');
  };

  return (
    <Card title="Profile Information">
      <Form
        form={form}
        layout="vertical"
        onValuesChange={handleValuesChange}
        style={{ maxWidth: 480 }}
      >
        {/* Avatar Section */}
        <div style={{ marginBottom: tokens.spacing[6], display: 'flex', alignItems: 'center', gap: tokens.spacing[4] }}>
          <Avatar
            size={80}
            icon={<UserOutlined />}
            src={user?.avatar}
            style={{ backgroundColor: tokens.colors.primary[500] }}
          />
          <div>
            <Button icon={<CameraOutlined />} onClick={handleAvatarChange}>
              Change photo
            </Button>
            <div style={{ marginTop: tokens.spacing[1] }}>
              <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
                JPG, GIF or PNG. Max size 2MB
              </Text>
            </div>
          </div>
        </div>

        {/* Name Field */}
        <Form.Item
          name="name"
          label="Full Name"
          rules={[{ required: true, message: 'Please enter your name' }]}
        >
          <Input placeholder="Enter your name" size="large" />
        </Form.Item>

        {/* Email Field (Read-only) */}
        <Form.Item
          name="email"
          label="Email"
          extra={<Text type="secondary">Contact support to change your email</Text>}
        >
          <Input disabled size="large" />
        </Form.Item>

        {/* Actions */}
        <Form.Item style={{ marginBottom: 0, marginTop: tokens.spacing[6] }}>
          <Space>
            <Button onClick={handleCancel} disabled={!isDirty || isSaving}>
              Cancel
            </Button>
            <Button
              type="primary"
              onClick={handleSave}
              loading={isSaving}
              disabled={!isDirty}
            >
              Save Changes
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  );
}

export default ProfileTab;
