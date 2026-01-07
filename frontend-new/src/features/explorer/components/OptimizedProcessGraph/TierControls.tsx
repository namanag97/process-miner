/**
 * TierControls Component
 *
 * UI controls for switching between graph detail tiers.
 * Shows current tier, loading state, and allows upgrading/downgrading detail.
 */

import { memo } from 'react';
import type { GraphTier } from '../../hooks/useTieredGraph';

export interface TierControlsProps {
  currentTier: GraphTier;
  isLoading: boolean;
  isLoadingTier: GraphTier | null;
  canUpgrade: boolean;
  canDowngrade: boolean;
  onUpgrade: () => void;
  onDowngrade: () => void;
  onSetTier: (tier: GraphTier) => void;
  tierStats: {
    overview: { nodes: number; edges: number } | null;
    standard: { nodes: number; edges: number } | null;
    detailed: { nodes: number; edges: number } | null;
  };
  compact?: boolean;
}

const tierLabels: Record<GraphTier, string> = {
  overview: 'Overview',
  standard: 'Standard',
  detailed: 'Full Detail',
};

const tierDescriptions: Record<GraphTier, string> = {
  overview: 'Fast loading with top activities',
  standard: 'Balanced view with most activities',
  detailed: 'Complete graph with all details',
};

export const TierControls = memo(function TierControls({
  currentTier,
  isLoading,
  isLoadingTier,
  canUpgrade,
  canDowngrade,
  onUpgrade,
  onDowngrade,
  onSetTier,
  tierStats,
  compact = false,
}: TierControlsProps) {
  const tiers: GraphTier[] = ['overview', 'standard', 'detailed'];

  if (compact) {
    return (
      <div style={compactContainerStyle}>
        <span style={labelStyle}>Detail:</span>
        <div style={compactButtonGroupStyle}>
          {tiers.map((tier) => {
            const isActive = currentTier === tier;
            const isLoadingThis = isLoadingTier === tier;
            const stats = tierStats[tier];

            return (
              <button
                key={tier}
                onClick={() => onSetTier(tier)}
                disabled={isLoading || isLoadingThis}
                style={{
                  ...compactButtonStyle,
                  ...(isActive ? activeButtonStyle : {}),
                  ...(isLoadingThis ? loadingButtonStyle : {}),
                }}
                title={`${tierLabels[tier]}${stats ? ` (${stats.nodes} nodes)` : ''}`}
              >
                {isLoadingThis ? '...' : tierLabels[tier].charAt(0)}
              </button>
            );
          })}
        </div>
      </div>
    );
  }

  return (
    <div style={containerStyle}>
      <div style={headerStyle}>
        <span style={titleStyle}>Graph Detail Level</span>
        <span style={currentTierStyle}>
          {tierLabels[currentTier]}
          {tierStats[currentTier] && (
            <span style={statsStyle}>
              ({tierStats[currentTier]!.nodes} nodes, {tierStats[currentTier]!.edges} edges)
            </span>
          )}
        </span>
      </div>

      <div style={tiersContainerStyle}>
        {tiers.map((tier, index) => {
          const isActive = currentTier === tier;
          const isLoadingThis = isLoadingTier === tier;
          const stats = tierStats[tier];
          const isPast = tiers.indexOf(currentTier) > index;

          return (
            <div key={tier} style={tierRowStyle}>
              {/* Connector line */}
              {index > 0 && (
                <div
                  style={{
                    ...connectorStyle,
                    backgroundColor: isPast || isActive ? '#1890ff' : '#d9d9d9',
                  }}
                />
              )}

              {/* Tier indicator */}
              <button
                onClick={() => onSetTier(tier)}
                disabled={isLoading}
                style={{
                  ...tierButtonStyle,
                  ...(isActive ? activeTierButtonStyle : {}),
                  ...(isPast ? pastTierButtonStyle : {}),
                  ...(isLoadingThis ? loadingTierButtonStyle : {}),
                }}
              >
                <div style={tierIndicatorStyle}>
                  {isLoadingThis ? (
                    <span style={spinnerStyle}>↻</span>
                  ) : isActive || isPast ? (
                    '✓'
                  ) : (
                    index + 1
                  )}
                </div>
                <div style={tierInfoStyle}>
                  <span style={tierNameStyle}>{tierLabels[tier]}</span>
                  <span style={tierDescStyle}>{tierDescriptions[tier]}</span>
                  {stats && (
                    <span style={tierStatsStyle}>
                      {stats.nodes} nodes, {stats.edges} edges
                    </span>
                  )}
                </div>
              </button>
            </div>
          );
        })}
      </div>

      {/* Quick actions */}
      <div style={actionsStyle}>
        <button
          onClick={onDowngrade}
          disabled={!canDowngrade || isLoading}
          style={{
            ...actionButtonStyle,
            opacity: canDowngrade && !isLoading ? 1 : 0.5,
          }}
        >
          ← Less Detail
        </button>
        <button
          onClick={onUpgrade}
          disabled={!canUpgrade || isLoading}
          style={{
            ...actionButtonStyle,
            ...primaryActionStyle,
            opacity: canUpgrade && !isLoading ? 1 : 0.5,
          }}
        >
          More Detail →
        </button>
      </div>
    </div>
  );
});

