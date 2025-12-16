'use client';

import { useState, useEffect, useMemo, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAppStore } from '@/lib/stores/useAppStore';
import { useLogStore } from '@/lib/stores/useLogStore';
import {
    autoDetectColumns,
    validateColumnConfiguration,
    type ValidationResult,
    type ColumnMapping,
} from '@/lib/validation';
import { ROUTES } from '@/lib/constants';

interface UseColumnConfigOptions {
    onValidationSuccess?: () => void;
    onValidationError?: (errors: string[]) => void;
}

export function useColumnConfig(options: UseColumnConfigOptions = {}) {
    const router = useRouter();
    const addLog = useLogStore((state) => state.addLog);
    const {
        parsedData,
        uploadedFile,
        setColumnConfig,
        setCurrentStep
    } = useAppStore();

    // Column mapping state
    const [caseId, setCaseId] = useState<string | null>(null);
    const [activity, setActivity] = useState<string | null>(null);
    const [timestamp, setTimestamp] = useState<string | null>(null);
    const [resource, setResource] = useState<string | null>(null);
    const [cost, setCost] = useState<string | null>(null);

    // UI state
    const [isValidating, setIsValidating] = useState(false);
    const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
    const [showWarningDialog, setShowWarningDialog] = useState(false);

    // Derived data
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
    const duplicateErrors = useMemo(() => {
        const selected = [caseId, activity, timestamp, resource, cost].filter(Boolean);
        const duplicates = selected.filter((item, index) => selected.indexOf(item) !== index);

        const errors: Record<string, string> = {};
        if (duplicates.length > 0) {
            const dupSet = new Set(duplicates);
            if (caseId && dupSet.has(caseId)) errors.caseId = 'Column already selected';
            if (activity && dupSet.has(activity)) errors.activity = 'Column already selected';
            if (timestamp && dupSet.has(timestamp)) errors.timestamp = 'Column already selected';
            if (resource && dupSet.has(resource)) errors.resource = 'Column already selected';
            if (cost && dupSet.has(cost)) errors.cost = 'Column already selected';
        }
        return errors;
    }, [caseId, activity, timestamp, resource, cost]);

    // Check if form is valid
    const isFormValid = useMemo(() => {
        return !!caseId && !!activity && !!timestamp && Object.keys(duplicateErrors).length === 0;
    }, [caseId, activity, timestamp, duplicateErrors]);

    // Get current mapping
    const getMapping = useCallback((): ColumnMapping | null => {
        if (!caseId || !activity || !timestamp) return null;
        return {
            caseId,
            activity,
            timestamp,
            resource: resource || undefined,
            cost: cost || undefined,
        };
    }, [caseId, activity, timestamp, resource, cost]);

    // Handle validation
    const handleValidate = useCallback(async () => {
        const mapping = getMapping();
        if (!mapping) return;

        setIsValidating(true);

        // Small delay to show loading state
        await new Promise(resolve => setTimeout(resolve, 100));

        const result = validateColumnConfiguration(rows, mapping, (level, message) => {
            addLog(level, message);
        });

        setValidationResult(result);
        setIsValidating(false);

        if (!result.isValid) {
            options.onValidationError?.(result.warnings);
        } else if (result.hasWarnings) {
            setShowWarningDialog(true);
        } else {
            handleProceed(mapping);
        }
    }, [getMapping, rows, addLog, options]);

    // Handle proceeding to next step
    const handleProceed = useCallback((mapping?: ColumnMapping) => {
        const config = mapping || getMapping();
        if (!config) return;

        setColumnConfig(config);
        setCurrentStep(3);
        addLog('success', '✅ Configuration saved. Proceeding to process mining...');
        options.onValidationSuccess?.();
        router.push(ROUTES.PROCESS_MAP);
    }, [getMapping, setColumnConfig, setCurrentStep, addLog, options, router]);

    // Reset all
    const reset = useCallback(() => {
        setCaseId(null);
        setActivity(null);
        setTimestamp(null);
        setResource(null);
        setCost(null);
        setValidationResult(null);
    }, []);

    return {
        // Data
        columns,
        rows,
        parsedData,
        uploadedFile,

        // Column state
        caseId,
        activity,
        timestamp,
        resource,
        cost,

        // Setters
        setCaseId,
        setActivity,
        setTimestamp,
        setResource,
        setCost,

        // Validation
        duplicateErrors,
        isFormValid,
        isValidating,
        validationResult,
        showWarningDialog,
        setShowWarningDialog,

        // Actions
        handleValidate,
        handleProceed,
        reset,

        // Computed
        hasData: !!parsedData,
    };
}
