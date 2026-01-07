/**
 * AnalysisModeSelector Component
 *
 * Allows users to select a discovery/analysis algorithm and configure its parameters.
 * Fetches available analysis types dynamically from the backend.
 */

import { useState, useEffect, useCallback } from 'react';
import { sdk } from '@/src/api/sdk';
import styles from './AnalysisModeSelector.module.css';

// ============================================
// Types
// ============================================

interface ConfigSchemaField {
    type: 'string' | 'integer' | 'float' | 'boolean';
    default?: unknown;
    min?: number;
    max?: number;
    enum?: string[];
    description?: string;
}

interface AnalysisTypeInfo {
    name: string;
    category: string;
    description: string;
    result_type: string;
    config_schema: Record<string, ConfigSchemaField>;
}

interface AnalysisMetadata {
    categories: string[];
    analysis_types: Record<string, AnalysisTypeInfo>;
}

export interface AnalysisModeSelectorProps {
    datasetId: string;
    onAnalysisStarted?: (jobId: string) => void;
    onClose?: () => void;
}

// ============================================
// Component
// ============================================

export function AnalysisModeSelector({
    datasetId,
    onAnalysisStarted,
    onClose,
}: AnalysisModeSelectorProps) {
    const [metadata, setMetadata] = useState<AnalysisMetadata | null>(null);
    const [selectedCategory, setSelectedCategory] = useState<string>('Discovery');
    const [selectedType, setSelectedType] = useState<string | null>(null);
    const [config, setConfig] = useState<Record<string, unknown>>({});
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    // Fetch analysis metadata on mount
    useEffect(() => {
        async function fetchMetadata() {
            setIsLoading(true);
            try {
                const data = await sdk.analyses.getMetadata();
                setMetadata(data);
                // Set default category
                if (data.categories && data.categories.length > 0) {
                    setSelectedCategory(data.categories.includes('Discovery') ? 'Discovery' : data.categories[0]);
                }
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Unknown error');
            } finally {
                setIsLoading(false);
            }
        }
        fetchMetadata();
    }, []);

    // Filter analysis types by selected category
    const filteredTypes = metadata
        ? Object.entries(metadata.analysis_types).filter(
            ([, info]) => info.category === selectedCategory
        )
        : [];

    // Initialize config when analysis type is selected
    useEffect(() => {
        if (selectedType && metadata) {
            const typeInfo = metadata.analysis_types[selectedType];
            if (typeInfo) {
                const initialConfig: Record<string, unknown> = {};
                Object.entries(typeInfo.config_schema).forEach(([key, field]) => {
                    initialConfig[key] = field.default;
                });
                setConfig(initialConfig);
            }
        }
    }, [selectedType, metadata]);

    const handleConfigChange = useCallback((key: string, value: unknown) => {
        setConfig((prev) => ({ ...prev, [key]: value }));
    }, []);

    const handleSubmit = async () => {
        if (!selectedType || !datasetId) return;

        setIsSubmitting(true);
        setError(null);

        try {
            // For discovery algorithms, use the discovery endpoint
            const typeInfo = metadata?.analysis_types[selectedType];
            const isDiscovery = typeInfo?.category === 'Discovery';

            if (isDiscovery) {
                // Map analysis type to miner type
                const minerTypeMap: Record<string, string> = {
                    dfg_discovery: 'dfg',
                    alpha_miner: 'alpha',
                    inductive_miner: 'inductive',
                    inductive_infrequent: 'inductive_infrequent',
                    heuristic_miner: 'heuristics',
                    performance_dfg: 'performance_dfg',
                    ilp_miner: 'ilp',
                    powl_miner: 'powl',
                    bpmn_discovery: 'bpmn_inductive',
                    declare_miner: 'declare',
                    log_skeleton: 'log_skeleton',
                    temporal_profile: 'temporal_profile',
                    prefix_tree: 'prefix_tree',
                    transition_system: 'transition_system',
                };

                const minerType = (minerTypeMap[selectedType] || selectedType) as 'alpha' | 'inductive' | 'heuristic' | 'split';

                const result = await sdk.discovery.discover({
                    datasetId,
                    minerType,
                    modelName: `${typeInfo?.name || selectedType} Model`,
                });

                onAnalysisStarted?.(result.jobId || result.modelId || '');
            } else {
                // For other analysis types, use the analyses endpoint
                const result = await sdk.analyses.create(datasetId, {
                    name: `${typeInfo?.name || selectedType} Analysis`,
                    analysisType: selectedType,
                    config,
                });

                onAnalysisStarted?.(result.id);
            }

            onClose?.();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to start analysis');
        } finally {
            setIsSubmitting(false);
        }
    };

    // ============================================
    // Render
    // ============================================

    if (isLoading) {
        return (
            <div className={styles.container}>
                <div className={styles.loading}>Loading analysis types...</div>
            </div>
        );
    }

    if (error && !metadata) {
        return (
            <div className={styles.container}>
                <div className={styles.error}>{error}</div>
            </div>
        );
    }

    const selectedTypeInfo = selectedType ? metadata?.analysis_types[selectedType] : null;

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h2 className={styles.title}>Run Analysis</h2>
                {onClose && (
                    <button className={styles.closeButton} onClick={onClose} aria-label="Close">
                        ×
                    </button>
                )}
            </div>

            {/* Category Tabs */}
            <div className={styles.categories}>
                {metadata?.categories.map((category) => (
                    <button
                        key={category}
                        className={`${styles.categoryTab} ${selectedCategory === category ? styles.active : ''}`}
                        onClick={() => {
                            setSelectedCategory(category);
                            setSelectedType(null);
                        }}
                    >
                        {category}
                    </button>
                ))}
            </div>

            {/* Analysis Types List */}
            <div className={styles.typesList}>
                {filteredTypes.map(([typeKey, typeInfo]) => (
                    <div
                        key={typeKey}
                        className={`${styles.typeCard} ${selectedType === typeKey ? styles.selected : ''}`}
                        onClick={() => setSelectedType(typeKey)}
                    >
                        <div className={styles.typeName}>{typeInfo.name}</div>
                        <div className={styles.typeDescription}>{typeInfo.description}</div>
                        <div className={styles.typeResultBadge}>{typeInfo.result_type}</div>
                    </div>
                ))}
            </div>

            {/* Configuration Form */}
            {selectedTypeInfo && Object.keys(selectedTypeInfo.config_schema).length > 0 && (
                <div className={styles.configSection}>
                    <h3 className={styles.configTitle}>Configuration</h3>
                    <div className={styles.configForm}>
                        {Object.entries(selectedTypeInfo.config_schema).map(([key, field]) => (
                            <div key={key} className={styles.configField}>
                                <label className={styles.configLabel}>
                                    {key.replace(/_/g, ' ')}
                                    {field.description && (
                                        <span className={styles.configHint} title={field.description}>
                                            ℹ️
                                        </span>
                                    )}
                                </label>
                                {renderConfigInput(key, field, config[key], handleConfigChange)}
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Error Message */}
            {error && <div className={styles.errorMessage}>{error}</div>}

            {/* Action Buttons */}
            <div className={styles.actions}>
                <button
                    className={styles.runButton}
                    onClick={handleSubmit}
                    disabled={!selectedType || isSubmitting}
                >
                    {isSubmitting ? 'Running...' : 'Run Analysis'}
                </button>
            </div>
        </div>
    );
}

// ============================================
// Config Input Renderer
// ============================================

function renderConfigInput(
    key: string,
    field: ConfigSchemaField,
    value: unknown,
    onChange: (key: string, value: unknown) => void
) {
    if (field.enum) {
        return (
            <select
                className={styles.configSelect}
                value={String(value ?? field.default ?? '')}
                onChange={(e) => onChange(key, e.target.value)}
            >
                {field.enum.map((opt) => (
                    <option key={opt} value={opt}>
                        {opt}
                    </option>
                ))}
            </select>
        );
    }

    if (field.type === 'boolean') {
        return (
            <input
                type="checkbox"
                className={styles.configCheckbox}
                checked={Boolean(value ?? field.default)}
                onChange={(e) => onChange(key, e.target.checked)}
            />
        );
    }

    if (field.type === 'integer' || field.type === 'float') {
        return (
            <input
                type="number"
                className={styles.configInput}
                value={String(value ?? field.default ?? '')}
                min={field.min}
                max={field.max}
                step={field.type === 'float' ? 0.1 : 1}
                onChange={(e) => {
                    const val = field.type === 'float' ? parseFloat(e.target.value) : parseInt(e.target.value, 10);
                    onChange(key, isNaN(val) ? field.default : val);
                }}
            />
        );
    }

    return (
        <input
            type="text"
            className={styles.configInput}
            value={String(value ?? field.default ?? '')}
            onChange={(e) => onChange(key, e.target.value)}
        />
    );
}

export default AnalysisModeSelector;
