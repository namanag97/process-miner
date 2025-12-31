/**
 * AI Feature Routes
 */

import React, { lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import type { RouteObject } from 'react-router-dom';

// Lazy load pages
const AIIndexPage = lazy(() => import('./pages/AIIndexPage'));
const AIAssistantPage = lazy(() => import('./pages/AIAssistantPage'));
const AIInsightsPage = lazy(() => import('./pages/AIInsightsPage'));
const PredictionsPage = lazy(() => import('./pages/PredictionsPage'));
const PredictorDetailPage = lazy(() => import('./pages/PredictorDetailPage'));

/**
 * Route configuration for FeatureRegistry
 */
export const aiRouteConfig: RouteObject[] = [
  {
    path: '/ai',
    children: [
      { index: true, element: <AIIndexPage /> },
      { path: 'assistant', element: <AIAssistantPage /> },
      { path: 'insights', element: <AIInsightsPage /> },
      { path: 'predictions', element: <PredictionsPage /> },
      { path: 'predictions/:predictorId', element: <PredictorDetailPage /> },
    ],
  },
];

/**
 * Routes component for standalone rendering
 */
export function AIRoutes() {
  return (
    <Routes>
      <Route index element={<AIIndexPage />} />
      <Route path="assistant" element={<AIAssistantPage />} />
      <Route path="insights" element={<AIInsightsPage />} />
      <Route path="predictions" element={<PredictionsPage />} />
      <Route path="predictions/:predictorId" element={<PredictorDetailPage />} />
      <Route path="*" element={<Navigate to="/ai" replace />} />
    </Routes>
  );
}
