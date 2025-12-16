'use client';

import { useMemo } from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Cell,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { ProcessModel } from '@/lib/mining/types';

interface ActivityFrequencyChartProps {
    model: ProcessModel;
}

// Color tiers based on frequency
function getFrequencyColor(frequency: number, maxFrequency: number): string {
    const ratio = frequency / maxFrequency;
    if (ratio >= 0.8) return '#22c55e'; // green - high
    if (ratio >= 0.5) return '#6366f1'; // indigo - medium
    if (ratio >= 0.2) return '#8b5cf6'; // violet - low-medium
    return '#94a3b8'; // slate - low
}

export function ActivityFrequencyChart({ model }: ActivityFrequencyChartProps) {
    const { activities } = model;

    const chartData = useMemo(() => {
        // Sort by frequency descending
        const sorted = [...activities].sort((a, b) => b.frequency - a.frequency);
        const maxFrequency = sorted[0]?.frequency || 1;

        return sorted.map((activity) => ({
            name: activity.name,
            frequency: activity.frequency,
            color: getFrequencyColor(activity.frequency, maxFrequency),
        }));
    }, [activities]);

    if (chartData.length === 0) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle className="text-lg">Activity Frequency</CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-muted-foreground text-sm">No activity data available</p>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card>
            <CardHeader className="pb-2">
                <CardTitle className="text-lg">Activity Frequency</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                            data={chartData}
                            layout="vertical"
                            margin={{ top: 5, right: 50, left: 100, bottom: 5 }}
                        >
                            <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
                            <XAxis type="number" fontSize={12} />
                            <YAxis
                                type="category"
                                dataKey="name"
                                width={90}
                                fontSize={12}
                                tickLine={false}
                            />
                            <Tooltip
                                formatter={(value: number) => [value.toLocaleString(), 'Occurrences']}
                                labelStyle={{ fontWeight: 'bold' }}
                            />
                            <Bar dataKey="frequency" radius={[0, 4, 4, 0]}>
                                {chartData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
                {/* Legend */}
                <div className="flex items-center justify-center gap-4 mt-4 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1">
                        <div className="w-3 h-3 rounded bg-green-500" />
                        <span>High</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <div className="w-3 h-3 rounded bg-indigo-500" />
                        <span>Medium</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <div className="w-3 h-3 rounded bg-violet-500" />
                        <span>Low-Med</span>
                    </div>
                    <div className="flex items-center gap-1">
                        <div className="w-3 h-3 rounded bg-slate-400" />
                        <span>Low</span>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
