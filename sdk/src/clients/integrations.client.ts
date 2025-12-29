/**
 * Integrations Client - External System Connectors
 *
 * Business verbs:
 * - listConnectorTypes() - Get available connector types
 * - createConnector() - Create new connector
 * - listConnectors() - List all connectors
 * - getConnector() - Get connector details
 * - removeConnector() - Delete connector
 * - connect() - Connect to external system
 * - disconnect() - Disconnect from external system
 * - testConnection() - Test connector connection
 * - sync() - Synchronize data from external system
 * - listTables() - Get available tables from connector
 * - fetchData() - Fetch event data from connector
 */

import { HttpClient } from "../client.js";
import {
  ConnectorTypeInfo,
  Connector,
  CreateConnectorOptions,
  SyncResult,
} from "../types/workflows.js";

export class IntegrationsClient {
  constructor(private readonly http: HttpClient) {}

  /**
   * List available connector types.
   */
  async listConnectorTypes(): Promise<ConnectorTypeInfo[]> {
    return this.http.get<ConnectorTypeInfo[]>("/integrations/connector-types");
  }

  /**
   * Create a new connector configuration.
   */
  async createConnector(options: CreateConnectorOptions): Promise<Connector> {
    return this.http.post<Connector>("/integrations/connectors", {
      name: options.name,
      connector_type: options.connectorType,
      settings: options.settings,
    });
  }

  /**
   * List all configured connectors.
   */
  async listConnectors(): Promise<Connector[]> {
    return this.http.get<Connector[]>("/integrations/connectors");
  }

  /**
   * Get connector details.
   */
  async getConnector(connectorId: string): Promise<Connector> {
    return this.http.get<Connector>(`/integrations/connectors/${connectorId}`);
  }

  /**
   * Remove a connector configuration.
   */
  async removeConnector(connectorId: string): Promise<void> {
    await this.http.delete(`/integrations/connectors/${connectorId}`);
  }

  /**
   * Connect to an external system.
   */
  async connect(connectorId: string): Promise<{ status: string }> {
    return this.http.post(`/integrations/connectors/${connectorId}/connect`);
  }

  /**
   * Disconnect from an external system.
   */
  async disconnect(connectorId: string): Promise<{ status: string }> {
    return this.http.post(`/integrations/connectors/${connectorId}/disconnect`);
  }

  /**
   * Test connector connection.
   */
  async testConnection(connectorId: string): Promise<{ success: boolean; message: string }> {
    return this.http.post(`/integrations/connectors/${connectorId}/test`);
  }

  /**
   * Synchronize data from external system.
   */
  async sync(connectorId: string): Promise<SyncResult> {
    return this.http.post<SyncResult>(`/integrations/connectors/${connectorId}/sync`);
  }

  /**
   * List available tables from a connected data source.
   */
  async listTables(connectorId: string): Promise<string[]> {
    const response = await this.http.get<{ tables: string[] }>(
      `/integrations/connectors/${connectorId}/tables`
    );
    return response.tables;
  }

  /**
   * Fetch event data from connector into the system.
   */
  async fetchData(
    connectorId: string,
    tableName: string,
    columnMapping: Record<string, string>
  ): Promise<{ logId: string; eventsImported: number }> {
    return this.http.post(`/integrations/connectors/${connectorId}/fetch`, {
      table_name: tableName,
      column_mapping: columnMapping,
    });
  }

  /**
   * Get synchronization history.
   */
  async getSyncHistory(): Promise<SyncResult[]> {
    return this.http.get<SyncResult[]>("/integrations/sync-history");
  }
}
