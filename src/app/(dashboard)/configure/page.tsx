'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
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
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
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

export default function ConfigurePage() {
    const router = useRouter();
    const { parsedData, uploadedFile, setColumnConfig, setCurrentStep } = useAppStore();
    const addLog = useLogStore((state) => state.addLog);

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

    // Get columns and rows from parsed data
    const columns = parsedData?.headers || [];
    const rows = (parsedData?.rows || []) as Record<string, unknown>[];

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

    // Handle validation
    const handleValidate = useCallback(async () => {
        if (!caseId || !activity || !timestamp) return;

        setIsValidating(true);

        // Small delay to show loading state
        await new Promise(resolve => setTimeout(resolve, 100));

        const mapping: ColumnMapping = {
            caseId,
            activity,
            timestamp,
            resource: resource || undefined,
            cost: cost || undefined,
        };

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
    }, [caseId, activity, timestamp, resource, cost, rows, addLog]);

    // Handle proceeding to next step
    const handleProceed = useCallback((mapping?: ColumnMapping) => {
        const config = mapping || {
            caseId: caseId!,
            activity: activity!,
            timestamp: timestamp!,
            resource: resource || undefined,
            cost: cost || undefined,
        };

        setColumnConfig(config);
        setCurrentStep(3);
        addLog('success', '✅ Configuration saved. Proceeding to process mining...');
        router.push('/process-map');
    }, [caseId, activity, timestamp, resource, cost, setColumnConfig, setCurrentStep, addLog, router]);

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
                                disabled={!isFormValid || isValidating}
                                onClick={handleValidate}
                            >
                                {isValidating ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        Validating...
                                    </>
                                ) : (
                                    'Validate & Continue'
                                )}
                            </Button>
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
