'use client';

import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

/**
 * Loading skeleton for metric cards
 */
export function MetricCardSkeleton() {
    return (
        <Card>
            <CardContent className="pt-6">
                <div className="flex items-start justify-between">
                    <div className="space-y-2">
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-8 w-16" />
                        <Skeleton className="h-3 w-32" />
                    </div>
                    <Skeleton className="h-10 w-10 rounded-lg" />
                </div>
            </CardContent>
        </Card>
    );
}

/**
 * Loading skeleton for the metrics grid
 */
export function MetricsGridSkeleton() {
    return (
        <div className="space-y-4">
            <Skeleton className="h-6 w-24" />
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {Array.from({ length: 8 }).map((_, i) => (
                    <MetricCardSkeleton key={i} />
                ))}
            </div>
        </div>
    );
}

/**
 * Loading skeleton for charts
 */
export function ChartSkeleton({ height = 300 }: { height?: number }) {
    return (
        <Card>
            <CardHeader className="pb-2">
                <Skeleton className="h-5 w-40" />
            </CardHeader>
            <CardContent>
                <Skeleton className="w-full" style={{ height }} />
            </CardContent>
        </Card>
    );
}

/**
 * Loading skeleton for tables
 */
export function TableSkeleton({ rows = 5 }: { rows?: number }) {
    return (
        <Card>
            <CardHeader className="pb-4">
                <div className="flex items-center justify-between">
                    <Skeleton className="h-5 w-32" />
                    <Skeleton className="h-9 w-64" />
                </div>
            </CardHeader>
            <CardContent>
                <div className="space-y-3">
                    {/* Header row */}
                    <div className="flex gap-4 pb-2 border-b">
                        <Skeleton className="h-4 w-24" />
                        <Skeleton className="h-4 w-32" />
                        <Skeleton className="h-4 w-20" />
                        <Skeleton className="h-4 w-16" />
                        <Skeleton className="h-4 w-20" />
                    </div>
                    {/* Data rows */}
                    {Array.from({ length: rows }).map((_, i) => (
                        <div key={i} className="flex gap-4 py-2">
                            <Skeleton className="h-4 w-24" />
                            <Skeleton className="h-4 w-32" />
                            <Skeleton className="h-4 w-20" />
                            <Skeleton className="h-4 w-16" />
                            <Skeleton className="h-4 w-20" />
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}

/**
 * Loading skeleton for process map
 */
export function ProcessMapSkeleton() {
    return (
        <Card className="h-[500px]">
            <CardContent className="pt-6 h-full flex items-center justify-center">
                <div className="space-y-4 w-full max-w-md">
                    <div className="flex justify-center gap-8">
                        <Skeleton className="h-16 w-16 rounded-full" />
                        <Skeleton className="h-16 w-24 rounded-lg" />
                        <Skeleton className="h-16 w-24 rounded-lg" />
                        <Skeleton className="h-16 w-16 rounded-full" />
                    </div>
                    <div className="flex justify-center">
                        <Skeleton className="h-1 w-64" />
                    </div>
                    <div className="flex justify-center gap-8">
                        <Skeleton className="h-16 w-24 rounded-lg" />
                        <Skeleton className="h-16 w-24 rounded-lg" />
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}

/**
 * Generic page loading skeleton
 */
export function PageSkeleton() {
    return (
        <div className="p-6 space-y-6 animate-pulse">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="space-y-2">
                    <Skeleton className="h-8 w-48" />
                    <Skeleton className="h-4 w-32" />
                </div>
                <div className="flex gap-2">
                    <Skeleton className="h-9 w-24" />
                    <Skeleton className="h-9 w-24" />
                </div>
            </div>

            {/* Content */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {Array.from({ length: 4 }).map((_, i) => (
                    <MetricCardSkeleton key={i} />
                ))}
            </div>

            <ChartSkeleton height={250} />
        </div>
    );
}
