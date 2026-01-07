import { useEffect } from 'react';
import { Tabs } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import { PageHeader, tokens, logAction } from '@/src/shared/design-system';
import { ProfileTab } from './ProfileTab';
import { PreferencesTab } from './PreferencesTab';
import { NotificationsTab } from './NotificationsTab';
import { createLogger } from '../../../../shared/lib/logger';

const log = createLogger('Settings');

const tabItems = [
  { key: 'profile', label: 'Profile', children: <ProfileTab /> },
  { key: 'preferences', label: 'Preferences', children: <PreferencesTab /> },
  { key: 'notifications', label: 'Notifications', children: <NotificationsTab /> },
];

export function SettingsPage() {
  const navigate = useNavigate();
  const location = useLocation();

  // Extract current tab from URL
  const currentTab = location.pathname.split('/').pop() || 'profile';
  const validTabs = ['profile', 'preferences', 'notifications'];
  const activeTab = validTabs.includes(currentTab) ? currentTab : 'profile';

  useEffect(() => {
    log.info('Settings page viewed', { tab: activeTab });
  }, [activeTab]);

  const handleTabChange = (key: string) => {
    logAction('SettingsPage', 'tab_changed', { from: activeTab, to: key });
    log.debug('Tab changed', { from: activeTab, to: key });
    navigate(`/settings/${key}`);
  };

  return (
    <div style={{ maxWidth: 800 }}>
      <PageHeader
        title="Settings"
        description="Manage your account settings and preferences"
      />

      <Tabs
        activeKey={activeTab}
        onChange={handleTabChange}
        items={tabItems}
        style={{ marginTop: tokens.spacing[4] }}
      />
    </div>
  );
}

export default SettingsPage;
