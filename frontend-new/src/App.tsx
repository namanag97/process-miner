import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { AppShell, SDKProvider, luminaTheme } from '@lumina/design-system';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LoginPage, HomePage, PlaceholderPage } from './pages';

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
  const { user, logout } = useAuth();

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
    };
    navigate(routes[id] || '/home');
  };

  return (
    <AppShell
      activeId={getActiveId()}
      onNavigate={handleNavigate}
      userName={user?.name}
      userEmail={user?.email}
      notificationCount={3}
    >
      <Routes>
        {/* Phase 1: Base Platform */}
        <Route path="/home" element={<HomePage />} />
        <Route path="/settings/*" element={<PlaceholderPage title="Settings" phase={1} />} />
        <Route path="/notifications" element={<PlaceholderPage title="Notifications" phase={1} />} />
        <Route path="/help" element={<PlaceholderPage title="Help Center" phase={1} />} />
        <Route path="/activity" element={<PlaceholderPage title="Activity Log" phase={1} />} />

        {/* Phase 2: Data Foundation */}
        <Route path="/logs" element={<PlaceholderPage title="Event Logs" phase={2} />} />
        <Route path="/logs/upload" element={<PlaceholderPage title="Upload Event Log" phase={2} />} />
        <Route path="/logs/:id/*" element={<PlaceholderPage title="Log Detail" phase={2} />} />

        {/* Phase 3: Process Discovery */}
        <Route path="/explorer" element={<PlaceholderPage title="Process Explorer" phase={3} />} />
        <Route path="/explorer/:logId/*" element={<PlaceholderPage title="Process Explorer" phase={3} />} />

        {/* Phase 4: Analytics */}
        <Route path="/analytics/*" element={<PlaceholderPage title="Analytics" phase={4} />} />

        {/* Phase 5: AI & Advanced */}
        <Route path="/ai/*" element={<PlaceholderPage title="AI Insights" phase={5} />} />

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
        </AuthProvider>
      </SDKProvider>
    </ConfigProvider>
  );
}

export default App;
