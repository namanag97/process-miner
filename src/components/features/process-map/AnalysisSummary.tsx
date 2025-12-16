'use client';

import {
    LayoutGrid,
    Activity,
    GitBranch,
    Clock,
    TrendingUp,
    CheckCircle,
} from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import type { ProcessModel } from '@/lib/mining/types';
import { formatDuration } from '@/lib/utils';

interface AnalysisSummaryProps {
    model: ProcessModel;
}

interface StatCardProps {
    icon: React.ReactNode;
    label: string;
    value: string | number;
    subtext?: string;
}

function StatCard({ icon, label, value, subtext }: StatCardProps) {
    return (
        <Card>
            <CardContent className="flex items-center gap-3 p-4">
                <div className="rounded-lg bg-primary/10 p-2 text-primary">
                    {icon}
                </div>
                <div>
                    <p className="text-2xl font-bold">{value}</p>
                    <p className="text-xs text-muted-foreground">{label}</p>
                    {subtext && (
                        <p className="text-xs text-muted-foreground">{subtext}</p>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}

export function AnalysisSummary({ model }: AnalysisSummaryProps) {
    const { stats, activities, variants } = model;

    // Calculate happy path percentage
    const happyPathVariant = variants.find((v) => v.isHappyPath);
    const happyPathPercentage = happyPathVariant
        ? Math.round(happyPathVariant.percentage)
        : 0;

    return (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            <StatCard
                icon={<LayoutGrid className="h-5 w-5" />}
                label="Total Cases"
                value={stats.totalCases.toLocaleString()}
            />

            <StatCard
                icon={<Activity className="h-5 w-5" />}
                label="Total Events"
                value={stats.totalEvents.toLocaleString()}
            />

            <StatCard
                icon={<GitBranch className="h-5 w-5" />}
                label="Unique Activities"
                value={activities.length}
            />

            <StatCard
                icon={<TrendingUp className="h-5 w-5" />}
                label="Process Variants"
                value={variants.length}
            />

            <StatCard
                icon={<Clock className="h-5 w-5" />}
                label="Avg Duration"
                value={formatDuration(stats.avgCaseDuration)}
            />

            <StatCard
                icon={<CheckCircle className="h-5 w-5" />}
                label="Happy Path"
                value={`${happyPathPercentage}%`}
                subtext="of cases"
            />
        </div>
    );
}
