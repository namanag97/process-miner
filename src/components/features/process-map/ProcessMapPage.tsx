'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { RefreshCw, BarChart3, Loader2 } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useAppStore } from '@/lib/stores/useAppStore';
import { getFullAnalysis } from '@/lib/api';

import { AnalysisSummary } from './AnalysisSummary';
import { ProcessMapViewer } from './ProcessMapViewer';
import { VariantsTab } from './VariantsTab';
import { DeviationsTab } from './DeviationsTab';
import { ExportDropdown } from '@/components/features/export';

/**
 * ProcessMapPage - Displays analysis results from backend.
 * Data is fetched via React Query using the datasetId from app store.
 */
export function ProcessMapPage() {
    const router = useRouter();
    const { datasetId } = useAppStore();

    // Redirect if no dataset
    useEffect(() => {
        if (!datasetId) {
            router.push('/upload');
        }
    }, [datasetId, router]);

    // Fetch analysis data from backend
    const { data: analysis, isLoading, error, refetch } = useQuery({
        queryKey: ['analysis', datasetId],
        queryFn: () => getFullAnalysis(datasetId!),
        enabled: !!datasetId,
        staleTime: 5 * 60 * 1000, // 5 minutes
    });

    // Loading state
    if (isLoading) {
        return (
            <div className="flex-1 flex items-center justify-center p-6">
                <div className="text-center space-y-4">
                    <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
                    <p className="text-muted-foreground">Loading analysis...</p>
                </div>
            </div>
        );
    }

    // Error state
    if (error) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
                <div className="text-red-500 text-lg mb-4">❌ Failed to load analysis</div>
                <p className="text-muted-foreground mb-4">{error.message}</p>
                <Button onClick={() => refetch()}>Retry</Button>
            </div>
        );
    }

    // No data state
    if (!analysis) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
                <p className="text-muted-foreground mb-4">No analysis data available.</p>
                <Button onClick={() => router.push('/upload')}>Upload Data</Button>
            </div>
        );
    }

    // Convert backend analysis to display format
    const displayModel = {
        stats: {
            totalCases: analysis.stats.total_cases,
            totalEvents: analysis.stats.total_events,
            totalActivities: analysis.stats.total_activities,
            totalVariants: analysis.stats.total_variants,
            avgCaseDuration: analysis.stats.avg_case_duration_ms,
            medianCaseDuration: analysis.stats.median_case_duration_ms,
        },
        dfg: analysis.dfg,
        variants: analysis.variants.variants,
        deviations: analysis.deviations,
    };

    return (
        <div className="flex-1 flex flex-col p-6 space-y-6">
            {/* Action buttons */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => refetch()}
                    >
                        <RefreshCw className="h-4 w-4 mr-2" />
                        Refresh
                    </Button>
                    <ExportDropdown model={displayModel as any} />
                    <Button
                        size="sm"
                        onClick={() => router.push('/insights')}
                    >
                        <BarChart3 className="h-4 w-4 mr-2" />
                        View Insights
                    </Button>
                </div>
            </div>

            {/* Summary stats */}
            <AnalysisSummary model={displayModel as any} />

            {/* Tabs */}
            <Tabs defaultValue="process-map" className="flex-1">
                <TabsList>
                    <TabsTrigger value="process-map">Process Map</TabsTrigger>
                    <TabsTrigger value="variants">Variants</TabsTrigger>
                    <TabsTrigger value="deviations">Deviations</TabsTrigger>
                </TabsList>

                <TabsContent value="process-map" className="mt-4">
                    <ProcessMapViewer model={displayModel as any} />
                </TabsContent>

                <TabsContent value="variants" className="mt-4">
                    <VariantsTab model={displayModel as any} />
                </TabsContent>

                <TabsContent value="deviations" className="mt-4">
                    <DeviationsTab model={displayModel as any} />
                </TabsContent>
            </Tabs>
        </div>
    );
}
