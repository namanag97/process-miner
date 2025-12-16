'use client';

import {
    AlertDialog,
    AlertDialogAction,
    AlertDialogCancel,
    AlertDialogContent,
    AlertDialogDescription,
    AlertDialogFooter,
    AlertDialogHeader,
    AlertDialogTitle,
} from '@/components/ui/alert-dialog';

interface ConfirmDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    title: string;
    description: string;
    confirmLabel?: string;
    cancelLabel?: string;
    onConfirm: () => void;
    onCancel?: () => void;
    variant?: 'default' | 'destructive';
}

export function ConfirmDialog({
    open,
    onOpenChange,
    title,
    description,
    confirmLabel = 'Continue',
    cancelLabel = 'Cancel',
    onConfirm,
    onCancel,
    variant = 'default',
}: ConfirmDialogProps) {
    const handleConfirm = () => {
        onConfirm();
        onOpenChange(false);
    };

    const handleCancel = () => {
        onCancel?.();
        onOpenChange(false);
    };

    return (
        <AlertDialog open={open} onOpenChange={onOpenChange}>
            <AlertDialogContent>
                <AlertDialogHeader>
                    <AlertDialogTitle>{title}</AlertDialogTitle>
                    <AlertDialogDescription>{description}</AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                    <AlertDialogCancel onClick={handleCancel}>
                        {cancelLabel}
                    </AlertDialogCancel>
                    <AlertDialogAction
                        onClick={handleConfirm}
                        className={variant === 'destructive' ? 'bg-red-600 hover:bg-red-700' : ''}
                    >
                        {confirmLabel}
                    </AlertDialogAction>
                </AlertDialogFooter>
            </AlertDialogContent>
        </AlertDialog>
    );
}

/**
 * Pre-configured confirmation dialogs for common actions
 */

interface RerunAnalysisDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onConfirm: () => void;
}

export function RerunAnalysisDialog({ open, onOpenChange, onConfirm }: RerunAnalysisDialogProps) {
    return (
        <ConfirmDialog
            open={open}
            onOpenChange={onOpenChange}
            title="Re-run Analysis?"
            description="This will clear the current results and run the analysis again. Are you sure you want to continue?"
            confirmLabel="Re-run"
            onConfirm={onConfirm}
            variant="default"
        />
    );
}

interface ClearLogsDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onConfirm: () => void;
}

export function ClearLogsDialog({ open, onOpenChange, onConfirm }: ClearLogsDialogProps) {
    return (
        <ConfirmDialog
            open={open}
            onOpenChange={onOpenChange}
            title="Clear All Logs?"
            description="This will permanently delete all log entries. This action cannot be undone."
            confirmLabel="Clear Logs"
            onConfirm={onConfirm}
            variant="destructive"
        />
    );
}

interface NavigateAwayDialogProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
    onConfirm: () => void;
    onCancel?: () => void;
}

export function NavigateAwayDialog({ open, onOpenChange, onConfirm, onCancel }: NavigateAwayDialogProps) {
    return (
        <ConfirmDialog
            open={open}
            onOpenChange={onOpenChange}
            title="Unsaved Changes"
            description="You have unsaved changes. Are you sure you want to leave this page? Your changes will be lost."
            confirmLabel="Leave Page"
            cancelLabel="Stay"
            onConfirm={onConfirm}
            onCancel={onCancel}
            variant="destructive"
        />
    );
}
