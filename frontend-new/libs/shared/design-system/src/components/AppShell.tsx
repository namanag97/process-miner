import React, { useState } from 'react';
import { Layout, Menu, Button, Tooltip, Avatar, ConfigProvider } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  HomeOutlined,
  FolderOutlined,
  SearchOutlined,
  BarChartOutlined,
  RobotOutlined,
  ExperimentOutlined,
  SettingOutlined,
  QuestionCircleOutlined,
  BellOutlined,
  UserOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { luminaTheme, tokens } from '../theme';

const { Sider, Content, Header } = Layout;

export interface NavItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  href?: string;
  onClick?: () => void;
  children?: NavItem[];
  badge?: number;
}

export interface AppShellProps {
  children: React.ReactNode;
  logo?: React.ReactNode;
  logoCollapsed?: React.ReactNode;
  navItems?: NavItem[];
  activeId?: string;
  onNavigate?: (id: string) => void;
  userName?: string;
  userEmail?: string;
  userAvatar?: string;
  notificationCount?: number;
}

// Default navigation items per Information Architecture
const defaultNavItems: NavItem[] = [
  { id: 'home', label: 'Home', icon: <HomeOutlined /> },
  { id: 'logs', label: 'Event Logs', icon: <FolderOutlined /> },
  { id: 'explorer', label: 'Process Explorer', icon: <SearchOutlined /> },
  { id: 'analytics', label: 'Analytics', icon: <BarChartOutlined /> },
  { id: 'ai-insights', label: 'AI Insights', icon: <RobotOutlined /> },
  { id: 'predictions', label: 'Predictions', icon: <ExperimentOutlined /> },
];

const bottomNavItems: NavItem[] = [
  { id: 'settings', label: 'Settings', icon: <SettingOutlined /> },
  { id: 'help', label: 'Help', icon: <QuestionCircleOutlined /> },
];

/**
 * AppShell - Main application layout with collapsible sidebar
 * 
 * Implements the layout from INFORMATION_ARCHITECTURE.md:
 * - 240px sidebar (64px collapsed)
 * - Light gray sidebar background (#F3F4F6)
 * - Navigation with sections
 * - User profile at bottom
 */
