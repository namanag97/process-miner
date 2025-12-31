import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { AppShell, SDKProvider, luminaTheme, logAction } from '@lumina/design-system';
import { AuthProvider, useAuth } from './context/AuthContext';
import { NotificationProvider, useNotifications } from './context/NotificationContext';
import { BackendHealthProvider } from './context/BackendHealthContext';
import {
  LoginPage,
  HomePage,
  PlaceholderPage,
  SettingsPage,
  NotificationsPage,
  ActivityLogPage,
  AuditLogsPage,
  HelpCenterPage,
  EventLogsPage,
  UploadWizardPage,
  LogDetailPage,
  ProcessExplorerIndexPage,
  ProcessExplorerPage,
  AnalyticsPage,
  AIIndexPage,
  AIInsightsPage,
  AIAssistantPage,
  PredictionsPage,
  PredictorDetailPage,
  TestBenchPage,
  ProjectDetailPage,
  ProcessQuestionsPage,
  KPIPage,
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

  // Log route changes for dev debugging
  useEffect(() => {
    logAction('Route', { path: location.pathname });
  }, [location.pathname]);

  // Determine active nav item from URL
  const getActiveId = () => {
    const path = location.pathname;
    if (path.startsWith('/home')) return 'home';
    if (path.startsWith('/projects')) return 'home'; // Projects are part of workspace
    if (path.startsWith('/processes')) return 'logs';
    if (path.startsWith('/explorer')) return 'explorer';
    if (path.startsWith('/analytics')) return 'analytics';
    if (path.startsWith('/ai')) return 'ai-insights';
    if (path.startsWith('/predictions')) return 'predictions';
    if (path.startsWith('/settings')) return 'settings';
    if (path.startsWith('/help')) return 'help';
    if (path.startsWith('/notifications')) return 'notifications';
    if (path.startsWith('/activity')) return 'activity';
    if (path.startsWith('/test-bench')) return 'test-bench';
    if (path.startsWith('/audit')) return 'audit-logs';
    return 'home';
  };

  const handleNavigate = (id: string) => {
    const routes: Record<string, string> = {
      home: '/home',
      logs: '/processes',
      explorer: '/explorer',
      analytics: '/analytics',
      'ai-insights': '/ai/assistant',
      predictions: '/ai/predictions',
      settings: '/settings/profile',
      help: '/help',
      notifications: '/notifications',
      activity: '/activity',
      'test-bench': '/test-bench',
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
        <Route path="/audit-logs" element={<AuditLogsPage />} />
        <Route path="/audit" element={<AuditLogsPage />} />

        {/* Project-centric flow (new primary flow) */}
        <Route path="/projects/:projectId" element={<ProjectDetailPage />} />
        <Route path="/projects/:projectId/upload" element={<UploadWizardPage />} />
        <Route path="/projects/:projectId/data/:logId/questions" element={<ProcessQuestionsPage />} />
        <Route path="/projects/:projectId/data/:logId/explorer" element={<ProcessExplorerPage />} />
        <Route path="/projects/:projectId/data/:logId/kpi" element={<KPIPage />} />

        {/* Phase 2: Data Foundation (legacy routes) */}
        <Route path="/processes" element={<EventLogsPage />} />
        <Route path="/processes/upload" element={<UploadWizardPage />} />
        <Route path="/processes/:id/*" element={<LogDetailPage />} />

        {/* Phase 3: Process Discovery (legacy routes) */}
        <Route path="/explorer" element={<ProcessExplorerIndexPage />} />
        <Route path="/explorer/:logId/*" element={<ProcessExplorerPage />} />

        {/* Phase 4: Analytics */}
        <Route path="/analytics" element={<AnalyticsPage />} />
        <Route path="/analytics/performance" element={<AnalyticsPage />} />
        <Route path="/analytics/conformance" element={<AnalyticsPage />} />
        <Route path="/analytics/rework" element={<AnalyticsPage />} />

        {/* Phase 5: AI & Advanced */}
        <Route path="/ai" element={<Navigate to="/ai/assistant" replace />} />
        <Route path="/ai/assistant" element={<AIAssistantPage />} />
        <Route path="/ai/insights" element={<AIInsightsPage />} />
        <Route path="/ai/predictions" element={<PredictionsPage />} />
        <Route path="/ai/predictions/:id" element={<PredictorDetailPage />} />

        {/* Developer Tools */}
        <Route path="/test-bench" element={<TestBenchPage />} />

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
        <BackendHealthProvider>
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
        </BackendHealthProvider>
      </SDKProvider>
    </ConfigProvider>
  );
}

export default App;
