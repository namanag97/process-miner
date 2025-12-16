'use client';

import { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import { useRouter } from 'next/navigation';
import {
    Hash,
    Activity,
    Clock,
    User,
    DollarSign,
    AlertCircle,
    ChevronDown,
    ChevronRight,
    Loader2,
    Wifi,
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Progress } from '@/components/ui/progress';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import {
    Collapsible,
    CollapsibleContent,
    CollapsibleTrigger,
} from '@/components/ui/collapsible';
import { Header } from '@/components/layout/Header';
import { ColumnSelector, ValidationResults } from '@/components/features/configure';
import { NavigationGuard } from '@/components/navigation';
import { useAppStore } from '@/lib/stores/useAppStore';
import { useLogStore } from '@/lib/stores/useLogStore';
import {
    autoDetectColumns,
    validateColumnConfiguration,
    type ValidationResult,
    type ColumnMapping,
} from '@/lib/validation';
import {
    useCreateMapping,
    useStartProcessing,
    useJobStatus,
    useFullAnalysis,
} from '@/lib/api/queries';
import { createLogger } from '@/lib/debug-logger';

const logger = createLogger('configure-page');


export default function ConfigurePage() {
    const router = useRouter();
    const {
        parsedData,
        uploadedFile,
        setColumnConfig,
        setCurrentStep,
        uploadId,
        sessionId,
        setMappingId,
        setDatasetId,
        setMiningResults,
        jobProgress,
        jobMessage,
        setJobProgress,
        setJobStatus,
    } = useAppStore();
    const addLog = useLogStore((state) => state.addLog);

    // React Query mutations
    const createMappingMutation = useCreateMapping();
    const startProcessingMutation = useStartProcessing();

    // Track current job for polling
    const [currentJobId, setCurrentJobId] = useState<string | null>(null);

    // Poll job status when we have a job ID
    const { data: jobData } = useJobStatus(currentJobId, {
        refetchInterval: currentJobId ? 1000 : false,
        enabled: !!currentJobId,
    });

    // Log session info on mount
    useEffect(() => {
        logger.info('Configure page mounted', {
            sessionId,
            uploadId,
            hasData: !!parsedData,
            columns: parsedData?.headers?.length ?? 0,
        });
    }, [sessionId, uploadId, parsedData]);

    // Column mapping state
    const [caseId, setCaseId] = useState<string | null>(null);
    const [activity, setActivity] = useState<string | null>(null);
    const [timestamp, setTimestamp] = useState<string | null>(null);
    const [resource, setResource] = useState<string | null>(null);
    const [cost, setCost] = useState<string | null>(null);

    // UI state
    const [optionalOpen, setOptionalOpen] = useState(true);
    const [isValidating, setIsValidating] = useState(false);
    const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
    const [showWarningDialog, setShowWarningDialog] = useState(false);

    // Derived processing state from mutations
    const isProcessing = createMappingMutation.isPending ||
        startProcessingMutation.isPending ||
        (!!currentJobId && jobData?.status === 'processing') ||
        (!!currentJobId && jobData?.status === 'queued');

    // Get columns and rows from parsed data
    const columns = parsedData?.headers || [];
    const rows = (parsedData?.rows || []) as Record<string, unknown>[];

    // Effect to handle job completion and navigation
    useEffect(() => {
        if (jobData?.status === 'completed' && jobData.dataset_id) {
            const datasetId = jobData.dataset_id;
            setDatasetId(datasetId);
            setCurrentJobId(null); // Stop polling

            addLog('success', `✅ [${datasetId.slice(0, 8)}] Mining complete`);
            logger.info('Processing complete, navigating', { datasetId });

            router.push('/process-map');
        } else if (jobData?.status === 'failed') {
            setCurrentJobId(null); // Stop polling
            addLog('error', `❌ Processing failed: ${jobData.error || 'Unknown error'}`);
            logger.error('Processing failed', { error: jobData.error });
        } else if (jobData?.progress !== undefined) {
            setJobProgress(jobData.progress, jobData.progress_message || '');
        }
    }, [jobData, setDatasetId, addLog, router, setJobProgress]);

    // Auto-detection on mount
    useEffect(() => {
        if (columns.length > 0 && !caseId && !activity && !timestamp) {
            const detected = autoDetectColumns(columns);

            if (detected.caseId) {
                setCaseId(detected.caseId);
                addLog('info', `🔍 Auto-detected '${detected.caseId}' as Case ID`);
            }
            if (detected.activity) {
                setActivity(detected.activity);
                addLog('info', `🔍 Auto-detected '${detected.activity}' as Activity`);
            }
            if (detected.timestamp) {
                setTimestamp(detected.timestamp);
                addLog('info', `🔍 Auto-detected '${detected.timestamp}' as Timestamp`);
            }
            if (detected.resource) {
                setResource(detected.resource);
                addLog('info', `🔍 Auto-detected '${detected.resource}' as Resource`);
            }
            if (detected.cost) {
                setCost(detected.cost);
                addLog('info', `🔍 Auto-detected '${detected.cost}' as Cost`);
            }
        }
    }, [columns, caseId, activity, timestamp, addLog]);

    // Validation errors for duplicate selection
    const errors = useMemo(() => {
        const selected = [caseId, activity, timestamp, resource, cost].filter(Boolean);
        const duplicates = selected.filter((item, index) => selected.indexOf(item) !== index);

        const errs: Record<string, string> = {};
        if (duplicates.length > 0) {
            const dupSet = new Set(duplicates);
            if (caseId && dupSet.has(caseId)) errs.caseId = 'Column already selected';
            if (activity && dupSet.has(activity)) errs.activity = 'Column already selected';
            if (timestamp && dupSet.has(timestamp)) errs.timestamp = 'Column already selected';
            if (resource && dupSet.has(resource)) errs.resource = 'Column already selected';
            if (cost && dupSet.has(cost)) errs.cost = 'Column already selected';
        }
        return errs;
    }, [caseId, activity, timestamp, resource, cost]);

    // Check if form is valid
    const isFormValid = useMemo(() => {
        return caseId && activity && timestamp && Object.keys(errors).length === 0;
    }, [caseId, activity, timestamp, errors]);

    // Handle proceeding to next step using React Query mutations
    const handleProceed = useCallback(async (mapping?: ColumnMapping) => {
        const config = mapping || {
            caseId: caseId!,
            activity: activity!,
            timestamp: timestamp!,
            resource: resource || undefined,
            cost: cost || undefined,
        };

        setColumnConfig(config);
        setCurrentStep(3);

        // Backend processing
        if (!uploadId) {
            addLog('error', 'No upload ID found');
            return;
        }

        setJobProgress(0, 'Starting processing...');

        logger.info('Starting backend processing', {
            sessionId: useAppStore.getState().sessionId,
            uploadId,
            config,
        });

        try {
            // Create mapping on backend using React Query mutation
            addLog('info', `📤 [${uploadId.slice(0, 8)}] Creating column mapping...`);
            logger.info('Creating mapping', { uploadId, config });

            const mappingResponse = await createMappingMutation.mutateAsync({
                uploadId,
                mapping: {
                    case_id_column: config.caseId,
                    activity_column: config.activity,
                    timestamp_column: config.timestamp,
                    resource_column: config.resource,
                    cost_column: config.cost,
                },
            });

            setMappingId(mappingResponse.mapping_id);
            addLog('success', `✅ [${uploadId.slice(0, 8)}] Mapping created: ${mappingResponse.mapping_id.slice(0, 8)}`);
            logger.info('Mapping created', { mappingId: mappingResponse.mapping_id });

            // Start processing using React Query mutation
            addLog('info', `⚙️ [${uploadId.slice(0, 8)}] Starting PM4Py processing...`);
            logger.info('Starting processing', { mappingId: mappingResponse.mapping_id });

            const job = await startProcessingMutation.mutateAsync(mappingResponse.mapping_id);
            logger.info('Job started', { jobId: job.job_id });

            // Set job ID to trigger polling via useJobStatus
            setCurrentJobId(job.job_id);
            addLog('info', `⏳ [${job.job_id.slice(0, 8)}] Processing started...`);

        } catch (error) {
            const message = error instanceof Error ? error.message : 'Processing failed';
            addLog('error', `❌ [${uploadId?.slice(0, 8) || 'unknown'}] Processing failed: ${message}`);
            logger.error('Processing failed', { error: message, uploadId });
        }
    }, [
        caseId, activity, timestamp, resource, cost,
        setColumnConfig, setCurrentStep, addLog,
        uploadId, setMappingId, setJobProgress,
        createMappingMutation, startProcessingMutation,
    ]);


    // Handle validation
    const handleValidate = useCallback(async () => {
        if (!caseId || !activity || !timestamp) return;

        const mapping: ColumnMapping = {
            caseId,
            activity,
            timestamp,
            resource: resource || undefined,
            cost: cost || undefined,
        };

        // Backend processing
        if (uploadId) {
            addLog('info', '🚀 Starting backend validation and processing...');
            handleProceed(mapping);
            return;
        }

        // Client-side validation (offline mode only)
        setIsValidating(true);
        await new Promise(resolve => setTimeout(resolve, 100));

        const result = validateColumnConfiguration(rows, mapping, (level, message) => {
            addLog(level, message);
        });

        setValidationResult(result);
        setIsValidating(false);

        if (result.isValid && result.hasWarnings) {
            setShowWarningDialog(true);
        } else if (result.isValid) {
            handleProceed(mapping);
        }
    }, [caseId, activity, timestamp, resource, cost, rows, addLog, uploadId, handleProceed]);

    return (
        <NavigationGuard>
            <div className="flex flex-col">
                <Header title="Configure" />

                <div className="flex-1 p-4 md:p-6 space-y-6">
                    {/* Summary Card */}
                    <Card>
                        <CardHeader className="pb-3">
                            <CardTitle>Configure: {uploadedFile?.name || 'Event Log'}</CardTitle>
                            <CardDescription>
                                {parsedData?.rowCount.toLocaleString() || 0} events • {columns.length} columns detected
                            </CardDescription>
                        </CardHeader>
                    </Card>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Column Mapping */}
                        <div className="space-y-6">
                            {/* Required Columns */}
                            <Card>
                                <CardHeader className="pb-3">
                                    <CardTitle className="text-base">Required Columns</CardTitle>
                                    <CardDescription>
                                        Map your data columns to the required process mining fields
                                    </CardDescription>
                                </CardHeader>
                                <CardContent className="space-y-6">
                                    <ColumnSelector
                                        icon={Hash}
                                        label="Case ID"
                                        description="Select the column that identifies each process instance"
                                        helperText="Each unique value represents one process execution (e.g., order ID, ticket number)"
                                        columns={columns}
                                        selectedColumn={caseId}
                                        onSelect={setCaseId}
                                        rows={rows}
                                        required
                                        error={errors.caseId}
                                    />

                                    <Separator />

                                    <ColumnSelector
                                        icon={Activity}
                                        label="Activity"
                                        description="Select the column containing activity/event names"
                                        helperText="The name of each step in your process (e.g., 'Order Created', 'Payment Received')"
                                        columns={columns}
                                        selectedColumn={activity}
                                        onSelect={setActivity}
                                        rows={rows}
                                        required
                                        error={errors.activity}
                                    />

                                    <Separator />

                                    <ColumnSelector
                                        icon={Clock}
                                        label="Timestamp"
                                        description="Select the column with event timestamps"
                                        helperText="When each activity occurred (date/time format)"
                                        columns={columns}
                                        selectedColumn={timestamp}
                                        onSelect={setTimestamp}
                                        rows={rows}
                                        required
                                        error={errors.timestamp}
                                    />
                                </CardContent>
                            </Card>

                            {/* Optional Columns */}
                            <Collapsible open={optionalOpen} onOpenChange={setOptionalOpen}>
                                <Card>
                                    <CollapsibleTrigger asChild>
                                        <CardHeader className="pb-3 cursor-pointer hover:bg-muted/50 transition-colors">
                                            <div className="flex items-center justify-between">
                                                <div>
                                                    <CardTitle className="text-base">Optional Columns</CardTitle>
                                                    <CardDescription>
                                                        Additional columns for enhanced analysis
                                                    </CardDescription>
                                                </div>
                                                {optionalOpen ? (
                                                    <ChevronDown className="h-4 w-4 text-muted-foreground" />
                                                ) : (
                                                    <ChevronRight className="h-4 w-4 text-muted-foreground" />
                                                )}
                                            </div>
                                        </CardHeader>
                                    </CollapsibleTrigger>
                                    <CollapsibleContent>
                                        <CardContent className="space-y-6 pt-0">
                                            <ColumnSelector
                                                icon={User}
                                                label="Resource"
                                                description="Who performed this activity? (optional)"
                                                helperText="The person or system that executed the activity"
                                                columns={columns}
                                                selectedColumn={resource}
                                                onSelect={setResource}
                                                rows={rows}
                                                error={errors.resource}
                                            />

                                            <Separator />

                                            <ColumnSelector
                                                icon={DollarSign}
                                                label="Cost"
                                                description="Cost associated with this event (optional)"
                                                helperText="Monetary value or cost for cost analysis"
                                                columns={columns}
                                                selectedColumn={cost}
                                                onSelect={setCost}
                                                rows={rows}
                                                error={errors.cost}
                                            />
                                        </CardContent>
                                    </CollapsibleContent>
                                </Card>
                            </Collapsible>

                            {/* Validate Button */}
                            <Button
                                size="lg"
                                className="w-full"
                                disabled={!isFormValid || isValidating || isProcessing}
                                onClick={handleValidate}
                            >
                                {isValidating ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        Validating...
                                    </>
                                ) : isProcessing ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        Processing with PM4Py...
                                    </>
                                ) : (
                                    <>
                                        <Wifi className="mr-2 h-4 w-4" />
                                        Validate & Process
                                    </>
                                )}
                            </Button>

                            {/* Processing Progress */}
                            {isProcessing && (
                                <Card className="mt-4">
                                    <CardContent className="pt-4">
                                        <div className="space-y-2">
                                            <div className="flex justify-between text-sm">
                                                <span>{jobMessage || 'Processing...'}</span>
                                                <span>{jobProgress}%</span>
                                            </div>
                                            <Progress value={jobProgress} className="h-2" />
                                        </div>
                                    </CardContent>
                                </Card>
                            )}
                        </div>

                        {/* Validation Results */}
                        <div>
                            {validationResult ? (
                                <ValidationResults result={validationResult} />
                            ) : (
                                <Card className="h-[400px] flex items-center justify-center">
                                    <div className="text-center text-muted-foreground">
                                        <Activity className="h-12 w-12 mx-auto mb-4 opacity-20" />
                                        <p>Configure your columns and click</p>
                                        <p className="font-medium">&quot;Validate &amp; Continue&quot;</p>
                                        <p>to see validation results</p>
                                    </div>
                                </Card>
                            )}
                        </div>
                    </div>
                </div>

                {/* Warning Dialog */}
                <Dialog open={showWarningDialog} onOpenChange={setShowWarningDialog}>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle className="flex items-center gap-2">
                                <AlertCircle className="h-5 w-5 text-yellow-500" />
                                Proceed with warnings?
                            </DialogTitle>
                            <DialogDescription>
                                The validation completed with some warnings. You can still proceed, but the results might not be optimal.
                            </DialogDescription>
                        </DialogHeader>

                        <div className="py-4">
                            <ul className="space-y-2">
                                {validationResult?.warnings.map((warning, i) => (
                                    <li key={i} className="flex items-start gap-2 text-sm">
                                        <AlertCircle className="h-4 w-4 text-yellow-500 mt-0.5 shrink-0" />
                                        <span>{warning}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>

                        <DialogFooter>
                            <Button variant="outline" onClick={() => setShowWarningDialog(false)}>
                                Go Back
                            </Button>
                            <Button onClick={() => {
                                setShowWarningDialog(false);
                                handleProceed();
                            }}>
                                Continue Anyway
                            </Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>
            </div>
        </NavigationGuard>
    );
}
