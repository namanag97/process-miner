'use client';

import { useEffect, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { AlertTriangle, FileText, Download, Calendar } from 'lucide-react';
import { format } from 'date-fns';

import { Header } from '@/components/layout/Header';
import { NavigationGuard } from '@/components/navigation';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';

import { useAppStore } from '@/lib/stores/useAppStore';
import { createLogger } from '@/lib/debug-logger';

import { MetricsGrid } from './MetricsGrid';
import { DurationChart } from './DurationChart';
import { ActivityFrequencyChart } from './ActivityFrequencyChart';
import { CasesTimelineChart } from './CasesTimelineChart';
import { TopLists } from './TopLists';
import { CaseExplorer } from './CaseExplorer';
import { ExportDropdown } from '@/components/features/export';

const logger = createLogger('insights-page');

export function InsightsPage() {
    const router = useRouter();
    const { miningResults, uploadedFile, parsedData, columnConfig } = useAppStore();

    // Build case data from parsed data for timeline and export
    const caseData = useMemo(() => {
        if (!parsedData || !columnConfig || !miningResults) return [];

        const rows = parsedData.rows as Array<Record<string, unknown>>;
        const caseMap = new Map<string, {
            caseId: string;
            events: Array<{ timestamp: Date; activity: string; resource?: string }>;
        }>();

        rows.forEach((row) => {
            const caseId = String(row[columnConfig.caseId] || '');
            const activity = String(row[columnConfig.activity] || '');
            const timestampValue = row[columnConfig.timestamp];
            const timestamp = timestampValue ? new Date(timestampValue as string | number) : null;
            const resource = columnConfig.resource ? String(row[columnConfig.resource] || '') : undefined;

            if (!caseId || !timestamp || isNaN(timestamp.getTime())) return;

            if (!caseMap.has(caseId)) {
                caseMap.set(caseId, { caseId, events: [] });
            }
            caseMap.get(caseId)!.events.push({ timestamp, activity, resource });
        });

        // Sort events and compute case data
        return Array.from(caseMap.values()).map((c) => {
            c.events.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
            const startTime = c.events[0].timestamp;
            const endTime = c.events[c.events.length - 1].timestamp;
            const duration = endTime.getTime() - startTime.getTime();

            // Get variant for this case
            const variant = c.events.map((e) => e.activity).join(' → ');

            // Check if case has deviation
            const hasDeviation = miningResults.deviations?.some((d: any) =>
                d.affectedCases?.includes(c.caseId)
            ) ?? false;

            return {
                caseId: c.caseId,
                startTime,
                endTime,
                duration,
                eventCount: c.events.length,
                variant,
                hasDeviation,
                events: c.events,
            };
        });
    }, [parsedData, columnConfig, miningResults]);

    // Log on mount
    useEffect(() => {
        if (miningResults) {
            logger.info(`📊 Process Insights loaded with ${miningResults.stats.totalCases} cases`);
        }
    }, [miningResults]);

    // No results state
    if (!miningResults) {
        return (
            <NavigationGuard>
                <div className="flex flex-col h-full">
                    <Header title="Insights" />
                    <div className="flex-1 flex items-center justify-center p-6">
                        <Alert className="max-w-md">
                            <AlertTriangle className="h-4 w-4" />
                            <AlertTitle>No Analysis Results</AlertTitle>
                            <AlertDescription className="mt-2">
                                <p className="mb-4">
                                    Run a process mining analysis first to view insights and statistics.
                                </p>
                                <Button onClick={() => router.push('/process-map')}>
                                    Go to Process Map
                                </Button>
                            </AlertDescription>
                        </Alert>
                    </div>
                </div>
            </NavigationGuard>
        );
    }

    return (
        <NavigationGuard>
            <div className="flex flex-col h-full">
                <Header title="Process Insights" />

                <ScrollArea className="flex-1">
                    <div className="p-6 space-y-6">
                        {/* Page Header */}
                        <div className="flex items-center justify-between">
                            <div className="space-y-1">
                                <div className="flex items-center gap-2 text-muted-foreground">
                                    <FileText className="h-4 w-4" />
                                    <span className="text-sm">
                                        Analysis of{' '}
                                        <strong className="text-foreground">
                                            {uploadedFile?.name || 'Uploaded File'}
                                        </strong>
                                    </span>
                                </div>
                                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                    <Calendar className="h-3 w-3" />
                                    <span>Last analyzed: {format(new Date(), 'PPp')}</span>
                                </div>
                            </div>

                            <div className="flex items-center gap-2">
                                <ExportDropdown
                                    model={miningResults as any}
                                    cases={caseData.map((c) => ({
                                        caseId: c.caseId,
                                        startTime: c.startTime,
                                        endTime: c.endTime,
                                        duration: c.duration,
                                        eventCount: c.eventCount,
                                        variant: c.variant,
                                        hasDeviation: c.hasDeviation,
                                    }))}
                                />
                                <Button variant="outline" size="sm" disabled>
                                    <Download className="h-4 w-4 mr-2" />
                                    Download Report
                                </Button>
                            </div>
                        </div>

                        {/* Tabs */}
                        <Tabs defaultValue="dashboard">
                            <TabsList>
                                <TabsTrigger value="dashboard">Dashboard</TabsTrigger>
                                <TabsTrigger value="cases">Case Explorer</TabsTrigger>
                            </TabsList>

                            <TabsContent value="dashboard" className="mt-6 space-y-6">
                                {/* Key Metrics */}
                                <MetricsGrid model={miningResults as any} />

                                {/* Charts Row */}
                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                    <DurationChart model={miningResults as any} />
                                    <ActivityFrequencyChart model={miningResults as any} />
                                </div>

                                {/* Timeline - only show if we have case data */}
                                {caseData.length > 0 && (
                                    <CasesTimelineChart
                                        cases={caseData.map((c) => ({
                                            caseId: c.caseId,
                                            startTime: c.startTime,
                                        }))}
                                    />
                                )}

                                <TopLists
                                    model={miningResults as any}
                                    cases={caseData.length > 0 ? caseData.map((c) => ({
                                        caseId: c.caseId,
                                        duration: c.duration,
                                    })) : []}
                                />
                            </TabsContent>

                            <TabsContent value="cases" className="mt-6">
                                {caseData.length > 0 ? (
                                    <CaseExplorer
                                        cases={caseData}
                                        model={miningResults as any}
                                    />
                                ) : (
                                    <Alert className="max-w-md mx-auto">
                                        <AlertTriangle className="h-4 w-4" />
                                        <AlertTitle>Case Data Not Available</AlertTitle>
                                        <AlertDescription>
                                            <p>
                                                Individual case data is only available when processing files locally.
                                                The overall metrics and charts on the Dashboard tab are based on the analysis results.
                                            </p>
                                        </AlertDescription>
                                    </Alert>
                                )}
                            </TabsContent>
                        </Tabs>
                    </div>
                </ScrollArea>
            </div>
        </NavigationGuard>
    );
}
