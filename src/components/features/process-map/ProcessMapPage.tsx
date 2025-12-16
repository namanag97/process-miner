'use client';

import { useCallback, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { RefreshCw, BarChart3 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useAppStore } from '@/lib/stores/useAppStore';
import { useMining } from '@/lib/mining/useMining';
import { createLogger } from '@/lib/debug-logger';

import { AnalysisReadyCard } from './AnalysisReadyCard';
import { AnalysisProgressCard } from './AnalysisProgressCard';
import { AnalysisSummary } from './AnalysisSummary';
import { ProcessMapViewer } from './ProcessMapViewer';
import { VariantsTab } from './VariantsTab';
import { DeviationsTab } from './DeviationsTab';
import { ExportDropdown } from '@/components/features/export';

const logger = createLogger('process-map-page');

export function ProcessMapPage() {
    const router = useRouter();
    const { parsedData, columnConfig, miningResults, setMiningResults } = useAppStore();

    const { mine, isProcessing, progress, results, error, warnings, reset } = useMining(
        parsedData,
        columnConfig
    );

    // Calculate event and case counts for the ready card
    const eventCount = parsedData?.rowCount || 0;
    const caseCount = useMemo(() => {
        if (!parsedData || !columnConfig) return 0;
        const rows = parsedData.rows as Array<Record<string, unknown>>;
        const caseIds = new Set(rows.map((row) => row[columnConfig.caseId]));
        return caseIds.size;
    }, [parsedData, columnConfig]);

    // Handle run analysis
    const handleRunAnalysis = useCallback(async () => {
        logger.info('Starting process mining analysis...');
        const result = await mine();

        if (result.success && result.model) {
            logger.info('Analysis complete, storing results in app store');
            setMiningResults(result.model);
        } else {
            logger.error(`Analysis failed: ${result.error}`);
        }
    }, [mine, setMiningResults]);

    // Handle re-run analysis
    const handleRerunAnalysis = useCallback(() => {
        logger.info('Re-running analysis...');
        reset();
        setMiningResults(null);
        // Start analysis after a short delay to allow state to update
        setTimeout(() => {
            handleRunAnalysis();
        }, 100);
    }, [reset, setMiningResults, handleRunAnalysis]);

    // Use stored results if available, otherwise use hook results
    const currentResults = miningResults || results;
    const hasResults = !!currentResults;

    // Show pre-analysis state
    if (!hasResults && !isProcessing) {
        return (
            <div className="flex-1 flex items-center justify-center p-6">
                <AnalysisReadyCard
                    eventCount={eventCount}
                    caseCount={caseCount}
                    onRunAnalysis={handleRunAnalysis}
                    isLoading={isProcessing}
                />
            </div>
        );
    }

    // Show processing state
    if (isProcessing) {
        return (
            <div className="flex-1 flex items-center justify-center p-6">
                <AnalysisProgressCard
                    stage={progress.stage}
                    progress={progress.progress}
                />
            </div>
        );
    }

    // Show error state
    if (error && !hasResults) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
                <div className="text-red-500 text-lg mb-4">❌ Analysis Failed</div>
                <p className="text-muted-foreground mb-4">{error}</p>
                <Button onClick={handleRerunAnalysis}>Try Again</Button>
            </div>
        );
    }

    // Show results
    return (
        <div className="flex-1 flex flex-col p-6 space-y-6">
            {/* Action buttons */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={handleRerunAnalysis}
                        disabled={isProcessing}
                    >
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Re-run Analysis
                    </Button>
                    {currentResults && <ExportDropdown model={currentResults} />}
                    <Button
                        size="sm"
                        onClick={() => router.push('/insights')}
                    >
                        <BarChart3 className="h-4 w-4 mr-2" />
                        View Insights
                    </Button>
                </div>

                {warnings.length > 0 && (
                    <p className="text-sm text-yellow-600">
                        ⚠️ {warnings.length} warning{warnings.length !== 1 ? 's' : ''} during analysis
                    </p>
                )}
            </div>

            {/* Summary stats */}
            {currentResults && <AnalysisSummary model={currentResults} />}

            {/* Tabs */}
            {currentResults && (
                <Tabs defaultValue="process-map" className="flex-1">
                    <TabsList>
                        <TabsTrigger value="process-map">Process Map</TabsTrigger>
                        <TabsTrigger value="variants">Variants</TabsTrigger>
                        <TabsTrigger value="deviations">Deviations</TabsTrigger>
                    </TabsList>

                    <TabsContent value="process-map" className="mt-4">
                        <ProcessMapViewer model={currentResults} />
                    </TabsContent>

                    <TabsContent value="variants" className="mt-4">
                        <VariantsTab model={currentResults} />
                    </TabsContent>

                    <TabsContent value="deviations" className="mt-4">
                        <DeviationsTab model={currentResults} />
                    </TabsContent>
                </Tabs>
            )}
        </div>
    );
}
