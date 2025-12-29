import { message, notification } from 'antd';
import type { NotificationArgsProps } from 'antd';
import { tokens } from '../theme';

type ToastType = 'success' | 'error' | 'warning' | 'info' | 'loading';

interface ToastConfig {
  content: string;
  duration?: number;
  key?: string;
  onClose?: () => void;
}

/**
 * Toast utility for lightweight, ephemeral messages
 * 
 * Usage:
 * ```ts
 * toast.success('Operation completed');
 * toast.error('Something went wrong');
 * const hide = toast.loading('Processing...');
 * // later: hide();
 * ```
 */
export const toast = {
  success: (content: string | ToastConfig) => {
    const config = typeof content === 'string' ? { content } : content;
    return message.success(config);
  },

  error: (content: string | ToastConfig) => {
    const config = typeof content === 'string' ? { content } : content;
    return message.error(config);
  },

  warning: (content: string | ToastConfig) => {
    const config = typeof content === 'string' ? { content } : content;
    return message.warning(config);
  },

  info: (content: string | ToastConfig) => {
    const config = typeof content === 'string' ? { content } : content;
    return message.info(config);
  },

  loading: (content: string | ToastConfig) => {
    const config = typeof content === 'string' ? { content, duration: 0 } : { ...content, duration: 0 };
    return message.loading(config);
  },

  destroy: (key?: string) => {
    if (key) {
      message.destroy(key);
    } else {
      message.destroy();
    }
  },
};

interface NotifyConfig extends Omit<NotificationArgsProps, 'message' | 'description'> {
  title: string;
  description?: string;
}

/**
 * Notify utility for richer, persistent notifications
 * 
 * Usage:
 * ```ts
 * notify.success({ title: 'Saved', description: 'Your changes have been saved' });
 * notify.error({ title: 'Error', description: 'Failed to save changes' });
 * ```
 */
export const notify = {
  success: ({ title, description, ...rest }: NotifyConfig) => {
    notification.success({
      message: title,
      description,
      ...rest,
    });
  },

  error: ({ title, description, ...rest }: NotifyConfig) => {
    notification.error({
      message: title,
      description,
      ...rest,
    });
  },

  warning: ({ title, description, ...rest }: NotifyConfig) => {
    notification.warning({
      message: title,
      description,
      ...rest,
    });
  },

  info: ({ title, description, ...rest }: NotifyConfig) => {
    notification.info({
      message: title,
      description,
      ...rest,
    });
  },

  open: ({ title, description, ...rest }: NotifyConfig) => {
    notification.open({
      message: title,
      description,
      ...rest,
    });
  },

  destroy: (key?: string) => {
    if (key) {
      notification.destroy(key);
    } else {
      notification.destroy();
    }
  },
};

/**
 * Format duration in human-readable format
 */
export const formatDuration = (ms: number): string => {
  if (ms < 1000) return `${Math.round(ms)}ms`;
  
  const seconds = Math.floor(ms / 1000);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);
  const days = Math.floor(hours / 24);
  
  if (days > 0) return `${days}d ${hours % 24}h`;
  if (hours > 0) return `${hours}h ${minutes % 60}m`;
  if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
  return `${seconds}s`;
};

/**
 * Format duration from seconds
 */
export const formatDurationFromSeconds = (seconds: number): string => 
  formatDuration(seconds * 1000);

/**
 * Format number with compact notation
 */
export const formatCompactNumber = (num: number): string => {
  if (num < 1000) return num.toString();
  if (num < 1000000) return `${(num / 1000).toFixed(1)}K`;
  if (num < 1000000000) return `${(num / 1000000).toFixed(1)}M`;
  return `${(num / 1000000000).toFixed(1)}B`;
};

/**
 * Format percentage with optional decimal places
 */
export const formatPercentage = (value: number, decimals = 1): string =>
  `${value.toFixed(decimals)}%`;
