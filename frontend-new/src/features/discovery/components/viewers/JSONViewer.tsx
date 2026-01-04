/**
 * JSONViewer Component
 * 
 * Display JSON model data (Temporal Profile, Log Skeleton, Batches, etc.)
 */

import styles from './JSONViewer.module.css';

export interface JSONViewerProps {
    data: unknown;
    title?: string;
}

export function JSONViewer({ data, title }: JSONViewerProps) {
    if (!data) {
        return (
            <div className={styles.container}>
                <div className={styles.empty}>No data to display</div>
            </div>
        );
    }

    // Handle temporal profile specifically
    if (isTemporalProfile(data)) {
        return (
            <div className={styles.container}>
                {title && <h3 className={styles.title}>{title}</h3>}
                <div className={styles.tableWrapper}>
                    <table className={styles.table}>
                        <thead>
                            <tr>
                                <th>From Activity</th>
                                <th>To Activity</th>
                                <th>Mean Duration</th>
                                <th>Std Deviation</th>
                            </tr>
                        </thead>
                        <tbody>
                            {Object.entries(data).map(([key, value]) => {
                                const [from, to] = key.replace(/[()'"]/g, '').split(',').map(s => s.trim());
                                const val = value as { mean?: number; stdev?: number } | number[];
                                const mean = Array.isArray(val) ? val[0] : val.mean;
                                const stdev = Array.isArray(val) ? val[1] : val.stdev;
                                return (
                                    <tr key={key}>
                                        <td>{from}</td>
                                        <td>{to}</td>
                                        <td>{formatDuration(mean)}</td>
                                        <td>{formatDuration(stdev)}</td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>
        );
    }

    // Handle declare constraints
    if (isDeclareModel(data)) {
        return (
            <div className={styles.container}>
                {title && <h3 className={styles.title}>{title}</h3>}
                <div className={styles.constraintList}>
                    {Object.entries(data).map(([template, constraints]) => (
                        <div key={template} className={styles.constraintGroup}>
                            <h4 className={styles.templateName}>{formatTemplateName(template)}</h4>
                            <div className={styles.constraints}>
                                {Array.isArray(constraints) ? (
                                    constraints.map((c, i) => (
                                        <span key={i} className={styles.constraintBadge}>
                                            {Array.isArray(c) ? c.join(' → ') : String(c)}
                                        </span>
                                    ))
                                ) : (
                                    <span className={styles.constraintBadge}>{String(constraints)}</span>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        );
    }

    // Default: formatted JSON
    return (
        <div className={styles.container}>
            {title && <h3 className={styles.title}>{title}</h3>}
            <pre className={styles.json}>
                {JSON.stringify(data, null, 2)}
            </pre>
        </div>
    );
}

// Helper functions
function isTemporalProfile(data: unknown): data is Record<string, unknown> {
    if (typeof data !== 'object' || data === null) return false;
    const keys = Object.keys(data);
    return keys.length > 0 && keys.some(k => k.includes(','));
}

function isDeclareModel(data: unknown): data is Record<string, unknown[]> {
    if (typeof data !== 'object' || data === null) return false;
    const keys = Object.keys(data);
    const declareTemplates = ['existence', 'choice', 'responded_existence', 'response', 'precedence'];
    return keys.some(k => declareTemplates.some(t => k.toLowerCase().includes(t)));
}

function formatDuration(seconds: number | undefined): string {
    if (seconds === undefined || seconds === null) return '-';
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    if (seconds < 3600) return `${(seconds / 60).toFixed(1)}m`;
    if (seconds < 86400) return `${(seconds / 3600).toFixed(1)}h`;
    return `${(seconds / 86400).toFixed(1)}d`;
}

function formatTemplateName(name: string): string {
    return name
        .replace(/_/g, ' ')
        .replace(/\b\w/g, l => l.toUpperCase());
}

export default JSONViewer;
