import React from 'react';
import { Layout, Menu, ConfigProvider, Button, Tooltip } from 'antd';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { luminaTheme, luminaDarkTheme } from '../../theme';

const { Sider, Content, Header } = Layout;

export interface NavItem {
  id: string;
  label: string;
  icon?: React.ReactNode;
  href?: string;
  onClick?: () => void;
  children?: NavItem[];
}

export interface AppShellProps {
  children: React.ReactNode;
  logo?: React.ReactNode;
  logoCollapsed?: React.ReactNode;
  navItems: NavItem[];
  activeId?: string;
  collapsed?: boolean;
  onCollapse?: (collapsed: boolean) => void;
  footer?: React.ReactNode;
  header?: React.ReactNode;
  theme?: 'light' | 'dark';
  siderWidth?: number;
  collapsedWidth?: number;
}

/**
 * AppShell - Main application layout with collapsible sidebar
 * 
 * Provides a Celonis-inspired enterprise layout with:
 * - Collapsible sidebar navigation
 * - Customizable header and footer
 * - Light/dark theme support
 * - Compact spacing for high-density UIs
 */
export const AppShell: React.FC<AppShellProps> = ({
  children,
  logo,
  logoCollapsed,
  navItems,
  activeId,
  collapsed = false,
  onCollapse,
  footer,
  header,
  theme: themeMode = 'light',
  siderWidth = 260,
  collapsedWidth = 72,
}) => {
  const isDark = themeMode === 'dark';
  const currentTheme = isDark ? luminaDarkTheme : luminaTheme;

  // Convert NavItems to Ant Design Menu items
  const menuItems: MenuProps['items'] = navItems.map((item) => ({
    key: item.id,
    icon: item.icon,
    label: item.label,
    onClick: item.onClick,
    children: item.children?.map((child) => ({
      key: child.id,
      icon: child.icon,
      label: child.label,
      onClick: child.onClick,
    })),
  }));

  return (
    <ConfigProvider theme={currentTheme}>
      <Layout style={{ minHeight: '100vh' }}>
        <Sider
          collapsible
          collapsed={collapsed}
          onCollapse={onCollapse}
          width={siderWidth}
          collapsedWidth={collapsedWidth}
          trigger={null}
          style={{
            overflow: 'auto',
            height: '100vh',
            position: 'fixed',
            left: 0,
            top: 0,
            bottom: 0,
            zIndex: 100,
          }}
        >
          {/* Logo */}
          <div
            style={{
              height: 56,
              display: 'flex',
              alignItems: 'center',
              justifyContent: collapsed ? 'center' : 'flex-start',
              padding: collapsed ? '0' : '0 16px',
              borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
            }}
          >
            {collapsed ? (logoCollapsed || logo) : logo}
          </div>

          {/* Navigation */}
          <Menu
            theme="dark"
            mode="inline"
            selectedKeys={activeId ? [activeId] : []}
            items={menuItems}
            style={{ borderRight: 0, marginTop: 8 }}
          />

          {/* Footer */}
          {footer && (
            <div
              style={{
                position: 'absolute',
                bottom: 0,
                left: 0,
                right: 0,
                padding: collapsed ? '8px' : '12px',
                borderTop: '1px solid rgba(255, 255, 255, 0.1)',
              }}
            >
              {footer}
            </div>
          )}

          {/* Collapse trigger */}
          <Tooltip title={collapsed ? 'Expand' : 'Collapse'} placement="right">
            <Button
              type="text"
              icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => onCollapse?.(!collapsed)}
              style={{
                position: 'absolute',
                bottom: footer ? 60 : 16,
                left: '50%',
                transform: 'translateX(-50%)',
                color: 'rgba(255, 255, 255, 0.65)',
              }}
            />
          </Tooltip>
        </Sider>

        <Layout
          style={{
            marginLeft: collapsed ? collapsedWidth : siderWidth,
            transition: 'margin-left 0.2s',
          }}
        >
          {header && (
            <Header
              style={{
                padding: '0 24px',
                background: isDark ? '#141419' : '#FFFFFF',
                borderBottom: `1px solid ${isDark ? '#27272A' : '#DFE1E6'}`,
                display: 'flex',
                alignItems: 'center',
                position: 'sticky',
                top: 0,
                zIndex: 10,
              }}
            >
              {header}
            </Header>
          )}
          <Content
            style={{
              padding: 24,
              minHeight: 'calc(100vh - 56px)',
              background: isDark ? '#0A0A0F' : '#F4F5F7',
            }}
          >
            {children}
          </Content>
        </Layout>
      </Layout>
    </ConfigProvider>
  );
};

export default AppShell;
