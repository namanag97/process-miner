'use client';

import { useState, useMemo, useEffect } from 'react';
import {
    RotateCcw,
    SkipForward,
    Shuffle,
    ChevronDown,
    ChevronRight,
    AlertTriangle,
    Lightbulb,
    Eye,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
    Collapsible,
    CollapsibleContent,
    CollapsibleTrigger,
} from '@/components/ui/collapsible';
import type { ProcessModel, Deviation } from '@/lib/mining/types';
import { createLogger } from '@/lib/debug-logger';
import { cn } from '@/lib/utils';

const logger = createLogger('deviations-tab');

interface DeviationsTabProps {
    model: ProcessModel;
}

interface DeviationWithMeta extends Deviation {
    activity?: string;
    avgRepetitions?: number;
    severity: 'high' | 'medium' | 'low';
}

/**
 * Determine severity based on frequency percentage
 */
function getSeverity(
    frequency: number,
    totalCases: number
): 'high' | 'medium' | 'low' {
    const percentage = (frequency / totalCases) * 100;
    if (percentage >= 10) return 'high';
    if (percentage >= 5) return 'medium';
    return 'low';
}

/**
 * Extract activity name from deviation description
 */
function extractActivity(description: string): string | undefined {
    const match = description.match(/Activity '([^']+)'/);
    return match ? match[1] : undefined;
}

/**
 * Extract avg repetitions from rework description
 */
function extractAvgRepetitions(description: string): number | undefined {
    const match = description.match(/repeated (\d+) times/);
    return match ? parseInt(match[1], 10) : undefined;
}

const SEVERITY_STYLES = {
    high: 'bg-red-500/20 text-red-700 border-red-500/50',
    medium: 'bg-yellow-500/20 text-yellow-700 border-yellow-500/50',
    low: 'bg-gray-500/20 text-gray-700 border-gray-500/50',
};

const SEVERITY_LABELS = {
    high: 'High Impact',
    medium: 'Medium Impact',
    low: 'Low Impact',
};

