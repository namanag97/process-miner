'use client';

import { useMemo } from 'react';
import type { Node, Edge } from '@xyflow/react';
import type { ProcessModel, ActivityStats, DirectlyFollowsEdge } from '@/lib/mining/types';
import type { ActivityNodeData } from './nodes/ActivityNode';
import type { ProcessEdgeData } from './edges/ProcessEdge';
import { createLogger } from '@/lib/debug-logger';

const logger = createLogger('process-map-flow');

interface FlowData {
    nodes: Node<ActivityNodeData>[];
    edges: Edge<ProcessEdgeData>[];
}

/**
 * Assigns layer to each activity based on typical flow order
 * Start activities = layer 0, end activities = max layer, others in between
 */
function assignLayers(
    activities: ActivityStats[],
    dfgEdges: DirectlyFollowsEdge[]
): Map<string, number> {
    const layers = new Map<string, number>();

    // Find start and end activities
    const startActivities = activities.filter(a => a.isStart).map(a => a.name);

    // If no explicit start activities, use the ones with no incoming edges or just the first one
    let effectiveStartActivities = [...startActivities];

    // Build adjacency list
    const successors = new Map<string, string[]>();
    // Track incoming edge counts to help identify start nodes if none marked
    const incomingCounts = new Map<string, number>();

    for (const edge of dfgEdges) {
        if (!successors.has(edge.source)) {
            successors.set(edge.source, []);
        }
        successors.get(edge.source)!.push(edge.target);

        incomingCounts.set(edge.target, (incomingCounts.get(edge.target) || 0) + 1);
    }

    // Fallback if no start activities found
    if (effectiveStartActivities.length === 0 && activities.length > 0) {
        // Try nodes with no incoming edges
        const noIncoming = activities
            .map(a => a.name)
            .filter(name => !incomingCounts.has(name) || incomingCounts.get(name) === 0);

        if (noIncoming.length > 0) {
            effectiveStartActivities = noIncoming;
        } else {
            // Just pick the first one to break the cycle
            effectiveStartActivities = [activities[0].name];
        }
    }

    // BFS from start activities
    const queue: Array<{ activity: string; layer: number }> = [];

    // Initialize start activities at layer 0
    for (const start of effectiveStartActivities) {
        layers.set(start, 0);
        queue.push({ activity: start, layer: 0 });
    }

    // Track updates to prevent infinite loops in cycles
    // Limit updates to total number of activities * 2 to allow for some re-layering but prevent infinite cycling
    const updateCounts = new Map<string, number>();
    const MAX_UPDATES = activities.length * 2;

    // Process queue
    while (queue.length > 0) {
        const { activity, layer } = queue.shift()!;
        const succs = successors.get(activity) || [];

        for (const succ of succs) {
            const currentLayer = layers.get(succ);
            const newLayer = layer + 1;

            const currentUpdates = updateCounts.get(succ) || 0;

            // Only update if we found a longer path (for better layout)
            // AND we haven't updated this node too many times (breaking cycles)
            if ((currentLayer === undefined || newLayer > currentLayer) && currentUpdates < MAX_UPDATES) {
                layers.set(succ, newLayer);
                updateCounts.set(succ, currentUpdates + 1);
                queue.push({ activity: succ, layer: newLayer });
            }
        }
    }

    // Handle unreachable nodes
    const maxLayer = Math.max(...Array.from(layers.values()), 0);
    for (const activity of activities) {
        if (!layers.has(activity.name)) {
            // Place disconnected nodes at layer 0 or after max layer
            layers.set(activity.name, 0);
        }
    }

    return layers;
}

/**
 * Convert ProcessModel to ReactFlow nodes and edges
 */
export function useProcessMapFlow(model: ProcessModel | null): FlowData {
    return useMemo(() => {
        if (!model) {
            return { nodes: [], edges: [] };
        }

        const { activities, edges: dfgEdges } = model;

        logger.info(`🎨 Rendering process map with ${activities.length} activities and ${dfgEdges.length} edges`);

        // Calculate max frequency for normalization
        const maxActivityFreq = Math.max(...activities.map(a => a.frequency), 1);
        const maxEdgeFreq = Math.max(...dfgEdges.map(e => e.frequency), 1);

        // Assign layers for left-to-right layout
        const layers = assignLayers(activities, dfgEdges);
        const _maxLayer = Math.max(...Array.from(layers.values()), 0);

        // Group activities by layer
        const layerGroups = new Map<number, ActivityStats[]>();
        for (const activity of activities) {
            const layer = layers.get(activity.name) || 0;
            if (!layerGroups.has(layer)) {
                layerGroups.set(layer, []);
            }
            layerGroups.get(layer)!.push(activity);
        }

        // Position nodes
        const LAYER_WIDTH = 250;
        const NODE_HEIGHT = 100;
        const PADDING_X = 50;
        const PADDING_Y = 50;

        const nodes: Node<ActivityNodeData>[] = activities.map(activity => {
            const layer = layers.get(activity.name) || 0;
            const layerActivities = layerGroups.get(layer) || [];
            const indexInLayer = layerActivities.findIndex(a => a.name === activity.name);
            const totalInLayer = layerActivities.length;

            // Center activities within their layer
            const x = PADDING_X + layer * LAYER_WIDTH;
            const y = PADDING_Y + indexInLayer * NODE_HEIGHT - ((totalInLayer - 1) * NODE_HEIGHT) / 2 + 200;

            return {
                id: activity.name,
                type: 'activityNode',
                position: { x, y },
                data: {
                    label: activity.name,
                    frequency: activity.frequency,
                    isStart: activity.isStart,
                    isEnd: activity.isEnd,
                    avgDuration: activity.avgDuration,
                    maxFrequency: maxActivityFreq,
                },
            };
        });

        // Create edges
        const edges: Edge<ProcessEdgeData>[] = dfgEdges.map((edge, index) => ({
            id: `edge-${index}`,
            source: edge.source,
            target: edge.target,
            type: 'processEdge',
            data: {
                frequency: edge.frequency,
                avgDuration: edge.avgDuration,
                caseCount: edge.cases.length,
                maxFrequency: maxEdgeFreq,
            },
        }));

        logger.info(`Created ${nodes.length} nodes and ${edges.length} edges for ReactFlow`);

        return { nodes, edges };
    }, [model]);
}
