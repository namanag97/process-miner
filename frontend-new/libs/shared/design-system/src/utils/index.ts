import { message, notification } from 'antd';

/**
 * Format duration from milliseconds to human-readable string
 * Examples: "2d 3h 15m", "5h 30m", "45m", "30s"
 */
export function formatDuration(ms: number): string {
  if (ms < 1000) return `${Math.round(ms)}ms`;
  
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  const parts: string[] = [];
  
  if (days > 0) parts.push(`${days}d`);
  if (hours % 24 > 0) parts.push(`${hours % 24}h`);
  if (minutes % 60 > 0) parts.push(`${minutes % 60}m`);
  if (parts.length === 0 && seconds % 60 > 0) parts.push(`${seconds % 60}s`);
  
  return parts.join(' ') || '0s';
}

/**
 * Format duration from seconds
 */
export function formatDurationFromSeconds(seconds: number): string {
  return formatDuration(seconds * 1000);
}

/**
 * Format number to compact notation
 * Examples: "1.5K", "2.3M", "45"
 */
export function formatCompactNumber(num: number): string {
  if (num < 1000) return num.toString();
  if (num < 1000000) return `${(num / 1000).toFixed(1).replace(/\.0$/, '')}K`;
  if (num < 1000000000) return `${(num / 1000000).toFixed(1).replace(/\.0$/, '')}M`;
  return `${(num / 1000000000).toFixed(1).replace(/\.0$/, '')}B`;
}

/**
 * Format percentage with specified decimal places
 */
export function formatPercentage(value: number, decimals = 1): string {
  return `${value.toFixed(decimals)}%`;
}

/**
 * Toast notification helpers
 */
export const toast = {
  success: (content: string) => message.success(content),
  error: (content: string) => message.error(content),
  warning: (content: string) => message.warning(content),
  info: (content: string) => message.info(content),
  loading: (content: string) => message.loading(content),
};

/**
 * Persistent notification helpers
 */
export const notify = {
  success: ({ title, description }: { title: string; description?: string }) =>
    notification.success({ message: title, description }),
  error: ({ title, description }: { title: string; description?: string }) =>
    notification.error({ message: title, description }),
  warning: ({ title, description }: { title: string; description?: string }) =>
    notification.warning({ message: title, description }),
  info: ({ title, description }: { title: string; description?: string }) =>
    notification.info({ message: title, description }),
};
