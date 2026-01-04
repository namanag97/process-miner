import { useState, useEffect } from 'react';
import { Card, Form, Select, Switch, Button, Space, Divider, Typography } from 'antd';
import { tokens, toast } from '@lumina/design-system';
import { createLogger } from '../../utils/logger';

const log = createLogger('Settings');
const { Text } = Typography;

const STORAGE_KEY = 'lumina_preferences';

interface PreferencesFormValues {
  theme: 'light' | 'dark' | 'system';
  dateFormat: string;
  timezone: string;
  shareUsageData: boolean;
  keyboardShortcuts: boolean;
}

const defaultPreferences: PreferencesFormValues = {
  theme: 'system',
  dateFormat: 'DD/MM/YYYY',
  timezone: 'UTC',
  shareUsageData: false,
  keyboardShortcuts: true,
};

const themeOptions = [
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
  { value: 'system', label: 'System default' },
];

const dateFormatOptions = [
  { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY (31/12/2024)' },
  { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY (12/31/2024)' },
  { value: 'YYYY-MM-DD', label: 'YYYY-MM-DD (2024-12-31)' },
];

const timezoneOptions = [
  { value: 'UTC', label: 'UTC (Coordinated Universal Time)' },
  { value: 'America/New_York', label: 'Eastern Time (ET)' },
  { value: 'America/Los_Angeles', label: 'Pacific Time (PT)' },
  { value: 'Europe/London', label: 'London (GMT/BST)' },
  { value: 'Europe/Paris', label: 'Central European Time (CET)' },
  { value: 'Asia/Tokyo', label: 'Japan Standard Time (JST)' },
  { value: 'Asia/Kolkata', label: 'India Standard Time (IST)' },
  { value: 'Australia/Sydney', label: 'Australian Eastern Time (AET)' },
];

export function PreferencesTab() {
  const [form] = Form.useForm<PreferencesFormValues>();
  const [isDirty, setIsDirty] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [savedPreferences, setSavedPreferences] = useState<PreferencesFormValues>(defaultPreferences);

  useEffect(() => {
    // Load from localStorage
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setSavedPreferences(parsed);
        form.setFieldsValue(parsed);
        log.debug('Preferences loaded from storage', parsed);
      } catch {
        log.warn('Failed to parse stored preferences');
        form.setFieldsValue(defaultPreferences);
      }
    } else {
      form.setFieldsValue(defaultPreferences);
    }
  }, [form]);

  const handleValuesChange = () => {
    setIsDirty(true);
  };

  const handleCancel = () => {
    form.setFieldsValue(savedPreferences);
    setIsDirty(false);
    log.info('Preferences changes cancelled');
  };

  const handleSave = async () => {
    setIsSaving(true);
    const values = form.getFieldsValue();
    log.info('Saving preferences', values);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 500));

    // Save to localStorage
    localStorage.setItem(STORAGE_KEY, JSON.stringify(values));
    setSavedPreferences(values);

    toast.success('Preferences saved successfully');
    setIsDirty(false);
    setIsSaving(false);
    log.info('Preferences saved successfully');
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: tokens.spacing[6] }}>
      {/* Display Settings */}
      <Card title="Display">
        <Form
          form={form}
          layout="vertical"
          onValuesChange={handleValuesChange}
          style={{ maxWidth: 480 }}
        >
          <Form.Item name="theme" label="Theme">
            <Select options={themeOptions} size="large" />
          </Form.Item>

          <Form.Item name="dateFormat" label="Date Format">
            <Select options={dateFormatOptions} size="large" />
          </Form.Item>

          <Form.Item name="timezone" label="Time Zone">
            <Select
              options={timezoneOptions}
              size="large"
              showSearch
              filterOption={(input, option) =>
                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
            />
          </Form.Item>
        </Form>
      </Card>

      {/* Privacy Settings */}
      <Card title="Data & Privacy">
        <Form
          form={form}
          layout="vertical"
          onValuesChange={handleValuesChange}
        >
          <Form.Item
            name="shareUsageData"
            valuePropName="checked"
            style={{ marginBottom: tokens.spacing[4] }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <Text strong>Share anonymous usage data</Text>
                <br />
                <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
                  Help us improve by sharing anonymous usage statistics
                </Text>
              </div>
              <Switch checked={form.getFieldValue('shareUsageData')} onChange={(checked) => {
                form.setFieldValue('shareUsageData', checked);
                setIsDirty(true);
              }} />
            </div>
          </Form.Item>

          <Divider style={{ margin: `${tokens.spacing[3]}px 0` }} />

          <Form.Item
            name="keyboardShortcuts"
            valuePropName="checked"
            style={{ marginBottom: 0 }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <Text strong>Enable keyboard shortcuts</Text>
                <br />
                <Text type="secondary" style={{ fontSize: tokens.fontSize.sm }}>
                  Use keyboard shortcuts for faster navigation
                </Text>
              </div>
              <Switch checked={form.getFieldValue('keyboardShortcuts')} onChange={(checked) => {
                form.setFieldValue('keyboardShortcuts', checked);
                setIsDirty(true);
              }} />
            </div>
          </Form.Item>
        </Form>
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

export default PreferencesTab;
