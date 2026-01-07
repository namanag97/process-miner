/**
 * Filter Section Types
 *
 * Shared types for all filter section components
 */

import type { AppliedFilter, FilterType } from '../../types';

export interface FilterSectionProps {
  onApply: (filter: AppliedFilter) => void;
}

export interface ActivityFilterSectionProps extends FilterSectionProps {
  activities: string[];
}

export interface SequenceFilterSectionProps extends FilterSectionProps {
  activities: string[];
}

export interface PerformanceFilterSectionProps extends FilterSectionProps {
  caseDuration: { min: number; max: number; mean: number; p90?: number };
}

export interface TimeRangeFilterSectionProps extends FilterSectionProps {
  timeRange: { start: string; end: string };
}

export interface ResourceFilterSectionProps extends FilterSectionProps {
  resources: string[];
}

export interface ReworkFilterSectionProps extends FilterSectionProps {
  activities: string[];
}

/** Color mapping for filter types */
export const FILTER_COLORS: Record<FilterType, string> = {
  timeRange: 'blue',
  activity: 'green',
  activitySequence: 'purple',
  performance: 'orange',
  resource: 'cyan',
  variant: 'magenta',
  rework: 'red',
};
