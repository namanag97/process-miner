/**
 * Bottleneck Heat Map Visualization
 *
 * Displays congestion and bottlenecks with heat coloring.
 */

import { useMemo } from 'react';

export interface BottleneckData {
    activity: string;
    avgWaitingTime: number;
    maxWaitingTime: number;
    p95WaitingTime: number;
    occurrences: number;
    severity: 'low' | 'medium' | 'high';
    heatIntensity: number; // 0-1
    queueLength: number;
    throughput: number;
}

export interface BottleneckHeatMapProps {
    bottlenecks: BottleneckData[];
    onActivityClick?: (activity: string) => void;
    className?: string;
}

export function BottleneckHeatMap({
    bottlenecks,
    onActivityClick,
    className = '',
}: BottleneckHeatMapProps) {
    // Sort by severity
    const sortedBottlenecks = useMemo(() => {
        return [...bottlenecks].sort((a, b) => b.avgWaitingTime - a.avgWaitingTime);
    }, [bottlenecks]);

    const getHeatColor = (intensity: number): string => {
        // Green -> Yellow -> Red gradient
        if (intensity < 0.3) {
            return `rgba(82, 196, 26, ${0.3 + intensity * 0.7})`;
        } else if (intensity < 0.7) {
            return `rgba(250, 173, 20, ${0.3 + intensity * 0.7})`;
        } else {
            return `rgba(245, 34, 45, ${0.3 + intensity * 0.7})`;
        }
    };

    const getSeverityBadge = (severity: string) => {
        const colors = {
            low: '#52c41a',
            medium: '#faad14',
            high: '#f5222d',
        };

        return (
            <span
                style={{
                    ...badgeStyle,
                    background: colors[severity as keyof typeof colors] || '#d9d9d9',
                }}
            >
                {severity.toUpperCase()}
            </span>
        );
    };

    const formatTime = (seconds: number): string => {
        if (seconds < 60) {
            return `${seconds.toFixed(1)}s`;
        } else if (seconds < 3600) {
            return `${(seconds / 60).toFixed(1)}m`;
        } else {
            return `${(seconds / 3600).toFixed(1)}h`;
        }
    };

    return (
        <div className={`bottleneck-heatmap ${className}`} style={containerStyle}>
            <div style={headerStyle}>
                <h3 style={titleStyle}>Bottleneck Analysis</h3>
                <div style={legendStyle}>
                    <span style={legendItemStyle}>
                        <span style={{ ...colorBoxStyle, background: 'rgba(82, 196, 26, 0.7)' }} />
                        Low
                    </span>
                    <span style={legendItemStyle}>
                        <span style={{ ...colorBoxStyle, background: 'rgba(250, 173, 20, 0.7)' }} />
                        Medium
                    </span>
                    <span style={legendItemStyle}>
                        <span style={{ ...colorBoxStyle, background: 'rgba(245, 34, 45, 0.7)' }} />
                        High
                    </span>
                </div>
            </div>

            <div style={listContainerStyle}>
                {sortedBottlenecks.length === 0 ? (
                    <div style={emptyStyle}>No bottlenecks detected</div>
                ) : (
                    sortedBottlenecks.map((bottleneck) => (
                        <div
                            key={bottleneck.activity}
                            style={{
                                ...itemStyle,
                                background: getHeatColor(bottleneck.heatIntensity),
                                cursor: onActivityClick ? 'pointer' : 'default',
                            }}
                            onClick={() => onActivityClick?.(bottleneck.activity)}
                        >
                            <div style={itemHeaderStyle}>
                                <span style={activityNameStyle}>{bottleneck.activity}</span>
                                {getSeverityBadge(bottleneck.severity)}
                            </div>

                            <div style={metricsGridStyle}>
                                <div style={metricStyle}>
                                    <span style={metricLabelStyle}>Avg Wait:</span>
                                    <span style={metricValueStyle}>
                                        {formatTime(bottleneck.avgWaitingTime)}
                                    </span>
                                </div>

                                <div style={metricStyle}>
                                    <span style={metricLabelStyle}>Max Wait:</span>
                                    <span style={metricValueStyle}>
                                        {formatTime(bottleneck.maxWaitingTime)}
                                    </span>
                                </div>

                                <div style={metricStyle}>
                                    <span style={metricLabelStyle}>Queue:</span>
                                    <span style={metricValueStyle}>
                                        {bottleneck.queueLength}
                                    </span>
                                </div>

                                <div style={metricStyle}>
                                    <span style={metricLabelStyle}>Throughput:</span>
                                    <span style={metricValueStyle}>
                                        {bottleneck.throughput}/hr
                                    </span>
                                </div>
                            </div>

                            <div style={progressBarContainerStyle}>
                                <div
                                    style={{
                                        ...progressBarStyle,
                                        width: `${bottleneck.heatIntensity * 100}%`,
                                    }}
                                />
                            </div>
                        </div>
                    ))
                )}
            </div>

            <div style={summaryStyle}>
                <div style={summaryItemStyle}>
                    <strong>Total Bottlenecks:</strong> {bottlenecks.length}
                </div>
                <div style={summaryItemStyle}>
                    <strong>High Severity:</strong> {bottlenecks.filter(b => b.severity === 'high').length}
                </div>
                <div style={summaryItemStyle}>
                    <strong>Total Cases Affected:</strong> {bottlenecks.reduce((sum, b) => sum + b.occurrences, 0)}
                </div>
            </div>
        </div>
    );
}

