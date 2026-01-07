/**
 * DiscoveryPage - Process Discovery Dashboard
 * 
 * Allows users to:
 * 1. Select a dataset
 * 2. Choose a discovery algorithm
 * 3. Configure parameters
 * 4. Run discovery (async job)
 * 5. View and interact with discovered models
 */

import { useState, useCallback, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { logAction, logError } from '@lumina/design-system';
import {
    useModelVisualization,
} from '../hooks';
import { JobStatusPanel, ModelList, JSONViewer, GraphViewer } from '../components';
import { AnalysisModeSelector } from '../../explorer/components/AnalysisModeSelector';
import type { Job, DiscoveredModel, ModelFormat } from '../types';
import type { ProcessModel } from '@/api/sdk';
import styles from './DiscoveryPage.module.css';

export function DiscoveryPage() {
    // IMPORTANT: Use datasetId (not datasetId) - this is the standard naming convention
    // Route: /workspace/:projectId/data/:datasetId/discovery
    const { datasetId, projectId } = useParams<{ datasetId: string; projectId: string }>();
    const navigate = useNavigate();

    // Log page mount
    useEffect(() => {
        logAction('DiscoveryPage', 'page_mounted', { datasetId, projectId });
    }, [datasetId, projectId]);

    // State
    const [activeJobId, setActiveJobId] = useState<string | null>(null);
    const [selectedModel, setSelectedModel] = useState<DiscoveredModel | null>(null);
    const [showAlgorithmSelector, setShowAlgorithmSelector] = useState(false);

    // Mutations and queries
    const { data: modelDetail } = useModelVisualization(selectedModel?.id || '');

    // Handle discovery completion
    const handleJobComplete = useCallback((job: Job) => {
        logAction('DiscoveryPage', 'job_completed', { jobId: job.id, entityId: job.entityId });
        setActiveJobId(null);
        // If job created a model, select it
        if (job.entityId) {
            // Refetch models list will pick it up
        }
    }, []);

    const handleJobError = useCallback((error: Error) => {
        logError('DiscoveryPage', error, { jobId: activeJobId });
        setActiveJobId(null);
    }, [activeJobId]);

    // Handle starting discovery
    const handleAnalysisStarted = useCallback((jobIdOrModelId: string) => {
        logAction('DiscoveryPage', 'discovery_started', { jobId: jobIdOrModelId, datasetId });
        setActiveJobId(jobIdOrModelId);
        setShowAlgorithmSelector(false);
    }, [datasetId]);

    // Handle model selection
    const handleSelectModel = useCallback((model: DiscoveredModel) => {
        logAction('DiscoveryPage', 'model_selected', { modelId: model.id, modelFormat: model.modelFormat });
        setSelectedModel(model);
    }, []);

    // Render model visualization based on format
    const renderModelVisualization = () => {
        if (!selectedModel || !modelDetail) {
            return (
                <div className={styles.emptyViewer}>
                    <span className={styles.emptyIcon}>📊</span>
                    <p>Select a model to view</p>
                </div>
            );
        }

        const format = selectedModel.modelFormat as ModelFormat;

        // Graph-based models (DFG, Petri Net, Transition System, etc.)
        if (['dfg', 'performance_dfg', 'petri_net', 'transition_system', 'prefix_tree'].includes(format)) {
            // Transform model data to graph format
            const graphData = transformToGraphData(modelDetail);
            return (
                <GraphViewer
                    nodes={graphData.nodes}
                    edges={graphData.edges}
                    title={selectedModel.name}
                />
            );
        }

        // JSON-based models (Temporal Profile, Log Skeleton, Declare, etc.)
        if (['temporal_profile', 'log_skeleton', 'declare', 'batches'].includes(format)) {
            return (
                <JSONViewer
                    data={modelDetail.data ?? modelDetail}
                    title={selectedModel.name}
                />
            );
        }

        // Default fallback
        return (
            <JSONViewer
                data={modelDetail.data ?? modelDetail}
                title={selectedModel.name}
            />
        );
    };

    if (!datasetId) {
        return (
            <div className={styles.container}>
                <div className={styles.error}>
                    No dataset selected. Please navigate from a dataset page.
                </div>
            </div>
        );
    }

    return (
        <div className={styles.container}>
            {/* Header */}
            <div className={styles.header}>
                <div className={styles.headerLeft}>
                    <button className={styles.backButton} onClick={() => navigate(-1)}>
                        ← Back
                    </button>
                    <h1 className={styles.title}>Process Discovery</h1>
                </div>
                <button
                    className={styles.runButton}
                    onClick={() => setShowAlgorithmSelector(true)}
                    disabled={!!activeJobId}
                >
                    {activeJobId ? 'Running...' : '+ Run Discovery'}
                </button>
            </div>

            {/* Main Content */}
            <div className={styles.content}>
                {/* Left Panel - Models List */}
                <div className={styles.leftPanel}>
                    <ModelList
                        datasetId={datasetId}
                        selectedModelId={selectedModel?.id}
                        onSelectModel={handleSelectModel}
                    />

                    {/* Active Job Status */}
                    {activeJobId && (
                        <div className={styles.jobSection}>
                            <h3 className={styles.sectionTitle}>Running Job</h3>
                            <JobStatusPanel
                                jobId={activeJobId}
                                onComplete={handleJobComplete}
                                onError={handleJobError}
                            />
                        </div>
                    )}
                </div>

                {/* Right Panel - Visualization */}
                <div className={styles.rightPanel}>
                    {renderModelVisualization()}
                </div>
            </div>

            {/* Algorithm Selector Modal */}
            {showAlgorithmSelector && (
                <div className={styles.modalOverlay} onClick={() => setShowAlgorithmSelector(false)}>
                    <div className={styles.modal} onClick={e => e.stopPropagation()}>
                        <AnalysisModeSelector
                            datasetId={datasetId}
                            onAnalysisStarted={handleAnalysisStarted}
                            onClose={() => setShowAlgorithmSelector(false)}
                        />
                    </div>
                </div>
            )}
        </div>
    );
}

// Type definitions for model data
interface DFGNode {
    id?: string;
    name?: string;
    label?: string;
    isStart?: boolean;
    is_start?: boolean;
    isEnd?: boolean;
    is_end?: boolean;
}

interface DFGEdge {
    source: string;
    target: string;
    frequency?: number;
}

interface PetriPlace {
    name?: string;
    id?: string;
    tokens?: number;
}

interface PetriTransition {
    name?: string;
    id?: string;
    label?: string;
}

interface PetriArc {
    source: string | { name?: string };
    target: string | { name?: string };
}

interface ModelData {
    // DFG format
    nodes?: DFGNode[];
    edges?: DFGEdge[];
    // Petri Net format
    places?: PetriPlace[];
    transitions?: PetriTransition[];
    arcs?: PetriArc[];
}

// Helper to transform model data to graph format
function transformToGraphData(model: ProcessModel) {
    // Extract the data from the model (could be in data field or directly on the model)
    const modelDetail = (model.data || model) as ModelData;
    // Handle DFG format (already has nodes/edges)
    if (modelDetail.nodes && modelDetail.edges) {
        return {
            nodes: modelDetail.nodes.map((n) => ({
                id: n.id || n.name || '',
                label: n.label || n.name || n.id || '',
                isStart: n.isStart || n.is_start,
                isEnd: n.isEnd || n.is_end,
            })),
            edges: modelDetail.edges.map((e) => ({
                source: e.source,
                target: e.target,
                label: e.frequency ? String(e.frequency) : undefined,
            })),
        };
    }

    // Handle Petri Net (places, transitions, arcs)
    if (modelDetail.places && modelDetail.transitions) {
        const nodes = [
            ...modelDetail.places.map((p) => ({
                id: p.name || p.id || '',
                label: p.name || '',
                type: 'place' as const,
                tokens: p.tokens,
            })),
            ...modelDetail.transitions.map((t) => ({
                id: t.name || t.id || '',
                label: t.label || t.name || '',
                type: 'transition' as const,
            })),
        ];

        const edges = (modelDetail.arcs || []).map((a) => ({
            source: typeof a.source === 'string' ? a.source : (a.source?.name || ''),
            target: typeof a.target === 'string' ? a.target : (a.target?.name || ''),
        }));

        return { nodes, edges };
    }

    // Fallback - try to extract any structure
    return { nodes: [], edges: [] };
}

export default DiscoveryPage;