export function AppShell({
  children,
  logo,
  logoCollapsed,
  navItems = defaultNavItems,
  activeId,
  onNavigate,
  userName = 'User',
  userEmail = 'user@example.com',
  userAvatar,
  notificationCount = 0,
}: AppShellProps) {
  const [collapsed, setCollapsed] = useState(false);

  // Build menu items
  const mainMenuItems: MenuProps['items'] = [
    {
      type: 'group',
      label: !collapsed ? 'MAIN' : undefined,
      children: navItems.slice(0, 4).map((item) => ({
        key: item.id,
        icon: item.icon,
        label: item.label,
        onClick: () => onNavigate?.(item.id),
      })),
    },
    {
      type: 'group',
      label: !collapsed ? 'AI & ADVANCED' : undefined,
      children: navItems.slice(4).map((item) => ({
        key: item.id,
        icon: item.icon,
        label: item.label,
        onClick: () => onNavigate?.(item.id),
      })),
    },
  ];

  const bottomMenuItems: MenuProps['items'] = [
    {
      type: 'group',
      label: !collapsed ? 'SYSTEM' : undefined,
      children: bottomNavItems.map((item) => ({
        key: item.id,
        icon: item.icon,
        label: item.label,
        onClick: () => onNavigate?.(item.id),
      })),
    },
  ];

  const siderStyle: React.CSSProperties = {
    overflow: 'auto',
    height: '100vh',
    position: 'fixed',
    left: 0,
    top: 0,
    bottom: 0,
    background: tokens.colors.surface.sidebar,
    borderRight: `1px solid ${tokens.colors.neutral[200]}`,
  };

  return (
    <ConfigProvider theme={luminaTheme}>
      <Layout style={{ minHeight: '100vh' }}>
        <Sider
          collapsible
          collapsed={collapsed}
          onCollapse={setCollapsed}
          width={tokens.sidebar.width}
          collapsedWidth={tokens.sidebar.collapsedWidth}
          trigger={null}
          style={siderStyle}
        >
          {/* Logo */}
          <div
            style={{
              height: 56,
              display: 'flex',
              alignItems: 'center',
              justifyContent: collapsed ? 'center' : 'flex-start',
              padding: collapsed ? 0 : '0 16px',
              borderBottom: `1px solid ${tokens.colors.neutral[200]}`,
            }}
          >
            {collapsed ? (
              logoCollapsed || (
                <div style={{ fontWeight: 700, fontSize: 20, color: tokens.colors.primary[500] }}>
                  PM
                </div>
              )
            ) : (
              logo || (
                <div style={{ fontWeight: 600, fontSize: 16, color: tokens.colors.neutral[800] }}>
                  Process Miner
                </div>
              )
            )}
          </div>

          {/* Main Navigation */}
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', height: 'calc(100% - 56px)' }}>
            <Menu
              mode="inline"
              selectedKeys={activeId ? [activeId] : []}
              items={mainMenuItems}
              style={{
                border: 'none',
                background: 'transparent',
              }}
            />

            {/* Spacer */}
            <div style={{ flex: 1 }} />

            {/* Bottom Navigation */}
            <Menu
              mode="inline"
              selectedKeys={activeId ? [activeId] : []}
              items={bottomMenuItems}
              style={{
                border: 'none',
                background: 'transparent',
              }}
            />

            {/* Notification Bell */}
            <div
              style={{
                padding: '8px 12px',
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                cursor: 'pointer',
              }}
              onClick={() => onNavigate?.('notifications')}
            >
              <Tooltip title="Notifications" placement="right">
                <div style={{ position: 'relative' }}>
                  <BellOutlined style={{ fontSize: 20, color: tokens.colors.neutral[500] }} />
                  {notificationCount > 0 && (
                    <span
                      style={{
                        position: 'absolute',
                        top: -4,
                        right: -4,
                        background: tokens.colors.error[500],
                        color: 'white',
                        fontSize: 10,
                        borderRadius: '50%',
                        width: 16,
                        height: 16,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      {notificationCount}
                    </span>
                  )}
                </div>
              </Tooltip>
              {!collapsed && (
                <span style={{ color: tokens.colors.neutral[600], fontSize: 14 }}>
                  Notifications
                </span>
              )}
            </div>

            {/* User Profile */}
            <div
              style={{
                padding: '12px',
                borderTop: `1px solid ${tokens.colors.neutral[200]}`,
                display: 'flex',
                alignItems: 'center',
                gap: 12,
              }}
            >
              <Tooltip title={collapsed ? userName : undefined} placement="right">
                <Avatar
                  src={userAvatar}
                  icon={!userAvatar ? <UserOutlined /> : undefined}
                  size={32}
                  style={{ background: tokens.colors.primary[500] }}
                />
              </Tooltip>
              {!collapsed && (
                <div style={{ overflow: 'hidden' }}>
                  <div
                    style={{
                      fontWeight: 500,
                      fontSize: 14,
                      color: tokens.colors.neutral[800],
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                    }}
                  >
                    {userName}
                  </div>
                  <div
                    style={{
                      fontSize: 12,
                      color: tokens.colors.neutral[500],
                      whiteSpace: 'nowrap',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                    }}
                  >
                    {userEmail}
                  </div>
                </div>
              )}
            </div>

            {/* Collapse Toggle */}
            <Tooltip title={collapsed ? 'Expand' : 'Collapse'} placement="right">
              <Button
                type="text"
                icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
                onClick={() => setCollapsed(!collapsed)}
                style={{
                  margin: '8px 12px',
                  color: tokens.colors.neutral[500],
                }}
              />
            </Tooltip>
          </div>
        </Sider>

        <Layout
          style={{
            marginLeft: collapsed ? tokens.sidebar.collapsedWidth : tokens.sidebar.width,
            transition: 'margin-left 0.2s',
          }}
        >
          <Header
            style={{
              padding: '0 24px',
              background: tokens.colors.neutral[0],
              borderBottom: `1px solid ${tokens.colors.neutral[200]}`,
              display: 'flex',
              alignItems: 'center',
              position: 'sticky',
              top: 0,
              zIndex: 10,
              height: 56,
            }}
          >
            {/* Header content can be passed as a prop or rendered here */}
          </Header>
          <Content
            style={{
              padding: 24,
              minHeight: 'calc(100vh - 56px)',
              background: tokens.colors.surface.page,
            }}
          >
            {children}
          </Content>
        </Layout>
      </Layout>
    </ConfigProvider>
  );
}

export default AppShell;
