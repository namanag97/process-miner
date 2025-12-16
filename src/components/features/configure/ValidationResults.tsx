'use client';

import { CheckCircle2, AlertCircle, XCircle, Activity, Calendar, Hash, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { cn } from '@/lib/utils';
import type { ValidationResult, ValidationCheck } from '@/lib/validation';

interface ValidationResultsProps {
    result: ValidationResult;
}

const statusIcons = {
    success: CheckCircle2,
    warning: AlertCircle,
    error: XCircle,
};

const statusColors = {
    success: 'text-green-600 dark:text-green-400',
    warning: 'text-yellow-600 dark:text-yellow-400',
    error: 'text-red-600 dark:text-red-400',
};

function ValidationCheckItem({ check }: { check: ValidationCheck }) {
    const Icon = statusIcons[check.status];

    return (
        <div className="flex items-start gap-3 py-2">
            <Icon className={cn('h-5 w-5 mt-0.5 shrink-0', statusColors[check.status])} />
            <div className="flex-1 min-w-0">
                <p className="font-medium text-sm">{check.label}</p>
                <p className="text-sm text-muted-foreground">{check.message}</p>
            </div>
        </div>
    );
}

function StatCard({
    icon: Icon,
    label,
    value
}: {
    icon: typeof Activity;
    label: string;
    value: string | number;
}) {
    return (
        <div className="flex items-center gap-3 rounded-lg border p-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-primary/10">
                <Icon className="h-4 w-4 text-primary" />
            </div>
            <div>
                <p className="text-lg font-bold">{value}</p>
                <p className="text-xs text-muted-foreground">{label}</p>
            </div>
        </div>
    );
}

export function ValidationResults({ result }: ValidationResultsProps) {
    const { checks, statistics, activities } = result;

    return (
        <div className="space-y-6">
            {/* Validation Checks */}
            <Card>
                <CardHeader className="pb-3">
                    <CardTitle className="text-base">Validation Results</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="divide-y">
                        {checks.map((check) => (
                            <ValidationCheckItem key={check.id} check={check} />
                        ))}
                    </div>
                </CardContent>
            </Card>

            {/* Statistics */}
            <Card>
                <CardHeader className="pb-3">
                    <CardTitle className="text-base">Data Statistics</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        <StatCard
                            icon={Hash}
                            label="Total Events"
                            value={statistics.totalEvents.toLocaleString()}
                        />
                        <StatCard
                            icon={Activity}
                            label="Total Cases"
                            value={statistics.totalCases.toLocaleString()}
                        />
                        <StatCard
                            icon={TrendingUp}
                            label="Unique Activities"
                            value={statistics.uniqueActivities}
                        />
                        <StatCard
                            icon={Calendar}
                            label="Avg Events/Case"
                            value={statistics.avgEventsPerCase}
                        />
                    </div>

                    {statistics.dateRange && (
                        <div className="mt-4 flex items-center gap-2 text-sm">
                            <Calendar className="h-4 w-4 text-muted-foreground" />
                            <span className="text-muted-foreground">Date range:</span>
                            <span className="font-medium">
                                {statistics.dateRange.start} to {statistics.dateRange.end}
                            </span>
                        </div>
                    )}

                    <div className="mt-2 text-sm text-muted-foreground">
                        Events per case: {statistics.minEventsPerCase} min, {statistics.maxEventsPerCase} max
                    </div>
                </CardContent>
            </Card>

            {/* Activities List */}
            <Card>
                <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center justify-between">
                        <span>Activities ({activities.length})</span>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <ScrollArea className="h-[150px]">
                        <div className="flex flex-wrap gap-1.5">
                            {activities.map((activity, i) => (
                                <Badge key={i} variant="outline" className="font-normal">
                                    {activity}
                                </Badge>
                            ))}
                        </div>
                    </ScrollArea>
                </CardContent>
            </Card>
        </div>
    );
}
