/**
 * Token Animation Player
 *
 * Animates tokens flowing through the process model.
 * Uses CSS animations for performance.
 */

import { useCallback, useEffect, useRef, useState } from 'react';

export interface Token {
    id: string;
    caseId: string;
    currentNode: string;
    nextNode: string | null;
    progress: number; // 0-1
    timestamp: Date;
}

export interface TokenPath {
    caseId: string;
    path: Array<{ nodeId: string; timestamp: Date; duration: number }>;
}

export interface TokenAnimationPlayerProps {
    tokenPaths: TokenPath[];
    onNodeActivation?: (nodeId: string, tokenCount: number) => void;
    className?: string;
}

export function TokenAnimationPlayer({
    tokenPaths,
    onNodeActivation,
    className = '',
}: TokenAnimationPlayerProps) {
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [playbackSpeed, setPlaybackSpeed] = useState(1);
    const [activeTokens, setActiveTokens] = useState<Token[]>([]);

    const animationRef = useRef<number | null>(null);
    const startTimeRef = useRef<number>(0);

    // Calculate time bounds
    const { minTime, maxTime, duration } = useCalculateTimeBounds(tokenPaths);

    const updateTokens = useCallback((time: number) => {
        const tokens: Token[] = [];
        const nodeActivations: Record<string, number> = {};

        tokenPaths.forEach(path => {
            // Find current position for this case
            for (let i = 0; i < path.path.length - 1; i++) {
                const current = path.path[i];
                const next = path.path[i + 1];

                const startTime = current.timestamp.getTime();
                const endTime = next.timestamp.getTime();

                if (time >= startTime && time <= endTime) {
                    // Token is in transit
                    const progress = (time - startTime) / (endTime - startTime);

                    tokens.push({
                        id: `${path.caseId}-${i}`,
                        caseId: path.caseId,
                        currentNode: current.nodeId,
                        nextNode: next.nodeId,
                        progress,
                        timestamp: new Date(time),
                    });

                    // Track node activations
                    nodeActivations[current.nodeId] = (nodeActivations[current.nodeId] || 0) + 1;
                }
            }
        });

        setActiveTokens(tokens);

        // Notify about node activations
        if (onNodeActivation) {
            Object.entries(nodeActivations).forEach(([nodeId, count]) => {
                onNodeActivation(nodeId, count);
            });
        }
    }, [tokenPaths, onNodeActivation]);

    const animate = useCallback((timestamp: number) => {
        if (!startTimeRef.current) {
            startTimeRef.current = timestamp;
        }

        const elapsed = (timestamp - startTimeRef.current) * playbackSpeed;
        const newTime = minTime + elapsed;

        if (newTime <= maxTime) {
            setCurrentTime(newTime);
            updateTokens(newTime);
            animationRef.current = requestAnimationFrame(animate);
        } else {
            setIsPlaying(false);
            setCurrentTime(minTime);
            updateTokens(minTime);
        }
    }, [minTime, maxTime, playbackSpeed, updateTokens]);

    const handlePlay = () => {
        if (!isPlaying) {
            setIsPlaying(true);
            startTimeRef.current = 0;
            animationRef.current = requestAnimationFrame(animate);
        }
    };

    const handlePause = () => {
        setIsPlaying(false);
        if (animationRef.current) {
            cancelAnimationFrame(animationRef.current);
            animationRef.current = null;
        }
    };

    const handleReset = () => {
        handlePause();
        setCurrentTime(minTime);
        updateTokens(minTime);
    };

    const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
        const newTime = parseFloat(e.target.value);
        setCurrentTime(newTime);
        updateTokens(newTime);
    };

    useEffect(() => {
        return () => {
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current);
            }
        };
    }, []);

    const progress = duration > 0 ? ((currentTime - minTime) / duration) * 100 : 0;

    return (
        <div className={`token-animation-player ${className}`} style={containerStyle}>
            <div style={headerStyle}>
                <span style={titleStyle}>Token Animation</span>
                <div style={statsStyle}>
                    Active Tokens: <strong>{activeTokens.length}</strong>
                </div>
            </div>

            <div style={timelineStyle}>
                <input
                    type="range"
                    min={minTime}
                    max={maxTime}
                    value={currentTime}
                    onChange={handleSeek}
                    style={sliderStyle}
                />
                <div style={timeLabelsStyle}>
                    <span>{formatTime(new Date(currentTime))}</span>
                    <span>{formatDuration(duration)}</span>
                </div>
            </div>

            <div style={controlsStyle}>
                <button
                    onClick={handleReset}
                    style={controlButtonStyle}
                    title="Reset"
                >
                    ⏮
                </button>

                {isPlaying ? (
                    <button
                        onClick={handlePause}
                        style={{ ...controlButtonStyle, ...playButtonStyle }}
                        title="Pause"
                    >
                        ⏸
                    </button>
                ) : (
                    <button
                        onClick={handlePlay}
                        style={{ ...controlButtonStyle, ...playButtonStyle }}
                        title="Play"
                    >
                        ▶
                    </button>
                )}

                <div style={speedControlStyle}>
                    <label style={speedLabelStyle}>Speed:</label>
                    <select
                        value={playbackSpeed}
                        onChange={(e) => setPlaybackSpeed(parseFloat(e.target.value))}
                        style={speedSelectStyle}
                    >
                        <option value="0.5">0.5x</option>
                        <option value="1">1x</option>
                        <option value="2">2x</option>
                        <option value="5">5x</option>
                        <option value="10">10x</option>
                    </select>
                </div>
            </div>

            <div style={progressBarContainerStyle}>
                <div style={{ ...progressBarStyle, width: `${progress}%` }} />
            </div>
        </div>
    );
}

