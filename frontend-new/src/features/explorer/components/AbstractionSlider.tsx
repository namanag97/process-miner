/**
 * AbstractionSlider Component
 * 
 * Controls for filtering process graph by frequency threshold.
 * Allows users to show/hide low-frequency nodes and edges.
 */

import { useState, useCallback } from 'react';

export interface AbstractionSliderProps {
    minNodeFrequency: number;
    maxNodeFrequency: number;
    minEdgeFrequency: number;
    maxEdgeFrequency: number;
    onThresholdChange: (nodeThreshold: number, edgeThreshold: number) => void;
    className?: string;
}

/**
 * AbstractionSlider - Frequency-based abstraction control
 */
export function AbstractionSlider({
    minNodeFrequency,
    maxNodeFrequency,
    minEdgeFrequency,
    maxEdgeFrequency,
    onThresholdChange,
    className = '',
}: AbstractionSliderProps) {
    const [nodeThreshold, setNodeThreshold] = useState(minNodeFrequency);
    const [edgeThreshold, setEdgeThreshold] = useState(minEdgeFrequency);

    const handleNodeChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const value = parseInt(e.target.value, 10);
        setNodeThreshold(value);
        onThresholdChange(value, edgeThreshold);
    }, [edgeThreshold, onThresholdChange]);

    const handleEdgeChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const value = parseInt(e.target.value, 10);
        setEdgeThreshold(value);
        onThresholdChange(nodeThreshold, value);
    }, [nodeThreshold, onThresholdChange]);

    const handleReset = useCallback(() => {
        setNodeThreshold(minNodeFrequency);
        setEdgeThreshold(minEdgeFrequency);
        onThresholdChange(minNodeFrequency, minEdgeFrequency);
    }, [minNodeFrequency, minEdgeFrequency, onThresholdChange]);

    return (
        <div className={`abstraction-slider ${className}`} style={containerStyle}>
            <div style={headerStyle}>
                <span style={titleStyle}>Abstraction Level</span>
                <button onClick={handleReset} style={resetButtonStyle}>Reset</button>
            </div>

            <div style={sliderGroupStyle}>
                <label style={labelStyle}>
                    <span>Activities (min frequency: {nodeThreshold})</span>
                    <input
                        type="range"
                        min={minNodeFrequency}
                        max={maxNodeFrequency}
                        value={nodeThreshold}
                        onChange={handleNodeChange}
                        style={sliderStyle}
                    />
                    <div style={rangeLabelsStyle}>
                        <span>{minNodeFrequency}</span>
                        <span>{maxNodeFrequency}</span>
                    </div>
                </label>
            </div>

            <div style={sliderGroupStyle}>
                <label style={labelStyle}>
                    <span>Transitions (min frequency: {edgeThreshold})</span>
                    <input
                        type="range"
                        min={minEdgeFrequency}
                        max={maxEdgeFrequency}
                        value={edgeThreshold}
                        onChange={handleEdgeChange}
                        style={sliderStyle}
                    />
                    <div style={rangeLabelsStyle}>
                        <span>{minEdgeFrequency}</span>
                        <span>{maxEdgeFrequency}</span>
                    </div>
                </label>
            </div>

            <div style={statsStyle}>
                <span>Higher values = simpler graph</span>
            </div>
        </div>
    );
}

// Styles
const containerStyle: React.CSSProperties = {
    padding: '16px',
    background: '#fff',
    borderRadius: '8px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    width: '280px',
};

const headerStyle: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '16px',
};

const titleStyle: React.CSSProperties = {
    fontWeight: 600,
    fontSize: '14px',
    color: '#333',
};

const resetButtonStyle: React.CSSProperties = {
    padding: '4px 12px',
    fontSize: '12px',
    background: '#f5f5f5',
    border: '1px solid #ddd',
    borderRadius: '4px',
    cursor: 'pointer',
};

const sliderGroupStyle: React.CSSProperties = {
    marginBottom: '16px',
};

const labelStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    fontSize: '12px',
    color: '#666',
};

const sliderStyle: React.CSSProperties = {
    width: '100%',
    height: '6px',
    cursor: 'pointer',
};

const rangeLabelsStyle: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    fontSize: '10px',
    color: '#999',
};

const statsStyle: React.CSSProperties = {
    fontSize: '11px',
    color: '#888',
    fontStyle: 'italic',
    textAlign: 'center',
};

export default AbstractionSlider;
