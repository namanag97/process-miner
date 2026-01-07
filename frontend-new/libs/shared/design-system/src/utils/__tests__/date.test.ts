/**
 * Date Utilities Tests
 *
 * Tests for date formatting utilities.
 */

import { formatTimeAgo, formatDuration, formatDateRange } from '../date';

describe('formatTimeAgo', () => {
  const now = new Date('2024-06-15T12:00:00Z');

  beforeEach(() => {
    jest.useFakeTimers();
    jest.setSystemTime(now);
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('returns "Just now" for very recent times', () => {
    const date = new Date('2024-06-15T11:59:30Z'); // 30 seconds ago
    expect(formatTimeAgo(date)).toBe('Just now');
  });

  it('formats minutes ago', () => {
    expect(formatTimeAgo(new Date('2024-06-15T11:55:00Z'))).toBe('5m ago');
    expect(formatTimeAgo(new Date('2024-06-15T11:30:00Z'))).toBe('30m ago');
    expect(formatTimeAgo(new Date('2024-06-15T11:01:00Z'))).toBe('59m ago');
  });

  it('formats hours ago', () => {
    expect(formatTimeAgo(new Date('2024-06-15T11:00:00Z'))).toBe('1h ago');
    expect(formatTimeAgo(new Date('2024-06-15T06:00:00Z'))).toBe('6h ago');
    expect(formatTimeAgo(new Date('2024-06-14T13:00:00Z'))).toBe('23h ago');
  });

  it('formats days ago', () => {
    expect(formatTimeAgo(new Date('2024-06-14T12:00:00Z'))).toBe('1d ago');
    expect(formatTimeAgo(new Date('2024-06-12T12:00:00Z'))).toBe('3d ago');
    expect(formatTimeAgo(new Date('2024-06-09T12:00:00Z'))).toBe('6d ago');
  });

  it('formats weeks ago', () => {
    expect(formatTimeAgo(new Date('2024-06-08T12:00:00Z'))).toBe('1w ago');
    expect(formatTimeAgo(new Date('2024-06-01T12:00:00Z'))).toBe('2w ago');
    expect(formatTimeAgo(new Date('2024-05-18T12:00:00Z'))).toBe('4w ago');
  });

  it('formats as date for older dates', () => {
    const oldDate = new Date('2024-05-01T12:00:00Z');
    const result = formatTimeAgo(oldDate);
    // Should return a date string (format depends on locale)
    expect(result).not.toContain('ago');
  });
});

describe('formatDuration (seconds)', () => {
  it('formats seconds', () => {
    expect(formatDuration(0)).toBe('0s');
    expect(formatDuration(30)).toBe('30s');
    expect(formatDuration(59)).toBe('59s');
  });

  it('formats minutes', () => {
    expect(formatDuration(60)).toBe('1m');
    expect(formatDuration(90)).toBe('2m'); // rounds 1.5 to 2
    expect(formatDuration(3599)).toBe('60m');
  });

  it('formats hours', () => {
    expect(formatDuration(3600)).toBe('1h');
    expect(formatDuration(5400)).toBe('1h 30m');
    expect(formatDuration(7200)).toBe('2h');
    expect(formatDuration(86399)).toBe('23h 60m');
  });

  it('formats days', () => {
    expect(formatDuration(86400)).toBe('1d');
    expect(formatDuration(90000)).toBe('1d 1h');
    expect(formatDuration(172800)).toBe('2d');
    expect(formatDuration(259200)).toBe('3d');
  });
});

describe('formatDateRange', () => {
  it('returns single date when start and end are same day', () => {
    const start = new Date('2024-06-15T00:00:00Z');
    const end = new Date('2024-06-15T23:59:59Z');
    const result = formatDateRange(start, end);
    // Both should format to the same date string
    expect(result).not.toContain(' - ');
  });

  it('returns range when start and end are different days', () => {
    const start = new Date('2024-06-01T00:00:00Z');
    const end = new Date('2024-06-15T00:00:00Z');
    const result = formatDateRange(start, end);
    expect(result).toContain(' - ');
  });
});
