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
    LabelList,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { ProcessModel } from '@/lib/mining/types';
import { formatDuration } from '@/lib/utils';

interface DurationChartProps {
    model: ProcessModel;
}

const COLORS = {
    normal: '#6366f1',
    bottleneck: '#ef4444',
};

export function DurationChart({ model }: DurationChartProps) {
    const { activities } = model;

    const chartData = useMemo(() => {
        // Sort by duration descending
        const sorted = [...activities]
            .filter((a) => a.avgDuration > 0)
            .sort((a, b) => b.avgDuration - a.avgDuration);

        const maxDuration = sorted[0]?.avgDuration || 0;

        return sorted.map((activity) => ({
            name: activity.name,
            duration: activity.avgDuration,
            formattedDuration: formatDuration(activity.avgDuration),
            isBottleneck: activity.avgDuration === maxDuration && sorted.length > 1,
        }));
    }, [activities]);

    if (chartData.length === 0) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle className="text-lg">Duration by Activity</CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-muted-foreground text-sm">No duration data available</p>
                </CardContent>
            </Card>
        );
    }

    const bottleneckActivity = chartData.find((d) => d.isBottleneck);

    return (
        <Card>
            <CardHeader className="pb-2">
                <CardTitle className="text-lg flex items-center justify-between">
                    <span>Duration by Activity</span>
                    {bottleneckActivity && (
                        <span className="text-sm font-normal text-red-600">
                            🔥 Bottleneck: {bottleneckActivity.name}
                        </span>
                    )}
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                            data={chartData}
                            layout="vertical"
                            margin={{ top: 5, right: 80, left: 100, bottom: 5 }}
                        >
                            <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} />
                            <XAxis
                                type="number"
                                tickFormatter={(value) => formatDuration(value)}
                                fontSize={12}
                            />
                            <YAxis
                                type="category"
                                dataKey="name"
                                width={90}
                                fontSize={12}
                                tickLine={false}
                            />
                            <Tooltip
                                formatter={(value) => value != null ? [formatDuration(value as number), 'Avg Duration'] : ['N/A', 'Avg Duration']}
                                labelStyle={{ fontWeight: 'bold' }}
                            />
                            <Bar dataKey="duration" radius={[0, 4, 4, 0]}>
                                {chartData.map((entry, index) => (
                                    <Cell
                                        key={`cell-${index}`}
                                        fill={entry.isBottleneck ? COLORS.bottleneck : COLORS.normal}
                                    />
                                ))}
                                <LabelList
                                    dataKey="formattedDuration"
                                    position="right"
                                    fontSize={11}
                                    fill="#64748b"
                                />
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </CardContent>
        </Card>
    );
}
