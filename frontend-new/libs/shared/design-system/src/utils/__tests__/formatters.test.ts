/**
 * Formatter Utilities Tests
 *
 * Tests for duration, number, and percentage formatting utilities.
 * These are pure functions with no dependencies - ideal for unit testing.
 */

import {
  formatDuration,
  formatDurationFromSeconds,
  formatCompactNumber,
  formatPercentage,
} from '../index';

describe('formatDuration', () => {
  describe('milliseconds', () => {
    it('formats sub-second durations', () => {
      expect(formatDuration(0)).toBe('0s');
      expect(formatDuration(500)).toBe('500ms');
      expect(formatDuration(999)).toBe('999ms');
    });

    it('formats seconds', () => {
      expect(formatDuration(1000)).toBe('1s');
      expect(formatDuration(30000)).toBe('30s');
      expect(formatDuration(59000)).toBe('59s');
    });

    it('formats minutes', () => {
      expect(formatDuration(60000)).toBe('1m');
      expect(formatDuration(90000)).toBe('1m'); // 1.5 min rounds to 1m
      expect(formatDuration(3540000)).toBe('59m');
    });

    it('formats hours', () => {
      expect(formatDuration(3600000)).toBe('1h');
      expect(formatDuration(5400000)).toBe('1h 30m');
      expect(formatDuration(7200000)).toBe('2h');
    });

    it('formats days', () => {
      expect(formatDuration(86400000)).toBe('1d');
      expect(formatDuration(172800000)).toBe('2d');
      expect(formatDuration(90000000)).toBe('1d 1h');
    });

    it('formats complex durations', () => {
      // 2 days, 3 hours, 15 minutes
      const duration = (2 * 24 * 60 * 60 + 3 * 60 * 60 + 15 * 60) * 1000;
      expect(formatDuration(duration)).toBe('2d 3h 15m');
    });
  });
});

describe('formatDurationFromSeconds', () => {
  it('converts seconds to formatted duration', () => {
    expect(formatDurationFromSeconds(0)).toBe('0s');
    expect(formatDurationFromSeconds(30)).toBe('30s');
    expect(formatDurationFromSeconds(60)).toBe('1m');
    expect(formatDurationFromSeconds(3600)).toBe('1h');
    expect(formatDurationFromSeconds(86400)).toBe('1d');
  });

  it('handles fractional seconds', () => {
    expect(formatDurationFromSeconds(0.5)).toBe('500ms');
    expect(formatDurationFromSeconds(1.5)).toBe('2s'); // rounds up
  });
});

describe('formatCompactNumber', () => {
  it('returns numbers under 1000 as-is', () => {
    expect(formatCompactNumber(0)).toBe('0');
    expect(formatCompactNumber(1)).toBe('1');
    expect(formatCompactNumber(999)).toBe('999');
  });

  it('formats thousands with K suffix', () => {
    expect(formatCompactNumber(1000)).toBe('1K');
    expect(formatCompactNumber(1500)).toBe('1.5K');
    expect(formatCompactNumber(10000)).toBe('10K');
    expect(formatCompactNumber(999999)).toBe('1000K');
  });

  it('formats millions with M suffix', () => {
    expect(formatCompactNumber(1000000)).toBe('1M');
    expect(formatCompactNumber(2500000)).toBe('2.5M');
    expect(formatCompactNumber(999999999)).toBe('1000M');
  });

  it('formats billions with B suffix', () => {
    expect(formatCompactNumber(1000000000)).toBe('1B');
    expect(formatCompactNumber(2500000000)).toBe('2.5B');
  });

  it('removes trailing .0 from formatted numbers', () => {
    expect(formatCompactNumber(2000)).toBe('2K');
    expect(formatCompactNumber(2000000)).toBe('2M');
    expect(formatCompactNumber(2000000000)).toBe('2B');
  });
});

describe('formatPercentage', () => {
  it('formats with default 1 decimal place', () => {
    expect(formatPercentage(0)).toBe('0.0%');
    expect(formatPercentage(50)).toBe('50.0%');
    expect(formatPercentage(100)).toBe('100.0%');
    expect(formatPercentage(33.333)).toBe('33.3%');
  });

  it('respects custom decimal places', () => {
    expect(formatPercentage(33.3333, 0)).toBe('33%');
    expect(formatPercentage(33.3333, 2)).toBe('33.33%');
    expect(formatPercentage(33.3333, 3)).toBe('33.333%');
  });

  it('handles edge cases', () => {
    expect(formatPercentage(-5)).toBe('-5.0%');
    expect(formatPercentage(150)).toBe('150.0%');
    expect(formatPercentage(0.1)).toBe('0.1%');
  });
});
