import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  NodeIndexOutlined,
  BarChartOutlined,
  CheckCircleOutlined,
  BulbOutlined,
  TeamOutlined,
  ExperimentOutlined,
  DatabaseOutlined,
  FileTextOutlined,
  UploadOutlined,
  ApiOutlined,
  SettingOutlined,
  LogoutOutlined,
} from '@ant-design/icons';
import { AppShell, type NavItem } from '@lumina/design-system';
import { useAuth } from '../context';
import { AppRoutes } from './routes';
import { DevPanel } from '../__dev__/DevPanel';

const Logo: React.FC = () => (
  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
    <div
      style={{
        width: 32,
        height: 32,
        borderRadius: 8,
        background: 'linear-gradient(135deg, #0052CC 0%, #0065FF 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        fontWeight: 700,
        fontSize: 16,
      }}
    >
      L
    </div>
    <span style={{ color: 'white', fontWeight: 600, fontSize: 18 }}>Lumina</span>
  </div>
);

const LogoCollapsed: React.FC = () => (
  <div
    style={{
      width: 32,
      height: 32,
      borderRadius: 8,
      background: 'linear-gradient(135deg, #0052CC 0%, #0065FF 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      color: 'white',
      fontWeight: 700,
      fontSize: 16,
    }}
  >
    L
  </div>
);

const App: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isAuthenticated, logout, user } = useAuth();
  const [collapsed, setCollapsed] = useState(false);

  // Don't show shell on login page
  if (location.pathname === '/login') {
    return <AppRoutes />;
  }

  const navItems: NavItem[] = [
    {
      id: 'analyze',
      label: 'ANALYZE',
      icon: <BarChartOutlined />,
      children: [
        {
          id: 'dashboard',
          label: 'Dashboard',
          icon: <DashboardOutlined />,
          onClick: () => navigate('/'),
        },
        {
          id: 'explorer',
          label: 'Process Explorer',
          icon: <NodeIndexOutlined />,
          onClick: () => navigate('/explorer/demo'),
        },
        {
          id: 'analytics',
          label: 'Analytics',
          icon: <BarChartOutlined />,
          onClick: () => navigate('/analytics/demo'),
        },
      ],
    },
    {
      id: 'monitor',
      label: 'MONITOR',
      icon: <CheckCircleOutlined />,
      children: [
        {
          id: 'conformance',
          label: 'Conformance',
          icon: <CheckCircleOutlined />,
          onClick: () => navigate('/conformance/demo'),
        },
        {
          id: 'predictions',
          label: 'Predictions',
          icon: <BulbOutlined />,
          onClick: () => navigate('/predictions/demo'),
        },
      ],
    },
    {
      id: 'optimize',
      label: 'OPTIMIZE',
      icon: <ExperimentOutlined />,
      children: [
        {
          id: 'resources',
          label: 'Resources',
          icon: <TeamOutlined />,
          onClick: () => navigate('/resources/demo'),
        },
        {
          id: 'simulation',
          label: 'Simulation',
          icon: <ExperimentOutlined />,
          onClick: () => navigate('/simulation/demo'),
        },
      ],
    },
    {
      id: 'data',
      label: 'DATA',
      icon: <DatabaseOutlined />,
      children: [
        {
          id: 'logs',
          label: 'Event Logs',
          icon: <FileTextOutlined />,
          onClick: () => navigate('/data/logs'),
        },
        {
          id: 'upload',
          label: 'Upload',
          icon: <UploadOutlined />,
          onClick: () => navigate('/data/upload'),
        },
        {
          id: 'models',
          label: 'Models',
          icon: <NodeIndexOutlined />,
          onClick: () => navigate('/data/models'),
        },
        {
          id: 'connectors',
          label: 'Connectors',
          icon: <ApiOutlined />,
          onClick: () => navigate('/data/connectors'),
        },
      ],
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: <SettingOutlined />,
      onClick: () => navigate('/settings'),
    },
  ];

  // Determine active menu item based on current path
  const getActiveId = (): string => {
    const path = location.pathname;
    if (path === '/') return 'dashboard';
    if (path.startsWith('/explorer')) return 'explorer';
    if (path.startsWith('/analytics')) return 'analytics';
    if (path.startsWith('/conformance')) return 'conformance';
    if (path.startsWith('/predictions')) return 'predictions';
    if (path.startsWith('/resources')) return 'resources';
    if (path.startsWith('/simulation')) return 'simulation';
    if (path.startsWith('/data/logs') || path.startsWith('/data/logs/')) return 'logs';
    if (path.startsWith('/data/upload')) return 'upload';
    if (path.startsWith('/data/models')) return 'models';
    if (path.startsWith('/data/connectors')) return 'connectors';
    if (path.startsWith('/settings')) return 'settings';
    return 'dashboard';
  };

  const footer = isAuthenticated ? (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: collapsed ? 'center' : 'space-between',
        color: 'rgba(255, 255, 255, 0.65)',
        fontSize: 12,
      }}
    >
      {!collapsed && (
        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {user?.email}
        </span>
      )}
      <LogoutOutlined
        style={{ cursor: 'pointer' }}
        onClick={logout}
        title="Sign out"
      />
    </div>
  ) : undefined;

  return (
    <>
      <AppShell
        logo={<Logo />}
        logoCollapsed={<LogoCollapsed />}
        navItems={navItems}
        activeId={getActiveId()}
        collapsed={collapsed}
        onCollapse={setCollapsed}
        footer={footer}
      >
        <AppRoutes />
      </AppShell>
      <DevPanel />
    </>
  );
};

export default App;
