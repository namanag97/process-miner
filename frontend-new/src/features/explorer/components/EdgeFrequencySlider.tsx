/**
 * EdgeFrequencySlider - Client-side edge filtering by frequency threshold
 * 
 * Instantly filters low-frequency edges without API calls.
 * Used in Explorer visualization controls.
 */

import { useState, useCallback, useMemo } from 'react';
import { Slider, Typography, Space, Tooltip } from 'antd';
import { FilterOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { tokens } from '@lumina/design-system';

const { Text } = Typography;

export interface EdgeFrequencySliderProps {
    /** Total number of edges in the graph */
    totalEdges: number;
    /** Minimum edge frequency percentage in the data */
    minFrequencyPercent?: number;
    /** Maximum edge frequency percentage in the data */
    maxFrequencyPercent?: number;
    /** Current threshold value (0-100) */
    value: number;
    /** Callback when threshold changes */
    onChange: (threshold: number) => void;
    /** Number of edges that pass the current filter */
    visibleEdges?: number;
    /** Debounce delay in ms (default: 100) */
    debounceMs?: number;
}

/**
 * Hook to create debounced edge filter state
 */
export function useEdgeFrequencyFilter(initialThreshold = 0) {
    const [threshold, setThreshold] = useState(initialThreshold);
    const [debouncedThreshold, setDebouncedThreshold] = useState(initialThreshold);

    const handleChange = useCallback((value: number) => {
        setThreshold(value);
        // Debounce the actual filter application
        const timer = setTimeout(() => {
            setDebouncedThreshold(value);
        }, 100);
        return () => clearTimeout(timer);
    }, []);

    return {
        threshold,
        debouncedThreshold,
        setThreshold: handleChange,
    };
}

export function EdgeFrequencySlider({
    totalEdges,
    minFrequencyPercent: _minFrequencyPercent = 0,
    maxFrequencyPercent = 100,
    value,
    onChange,
    visibleEdges,
    debounceMs = 100,
}: EdgeFrequencySliderProps) {
    // Note: _minFrequencyPercent reserved for future dynamic range feature
    void _minFrequencyPercent;

    const [localValue, setLocalValue] = useState(value);

    // Debounced onChange handler
    const handleChange = useCallback(
        (newValue: number) => {
            setLocalValue(newValue);
            const timer = setTimeout(() => {
                onChange(newValue);
            }, debounceMs);
            return () => clearTimeout(timer);
        },
        [onChange, debounceMs]
    );

    // Calculate gradient for slider track
    const trackStyle = useMemo(() => ({
        background: `linear-gradient(to right, 
      ${tokens.colors.neutral[300]} 0%, 
      ${tokens.colors.primary[500]} 100%)`,
    }), []);

    const displayVisible = visibleEdges ?? totalEdges;
    const hiddenCount = totalEdges - displayVisible;

    return (
        <div
            style={{
                padding: tokens.spacing[3],
                backgroundColor: tokens.colors.neutral[50],
                borderRadius: tokens.radius.md,
                border: `1px solid ${tokens.colors.neutral[200]}`,
            }}
        >
            <Space direction="vertical" style={{ width: '100%' }} size={8}>
                {/* Header */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Space size={4}>
                        <FilterOutlined style={{ color: tokens.colors.primary[500] }} />
                        <Text strong style={{ fontSize: 13 }}>
                            Edge Frequency Filter
                        </Text>
                    </Space>
                    <Tooltip title="Filter out low-frequency edges to simplify the graph. Changes apply instantly.">
                        <InfoCircleOutlined style={{ color: tokens.colors.neutral[400] }} />
                    </Tooltip>
                </div>

                {/* Slider */}
                <div style={{ padding: '0 4px' }}>
                    <Slider
                        min={0}
                        max={Math.min(maxFrequencyPercent, 50)}
                        step={1}
                        value={localValue}
                        onChange={handleChange}
                        tooltip={{
                            formatter: (val) => `≥ ${val}%`,
                        }}
                        styles={{
                            track: trackStyle,
                        }}
                    />
                </div>

                {/* Labels */}
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11 }}>
                    <Text type="secondary">Show all</Text>
                    <Text type="secondary">Most frequent</Text>
                </div>

                {/* Stats */}
                <div
                    style={{
                        display: 'flex',
                        justifyContent: 'center',
                        paddingTop: tokens.spacing[2],
                        borderTop: `1px solid ${tokens.colors.neutral[200]}`,
                    }}
                >
                    <Text
                        style={{
                            fontSize: 12,
                            color: hiddenCount > 0 ? tokens.colors.warning[600] : tokens.colors.neutral[500],
                        }}
                    >
                        Showing{' '}
                        <strong>
                            {displayVisible} of {totalEdges}
                        </strong>{' '}
                        edges
                        {hiddenCount > 0 && ` (${hiddenCount} hidden)`}
                    </Text>
                </div>
            </Space>
        </div>
    );
}

export default EdgeFrequencySlider;
