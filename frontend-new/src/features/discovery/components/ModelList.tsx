/**
 * ModelList Component
 * 
 * Displays list of discovered models for a dataset with actions.
 */

import { useDiscoveredModels } from '../hooks';
import type { DiscoveredModel, ModelFormat } from '../types';
import styles from './ModelList.module.css';

export interface ModelListProps {
    datasetId: string;
    selectedModelId?: string | null;
    onSelectModel: (model: DiscoveredModel) => void;
    onDeleteModel?: (modelId: string) => void;
}

const formatLabels: Record<ModelFormat, string> = {
    petri_net: 'Petri Net',
    process_tree: 'Process Tree',
    dfg: 'DFG',
    performance_dfg: 'Performance DFG',
    bpmn: 'BPMN',
    powl: 'POWL',
    declare: 'Declare',
    log_skeleton: 'Log Skeleton',
    temporal_profile: 'Temporal Profile',
    prefix_tree: 'Prefix Tree',
    transition_system: 'Transition System',
    batches: 'Batches',
};

const formatIcons: Record<string, string> = {
    petri_net: '🔵',
    process_tree: '🌳',
    dfg: '📊',
    performance_dfg: '⏱️',
    bpmn: '📋',
    powl: '🔀',
    declare: '📝',
    log_skeleton: '🦴',
    temporal_profile: '📅',
    prefix_tree: '🌲',
    transition_system: '🔄',
    batches: '📦',
};

export function ModelList({
    datasetId,
    selectedModelId,
    onSelectModel,
    onDeleteModel
}: ModelListProps) {
    const { data: models, isLoading, error } = useDiscoveredModels(datasetId);

    if (isLoading) {
        return (
            <div className={styles.container}>
                <div className={styles.loading}>
                    <div className={styles.spinner} />
                    <span>Loading models...</span>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className={styles.container}>
                <div className={styles.error}>
                    Failed to load models: {error.message}
                </div>
            </div>
        );
    }

    if (!models || models.length === 0) {
        return (
            <div className={styles.container}>
                <div className={styles.empty}>
                    <span className={styles.emptyIcon}>📭</span>
                    <p>No models discovered yet</p>
                    <p className={styles.emptyHint}>Select an algorithm above to discover a model</p>
                </div>
            </div>
        );
    }

    return (
        <div className={styles.container}>
            <h3 className={styles.title}>Discovered Models ({models.length})</h3>
            <div className={styles.list}>
                {models.map((model) => (
                    <div
                        key={model.id}
                        className={`${styles.modelCard} ${selectedModelId === model.id ? styles.selected : ''}`}
                        onClick={() => onSelectModel(model)}
                    >
                        <div className={styles.modelHeader}>
                            <span className={styles.formatIcon}>
                                {formatIcons[model.modelFormat] || '📄'}
                            </span>
                            <span className={styles.modelName}>{model.name}</span>
                        </div>
                        <div className={styles.modelMeta}>
                            <span className={styles.formatBadge}>
                                {formatLabels[model.modelFormat] || model.modelFormat}
                            </span>
                            <span className={styles.minerType}>{model.minerType}</span>
                        </div>
                        {(model.fitness !== undefined || model.precision !== undefined) && (
                            <div className={styles.metrics}>
                                {model.fitness !== undefined && (
                                    <span className={styles.metric}>
                                        Fitness: {(model.fitness * 100).toFixed(1)}%
                                    </span>
                                )}
                                {model.precision !== undefined && (
                                    <span className={styles.metric}>
                                        Precision: {(model.precision * 100).toFixed(1)}%
                                    </span>
                                )}
                            </div>
                        )}
                        <div className={styles.modelFooter}>
                            <span className={styles.createdAt}>
                                {new Date(model.createdAt).toLocaleDateString()}
                            </span>
                            {onDeleteModel && (
                                <button
                                    className={styles.deleteButton}
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        onDeleteModel(model.id);
                                    }}
                                >
                                    🗑️
                                </button>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default ModelList;
