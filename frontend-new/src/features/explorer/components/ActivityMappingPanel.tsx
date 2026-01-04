/**
 * Activity Mapping Panel
 *
 * UI for creating and managing hierarchical activity mappings.
 */

import { useState } from 'react';

export interface ActivityMapping {
    id: string;
    lowLevelActivity: string;
    highLevelActivity: string;
}

export interface ActivityMappingPanelProps {
    activities: string[];
    existingMappings?: ActivityMapping[];
    onMappingsChange: (mappings: ActivityMapping[]) => void;
    onApply: () => void;
}

export function ActivityMappingPanel({
    activities,
    existingMappings = [],
    onMappingsChange,
    onApply,
}: ActivityMappingPanelProps) {
    const [mappings, setMappings] = useState<ActivityMapping[]>(existingMappings);
    const [selectedActivity, setSelectedActivity] = useState('');
    const [groupName, setGroupName] = useState('');

    const handleAddMapping = () => {
        if (!selectedActivity || !groupName) return;

        const newMapping: ActivityMapping = {
            id: `${Date.now()}-${selectedActivity}`,
            lowLevelActivity: selectedActivity,
            highLevelActivity: groupName,
        };

        const updated = [...mappings, newMapping];
        setMappings(updated);
        onMappingsChange(updated);

        setSelectedActivity('');
        setGroupName('');
    };

    const handleRemoveMapping = (id: string) => {
        const updated = mappings.filter(m => m.id !== id);
        setMappings(updated);
        onMappingsChange(updated);
    };

    const handleAutoGroup = () => {
        // Auto-suggest groupings (5 groups)
        // In real implementation, this would call backend API
        const groupSize = Math.ceil(activities.length / 5);
        const autoMappings: ActivityMapping[] = [];

        activities.forEach((activity, idx) => {
            const groupIdx = Math.floor(idx / groupSize);
            autoMappings.push({
                id: `auto-${idx}`,
                lowLevelActivity: activity,
                highLevelActivity: `Group ${groupIdx + 1}`,
            });
        });

        setMappings(autoMappings);
        onMappingsChange(autoMappings);
    };

    return (
        <div style={containerStyle}>
            <div style={headerStyle}>
                <h3 style={titleStyle}>Activity Mapping</h3>
                <button onClick={handleAutoGroup} style={buttonStyle}>
                    Auto-Group
                </button>
            </div>

            <div style={formStyle}>
                <select
                    value={selectedActivity}
                    onChange={(e) => setSelectedActivity(e.target.value)}
                    style={selectStyle}
                >
                    <option value="">Select activity...</option>
                    {activities.map(act => (
                        <option key={act} value={act}>{act}</option>
                    ))}
                </select>

                <input
                    type="text"
                    placeholder="High-level group name"
                    value={groupName}
                    onChange={(e) => setGroupName(e.target.value)}
                    style={inputStyle}
                />

                <button
                    onClick={handleAddMapping}
                    disabled={!selectedActivity || !groupName}
                    style={addButtonStyle}
                >
                    Add Mapping
                </button>
            </div>

            <div style={listContainerStyle}>
                <div style={listHeaderStyle}>
                    <span>Current Mappings ({mappings.length})</span>
                </div>
                <div style={listStyle}>
                    {mappings.length === 0 ? (
                        <div style={emptyStyle}>No mappings defined</div>
                    ) : (
                        mappings.map(mapping => (
                            <div key={mapping.id} style={mappingItemStyle}>
                                <div style={mappingTextStyle}>
                                    <span style={lowLevelStyle}>{mapping.lowLevelActivity}</span>
                                    <span style={arrowStyle}>→</span>
                                    <span style={highLevelStyle}>{mapping.highLevelActivity}</span>
                                </div>
                                <button
                                    onClick={() => handleRemoveMapping(mapping.id)}
                                    style={removeButtonStyle}
                                >
                                    ×
                                </button>
                            </div>
                        ))
                    )}
                </div>
            </div>

            <button
                onClick={onApply}
                disabled={mappings.length === 0}
                style={applyButtonStyle}
            >
                Apply & Discover
            </button>
        </div>
    );
}

// Styles
const containerStyle: React.CSSProperties = {
    background: '#fff',
    borderRadius: '8px',
    padding: '16px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    minWidth: '320px',
};

const headerStyle: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '16px',
};

const titleStyle: React.CSSProperties = {
    margin: 0,
    fontSize: '16px',
    fontWeight: 600,
};

const buttonStyle: React.CSSProperties = {
    padding: '6px 12px',
    fontSize: '13px',
    background: '#f0f0f0',
    border: '1px solid #d9d9d9',
    borderRadius: '4px',
    cursor: 'pointer',
};

const formStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
    marginBottom: '16px',
};

const selectStyle: React.CSSProperties = {
    padding: '8px',
    border: '1px solid #d9d9d9',
    borderRadius: '4px',
    fontSize: '14px',
};

const inputStyle: React.CSSProperties = {
    padding: '8px',
    border: '1px solid #d9d9d9',
    borderRadius: '4px',
    fontSize: '14px',
};

const addButtonStyle: React.CSSProperties = {
    padding: '8px',
    background: '#1890ff',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
};

const listContainerStyle: React.CSSProperties = {
    marginBottom: '16px',
};

const listHeaderStyle: React.CSSProperties = {
    fontSize: '13px',
    fontWeight: 500,
    marginBottom: '8px',
    color: '#666',
};

const listStyle: React.CSSProperties = {
    maxHeight: '200px',
    overflowY: 'auto',
    border: '1px solid #e8e8e8',
    borderRadius: '4px',
    padding: '8px',
};

const emptyStyle: React.CSSProperties = {
    textAlign: 'center',
    color: '#999',
    fontSize: '13px',
    padding: '16px',
};

const mappingItemStyle: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '8px',
    background: '#fafafa',
    borderRadius: '4px',
    marginBottom: '4px',
};

const mappingTextStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '13px',
};

const lowLevelStyle: React.CSSProperties = {
    color: '#333',
    fontFamily: 'monospace',
};

const arrowStyle: React.CSSProperties = {
    color: '#999',
};

const highLevelStyle: React.CSSProperties = {
    color: '#1890ff',
    fontWeight: 500,
};

const removeButtonStyle: React.CSSProperties = {
    background: 'none',
    border: 'none',
    cursor: 'pointer',
    fontSize: '20px',
    color: '#ff4d4f',
    padding: '0 4px',
};

const applyButtonStyle: React.CSSProperties = {
    width: '100%',
    padding: '10px',
    background: '#52c41a',
    color: '#fff',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: 500,
};

export default ActivityMappingPanel;
