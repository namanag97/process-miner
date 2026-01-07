/**
 * Filter Section Components
 *
 * Modular filter section components extracted from FilterPanel
 * for better maintainability and testability.
 */

export { ActivityFilterSection } from './ActivityFilterSection';
export { SequenceFilterSection } from './SequenceFilterSection';
export { PerformanceFilterSection } from './PerformanceFilterSection';
export { TimeRangeFilterSection } from './TimeRangeFilterSection';
export { ResourceFilterSection } from './ResourceFilterSection';
export { ReworkFilterSection } from './ReworkFilterSection';

export { FILTER_COLORS } from './types';
export type {
  FilterSectionProps,
  ActivityFilterSectionProps,
  SequenceFilterSectionProps,
  PerformanceFilterSectionProps,
  TimeRangeFilterSectionProps,
  ResourceFilterSectionProps,
  ReworkFilterSectionProps,
} from './types';
