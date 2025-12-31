import React, { useEffect, lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { AppShell, SDKProvider, luminaTheme, logAction } from '@lumina/design-system';
import { UserProvider, useUser } from './context/UserContext';
import { NotificationProvider, useNotifications } from './context/NotificationContext';
import { BackendHealthProvider } from './context/BackendHealthContext';
import { GlobalErrorBoundary, ErrorReport } from './components/GlobalErrorBoundary';
import { PageLoader } from './components/PageLoader';
import { DevConsole, devLog } from './components/DevConsole';
import { createLogger } from './utils/logger';

// ============================================
// Lazy-loaded Page Components (Code Splitting)
// ============================================
// Pages are loaded on-demand to reduce initial bundle size

// ============================================
// Feature Module Pages
// ============================================

// Projects feature
const ProjectsListPage = lazy(() => import('./features/projects/pages/ProjectsListPage'));
const ProjectDetailPage = lazy(() => import('./features/projects/pages/ProjectDetailPage'));

// Explorer feature
const ExplorerIndexPage = lazy(() => import('./features/explorer/pages/ExplorerIndexPage'));
const ExplorerDetailPage = lazy(() => import('./features/explorer/pages/ExplorerDetailPage'));

// KPI feature
const KPIPage = lazy(() => import('./features/kpi/pages/KPIPage'));

// Analytics feature
const AnalyticsPage = lazy(() => import('./features/analytics/pages/AnalyticsPage'));

// AI feature
const AIIndexPage = lazy(() => import('./features/ai/pages/AIIndexPage'));
const AIAssistantPage = lazy(() => import('./features/ai/pages/AIAssistantPage'));
const AIInsightsPage = lazy(() => import('./features/ai/pages/AIInsightsPage'));
const PredictionsPage = lazy(() => import('./features/ai/pages/PredictionsPage'));
const PredictorDetailPage = lazy(() => import('./features/ai/pages/PredictorDetailPage'));

// ============================================
// Legacy Pages (to be migrated)
// ============================================

const SettingsPage = lazy(() => import('./pages/settings/SettingsPage'));
const NotificationsPage = lazy(() => import('./pages/NotificationsPage'));
const ActivityLogPage = lazy(() => import('./pages/ActivityLogPage'));
const AuditLogsPage = lazy(() => import('./pages/AuditLogsPage'));
const HelpCenterPage = lazy(() => import('./pages/HelpCenterPage'));
const EventLogsPage = lazy(() => import('./pages/logs/EventLogsPage'));
const UploadWizardPage = lazy(() => import('./pages/logs/UploadWizardPage'));
const LogDetailPage = lazy(() => import('./pages/logs/LogDetailPage'));
const ProcessQuestionsPage = lazy(() => import('./pages/questions/ProcessQuestionsPage'));

// Developer pages
const TestBenchPage = lazy(() => import('./pages/TestBenchPage'));

const log = createLogger('Navigation');

// Error reporting handler (integrate with your error tracking service)
function handleGlobalError(report: ErrorReport): void {
  // Log to console in development
  if (process.env.NODE_ENV === 'development') {
    console.error('[App] Global error captured:', report);
  }

  // TODO: Send to error tracking service (Sentry, LogRocket, etc.)
  // Example:
  // Sentry.captureException(report.error, {
  //   extra: {
  //     componentStack: report.componentStack,
  //     url: report.url,
  //     userId: report.userId,
  //     sessionId: report.sessionId,
  //   },
  // });

  // Send to dev log endpoint if available
  try {
    fetch('/dev/log', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        level: 'error',
        category: 'GlobalErrorBoundary',
        message: report.error.message,
        data: {
          errorId: report.timestamp,
          stack: report.error.stack,
          componentStack: report.componentStack,
          url: report.url,
          userAgent: report.userAgent,
          userId: report.userId,
          sessionId: report.sessionId,
        },
      }),
    }).catch(() => {
      // Ignore logging errors
    });
  } catch {
    // Ignore
  }
}

// Note: ProtectedRoute removed - MVP mode has no authentication
// When auth is needed, re-add ProtectedRoute using useUser().isAuthenticated

