import React, { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Spin } from 'antd';
import { useAuth } from '../context';

// Lazy-loaded page components
const Dashboard = lazy(() => import('../pages/dashboard/DashboardPage'));
const ProcessExplorer = lazy(() => import('../pages/explorer/ProcessExplorerPage'));
const VariantExplorer = lazy(() => import('../pages/explorer/VariantExplorerPage'));
const Analytics = lazy(() => import('../pages/analytics/AnalyticsPage'));
const BottleneckAnalysis = lazy(() => import('../pages/analytics/BottleneckAnalysisPage'));
const Conformance = lazy(() => import('../pages/conformance/ConformancePage'));
const DeviationExplorer = lazy(() => import('../pages/conformance/DeviationExplorerPage'));
const Predictions = lazy(() => import('../pages/predictions/PredictionsPage'));
const PredictionStudio = lazy(() => import('../pages/predictions/PredictionStudioPage'));
const Resources = lazy(() => import('../pages/resources/ResourcesPage'));
const ResourceProfiles = lazy(() => import('../pages/resources/ResourceProfilesPage'));
const Simulation = lazy(() => import('../pages/simulation/SimulationPage'));
const EventLogs = lazy(() => import('../pages/data/EventLogsPage'));
const LogDetail = lazy(() => import('../pages/data/LogDetailPage'));
const Upload = lazy(() => import('../pages/data/UploadPage'));
const Models = lazy(() => import('../pages/data/ModelsPage'));
const Connectors = lazy(() => import('../pages/data/ConnectorsPage'));
const Settings = lazy(() => import('../pages/settings/SettingsPage'));
const Login = lazy(() => import('../pages/auth/LoginPage'));

// Loading fallback
const PageLoader: React.FC = () => (
  <div style={{
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100%',
    minHeight: 400
  }}>
    <Spin size="large" />
  </div>
);

// Protected route wrapper
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <PageLoader />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Public route wrapper (redirects to dashboard if authenticated)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <PageLoader />;
  }

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export const AppRoutes: React.FC = () => {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        {/* Public routes */}
        <Route
          path="/login"
          element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          }
        />

        {/* Protected routes */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        {/* Process Explorer */}
        <Route
          path="/explorer/:logId"
          element={
            <ProtectedRoute>
              <ProcessExplorer />
            </ProtectedRoute>
          }
        />
        <Route
          path="/explorer/:logId/variants"
          element={
            <ProtectedRoute>
              <VariantExplorer />
            </ProtectedRoute>
          }
        />

        {/* Analytics */}
        <Route
          path="/analytics/:logId"
          element={
            <ProtectedRoute>
              <Analytics />
            </ProtectedRoute>
          }
        />
        <Route
          path="/analytics/:logId/bottlenecks"
          element={
            <ProtectedRoute>
              <BottleneckAnalysis />
            </ProtectedRoute>
          }
        />

        {/* Conformance */}
        <Route
          path="/conformance/:logId"
          element={
            <ProtectedRoute>
              <Conformance />
            </ProtectedRoute>
          }
        />
        <Route
          path="/conformance/:logId/deviations"
          element={
            <ProtectedRoute>
              <DeviationExplorer />
            </ProtectedRoute>
          }
        />

        {/* Predictions */}
        <Route
          path="/predictions/:logId"
          element={
            <ProtectedRoute>
              <Predictions />
            </ProtectedRoute>
          }
        />
        <Route
          path="/predictions/studio"
          element={
            <ProtectedRoute>
              <PredictionStudio />
            </ProtectedRoute>
          }
        />

        {/* Resources */}
        <Route
          path="/resources/:logId"
          element={
            <ProtectedRoute>
              <Resources />
            </ProtectedRoute>
          }
        />
        <Route
          path="/resources/:logId/profiles"
          element={
            <ProtectedRoute>
              <ResourceProfiles />
            </ProtectedRoute>
          }
        />

        {/* Simulation */}
        <Route
          path="/simulation/:logId"
          element={
            <ProtectedRoute>
              <Simulation />
            </ProtectedRoute>
          }
        />

        {/* Data Hub */}
        <Route
          path="/data/logs"
          element={
            <ProtectedRoute>
              <EventLogs />
            </ProtectedRoute>
          }
        />
        <Route
          path="/data/logs/:id"
          element={
            <ProtectedRoute>
              <LogDetail />
            </ProtectedRoute>
          }
        />
        <Route
          path="/data/upload"
          element={
            <ProtectedRoute>
              <Upload />
            </ProtectedRoute>
          }
        />
        <Route
          path="/data/models"
          element={
            <ProtectedRoute>
              <Models />
            </ProtectedRoute>
          }
        />
        <Route
          path="/data/connectors"
          element={
            <ProtectedRoute>
              <Connectors />
            </ProtectedRoute>
          }
        />

        {/* Settings */}
        <Route
          path="/settings/*"
          element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          }
        />

        {/* Catch-all redirect */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
};

export default AppRoutes;