// Styles
const containerStyle: React.CSSProperties = {
    background: '#fff',
    borderRadius: '8px',
    padding: '16px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    minWidth: '400px',
};

const headerStyle: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '16px',
};

const titleStyle: React.CSSProperties = {
    margin: 0,
    fontSize: '16px',
    fontWeight: 600,
};

const legendStyle: React.CSSProperties = {
    display: 'flex',
    gap: '12px',
    fontSize: '12px',
};

const legendItemStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
};

const colorBoxStyle: React.CSSProperties = {
    width: '12px',
    height: '12px',
    borderRadius: '2px',
};

const listContainerStyle: React.CSSProperties = {
    maxHeight: '500px',
    overflowY: 'auto',
    marginBottom: '16px',
};

const emptyStyle: React.CSSProperties = {
    textAlign: 'center',
    color: '#999',
    padding: '32px',
    fontSize: '14px',
};

const itemStyle: React.CSSProperties = {
    padding: '12px',
    borderRadius: '6px',
    marginBottom: '8px',
    border: '1px solid rgba(0,0,0,0.06)',
};

const itemHeaderStyle: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '8px',
};

const activityNameStyle: React.CSSProperties = {
    fontWeight: 600,
    fontSize: '14px',
    color: '#333',
};

const badgeStyle: React.CSSProperties = {
    padding: '2px 8px',
    borderRadius: '4px',
    fontSize: '10px',
    fontWeight: 600,
    color: '#fff',
};

const metricsGridStyle: React.CSSProperties = {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '8px',
    marginBottom: '8px',
};

const metricStyle: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '12px',
};

const metricLabelStyle: React.CSSProperties = {
    color: '#666',
};

const metricValueStyle: React.CSSProperties = {
    fontWeight: 500,
    color: '#333',
};

const progressBarContainerStyle: React.CSSProperties = {
    height: '4px',
    background: 'rgba(0,0,0,0.1)',
    borderRadius: '2px',
    overflow: 'hidden',
};

const progressBarStyle: React.CSSProperties = {
    height: '100%',
    background: 'rgba(0,0,0,0.3)',
};

const summaryStyle: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-around',
    padding: '12px',
    background: '#fafafa',
    borderRadius: '6px',
    fontSize: '13px',
};

const summaryItemStyle: React.CSSProperties = {
    textAlign: 'center',
};

export default BottleneckHeatMap;