// Styles
const containerStyle: React.CSSProperties = {
  background: '#fff',
  borderRadius: 8,
  padding: 16,
  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
};

const headerStyle: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: 16,
};

const titleStyle: React.CSSProperties = {
  fontWeight: 600,
  fontSize: 14,
  color: '#333',
};

const currentTierStyle: React.CSSProperties = {
  fontSize: 12,
  color: '#1890ff',
  fontWeight: 500,
};

const statsStyle: React.CSSProperties = {
  marginLeft: 8,
  color: '#888',
  fontWeight: 400,
};

const tiersContainerStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: 0,
  marginBottom: 16,
};

const tierRowStyle: React.CSSProperties = {
  position: 'relative',
};

const connectorStyle: React.CSSProperties = {
  position: 'absolute',
  left: 15,
  top: -8,
  width: 2,
  height: 8,
};

const tierButtonStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 12,
  width: '100%',
  padding: '8px 12px',
  border: '1px solid #d9d9d9',
  borderRadius: 6,
  background: '#fff',
  cursor: 'pointer',
  textAlign: 'left',
  transition: 'all 0.2s',
};

const activeTierButtonStyle: React.CSSProperties = {
  borderColor: '#1890ff',
  background: '#e6f7ff',
};

const pastTierButtonStyle: React.CSSProperties = {
  borderColor: '#b7eb8f',
  background: '#f6ffed',
};

const loadingTierButtonStyle: React.CSSProperties = {
  borderColor: '#ffc53d',
  background: '#fffbe6',
};

const tierIndicatorStyle: React.CSSProperties = {
  width: 32,
  height: 32,
  borderRadius: '50%',
  background: '#f0f0f0',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontSize: 14,
  fontWeight: 600,
  color: '#666',
  flexShrink: 0,
};

const tierInfoStyle: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: 2,
};

const tierNameStyle: React.CSSProperties = {
  fontSize: 13,
  fontWeight: 500,
  color: '#333',
};

const tierDescStyle: React.CSSProperties = {
  fontSize: 11,
  color: '#888',
};

const tierStatsStyle: React.CSSProperties = {
  fontSize: 11,
  color: '#1890ff',
};

const spinnerStyle: React.CSSProperties = {
  animation: 'spin 1s linear infinite',
};

const actionsStyle: React.CSSProperties = {
  display: 'flex',
  gap: 8,
  justifyContent: 'space-between',
};

const actionButtonStyle: React.CSSProperties = {
  flex: 1,
  padding: '8px 16px',
  border: '1px solid #d9d9d9',
  borderRadius: 4,
  background: '#fff',
  cursor: 'pointer',
  fontSize: 13,
  transition: 'all 0.2s',
};

const primaryActionStyle: React.CSSProperties = {
  background: '#1890ff',
  borderColor: '#1890ff',
  color: '#fff',
};

// Compact styles
const compactContainerStyle: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: 8,
};

const labelStyle: React.CSSProperties = {
  fontSize: 12,
  color: '#666',
};

const compactButtonGroupStyle: React.CSSProperties = {
  display: 'flex',
  gap: 2,
};

const compactButtonStyle: React.CSSProperties = {
  width: 24,
  height: 24,
  border: '1px solid #d9d9d9',
  borderRadius: 4,
  background: '#fff',
  cursor: 'pointer',
  fontSize: 11,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
};

const activeButtonStyle: React.CSSProperties = {
  background: '#1890ff',
  borderColor: '#1890ff',
  color: '#fff',
};

const loadingButtonStyle: React.CSSProperties = {
  background: '#fffbe6',
  borderColor: '#ffc53d',
};

export default TierControls;
