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
  SearchOutlined,
  QuestionCircleOutlined,
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
    // Primary navigation (Celonis-style)
    {
      id: 'quickstarts',
      label: 'Quickstarts',
      icon: <DashboardOutlined />,
      onClick: () => navigate('/'),
    },
    {
      id: 'business-miner',
      label: 'Business Miner',
      icon: <NodeIndexOutlined />,
      onClick: () => navigate('/explorer/demo'),
    },
    {
      id: 'gallery',
      label: 'Celonis Gallery',
      icon: <ApiOutlined />,
      onClick: () => navigate('/data/connectors'),
    },
    {
      id: 'more',
      label: 'More',
      icon: <BarChartOutlined />,
      children: [
        {
          id: 'analytics',
          label: 'Analytics',
          icon: <BarChartOutlined />,
          onClick: () => navigate('/analytics/demo'),
        },
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
    // Data section
    {
      id: 'data',
      label: 'Data',
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
      ],
    },
    // Studio section
    {
      id: 'studio',
      label: 'Studio',
      icon: <ExperimentOutlined />,
      onClick: () => navigate('/data/models'),
    },
    // Admin & Settings
    {
      id: 'admin-settings',
      label: 'Admin & Settings',
      icon: <SettingOutlined />,
      onClick: () => navigate('/settings'),
    },
    // Search
    {
      id: 'search',
      label: 'Search',
      icon: <SearchOutlined />,
      onClick: () => {/* TODO: Open search modal */},
    },
    // Help Center
    {
      id: 'help',
      label: 'Help Center',
      icon: <QuestionCircleOutlined />,
      onClick: () => {/* TODO: Open help */},
    },
  ];

  // Determine active menu item based on current path
  const getActiveId = (): string => {
    const path = location.pathname;
    if (path === '/') return 'quickstarts';
    if (path.startsWith('/explorer')) return 'business-miner';
    if (path.startsWith('/analytics')) return 'analytics';
    if (path.startsWith('/conformance')) return 'conformance';
    if (path.startsWith('/predictions')) return 'predictions';
    if (path.startsWith('/resources')) return 'resources';
    if (path.startsWith('/simulation')) return 'simulation';
    if (path.startsWith('/data/logs') || path.startsWith('/data/logs/')) return 'logs';
    if (path.startsWith('/data/upload')) return 'upload';
    if (path.startsWith('/data/models')) return 'models';
    if (path.startsWith('/data/connectors')) return 'gallery';
    if (path.startsWith('/settings')) return 'admin-settings';
    return 'quickstarts';
  };

  const footer = isAuthenticated ? (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        color: 'rgba(255, 255, 255, 0.85)',
        padding: collapsed ? '8px 0' : '8px 0',
      }}
    >
      {/* User Avatar */}
      <div
        style={{
          width: 32,
          height: 32,
          borderRadius: '50%',
          background: '#36B37E',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'white',
          fontWeight: 600,
          fontSize: 14,
          flexShrink: 0,
        }}
      >
        {user?.email?.[0]?.toUpperCase() || 'U'}
      </div>
      
      {!collapsed && (
        <div style={{ overflow: 'hidden', flex: 1 }}>
          <div
            style={{
              fontSize: 13,
              fontWeight: 500,
              color: 'white',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {user?.name || user?.email?.split('@')[0] || 'User'}
          </div>
          <div
            style={{
              fontSize: 11,
              color: 'rgba(255, 255, 255, 0.6)',
            }}
          >
            Admin
          </div>
        </div>
      )}
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
