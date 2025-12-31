/**
 * Color Scales and Visual Encoding Utilities for Process Explorer
 * Uses d3-scale for performance-based coloring
 */

import { scaleLinear, scaleSequential, scaleQuantize } from 'd3-scale';
import { interpolateRgb, interpolateRgbBasis } from 'd3-interpolate';

// =============================================================================
// COLOR PALETTES
// =============================================================================

export const COLORS = {
  // Performance scale (green = good, yellow = warning, red = bad)
  performance: {
    good: '#10B981',      // Green
    moderate: '#F59E0B',  // Amber
    poor: '#EF4444',      // Red
  },
  // Frequency scale (light = low, dark = high)
  frequency: {
    low: '#E5E7EB',
    medium: '#6366F1',
    high: '#312E81',
  },
  // Node states
  node: {
    default: '#FFFFFF',
    selected: '#EEF2FF',
    highlighted: '#DBEAFE',
    start: '#D1FAE5',
    end: '#FEE2E2',
  },
  // Edge colors
  edge: {
    default: '#9CA3AF',
    selected: '#6366F1',
    highlighted: '#3B82F6',
    critical: '#EF4444',
  },
  // Border colors
  border: {
    default: '#D1D5DB',
    selected: '#6366F1',
    start: '#10B981',
    end: '#EF4444',
  },
};

// =============================================================================
// PERFORMANCE COLOR SCALE
// =============================================================================

/**
 * Create a performance color scale (green → yellow → red)
 * @param minValue - Minimum duration in seconds
 * @param maxValue - Maximum duration in seconds
 */
export function createPerformanceScale(minValue: number, maxValue: number) {
  return scaleSequential<string>()
    .domain([minValue, maxValue])
    .interpolator(
      interpolateRgbBasis([
        COLORS.performance.good,
        COLORS.performance.moderate,
        COLORS.performance.poor,
      ])
    );
}

/**
 * Get performance color for a given duration
 */
export function getPerformanceColor(
  duration: number,
  minDuration: number,
  maxDuration: number
): string {
  if (maxDuration === minDuration) return COLORS.performance.good;
  const scale = createPerformanceScale(minDuration, maxDuration);
  return scale(duration);
}

/**
 * Get performance level (good, moderate, poor) based on percentile
 */
export function getPerformanceLevel(
  duration: number,
  p25: number,
  p75: number
): 'good' | 'moderate' | 'poor' {
  if (duration <= p25) return 'good';
  if (duration <= p75) return 'moderate';
  return 'poor';
}

// =============================================================================
// FREQUENCY COLOR SCALE
// =============================================================================

/**
 * Create a frequency-based opacity scale
 */
export function createFrequencyOpacityScale(minFreq: number, maxFreq: number) {
  return scaleLinear<number>()
    .domain([minFreq, maxFreq])
    .range([0.4, 1])
    .clamp(true);
}

/**
 * Create a frequency-based color intensity scale
 */
export function createFrequencyColorScale(minFreq: number, maxFreq: number) {
  return scaleLinear<string>()
    .domain([minFreq, (minFreq + maxFreq) / 2, maxFreq])
    .range([COLORS.frequency.low, COLORS.frequency.medium, COLORS.frequency.high])
    .interpolate(interpolateRgb as never);
}

/**
 * Get frequency-based color
 */
export function getFrequencyColor(
  frequency: number,
  minFrequency: number,
  maxFrequency: number
): string {
  if (maxFrequency === minFrequency) return COLORS.frequency.medium;
  const scale = createFrequencyColorScale(minFrequency, maxFrequency);
  return scale(frequency);
}

// =============================================================================
// EDGE STYLING
// =============================================================================

export interface EdgeStyle {
  stroke: string;
  strokeWidth: number;
  opacity: number;
  animated: boolean;
}

/**
 * Calculate edge style based on frequency and performance
 */
export function getEdgeStyle(
  frequency: number,
  minFreq: number,
  maxFreq: number,
  duration?: number,
  minDuration?: number,
  maxDuration?: number,
  showPerformance = false
): EdgeStyle {
  // Calculate width based on frequency (1 to 6)
  const normalizedFreq =
    maxFreq === minFreq ? 0.5 : (frequency - minFreq) / (maxFreq - minFreq);
  const strokeWidth = 1 + normalizedFreq * 5;

  // Calculate opacity based on frequency (0.3 to 1)
  const opacity = 0.3 + normalizedFreq * 0.7;

  // Determine color based on mode
  let stroke = COLORS.edge.default;
  if (showPerformance && duration !== undefined && minDuration !== undefined && maxDuration !== undefined) {
    stroke = getPerformanceColor(duration, minDuration, maxDuration);
  }

  // Animate critical paths (high frequency)
  const animated = normalizedFreq > 0.8;

  return {
    stroke,
    strokeWidth,
    opacity,
    animated,
  };
}

