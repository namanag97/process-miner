/**
 * FullViewportPage - Layout for immersive canvas experiences
 *
 * Use this instead of FeaturePage when you need full viewport control
 * without default padding (e.g., for process maps, diagrams, editors).
 *
 * @example
 * <FullViewportPage
 *   toolbar={<ProcessToolbar />}
 *   sidePanel={<VariantPanel />}
 *   sidePanelWidth={360}
 * >
 *   <ProcessCanvas />
 * </FullViewportPage>
 */

import React from 'react';
import { tokens } from '../theme';

export interface FullViewportPageProps {
  /** Main content (typically a canvas or editor) */
  children: React.ReactNode;
  /** Optional toolbar at the top */
  toolbar?: React.ReactNode;
  /** Optional side panel (right side) */
  sidePanel?: React.ReactNode;
  /** Width of the side panel in pixels */
  sidePanelWidth?: number;
  /** Whether the side panel is open */
  sidePanelOpen?: boolean;
  /** Optional footer bar (e.g., for KPIs or status) */
  footer?: React.ReactNode;
  /** Background color for the main content area */
  backgroundColor?: string;
}

const containerStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  height: '100vh',
  width: '100%',
  overflow: 'hidden',
  // Compensate for AppShell padding
  margin: -24,
  marginLeft: -24,
  marginRight: -24,
  // Extend to fill the space
  paddingLeft: 0,
  paddingRight: 0,
};

const toolbarStyle: React.CSSProperties = {
  height: 56,
  backgroundColor: tokens.colors.neutral[0],
  borderBottom: `1px solid ${tokens.colors.neutral[200]}`,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: `0 ${tokens.spacing[4]}`,
  flexShrink: 0,
};

const contentContainerStyle: React.CSSProperties = {
  display: 'flex',
  flex: 1,
  overflow: 'hidden',
};

const mainContentStyle: React.CSSProperties = {
  flex: 1,
  position: 'relative',
  overflow: 'hidden',
};

const getSidePanelStyle = (width: number): React.CSSProperties => ({
  width,
  backgroundColor: tokens.colors.neutral[0],
  borderLeft: `1px solid ${tokens.colors.neutral[200]}`,
  display: 'flex',
  flexDirection: 'column',
  overflow: 'hidden',
  flexShrink: 0,
});

export function FullViewportPage({
  children,
  toolbar,
  sidePanel,
  sidePanelWidth = 360,
  sidePanelOpen = true,
  footer,
  backgroundColor = tokens.colors.neutral[50],
}: FullViewportPageProps) {
  return (
    <div style={containerStyle}>
      {/* Toolbar */}
      {toolbar && <div style={toolbarStyle}>{toolbar}</div>}

      {/* Footer (e.g., KPI Bar) - placed before main content for layout */}
      {footer}

      {/* Main Content Area */}
      <div style={contentContainerStyle}>
        {/* Canvas/Editor Area */}
        <div style={{ ...mainContentStyle, backgroundColor }}>
          {children}
        </div>

        {/* Side Panel */}
        {sidePanel && sidePanelOpen && (
          <div style={getSidePanelStyle(sidePanelWidth)}>
            {sidePanel}
          </div>
        )}
      </div>
    </div>
  );
}

export default FullViewportPage;