// Utility hooks
function useCalculateTimeBounds(tokenPaths: TokenPath[]) {
    const [bounds, setBounds] = useState({ minTime: 0, maxTime: 0, duration: 0 });

    useEffect(() => {
        if (tokenPaths.length === 0) {
            setBounds({ minTime: 0, maxTime: 0, duration: 0 });
            return;
        }

        let min = Infinity;
        let max = -Infinity;

        tokenPaths.forEach(path => {
            path.path.forEach(node => {
                const time = node.timestamp.getTime();
                if (time < min) min = time;
                if (time > max) max = time;
            });
        });

        setBounds({
            minTime: min,
            maxTime: max,
            duration: max - min,
        });
    }, [tokenPaths]);

    return bounds;
}

// Utility functions
function formatTime(date: Date): string {
    return date.toLocaleTimeString();
}

function formatDuration(ms: number): string {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);

    if (hours > 0) {
        return `${hours}h ${minutes % 60}m`;
    } else if (minutes > 0) {
        return `${minutes}m ${seconds % 60}s`;
    } else {
        return `${seconds}s`;
    }
}

// Styles
const containerStyle: React.CSSProperties = {
    background: '#fff',
    borderRadius: '8px',
    padding: '16px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    minWidth: '320px',
};

const headerStyle: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '12px',
};

const titleStyle: React.CSSProperties = {
    fontSize: '14px',
    fontWeight: 600,
    color: '#333',
};

const statsStyle: React.CSSProperties = {
    fontSize: '12px',
    color: '#666',
};

const timelineStyle: React.CSSProperties = {
    marginBottom: '12px',
};

const sliderStyle: React.CSSProperties = {
    width: '100%',
    height: '6px',
    cursor: 'pointer',
};

const timeLabelsStyle: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '11px',
    color: '#999',
    marginTop: '4px',
};

const controlsStyle: React.CSSProperties = {
    display: 'flex',
    gap: '12px',
    alignItems: 'center',
    marginBottom: '12px',
};

const controlButtonStyle: React.CSSProperties = {
    padding: '8px 12px',
    background: '#f5f5f5',
    border: '1px solid #d9d9d9',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '16px',
};

const playButtonStyle: React.CSSProperties = {
    background: '#1890ff',
    color: '#fff',
    borderColor: '#1890ff',
};

const speedControlStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginLeft: 'auto',
};

const speedLabelStyle: React.CSSProperties = {
    fontSize: '12px',
    color: '#666',
};

const speedSelectStyle: React.CSSProperties = {
    padding: '4px 8px',
    border: '1px solid #d9d9d9',
    borderRadius: '4px',
    fontSize: '12px',
};

const progressBarContainerStyle: React.CSSProperties = {
    height: '4px',
    background: '#f0f0f0',
    borderRadius: '2px',
    overflow: 'hidden',
};

const progressBarStyle: React.CSSProperties = {
    height: '100%',
    background: '#1890ff',
    transition: 'width 0.1s linear',
};

export default TokenAnimationPlayer;
