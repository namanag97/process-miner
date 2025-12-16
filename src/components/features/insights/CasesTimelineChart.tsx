'use client';

import { useMemo } from 'react';
import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { format, parseISO, startOfDay, startOfWeek, startOfMonth, eachDayOfInterval, eachWeekOfInterval, eachMonthOfInterval } from 'date-fns';

interface CasesTimelineChartProps {
    cases: Array<{
        caseId: string;
        startTime: Date;
    }>;
}

type TimeGranularity = 'day' | 'week' | 'month';

function determineGranularity(start: Date, end: Date): TimeGranularity {
    const diffMs = end.getTime() - start.getTime();
    const diffDays = diffMs / (1000 * 60 * 60 * 24);

    if (diffDays <= 14) return 'day';
    if (diffDays <= 90) return 'week';
    return 'month';
}

function formatDateKey(date: Date, granularity: TimeGranularity): string {
    switch (granularity) {
        case 'day':
            return format(date, 'yyyy-MM-dd');
        case 'week':
            return format(startOfWeek(date), 'yyyy-MM-dd');
        case 'month':
            return format(startOfMonth(date), 'yyyy-MM');
    }
}

function formatLabel(dateKey: string, granularity: TimeGranularity): string {
    switch (granularity) {
        case 'day':
            return format(parseISO(dateKey), 'MMM d');
        case 'week':
            return `Week of ${format(parseISO(dateKey), 'MMM d')}`;
        case 'month':
            return format(parseISO(dateKey + '-01'), 'MMM yyyy');
    }
}

export function CasesTimelineChart({ cases }: CasesTimelineChartProps) {
    const chartData = useMemo(() => {
        if (cases.length === 0) return { data: [], granularity: 'day' as TimeGranularity };

        // Find date range
        const dates = cases.map((c) => c.startTime);
        const minDate = new Date(Math.min(...dates.map((d) => d.getTime())));
        const maxDate = new Date(Math.max(...dates.map((d) => d.getTime())));

        // Determine granularity
        const granularity = determineGranularity(minDate, maxDate);

        // Count cases per time period
        const counts = new Map<string, number>();
        cases.forEach((c) => {
            const key = formatDateKey(c.startTime, granularity);
            counts.set(key, (counts.get(key) || 0) + 1);
        });

        // Generate all periods in range
        let periods: Date[];
        switch (granularity) {
            case 'day':
                periods = eachDayOfInterval({ start: startOfDay(minDate), end: startOfDay(maxDate) });
                break;
            case 'week':
                periods = eachWeekOfInterval({ start: startOfWeek(minDate), end: startOfWeek(maxDate) });
                break;
            case 'month':
                periods = eachMonthOfInterval({ start: startOfMonth(minDate), end: startOfMonth(maxDate) });
                break;
        }

        const data = periods.map((date) => {
            const key = formatDateKey(date, granularity);
            return {
                date: key,
                label: formatLabel(key, granularity),
                cases: counts.get(key) || 0,
            };
        });

        return { data, granularity };
    }, [cases]);

    // Don't show if all cases are on the same day
    if (chartData.data.length <= 1) {
        return null;
    }

    return (
        <Card>
            <CardHeader className="pb-2">
                <CardTitle className="text-lg">Cases Over Time</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="h-[250px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart
                            data={chartData.data}
                            margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                        >
                            <CartesianGrid strokeDasharray="3 3" vertical={false} />
                            <XAxis
                                dataKey="label"
                                fontSize={11}
                                tickLine={false}
                                axisLine={false}
                                interval="preserveStartEnd"
                            />
                            <YAxis
                                fontSize={12}
                                tickLine={false}
                                axisLine={false}
                                allowDecimals={false}
                            />
                            <Tooltip
                                formatter={(value) => [value ?? 0, 'Cases Started']}
                                labelFormatter={(label) => label}
                            />
                            <Line
                                type="monotone"
                                dataKey="cases"
                                stroke="#6366f1"
                                strokeWidth={2}
                                dot={{ fill: '#6366f1', strokeWidth: 0, r: 4 }}
                                activeDot={{ r: 6 }}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
                <p className="text-xs text-muted-foreground text-center mt-2">
                    Grouped by {chartData.granularity}
                </p>
            </CardContent>
        </Card>
    );
}
