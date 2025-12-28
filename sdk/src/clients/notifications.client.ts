/**
 * Notifications Client - Alert & Notification Management
 * 
 * Business verbs:
 * - send() - Send a notification
 * - list() - List notifications
 * - get() - Get notification details
 * - listChannels() - Get available channels
 * - subscribe() - Subscribe to events
 * - configure() - Configure notification channel
 */

import { HttpClient } from '../client.js';
import {
  Notification,
  NotificationChannelInfo,
  SendNotificationOptions,
} from '../types/workflows.js';

export class NotificationsClient {
  constructor(private readonly http: HttpClient) {}

  /**
   * Send a notification.
   */
  async send(options: SendNotificationOptions): Promise<{ status: string; notificationId: string }> {
    return this.http.post('/notifications/send', options);
  }

  /**
   * List notifications with optional filtering.
   */
  async list(channel?: string): Promise<Notification[]> {
    return this.http.get<Notification[]>('/notifications/', { channel });
  }

  /**
   * Get notification details.
   */
  async get(notificationId: string): Promise<Notification> {
    return this.http.get<Notification>(`/notifications/${notificationId}`);
  }

  /**
   * List available notification channels.
   */
  async listChannels(): Promise<NotificationChannelInfo[]> {
    const response = await this.http.get<{ channels: NotificationChannelInfo[] }>(
      '/notifications/channels'
    );
    return response.channels;
  }

  /**
   * Subscribe to event notifications.
   */
  async subscribe(eventType: string, channel: string, recipient: string): Promise<{ subscriptionId: string }> {
    return this.http.post('/notifications/subscribe', {
      event_type: eventType,
      channel,
      recipient,
    });
  }

  /**
   * Configure a notification channel.
   */
  async configure(channel: string, settings: Record<string, unknown>): Promise<void> {
    await this.http.post('/notifications/configure', { channel, settings });
  }
}
