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
    const _endActivities = activities.filter(a => a.isEnd).map(a => a.name);

    // Build adjacency list
    const successors = new Map<string, string[]>();
    for (const edge of dfgEdges) {
        if (!successors.has(edge.source)) {
            successors.set(edge.source, []);
        }
        successors.get(edge.source)!.push(edge.target);
    }

    // BFS from start activities
    const queue: Array<{ activity: string; layer: number }> = [];

    // Initialize start activities at layer 0
    for (const start of startActivities) {
        layers.set(start, 0);
        queue.push({ activity: start, layer: 0 });
    }

    // Process queue
    while (queue.length > 0) {
        const { activity, layer } = queue.shift()!;
        const succs = successors.get(activity) || [];

        for (const succ of succs) {
            const currentLayer = layers.get(succ);
            const newLayer = layer + 1;

            // Only update if we found a longer path (for better layout)
            if (currentLayer === undefined || newLayer > currentLayer) {
                layers.set(succ, newLayer);
                queue.push({ activity: succ, layer: newLayer });
            }
        }
    }

    // Handle activities not reachable from start (shouldn't happen normally)
    for (const activity of activities) {
        if (!layers.has(activity.name)) {
            // Put them in the middle
            const maxLayer = Math.max(...Array.from(layers.values()), 0);
            layers.set(activity.name, Math.floor(maxLayer / 2));
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
