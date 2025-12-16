'use client';

import { useMemo } from 'react';
import { Clock, AlertTriangle, RotateCcw } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { ProcessModel, Deviation } from '@/lib/mining/types';
import { formatDuration } from '@/lib/utils';

interface TopListsProps {
    model: ProcessModel;
    cases: Array<{
        caseId: string;
        duration: number;
    }>;
}

interface ReworkInfo {
    activity: string;
    frequency: number;
    caseCount: number;
}

export function TopLists({ model, cases }: TopListsProps) {
    // Top 5 longest cases
    const longestCases = useMemo(() => {
        return [...cases]
            .sort((a, b) => b.duration - a.duration)
            .slice(0, 5);
    }, [cases]);

    // Top 5 most reworked activities
    const mostReworked = useMemo((): ReworkInfo[] => {
        const reworkDeviations = model.deviations.filter((d) => d.type === 'rework');

        // Extract activity name from deviation description
        const reworkMap = new Map<string, { frequency: number; cases: Set<string> }>();

        reworkDeviations.forEach((d) => {
            const match = d.description.match(/Activity '([^']+)'/);
            if (match) {
                const activity = match[1];
                const existing = reworkMap.get(activity) || { frequency: 0, cases: new Set<string>() };
                existing.frequency += d.frequency;
                d.affectedCases.forEach((c) => existing.cases.add(c));
                reworkMap.set(activity, existing);
            }
        });

        return Array.from(reworkMap.entries())
            .map(([activity, data]) => ({
                activity,
                frequency: data.frequency,
                caseCount: data.cases.size,
            }))
            .sort((a, b) => b.frequency - a.frequency)
            .slice(0, 5);
    }, [model.deviations]);

    return (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Longest Cases */}
            <Card>
                <CardHeader className="pb-2">
                    <CardTitle className="text-lg flex items-center gap-2">
                        <Clock className="h-5 w-5 text-orange-500" />
                        Longest Cases
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    {longestCases.length === 0 ? (
                        <p className="text-muted-foreground text-sm">No case data available</p>
                    ) : (
                        <div className="space-y-3">
                            {longestCases.map((c, idx) => (
                                <div
                                    key={c.caseId}
                                    className="flex items-center justify-between p-2 rounded-lg bg-muted/50"
                                >
                                    <div className="flex items-center gap-3">
                                        <Badge variant="outline" className="font-mono w-6 h-6 flex items-center justify-center p-0">
                                            {idx + 1}
                                        </Badge>
                                        <span className="font-mono text-sm truncate max-w-[120px]" title={c.caseId}>
                                            {c.caseId}
                                        </span>
                                    </div>
                                    <span className="text-sm font-medium text-orange-600">
                                        {formatDuration(c.duration)}
                                    </span>
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Most Reworked Activities */}
            <Card>
                <CardHeader className="pb-2">
                    <CardTitle className="text-lg flex items-center gap-2">
                        <RotateCcw className="h-5 w-5 text-red-500" />
                        Most Reworked Activities
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    {mostReworked.length === 0 ? (
                        <div className="flex items-center gap-2 text-muted-foreground text-sm">
                            <AlertTriangle className="h-4 w-4" />
                            No rework detected in this process
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {mostReworked.map((r, idx) => (
                                <div
                                    key={r.activity}
                                    className="flex items-center justify-between p-2 rounded-lg bg-muted/50"
                                >
                                    <div className="flex items-center gap-3">
                                        <Badge variant="outline" className="font-mono w-6 h-6 flex items-center justify-center p-0">
                                            {idx + 1}
                                        </Badge>
                                        <span className="text-sm truncate max-w-[140px]" title={r.activity}>
                                            {r.activity}
                                        </span>
                                    </div>
                                    <div className="text-right">
                                        <span className="text-sm font-medium text-red-600">
                                            {r.caseCount} cases
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
