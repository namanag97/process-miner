import { useEffect, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation, type RouteObject } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { AppShell, SDKProvider, luminaTheme, logAction } from '@lumina/design-system';
import { UserProvider, useUser } from './shared/context/UserContext';
import { NotificationProvider, useNotifications } from './shared/context/NotificationContext';
import { BackendHealthProvider } from './shared/context/BackendHealthContext';
import { GlobalErrorBoundary, ErrorReport } from './shared/ui/GlobalErrorBoundary';
import { PageLoader } from './shared/ui/PageLoader';
import { DevConsole, devLog } from './shared/ui/DevConsole';
import { OfflineBanner } from './shared/ui/OfflineBanner';
import { createLogger } from './shared/lib/logger';
import { useFeatureRoutes } from './shared/core/plugins/FeatureRegistry';
import { initializeQueryPersistence } from './api/queryClient';
import { useOfflineQueueProcessor } from './api/offlineQueue';

// ============================================
// Feature Auto-Registration
// ============================================
// This import triggers auto-registration of all features via FeatureRegistry
import './features';

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

/**
 * Recursively render RouteObject as React Router Route elements
 */
function renderRouteObject(route: RouteObject, index: number): React.ReactNode {
  const key = route.path || `route-${index}`;

  if (route.children && route.children.length > 0) {
    return (
      <Route key={key} path={route.path} element={route.element}>
        {route.children.map((child, i) => renderRouteObject(child, i))}
      </Route>
    );
  }

  return (
    <Route
      key={key}
      path={route.path}
      index={route.index}
      element={route.element}
    />
  );
}

// Component to handle offline queue processing
function OfflineQueueManager() {
  // This hook processes queued mutations when back online
  useOfflineQueueProcessor();
  return null;
}

// Main app layout with shell
function AppLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useUser();
  const { unreadCount } = useNotifications();

  // Get all routes from registered features
  const featureRoutes = useFeatureRoutes();

  // Log route changes for dev debugging
  useEffect(() => {
    logAction('Navigation', location.pathname, { from: document.referrer || 'direct' });
    devLog.action('Route Change', location.pathname);
  }, [location.pathname]);

  // Determine active nav item from URL
  const getActiveId = () => {
    const path = location.pathname;
    if (path.startsWith('/workspace')) return 'workspace';
    if (path.startsWith('/home')) return 'workspace'; // Legacy redirect
    if (path.startsWith('/projects')) return 'workspace'; // Projects are part of workspace
    if (path.startsWith('/processes')) return 'logs';
    if (path.startsWith('/explorer') || path.startsWith('/explore')) return 'explorer';
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
      explorer: '/explore',
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
          {/* Dynamic Feature Routes */}
          {/* ============================================ */}
          {featureRoutes.map((route, i) => renderRouteObject(route, i))}

          {/* ============================================ */}
          {/* Legacy Redirects - Keep for backward compatibility */}
          {/* ============================================ */}
          <Route path="/explorer" element={<Navigate to="/explore" replace />} />
          <Route path="/processes" element={<Navigate to="/workspace" replace />} />
          <Route path="/processes/upload" element={<Navigate to="/workspace" replace />} />
          <Route path="/processes/:id/*" element={<Navigate to="/workspace" replace />} />
          <Route path="/" element={<Navigate to="/workspace" replace />} />
          <Route path="/home" element={<Navigate to="/workspace" replace />} />
          <Route path="/projects" element={<Navigate to="/workspace" replace />} />
          <Route path="/projects/*" element={<Navigate to="/workspace" replace />} />

          {/* Fallback - catch all unmatched routes */}
          <Route path="*" element={<Navigate to="/workspace" replace />} />
        </Routes>
      </Suspense>
    </AppShell>
  );
}

function App() {
  // Initialize query persistence on mount
  useEffect(() => {
    initializeQueryPersistence();
  }, []);

  return (
    <GlobalErrorBoundary onError={handleGlobalError}>
      <ConfigProvider theme={luminaTheme}>
        <SDKProvider>
          <BackendHealthProvider>
            <UserProvider>
              <NotificationProvider>
                <BrowserRouter>
                  {/* Offline status banner */}
                  <OfflineBanner />
                  {/* Offline queue processor */}
                  <OfflineQueueManager />
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