// Main app layout with shell
function AppLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useUser();
  const { unreadCount } = useNotifications();

  // Log route changes for dev debugging
  useEffect(() => {
    logAction('Route', { path: location.pathname });
    devLog.action('Navigation', `Route: ${location.pathname}`);
  }, [location.pathname]);

  // Determine active nav item from URL
  const getActiveId = () => {
    const path = location.pathname;
    if (path.startsWith('/workspace')) return 'workspace';
    if (path.startsWith('/home')) return 'workspace'; // Legacy redirect
    if (path.startsWith('/projects')) return 'workspace'; // Projects are part of workspace
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
    return 'workspace';
  };

  const handleNavigate = (id: string) => {
    const routes: Record<string, string> = {
      workspace: '/workspace',
      home: '/workspace', // Legacy - redirect to workspace
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
    navigate(routes[id] || '/workspace');
  };

  return (
    <AppShell
      activeId={getActiveId()}
      onNavigate={handleNavigate}
      userName={user?.name}
      userEmail={user?.email}
      notificationCount={unreadCount}
    >
      <Suspense fallback={<PageLoader fullPage={false} message="Loading page..." />}>
        <Routes>
          {/* ============================================ */}
          {/* Workspace - Primary entry point */}
          {/* ============================================ */}
          <Route path="/workspace" element={<ProjectsListPage />} />
          <Route path="/workspace/:projectId" element={<ProjectDetailPage />} />
          <Route path="/workspace/:projectId/upload" element={<UploadWizardPage />} />
          <Route path="/workspace/:projectId/data/:logId/questions" element={<ProcessQuestionsPage />} />
          <Route path="/workspace/:projectId/data/:logId/explorer" element={<ExplorerDetailPage />} />
          <Route path="/workspace/:projectId/data/:logId/kpi" element={<KPIPage />} />

          {/* ============================================ */}
          {/* Explorer Feature (standalone) */}
          {/* ============================================ */}
          <Route path="/explorer" element={<ExplorerIndexPage />} />
          <Route path="/explorer/:logId/*" element={<ExplorerDetailPage />} />

          {/* ============================================ */}
          {/* Analytics Feature */}
          {/* ============================================ */}
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/analytics/performance" element={<AnalyticsPage />} />
          <Route path="/analytics/conformance" element={<AnalyticsPage />} />
          <Route path="/analytics/rework" element={<AnalyticsPage />} />
          <Route path="/analytics/resources" element={<AnalyticsPage />} />

          {/* ============================================ */}
          {/* AI Feature */}
          {/* ============================================ */}
          <Route path="/ai" element={<AIIndexPage />} />
          <Route path="/ai/assistant" element={<AIAssistantPage />} />
          <Route path="/ai/insights" element={<AIInsightsPage />} />
          <Route path="/ai/predictions" element={<PredictionsPage />} />
          <Route path="/ai/predictions/:id" element={<PredictorDetailPage />} />

          {/* ============================================ */}
          {/* Platform Features */}
          {/* ============================================ */}
          <Route path="/settings/*" element={<SettingsPage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/help" element={<HelpCenterPage />} />
          <Route path="/activity" element={<ActivityLogPage />} />
          <Route path="/audit-logs" element={<AuditLogsPage />} />
          <Route path="/audit" element={<AuditLogsPage />} />

          {/* ============================================ */}
          {/* Data Foundation (legacy) */}
          {/* ============================================ */}
          <Route path="/processes" element={<EventLogsPage />} />
          <Route path="/processes/upload" element={<UploadWizardPage />} />
          <Route path="/processes/:id/*" element={<LogDetailPage />} />

          {/* ============================================ */}
          {/* Developer Tools */}
          {/* ============================================ */}
          <Route path="/test-bench" element={<TestBenchPage />} />

          {/* ============================================ */}
          {/* Redirects */}
          {/* ============================================ */}
          <Route path="/" element={<Navigate to="/workspace" replace />} />
          <Route path="/home" element={<Navigate to="/workspace" replace />} />
          <Route path="/projects" element={<Navigate to="/workspace" replace />} />
          <Route path="/projects/*" element={<Navigate to="/workspace" replace />} />
          <Route path="*" element={<Navigate to="/workspace" replace />} />
        </Routes>
      </Suspense>
    </AppShell>
  );
}

function App() {
  return (
    <GlobalErrorBoundary onError={handleGlobalError}>
      <ConfigProvider theme={luminaTheme}>
        <SDKProvider>
          <BackendHealthProvider>
            <UserProvider>
              <NotificationProvider>
                <BrowserRouter>
                  {/* No authentication - direct access to app */}
                  <AppLayout />
                  {/* Dev Console - only renders in development */}
                  <DevConsole />
                </BrowserRouter>
              </NotificationProvider>
            </UserProvider>
          </BackendHealthProvider>
        </SDKProvider>
      </ConfigProvider>
    </GlobalErrorBoundary>
  );
}

export default App;
