/**
 * FeatureRegistry - Plugin system for dynamic feature loading
 *
 * Enables:
 * - Self-registering feature modules
 * - Dynamic route generation
 * - Dynamic navigation generation
 * - Future extensibility for plugins
 *
 * @example
 * // In feature module (features/projects/index.ts)
 * import { FeatureRegistry } from '@/core/plugins/FeatureRegistry';
 *
 * FeatureRegistry.register({
 *   id: 'projects',
 *   name: 'Projects',
 *   version: '1.0.0',
 *   icon: 'FolderOutlined',
 *   navPath: '/workspace',
 *   navOrder: 1,
 *   routes: projectRoutes,
 * });
 *
 * // In App.tsx or router
 * const routes = FeatureRegistry.getRoutes();
 * const navItems = FeatureRegistry.getNavItems();
 */

import React from 'react';
import type { RouteObject } from 'react-router-dom';
import type { ComponentType, ReactNode } from 'react';

// ============================================
// Types
// ============================================

export interface NavItem {
  id: string;
  label: string;
  path: string;
  icon: string;
  order: number;
  badge?: number;
  children?: NavItem[];
}

export interface FeatureConfig {
  /** Unique feature identifier */
  id: string;
  /** Display name */
  name: string;
  /** Semantic version */
  version: string;
  /** Ant Design icon name */
  icon: string;
  /** Primary navigation path (optional) */
  navPath?: string;
  /** Navigation order (lower = higher) */
  navOrder?: number;
  /** Route configuration */
  routes?: RouteObject[];
  /** Additional navigation items */
  navItems?: NavItem[];
  /** Context providers to wrap the app */
  providers?: ComponentType<{ children: ReactNode }>[];
  /** Feature-specific settings */
  settings?: Record<string, unknown>;
  /** Whether feature is enabled */
  enabled?: boolean;
}

type FeatureListener = () => void;

// ============================================
// Registry Implementation
// ============================================

class FeatureRegistryImpl {
  private features = new Map<string, FeatureConfig>();
  private listeners = new Set<FeatureListener>();
  private initialized = false;

  /**
   * Register a feature module
   */
  register(config: FeatureConfig): void {
    const { id, enabled = true } = config;

    if (!enabled) {
      console.debug(`[FeatureRegistry] Feature ${id} is disabled, skipping registration`);
      return;
    }

    if (this.features.has(id)) {
      console.warn(`[FeatureRegistry] Feature ${id} already registered, overwriting`);
    }

    this.features.set(id, { ...config, enabled });
    this.notifyListeners();

    console.debug(`[FeatureRegistry] Registered feature: ${id} v${config.version}`);
  }

  /**
   * Unregister a feature module
   */
  unregister(id: string): boolean {
    const deleted = this.features.delete(id);
    if (deleted) {
      this.notifyListeners();
      console.debug(`[FeatureRegistry] Unregistered feature: ${id}`);
    }
    return deleted;
  }

  /**
   * Get all registered features (sorted by navOrder)
   */
  getAll(): FeatureConfig[] {
    return Array.from(this.features.values())
      .filter((f) => f.enabled !== false)
      .sort((a, b) => (a.navOrder ?? 100) - (b.navOrder ?? 100));
  }

  /**
   * Get a specific feature by ID
   */
  get(id: string): FeatureConfig | undefined {
    return this.features.get(id);
  }

  /**
   * Check if a feature is registered
   */
  has(id: string): boolean {
    return this.features.has(id);
  }

  /**
   * Get all routes from registered features
   */
  getRoutes(): RouteObject[] {
    return this.getAll().flatMap((f) => f.routes ?? []);
  }

  /**
   * Get navigation items from registered features
   */
  getNavItems(): NavItem[] {
    const items: NavItem[] = [];

    for (const feature of this.getAll()) {
      // Add main nav item if feature has navPath
      if (feature.navPath) {
        items.push({
          id: feature.id,
          label: feature.name,
          path: feature.navPath,
          icon: feature.icon,
          order: feature.navOrder ?? 100,
        });
      }

      // Add additional nav items
      if (feature.navItems) {
        items.push(...feature.navItems);
      }
    }

    return items.sort((a, b) => a.order - b.order);
  }

  /**
   * Get all providers from registered features
   */
  getProviders(): ComponentType<{ children: ReactNode }>[] {
    return this.getAll().flatMap((f) => f.providers ?? []);
  }

  /**
   * Subscribe to registry changes
   */
  subscribe(listener: FeatureListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  /**
   * Mark initialization complete
   */
  markInitialized(): void {
    this.initialized = true;
    console.debug(`[FeatureRegistry] Initialization complete. ${this.features.size} features registered.`);
  }

  /**
   * Check if registry is initialized
   */
  isInitialized(): boolean {
    return this.initialized;
  }

  /**
   * Get feature count
   */
  get size(): number {
    return this.features.size;
  }

  private notifyListeners(): void {
    this.listeners.forEach((listener) => {
      try {
        listener();
      } catch (error) {
        console.error('[FeatureRegistry] Listener error:', error);
      }
    });
  }
}

// ============================================
// Singleton Export
// ============================================

export const FeatureRegistry = new FeatureRegistryImpl();

// ============================================
// React Hook
// ============================================

/**
 * Hook to access FeatureRegistry with reactive updates
 */
export function useFeatureRegistry() {
  const [, forceUpdate] = React.useReducer((x: number) => x + 1, 0);

  React.useEffect(() => {
    return FeatureRegistry.subscribe(forceUpdate);
  }, []);

  return FeatureRegistry;
}

/**
 * Hook to get navigation items from registry
 */
export function useFeatureNavigation(): NavItem[] {
  const registry = useFeatureRegistry();
  return registry.getNavItems();
}

/**
 * Hook to get routes from registry
 */
export function useFeatureRoutes(): RouteObject[] {
  const registry = useFeatureRegistry();
  return registry.getRoutes();
}
