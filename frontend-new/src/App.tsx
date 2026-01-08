import { useEffect, lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation, type RouteObject } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { AppShell, SDKProvider, luminaTheme, logAction } from '@lumina/design-system';
import { UserProvider, useUser } from './shared/context/UserContext';
import { NotificationProvider, useNotifications } from './shared/context/NotificationContext';
import { BackendHealthProvider } from './shared/context/BackendHealthContext';
import { GlobalErrorBoundary, ErrorReport } from './shared/ui/GlobalErrorBoundary';
import { DevConsole, devLog } from './shared/ui/DevConsole';
import { createLogger } from './shared/lib/logger';

// Explicit routes and navigation (no more FeatureRegistry magic)
import { routes } from './routes';
import { navRoutes, getActiveNavId } from './navigation';
import { PageLoader } from './shared/ui/PageLoader';

// Landing page lazy-loaded separately (rendered outside AppShell)
const LandingPage = lazy(() => import('./features/landing/pages/LandingPage'));

// Login page also rendered outside AppShell
const LoginPage = lazy(() => import('./features/auth/pages/LoginPage'));

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

// Main app layout with shell
function AppLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useUser();
  const { unreadCount } = useNotifications();

  // Log route changes for dev debugging
  useEffect(() => {
    logAction('Navigation', location.pathname, { from: document.referrer || 'direct' });
    devLog.action('Route Change', location.pathname);
  }, [location.pathname]);

  const handleNavigate = (id: string) => {
    const targetPath = navRoutes[id] || '/workspace';
    log.debug('Navigating', { from: location.pathname, to: targetPath });
    navigate(targetPath);
  };

  return (
    <AppShell
      activeId={getActiveNavId(location.pathname)}
      onNavigate={handleNavigate}
      userName={user?.name}
      userEmail={user?.email}
      notificationCount={unreadCount}
    >
      <Routes>
        {/* ============================================ */}
        {/* Explicit Application Routes */}
        {/* ============================================ */}
        {routes.map((route, i) => renderRouteObject(route, i))}

        {/* ============================================ */}
        {/* Legacy Redirects - Keep for backward compatibility */}
        {/* ============================================ */}
        <Route path="/explorer" element={<Navigate to="/explore" replace />} />
        <Route path="/processes" element={<Navigate to="/workspace" replace />} />
        <Route path="/processes/upload" element={<Navigate to="/workspace" replace />} />
        <Route path="/processes/:id/*" element={<Navigate to="/workspace" replace />} />
        {/* "/" is now the landing page - handled by AppRouter */}
        <Route path="/home" element={<Navigate to="/" replace />} />
        <Route path="/projects" element={<Navigate to="/workspace" replace />} />
        <Route path="/projects/*" element={<Navigate to="/workspace" replace />} />

        {/* Fallback - catch all unmatched routes */}
        <Route path="*" element={<Navigate to="/workspace" replace />} />
      </Routes>
    </AppShell>
  );
}

/**
 * Landing page wrapper - renders outside the AppShell
 */
function LandingWrapper() {
  return (
    <Suspense fallback={<PageLoader fullPage message="Loading..." />}>
      <LandingPage />
    </Suspense>
  );
}

/**
 * Login page wrapper - renders outside the AppShell
 */
function LoginWrapper() {
  return (
    <Suspense fallback={<PageLoader fullPage message="Loading..." />}>
      <LoginPage />
    </Suspense>
  );
}

/**
 * Router component that handles landing page vs app routes
 */
function AppRouter() {
  const location = useLocation();

  // Landing page renders without AppShell
  if (location.pathname === '/') {
    return <LandingWrapper />;
  }

  // Login page renders without AppShell
  if (location.pathname === '/login') {
    return <LoginWrapper />;
  }

  // All other routes render within AppShell
  return <AppLayout />;
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
                  {/* Router decides between landing page and app */}
                  <AppRouter />
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
