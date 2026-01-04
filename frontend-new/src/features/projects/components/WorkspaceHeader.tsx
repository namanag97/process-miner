/**
 * WorkspaceHeader - Header component showing workspace context and breadcrumbs
 */

import { Breadcrumb, Dropdown, Space, Typography, theme } from 'antd';
import { HomeOutlined, AppstoreOutlined, DownOutlined } from '@ant-design/icons';
import { Link, useLocation } from 'react-router-dom';
import { useWorkspace, type Workspace } from '../../../context/UserContext';
import type { MenuProps } from 'antd';

const { Text } = Typography;

interface WorkspaceHeaderProps {
  /**
   * Additional breadcrumb items after the workspace
   */
  breadcrumbItems?: Array<{
    title: string;
    path?: string;
  }>;
}

export function WorkspaceHeader({ breadcrumbItems = [] }: WorkspaceHeaderProps) {
  const { token } = theme.useToken();
  const { workspace, workspaces, setWorkspace } = useWorkspace();
  const location = useLocation();

  // Build workspace dropdown menu
  const workspaceMenuItems: MenuProps['items'] = workspaces.map((ws) => ({
    key: ws.id,
    label: (
      <Space>
        <AppstoreOutlined />
        <Text strong={ws.id === workspace?.id}>{ws.name}</Text>
      </Space>
    ),
    onClick: () => setWorkspace(ws),
  }));

  // Build breadcrumb items
  const fullBreadcrumbItems = [
    {
      title: (
        <Link to="/">
          <HomeOutlined />
        </Link>
      ),
    },
    {
      title: workspaces.length > 1 ? (
        <Dropdown menu={{ items: workspaceMenuItems }} trigger={['click']}>
          <a onClick={(e) => e.preventDefault()}>
            <Space>
              <AppstoreOutlined />
              {workspace?.name || 'Select Workspace'}
              <DownOutlined style={{ fontSize: 10 }} />
            </Space>
          </a>
        </Dropdown>
      ) : (
        <Link to="/workspace">
          <Space>
            <AppstoreOutlined />
            {workspace?.name || 'Workspace'}
          </Space>
        </Link>
      ),
    },
    // Add additional breadcrumb items
    ...breadcrumbItems.map((item) => ({
      title: item.path ? <Link to={item.path}>{item.title}</Link> : item.title,
    })),
  ];

  return (
    <div
      style={{
        padding: `${token.paddingSM}px ${token.paddingLG}px`,
        background: token.colorBgContainer,
        borderBottom: `1px solid ${token.colorBorderSecondary}`,
      }}
    >
      <Breadcrumb items={fullBreadcrumbItems} />
    </div>
  );
}

export default WorkspaceHeader;
