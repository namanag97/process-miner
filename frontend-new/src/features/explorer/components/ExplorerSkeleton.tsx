/**
 * ExplorerSkeleton - Loading skeleton for Explorer page
 * 
 * Shows placeholder content while data is loading.
 */

import { Skeleton, Card, Space } from 'antd';
import { tokens } from '@/src/shared/design-system';

export interface ExplorerSkeletonProps {
    /** Show full page skeleton or just graph area */
    fullPage?: boolean;
}

function KPIBarSkeleton() {
    return (
        <div
            style={{
                display: 'flex',
                gap: tokens.spacing[4],
                padding: tokens.spacing[4],
                backgroundColor: tokens.colors.neutral[0],
                borderBottom: `1px solid ${tokens.colors.neutral[200]}`,
            }}
        >
            {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                    <Skeleton.Input active size="small" style={{ width: 60, height: 12 }} />
                    <Skeleton.Input active size="large" style={{ width: 80, height: 28 }} />
                </div>
            ))}
        </div>
    );
}

function GraphSkeleton() {
    return (
        <div
            style={{
                flex: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: tokens.colors.neutral[50],
                position: 'relative',
                overflow: 'hidden',
            }}
        >
            {/* Animated graph placeholder */}
            <div style={{ position: 'relative', width: 400, height: 300 }}>
                {/* Nodes */}
                {[
                    { x: 50, y: 50 },
                    { x: 200, y: 30 },
                    { x: 350, y: 50 },
                    { x: 100, y: 150 },
                    { x: 250, y: 150 },
                    { x: 175, y: 250 },
                ].map((pos, i) => (
                    <div
                        key={i}
                        style={{
                            position: 'absolute',
                            left: pos.x,
                            top: pos.y,
                            width: 80,
                            height: 40,
                            borderRadius: 8,
                            backgroundColor: tokens.colors.neutral[200],
                            animation: `pulse 1.5s ease-in-out ${i * 0.1}s infinite`,
                        }}
                    />
                ))}

                {/* Edges (simplified lines) */}
                <svg
                    style={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: '100%',
                        pointerEvents: 'none',
                    }}
                >
                    <defs>
                        <linearGradient id="edgeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                            <stop offset="0%" stopColor={tokens.colors.neutral[300]} />
                            <stop offset="100%" stopColor={tokens.colors.neutral[200]} />
                        </linearGradient>
                    </defs>
                    {[
                        { x1: 90, y1: 70, x2: 200, y2: 50 },
                        { x1: 240, y1: 50, x2: 350, y2: 70 },
                        { x1: 90, y1: 70, x2: 140, y2: 150 },
                        { x1: 240, y1: 50, x2: 250, y2: 150 },
                        { x1: 140, y1: 190, x2: 175, y2: 250 },
                        { x1: 290, y1: 190, x2: 215, y2: 250 },
                    ].map((line, i) => (
                        <line
                            key={i}
                            x1={line.x1}
                            y1={line.y1}
                            x2={line.x2}
                            y2={line.y2}
                            stroke="url(#edgeGradient)"
                            strokeWidth={2}
                            opacity={0.5}
                        />
                    ))}
                </svg>
            </div>

            {/* Loading text */}
            <div
                style={{
                    position: 'absolute',
                    bottom: 40,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 8,
                    color: tokens.colors.neutral[500],
                }}
            >
                <div
                    style={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        backgroundColor: tokens.colors.primary[500],
                        animation: 'pulse 1s ease-in-out infinite',
                    }}
                />
                Loading process graph...
            </div>

            {/* CSS Animation */}
            <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 0.4; }
          50% { opacity: 0.8; }
        }
      `}</style>
        </div>
    );
}

function SidebarSkeleton() {
    return (
        <div
            style={{
                width: 320,
                backgroundColor: tokens.colors.neutral[0],
                borderLeft: `1px solid ${tokens.colors.neutral[200]}`,
                padding: tokens.spacing[4],
            }}
        >
            <Space direction="vertical" style={{ width: '100%' }} size={16}>
                <Skeleton.Input active style={{ width: '100%', height: 32 }} />
                <Card size="small">
                    <Skeleton active paragraph={{ rows: 3 }} />
                </Card>
                <Card size="small">
                    <Skeleton active paragraph={{ rows: 4 }} />
                </Card>
            </Space>
        </div>
    );
}

export function ExplorerSkeleton({ fullPage = true }: ExplorerSkeletonProps) {
    if (!fullPage) {
        return <GraphSkeleton />;
    }

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', margin: -24 }}>
            {/* Toolbar skeleton */}
            <div
                style={{
                    height: 56,
                    backgroundColor: tokens.colors.neutral[0],
                    borderBottom: `1px solid ${tokens.colors.neutral[200]}`,
                    display: 'flex',
                    alignItems: 'center',
                    padding: `0 ${tokens.spacing[4]}`,
                    gap: tokens.spacing[4],
                }}
            >
                <Skeleton.Button active size="small" />
                <Skeleton.Input active size="small" style={{ width: 200 }} />
                <div style={{ flex: 1 }} />
                <Space>
                    <Skeleton.Button active size="small" />
                    <Skeleton.Button active size="small" />
                </Space>
            </div>

            {/* KPI Bar */}
            <KPIBarSkeleton />

            {/* Main content */}
            <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
                <GraphSkeleton />
                <SidebarSkeleton />
            </div>
        </div>
    );
}

export default ExplorerSkeleton;