export function DeviationsTab({ model }: DeviationsTabProps) {
    const { deviations, stats } = model;
    const totalCases = stats.totalCases;

    // Section open states
    const [reworkOpen, setReworkOpen] = useState(true);
    const [skipsOpen, setSkipsOpen] = useState(false);
    const [unusualOpen, setUnusualOpen] = useState(false);
    const [expandedItems, setExpandedItems] = useState<Set<number>>(new Set());

    // Enrich deviations with metadata
    const enrichedDeviations = useMemo<DeviationWithMeta[]>(() => {
        return deviations.map((d) => ({
            ...d,
            activity: extractActivity(d.description),
            avgRepetitions: d.type === 'rework' ? extractAvgRepetitions(d.description) : undefined,
            severity: getSeverity(d.frequency, totalCases),
        }));
    }, [deviations, totalCases]);

    // Group by type
    const reworkDeviations = enrichedDeviations.filter((d) => d.type === 'rework');
    const skipDeviations = enrichedDeviations.filter((d) => d.type === 'skip');
    const unusualDeviations = enrichedDeviations.filter((d) => d.type === 'unusual_path');

    // Calculate summary stats
    const affectedCaseIds = useMemo(() => {
        const ids = new Set<string>();
        deviations.forEach((d) => d.affectedCases.forEach((c) => ids.add(c)));
        return ids;
    }, [deviations]);

    const affectedPercentage = totalCases > 0
        ? ((affectedCaseIds.size / totalCases) * 100).toFixed(1)
        : '0';

    // Most common patterns
    const mostCommonRework = reworkDeviations[0];
    const mostCommonSkip = skipDeviations[0];
    const unusualPathPercentage = unusualDeviations.length > 0
        ? ((unusualDeviations[0].frequency / totalCases) * 100).toFixed(1)
        : '0';

    // Log on mount
    useEffect(() => {
        logger.info(`🔍 Displaying ${deviations.length} deviation patterns`);
    }, [deviations.length]);

    const toggleExpand = (index: number) => {
        setExpandedItems((prev) => {
            const next = new Set(prev);
            if (next.has(index)) {
                next.delete(index);
            } else {
                next.add(index);
            }
            return next;
        });
    };

    // Empty state
    if (deviations.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-12 text-center">
                <div className="rounded-full bg-green-500/10 p-4 mb-4">
                    <AlertTriangle className="h-8 w-8 text-green-600" />
                </div>
                <h3 className="text-lg font-medium">No Deviations Detected</h3>
                <p className="text-sm text-muted-foreground mt-1">
                    All cases follow expected process patterns
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Summary Section */}
            <Card>
                <CardHeader className="pb-2">
                    <CardTitle className="text-lg flex items-center gap-2">
                        <AlertTriangle className="h-5 w-5 text-orange-500" />
                        Deviation Summary
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-2xl font-bold">
                        {deviations.length} <span className="text-base font-normal text-muted-foreground">deviation patterns</span>
                    </p>
                    <p className="text-sm text-muted-foreground mt-1">
                        Affecting <strong>{affectedPercentage}%</strong> of cases ({affectedCaseIds.size} of {totalCases})
                    </p>

                    {/* Key Insights */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4">
                        {mostCommonRework && (
                            <div className="rounded-lg border bg-orange-500/5 border-orange-500/30 p-3">
                                <div className="flex items-center gap-2 text-sm font-medium text-orange-700">
                                    <RotateCcw className="h-4 w-4" />
                                    Most Common Rework
                                </div>
                                <p className="text-sm mt-1 truncate" title={mostCommonRework.activity}>
                                    {mostCommonRework.activity || 'Unknown'}
                                </p>
                                <p className="text-xs text-muted-foreground">
                                    {mostCommonRework.frequency} cases
                                </p>
                            </div>
                        )}

                        {mostCommonSkip && (
                            <div className="rounded-lg border bg-red-500/5 border-red-500/30 p-3">
                                <div className="flex items-center gap-2 text-sm font-medium text-red-700">
                                    <SkipForward className="h-4 w-4" />
                                    Most Common Skip
                                </div>
                                <p className="text-sm mt-1 truncate" title={mostCommonSkip.activity}>
                                    {mostCommonSkip.activity || 'Unknown'}
                                </p>
                                <p className="text-xs text-muted-foreground">
                                    {mostCommonSkip.frequency} cases
                                </p>
                            </div>
                        )}

                        {unusualDeviations.length > 0 && (
                            <div className="rounded-lg border bg-yellow-500/5 border-yellow-500/30 p-3">
                                <div className="flex items-center gap-2 text-sm font-medium text-yellow-700">
                                    <Shuffle className="h-4 w-4" />
                                    Unusual Paths
                                </div>
                                <p className="text-sm mt-1">
                                    {unusualPathPercentage}% of cases
                                </p>
                                <p className="text-xs text-muted-foreground">
                                    {unusualDeviations[0].frequency} cases
                                </p>
                            </div>
                        )}
                    </div>
                </CardContent>
            </Card>

            {/* Collapsible Sections */}
            <ScrollArea className="h-[400px]">
                <div className="space-y-4 pr-4">
                    {/* Rework Section */}
                    {reworkDeviations.length > 0 && (
                        <Collapsible open={reworkOpen} onOpenChange={setReworkOpen}>
                            <Card>
                                <CollapsibleTrigger asChild>
                                    <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors">
                                        <CardTitle className="text-sm font-medium flex items-center justify-between">
                                            <div className="flex items-center gap-2">
                                                <RotateCcw className="h-4 w-4 text-orange-600" />
                                                <span>Rework Patterns</span>
                                                <Badge variant="secondary">{reworkDeviations.length}</Badge>
                                            </div>
                                            {reworkOpen ? (
                                                <ChevronDown className="h-4 w-4" />
                                            ) : (
                                                <ChevronRight className="h-4 w-4" />
                                            )}
                                        </CardTitle>
                                        <p className="text-xs text-muted-foreground text-left">
                                            Activities that repeat within the same case
                                        </p>
                                    </CardHeader>
                                </CollapsibleTrigger>
                                <CollapsibleContent>
                                    <CardContent className="pt-0 space-y-2">
                                        {reworkDeviations.map((deviation, idx) => (
                                            <DeviationItem
                                                key={`rework-${idx}`}
                                                deviation={deviation}
                                                index={idx}
                                                totalCases={totalCases}
                                                expanded={expandedItems.has(idx)}
                                                onToggle={() => toggleExpand(idx)}
                                            />
                                        ))}
                                    </CardContent>
                                </CollapsibleContent>
                            </Card>
                        </Collapsible>
                    )}

                    {/* Skipped Activities Section */}
                    {skipDeviations.length > 0 && (
                        <Collapsible open={skipsOpen} onOpenChange={setSkipsOpen}>
                            <Card>
                                <CollapsibleTrigger asChild>
                                    <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors">
                                        <CardTitle className="text-sm font-medium flex items-center justify-between">
                                            <div className="flex items-center gap-2">
                                                <SkipForward className="h-4 w-4 text-red-600" />
                                                <span>Skipped Activities</span>
                                                <Badge variant="secondary">{skipDeviations.length}</Badge>
                                            </div>
                                            {skipsOpen ? (
                                                <ChevronDown className="h-4 w-4" />
                                            ) : (
                                                <ChevronRight className="h-4 w-4" />
                                            )}
                                        </CardTitle>
                                        <p className="text-xs text-muted-foreground text-left">
                                            Happy path activities that were skipped
                                        </p>
                                    </CardHeader>
                                </CollapsibleTrigger>
                                <CollapsibleContent>
                                    <CardContent className="pt-0 space-y-2">
                                        {skipDeviations.map((deviation, idx) => {
                                            const globalIdx = reworkDeviations.length + idx;
                                            return (
                                                <DeviationItem
                                                    key={`skip-${idx}`}
                                                    deviation={deviation}
                                                    index={globalIdx}
                                                    totalCases={totalCases}
                                                    expanded={expandedItems.has(globalIdx)}
                                                    onToggle={() => toggleExpand(globalIdx)}
                                                />
                                            );
                                        })}
                                    </CardContent>
                                </CollapsibleContent>
                            </Card>
                        </Collapsible>
                    )}

                    {/* Unusual Paths Section */}
                    {unusualDeviations.length > 0 && (
                        <Collapsible open={unusualOpen} onOpenChange={setUnusualOpen}>
                            <Card>
                                <CollapsibleTrigger asChild>
                                    <CardHeader className="cursor-pointer hover:bg-muted/50 transition-colors">
                                        <CardTitle className="text-sm font-medium flex items-center justify-between">
                                            <div className="flex items-center gap-2">
                                                <Shuffle className="h-4 w-4 text-yellow-600" />
                                                <span>Unusual Paths</span>
                                                <Badge variant="secondary">{unusualDeviations.length}</Badge>
                                            </div>
                                            {unusualOpen ? (
                                                <ChevronDown className="h-4 w-4" />
                                            ) : (
                                                <ChevronRight className="h-4 w-4" />
                                            )}
                                        </CardTitle>
                                        <p className="text-xs text-muted-foreground text-left">
                                            Cases following rare process variants (&lt;1% frequency)
                                        </p>
                                    </CardHeader>
                                </CollapsibleTrigger>
                                <CollapsibleContent>
                                    <CardContent className="pt-0 space-y-2">
                                        {unusualDeviations.map((deviation, idx) => {
                                            const globalIdx = reworkDeviations.length + skipDeviations.length + idx;
                                            return (
                                                <DeviationItem
                                                    key={`unusual-${idx}`}
                                                    deviation={deviation}
                                                    index={globalIdx}
                                                    totalCases={totalCases}
                                                    expanded={expandedItems.has(globalIdx)}
                                                    onToggle={() => toggleExpand(globalIdx)}
                                                />
                                            );
                                        })}
                                    </CardContent>
                                </CollapsibleContent>
                            </Card>
                        </Collapsible>
                    )}
                </div>
            </ScrollArea>

            {/* Insights Card */}
            <Card className="bg-gradient-to-r from-blue-500/5 to-purple-500/5 border-blue-500/30">
                <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                        <Lightbulb className="h-4 w-4 text-blue-600" />
                        Insights
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                    {mostCommonRework && (
                        <p>
                            <span className="text-muted-foreground">→</span>{' '}
                            The most common deviation is <strong>rework</strong> of activity &quot;{mostCommonRework.activity}&quot;,
                            affecting <strong>{mostCommonRework.frequency}</strong> cases.
                        </p>
                    )}
                    {mostCommonRework && (
                        <p>
                            <span className="text-muted-foreground">→</span>{' '}
                            Consider investigating why &quot;{mostCommonRework.activity}&quot; requires rework in{' '}
                            <strong>{((mostCommonRework.frequency / totalCases) * 100).toFixed(1)}%</strong> of cases.
                        </p>
                    )}
                    {mostCommonSkip && !mostCommonRework && (
                        <p>
                            <span className="text-muted-foreground">→</span>{' '}
                            The most common deviation is <strong>skipping</strong> activity &quot;{mostCommonSkip.activity}&quot;,
                            affecting <strong>{mostCommonSkip.frequency}</strong> cases.
                        </p>
                    )}
                    {deviations.length > 0 && !mostCommonRework && !mostCommonSkip && (
                        <p>
                            <span className="text-muted-foreground">→</span>{' '}
                            {affectedCaseIds.size} cases follow unusual process paths.
                        </p>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}

interface DeviationItemProps {
    deviation: DeviationWithMeta;
    index: number;
    totalCases: number;
    expanded: boolean;
    onToggle: () => void;
}

function DeviationItem({ deviation, index, totalCases, expanded, onToggle }: DeviationItemProps) {
    const percentage = ((deviation.frequency / totalCases) * 100).toFixed(1);

    return (
        <div
            className={cn(
                'rounded-lg border p-3',
                SEVERITY_STYLES[deviation.severity]
            )}
        >
            <div className="flex items-start justify-between gap-2">
                <div className="flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                        <Badge
                            variant="outline"
                            className={SEVERITY_STYLES[deviation.severity]}
                        >
                            {SEVERITY_LABELS[deviation.severity]}
                        </Badge>
                        {deviation.activity && (
                            <span className="font-medium text-sm">{deviation.activity}</span>
                        )}
                    </div>
                    <p className="text-sm mt-1">{deviation.description}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                        Affects {deviation.affectedCases.length} case{deviation.affectedCases.length !== 1 ? 's' : ''} ({percentage}%)
                    </p>
                </div>
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={onToggle}
                    className="shrink-0"
                >
                    <Eye className="h-4 w-4 mr-1" />
                    {expanded ? 'Hide' : 'Cases'}
                </Button>
            </div>

            {expanded && (
                <div className="mt-3 pt-3 border-t border-current/10">
                    <p className="text-xs font-medium mb-2">Affected Case IDs:</p>
                    <div className="flex flex-wrap gap-1 max-h-32 overflow-y-auto">
                        {deviation.affectedCases.slice(0, 50).map((caseId) => (
                            <code
                                key={caseId}
                                className="text-xs bg-white/50 dark:bg-black/20 px-1.5 py-0.5 rounded"
                            >
                                {caseId}
                            </code>
                        ))}
                        {deviation.affectedCases.length > 50 && (
                            <span className="text-xs text-muted-foreground">
                                ...and {deviation.affectedCases.length - 50} more
                            </span>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
