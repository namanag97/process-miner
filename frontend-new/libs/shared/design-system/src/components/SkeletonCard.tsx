import { Card } from 'antd';
import { tokens } from '../theme';

export interface SkeletonCardProps {
  /** Number of text lines to show */
  lines?: number;
  /** Whether to show an avatar placeholder */
  avatar?: boolean;
  /** Card height override */
  height?: number | string;
}

/**
 * SkeletonCard - Premium loading placeholder with shimmer animation
 * Use instead of spinners for a more polished loading experience
 */
export function SkeletonCard({
  lines = 3,
  avatar = false,
  height,
}: SkeletonCardProps) {
  return (
    <Card
      style={{
        borderRadius: tokens.radius.lg,
        height,
      }}
      bodyStyle={{ padding: tokens.spacing[4] }}
    >
      <div style={{ display: 'flex', gap: tokens.spacing[3] }}>
        {avatar && (
          <div
            className="skeleton skeleton-avatar"
            style={{
              flexShrink: 0,
            }}
          />
        )}
        <div style={{ flex: 1 }}>
          <div
            className="skeleton skeleton-title"
            style={{ marginBottom: tokens.spacing[3] }}
          />
          {Array.from({ length: lines }).map((_, i) => (
            <div
              key={i}
              className="skeleton skeleton-text"
              style={{
                width: i === lines - 1 ? '60%' : '100%',
              }}
            />
          ))}
        </div>
      </div>
    </Card>
  );
}

export default SkeletonCard;