// =============================================================================
// NODE STYLING
// =============================================================================

export interface NodeStyle {
  backgroundColor: string;
  borderColor: string;
  borderWidth: number;
  scale: number;
}

/**
 * Calculate node style based on type and state
 */
export function getNodeStyle(
  frequency: number,
  minFreq: number,
  maxFreq: number,
  isStart: boolean,
  isEnd: boolean,
  isSelected: boolean,
  isHighlighted: boolean,
  showPerformance = false,
  duration?: number,
  minDuration?: number,
  maxDuration?: number
): NodeStyle {
  // Calculate scale based on frequency (0.85 to 1.15)
  const normalizedFreq =
    maxFreq === minFreq ? 0.5 : (frequency - minFreq) / (maxFreq - minFreq);
  const scale = 0.85 + normalizedFreq * 0.3;

  // Determine background color
  let backgroundColor = COLORS.node.default;
  if (showPerformance && duration !== undefined && minDuration !== undefined && maxDuration !== undefined) {
    // Light tint of performance color
    const perfColor = getPerformanceColor(duration, minDuration, maxDuration);
    backgroundColor = hexToRgba(perfColor, 0.15);
  } else if (isStart) {
    backgroundColor = COLORS.node.start;
  } else if (isEnd) {
    backgroundColor = COLORS.node.end;
  } else if (isSelected) {
    backgroundColor = COLORS.node.selected;
  } else if (isHighlighted) {
    backgroundColor = COLORS.node.highlighted;
  }

  // Determine border color
  let borderColor = COLORS.border.default;
  if (isStart) {
    borderColor = COLORS.border.start;
  } else if (isEnd) {
    borderColor = COLORS.border.end;
  } else if (isSelected) {
    borderColor = COLORS.border.selected;
  }

  const borderWidth = isSelected ? 2 : 1;

  return {
    backgroundColor,
    borderColor,
    borderWidth,
    scale,
  };
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Convert hex color to rgba
 */
export function hexToRgba(hex: string, alpha: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

/**
 * Get contrasting text color (black or white) for a background
 */
export function getContrastColor(backgroundColor: string): string {
  // Simple luminance calculation
  const hex = backgroundColor.replace('#', '');
  const r = parseInt(hex.slice(0, 2), 16);
  const g = parseInt(hex.slice(2, 4), 16);
  const b = parseInt(hex.slice(4, 6), 16);
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
  return luminance > 0.5 ? '#000000' : '#FFFFFF';
}

/**
 * Format duration for display
 */
export function formatDuration(seconds: number): string {
  if (seconds < 60) {
    return `${Math.round(seconds)}s`;
  } else if (seconds < 3600) {
    return `${Math.round(seconds / 60)}m`;
  } else if (seconds < 86400) {
    const hours = seconds / 3600;
    return hours < 10 ? `${hours.toFixed(1)}h` : `${Math.round(hours)}h`;
  } else {
    const days = seconds / 86400;
    return days < 10 ? `${days.toFixed(1)}d` : `${Math.round(days)}d`;
  }
}

/**
 * Format large numbers with K, M suffixes
 */
export function formatNumber(num: number): string {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`;
  } else if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}K`;
  }
  return num.toLocaleString();
}

/**
 * Calculate statistics for an array of numbers
 */
export function calculateStats(values: number[]): {
  min: number;
  max: number;
  avg: number;
  p25: number;
  p50: number;
  p75: number;
} {
  if (values.length === 0) {
    return { min: 0, max: 0, avg: 0, p25: 0, p50: 0, p75: 0 };
  }

  const sorted = [...values].sort((a, b) => a - b);
  const sum = sorted.reduce((acc, v) => acc + v, 0);

  return {
    min: sorted[0],
    max: sorted[sorted.length - 1],
    avg: sum / sorted.length,
    p25: sorted[Math.floor(sorted.length * 0.25)],
    p50: sorted[Math.floor(sorted.length * 0.5)],
    p75: sorted[Math.floor(sorted.length * 0.75)],
  };
}
