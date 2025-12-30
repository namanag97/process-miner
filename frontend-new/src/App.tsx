import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { AppShell, SDKProvider, luminaTheme } from '@lumina/design-system';
import { AuthProvider, useAuth } from './context/AuthContext';
import { NotificationProvider, useNotifications } from './context/NotificationContext';
import {
  LoginPage,
  HomePage,
  PlaceholderPage,
  SettingsPage,
  NotificationsPage,
  ActivityLogPage,
  HelpCenterPage,
  EventLogsPage,
  UploadWizardPage,
  LogDetailPage,
  ProcessExplorerIndexPage,
  ProcessExplorerPage,
  AnalyticsPage,
  AIIndexPage,
  AIInsightsPage,
  PredictionsPage,
  PredictorDetailPage,
} from './pages';
import { createLogger } from './utils/logger';

const log = createLogger('Navigation');

// Protected route wrapper
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return <div>Loading...</div>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
}

// Main app layout with shell
function AppLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();
  const { unreadCount } = useNotifications();

  // Determine active nav item from URL
  const getActiveId = () => {
    const path = location.pathname;
    if (path.startsWith('/home')) return 'home';
    if (path.startsWith('/logs')) return 'logs';
    if (path.startsWith('/explorer')) return 'explorer';
    if (path.startsWith('/analytics')) return 'analytics';
    if (path.startsWith('/ai')) return 'ai-insights';
    if (path.startsWith('/predictions')) return 'predictions';
    if (path.startsWith('/settings')) return 'settings';
    if (path.startsWith('/help')) return 'help';
    if (path.startsWith('/notifications')) return 'notifications';
    if (path.startsWith('/activity')) return 'activity';
    return 'home';
  };

  const handleNavigate = (id: string) => {
    const routes: Record<string, string> = {
      home: '/home',
      logs: '/logs',
      explorer: '/explorer',
      analytics: '/analytics',
      'ai-insights': '/ai/insights',
      predictions: '/ai/predictions',
      settings: '/settings/profile',
      help: '/help',
      notifications: '/notifications',
      activity: '/activity',
    };
    log.debug('Navigating', { from: location.pathname, to: routes[id] });
    navigate(routes[id] || '/home');
  };

  return (
    <AppShell
      activeId={getActiveId()}
      onNavigate={handleNavigate}
      userName={user?.name}
      userEmail={user?.email}
      notificationCount={unreadCount}
    >
      <Routes>
        {/* Phase 1: Base Platform */}
        <Route path="/home" element={<HomePage />} />
        <Route path="/settings/*" element={<SettingsPage />} />
        <Route path="/notifications" element={<NotificationsPage />} />
        <Route path="/help" element={<HelpCenterPage />} />
        <Route path="/activity" element={<ActivityLogPage />} />

        {/* Phase 2: Data Foundation */}
        <Route path="/logs" element={<EventLogsPage />} />
        <Route path="/logs/upload" element={<UploadWizardPage />} />
        <Route path="/logs/:id/*" element={<LogDetailPage />} />

        {/* Phase 3: Process Discovery */}
        <Route path="/explorer" element={<ProcessExplorerIndexPage />} />
        <Route path="/explorer/:logId/*" element={<ProcessExplorerPage />} />

        {/* Phase 4: Analytics */}
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/analytics/performance" element={<AnalyticsPage />} />
        <Route path="/analytics/conformance" element={<AnalyticsPage />} />
        <Route path="/analytics/rework" element={<AnalyticsPage />} />

        {/* Phase 5: AI & Advanced */}
        <Route path="/ai" element={<AIIndexPage />} />
        <Route path="/ai/insights" element={<AIInsightsPage />} />
        <Route path="/ai/predictions" element={<PredictionsPage />} />
        <Route path="/ai/predictions/:id" element={<PredictorDetailPage />} />

        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/home" replace />} />
        <Route path="*" element={<Navigate to="/home" replace />} />
      </Routes>
    </AppShell>
  );
}

function App() {
  return (
    <ConfigProvider theme={luminaTheme}>
      <SDKProvider>
        <AuthProvider>
          <NotificationProvider>
            <BrowserRouter>
              <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route
                  path="/*"
                  element={
                    <ProtectedRoute>
                      <AppLayout />
                    </ProtectedRoute>
                  }
                />
              </Routes>
            </BrowserRouter>
          </NotificationProvider>
        </AuthProvider>
      </SDKProvider>
    </ConfigProvider>
  );
}

export default App;
