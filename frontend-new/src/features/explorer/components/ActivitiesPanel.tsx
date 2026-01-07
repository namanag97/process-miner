/**
 * ActivitiesPanel - Activity List with Case Coverage
 *
 * Displays all activities in the process with their case coverage percentages.
 * Allows filtering and highlighting by clicking activities.
 */

import { useState, useMemo } from 'react';
import { Input, Button, Badge, Tooltip, Empty } from 'antd';
import { SearchOutlined, PlusOutlined, FilterOutlined } from '@ant-design/icons';
import { tokens } from '@lumina/design-system';

export interface ActivityItem {
    id: string;
    name: string;
    frequency: number;
    casePercent: number;
    avgDuration?: number;
}

export interface ActivitiesPanelProps {
    activities: ActivityItem[];
    selectedActivityId?: string | null;
    onActivityClick?: (activityId: string) => void;
    onFilterWithActivity?: (activityId: string) => void;
    onFilterWithoutActivity?: (activityId: string) => void;
    totalActivities?: number;
    loading?: boolean;
}

export function ActivitiesPanel({
    activities,
    selectedActivityId,
    onActivityClick,
    onFilterWithActivity,
    totalActivities,
    loading = false,
}: ActivitiesPanelProps) {
    const [searchText, setSearchText] = useState('');

    const filteredActivities = useMemo(() => {
        if (!searchText) return activities;
        const lower = searchText.toLowerCase();
        return activities.filter((a) => a.name.toLowerCase().includes(lower));
    }, [activities, searchText]);

    // Sort by case percentage descending
    const sortedActivities = useMemo(() => {
        return [...filteredActivities].sort((a, b) => b.casePercent - a.casePercent);
    }, [filteredActivities]);

    if (loading) {
        return (
            <div style={{ padding: tokens.spacing[4] }}>
                <div className="skeleton" style={{ height: 200 }} />
            </div>
        );
    }

    return (
        <div
            style={{
                display: 'flex',
                flexDirection: 'column',
                height: '100%',
                backgroundColor: tokens.colors.neutral[0],
            }}
        >
            {/* Header */}
            <div
                style={{
                    padding: `${tokens.spacing[3]} ${tokens.spacing[4]}`,
                    borderBottom: `1px solid ${tokens.colors.neutral[200]}`,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                }}
            >
                <span style={{ fontWeight: 600, color: tokens.colors.neutral[900] }}>
                    Activities
                </span>
                <Badge
                    count={`${filteredActivities.length} of ${totalActivities ?? activities.length}`}
                    style={{
                        backgroundColor: tokens.colors.primary[50],
                        color: tokens.colors.primary[600],
                        fontSize: 11,
                        fontWeight: 500,
                    }}
                />
            </div>

            {/* Search */}
            <div style={{ padding: tokens.spacing[3] }}>
                <Input
                    placeholder="Search activities..."
                    prefix={<SearchOutlined style={{ color: tokens.colors.neutral[400] }} />}
                    value={searchText}
                    onChange={(e) => setSearchText(e.target.value)}
                    allowClear
                    size="small"
                    style={{
                        borderRadius: tokens.radius.md,
                    }}
                />
            </div>

            {/* Activities List */}
            <div
                style={{
                    flex: 1,
                    overflowY: 'auto',
                    padding: `0 ${tokens.spacing[2]}`,
                }}
            >
                {sortedActivities.length === 0 ? (
                    <Empty
                        image={Empty.PRESENTED_IMAGE_SIMPLE}
                        description="No activities found"
                        style={{ marginTop: tokens.spacing[8] }}
                    />
                ) : (
                    sortedActivities.map((activity) => (
                        <div
                            key={activity.id}
                            onClick={() => onActivityClick?.(activity.id)}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: tokens.spacing[2],
                                padding: `${tokens.spacing[2]} ${tokens.spacing[3]}`,
                                marginBottom: tokens.spacing[1],
                                borderRadius: tokens.radius.md,
                                cursor: 'pointer',
                                backgroundColor:
                                    selectedActivityId === activity.id
                                        ? tokens.colors.primary[50]
                                        : 'transparent',
                                border:
                                    selectedActivityId === activity.id
                                        ? `1px solid ${tokens.colors.primary[200]}`
                                        : '1px solid transparent',
                                transition: 'all 0.15s ease',
                            }}
                            onMouseEnter={(e) => {
                                if (selectedActivityId !== activity.id) {
                                    e.currentTarget.style.backgroundColor = tokens.colors.neutral[50];
                                }
                            }}
                            onMouseLeave={(e) => {
                                if (selectedActivityId !== activity.id) {
                                    e.currentTarget.style.backgroundColor = 'transparent';
                                }
                            }}
                        >
                            {/* Activity Dot */}
                            <div
                                style={{
                                    width: 8,
                                    height: 8,
                                    borderRadius: '50%',
                                    backgroundColor: tokens.colors.primary[500],
                                    flexShrink: 0,
                                }}
                            />

                            {/* Activity Name */}
                            <span
                                style={{
                                    flex: 1,
                                    fontSize: 13,
                                    color: tokens.colors.neutral[800],
                                    overflow: 'hidden',
                                    textOverflow: 'ellipsis',
                                    whiteSpace: 'nowrap',
                                }}
                            >
                                {activity.name}
                            </span>

                            {/* Case Percentage */}
                            <Tooltip title={`Present in ${activity.casePercent.toFixed(1)}% of cases`}>
                                <span
                                    style={{
                                        fontSize: 11,
                                        fontWeight: 500,
                                        color: tokens.colors.primary[600],
                                        backgroundColor: tokens.colors.primary[50],
                                        padding: '2px 6px',
                                        borderRadius: tokens.radius.sm,
                                    }}
                                >
                                    {activity.casePercent >= 100
                                        ? '100%'
                                        : `+${activity.casePercent.toFixed(0)}%`}
                                </span>
                            </Tooltip>

                            {/* Filter Button (on hover) */}
                            <Tooltip title="Filter to cases with this activity">
                                <Button
                                    type="text"
                                    size="small"
                                    icon={<FilterOutlined style={{ fontSize: 12 }} />}
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        onFilterWithActivity?.(activity.id);
                                    }}
                                    style={{
                                        opacity: 0.5,
                                        padding: '2px 4px',
                                        height: 'auto',
                                    }}
                                />
                            </Tooltip>
                        </div>
                    ))
                )}
            </div>

            {/* Add Filter Button */}
            <div
                style={{
                    padding: tokens.spacing[3],
                    borderTop: `1px solid ${tokens.colors.neutral[200]}`,
                }}
            >
                <Button
                    type="link"
                    icon={<PlusOutlined />}
                    style={{ padding: 0, height: 'auto' }}
                >
                    Add filter
                </Button>
            </div>
        </div>
    );
}

export default ActivitiesPanel;
