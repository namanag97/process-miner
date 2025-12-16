'use client';

import { useMemo } from 'react';
import {
    BarChart2,
    GitBranch,
    Clock,
    Activity,
    TrendingUp,
    CheckCircle2,
    AlertTriangle,
    Layers,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import type { ProcessModel } from '@/lib/mining/types';
import { formatDuration } from '@/lib/utils';
import { cn } from '@/lib/utils';

interface MetricsGridProps {
    model: ProcessModel;
}

interface MetricCardProps {
    title: string;
    value: string | number;
    subtitle?: string;
    icon: React.ReactNode;
    trend?: 'up' | 'down' | 'neutral';
    color?: 'default' | 'green' | 'yellow' | 'blue';
}

function MetricCard({ title, value, subtitle, icon, color = 'default' }: MetricCardProps) {
    const colorStyles = {
        default: 'bg-muted/50',
        green: 'bg-green-500/10 text-green-600',
        yellow: 'bg-yellow-500/10 text-yellow-600',
        blue: 'bg-blue-500/10 text-blue-600',
    };

    return (
        <Card>
            <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                    <div className="space-y-1">
                        <p className="text-sm text-muted-foreground">{title}</p>
                        <p className="text-2xl font-bold">{value}</p>
                        {subtitle && (
                            <p className="text-xs text-muted-foreground">{subtitle}</p>
                        )}
                    </div>
                    <div className={cn('p-2 rounded-lg', colorStyles[color])}>
                        {icon}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}

export function MetricsGrid({ model }: MetricsGridProps) {
    const { stats, activities, variants, deviations } = model;

    // Calculate derived metrics
    const metrics = useMemo(() => {
        const happyPathVariant = variants.find((v) => v.isHappyPath);
        const happyPathRate = happyPathVariant?.percentage || 0;

        const affectedCases = new Set<string>();
        deviations.forEach((d) => d.affectedCases.forEach((c) => affectedCases.add(c)));
        const deviationRate = stats.totalCases > 0
            ? (affectedCases.size / stats.totalCases) * 100
            : 0;
        const conformanceRate = 100 - deviationRate;

        return {
            totalCases: stats.totalCases,
            totalEvents: stats.totalEvents,
            uniqueActivities: activities.length,
            processVariants: variants.length,
            avgDuration: formatDuration(stats.avgCaseDuration),
            medianDuration: formatDuration(stats.medianCaseDuration),
            happyPathRate: happyPathRate.toFixed(1),
            conformanceRate: conformanceRate.toFixed(1),
        };
    }, [stats, activities, variants, deviations]);

    return (
        <div className="space-y-4">
            <h2 className="text-lg font-semibold">Key Metrics</h2>

            {/* Row 1 */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricCard
                    title="Total Cases"
                    value={metrics.totalCases.toLocaleString()}
                    icon={<Layers className="h-5 w-5" />}
                    color="blue"
                />
                <MetricCard
                    title="Total Events"
                    value={metrics.totalEvents.toLocaleString()}
                    icon={<Activity className="h-5 w-5" />}
                />
                <MetricCard
                    title="Unique Activities"
                    value={metrics.uniqueActivities}
                    icon={<BarChart2 className="h-5 w-5" />}
                />
                <MetricCard
                    title="Process Variants"
                    value={metrics.processVariants}
                    icon={<GitBranch className="h-5 w-5" />}
                />
            </div>

            {/* Row 2 */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <MetricCard
                    title="Average Duration"
                    value={metrics.avgDuration}
                    icon={<Clock className="h-5 w-5" />}
                />
                <MetricCard
                    title="Median Duration"
                    value={metrics.medianDuration}
                    icon={<Clock className="h-5 w-5" />}
                />
                <MetricCard
                    title="Happy Path Rate"
                    value={`${metrics.happyPathRate}%`}
                    subtitle="Cases following the most common path"
                    icon={<TrendingUp className="h-5 w-5" />}
                    color="green"
                />
                <MetricCard
                    title="Conformance Rate"
                    value={`${metrics.conformanceRate}%`}
                    subtitle="Cases without deviations"
                    icon={Number(metrics.conformanceRate) >= 80 ? <CheckCircle2 className="h-5 w-5" /> : <AlertTriangle className="h-5 w-5" />}
                    color={Number(metrics.conformanceRate) >= 80 ? 'green' : 'yellow'}
                />
            </div>
        </div>
    );
}
