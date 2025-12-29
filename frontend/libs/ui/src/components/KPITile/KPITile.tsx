import React from 'react';
import './KPITile.css';

export interface KPITileProps {
  title: string;
  value: string | number;
  change?: {
    value: number;
    direction: 'up' | 'down' | 'neutral';
    label?: string;
  };
  icon?: React.ReactNode;
  status?: 'success' | 'warning' | 'error' | 'info' | 'neutral';
  subtitle?: string;
  onClick?: () => void;
}

export const KPITile: React.FC<KPITileProps> = ({
  title,
  value,
  change,
  icon,
  status = 'neutral',
  subtitle,
  onClick,
}) => {
  const formatChange = (val: number): string => {
    const prefix = val > 0 ? '+' : '';
    return `${prefix}${val.toFixed(1)}%`;
  };

  return (
    <div className={`kpi-tile kpi-tile-${status} ${onClick ? 'kpi-tile-interactive' : ''}`} onClick={onClick}>
      <div className="kpi-header">
        {icon && <span className="kpi-icon">{icon}</span>}
        <span className="kpi-title">{title}</span>
      </div>

      <div className="kpi-value-row">
        <span className="kpi-value tabular-nums">{value}</span>
        {change && (
          <span className={`kpi-change kpi-change-${change.direction}`}>
            <span className="kpi-change-arrow">
              {change.direction === 'up' ? '↑' : change.direction === 'down' ? '↓' : '→'}
            </span>
            <span className="kpi-change-value">{formatChange(change.value)}</span>
          </span>
        )}
      </div>

      {subtitle && <p className="kpi-subtitle">{subtitle}</p>}
    </div>
  );
};

export default KPITile;
