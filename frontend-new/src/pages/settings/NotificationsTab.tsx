import React, { useState, useEffect } from 'react';
import { Card, Form, Switch, Button, Space, Divider, Typography } from 'antd';
import { tokens, toast } from '@lumina/design-system';
import { createLogger } from '../../utils/logger';

const log = createLogger('Settings');
const { Text } = Typography;

const STORAGE_KEY = 'lumina_notification_settings';

interface NotificationSettingsFormValues {
  emailProcessingComplete: boolean;
  emailWeeklySummary: boolean;
  emailProductUpdates: boolean;
  inAppDesktop: boolean;
  inAppSound: boolean;
}

const defaultSettings: NotificationSettingsFormValues = {
  emailProcessingComplete: true,
  emailWeeklySummary: true,
  emailProductUpdates: false,
  inAppDesktop: true,
  inAppSound: false,
};

interface ToggleRowProps {
  label: string;
  description: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}

function ToggleRow({ label, description, checked, onChange }: ToggleRowProps) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: `${tokens.spacing[3]}px 0` }}>
      <div>
        <Text strong>{label}</Text>
        <br />
        <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
          {description}
        </Text>
      </div>
      <Switch checked={checked} onChange={onChange} />
    </div>
  );
}

export function NotificationsTab() {
  const [settings, setSettings] = useState<NotificationSettingsFormValues>(defaultSettings);
  const [savedSettings, setSavedSettings] = useState<NotificationSettingsFormValues>(defaultSettings);
  const [isDirty, setIsDirty] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    // Load from localStorage
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setSettings(parsed);
        setSavedSettings(parsed);
        log.debug('Notification settings loaded from storage', parsed);
      } catch {
        log.warn('Failed to parse stored notification settings');
      }
    }
  }, []);

  const handleChange = (key: keyof NotificationSettingsFormValues, value: boolean) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
    setIsDirty(true);
  };

  const handleCancel = () => {
    setSettings(savedSettings);
    setIsDirty(false);
    log.info('Notification settings changes cancelled');
  };

  const handleSave = async () => {
    setIsSaving(true);
    log.info('Saving notification settings', settings);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 500));

    // Save to localStorage
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
    setSavedSettings(settings);
    
    toast.success('Notification settings saved');
    setIsDirty(false);
    setIsSaving(false);
    log.info('Notification settings saved successfully');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: tokens.spacing[6] }}>
      {/* Email Notifications */}
      <Card title="Email Notifications">
        <ToggleRow
          label="Processing complete"
          description="Get notified when file processing finishes"
          checked={settings.emailProcessingComplete}
          onChange={(checked) => handleChange('emailProcessingComplete', checked)}
        />
        <Divider style={{ margin: 0 }} />
        <ToggleRow
          label="Weekly summary"
          description="Receive a weekly digest of your activity"
          checked={settings.emailWeeklySummary}
          onChange={(checked) => handleChange('emailWeeklySummary', checked)}
        />
        <Divider style={{ margin: 0 }} />
        <ToggleRow
          label="Product updates"
          description="Learn about new features and improvements"
          checked={settings.emailProductUpdates}
          onChange={(checked) => handleChange('emailProductUpdates', checked)}
        />
      </Card>

      {/* In-App Notifications */}
      <Card title="In-App Notifications">
        <ToggleRow
          label="Desktop notifications"
          description="Show notifications in your desktop notification center"
          checked={settings.inAppDesktop}
          onChange={(checked) => handleChange('inAppDesktop', checked)}
        />
        <Divider style={{ margin: 0 }} />
        <ToggleRow
          label="Sound"
          description="Play a sound when you receive a notification"
          checked={settings.inAppSound}
          onChange={(checked) => handleChange('inAppSound', checked)}
        />
      </Card>

      {/* Actions */}
      <div>
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
      </div>
    </div>
  );
}

export default NotificationsTab;
