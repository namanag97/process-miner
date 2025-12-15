'use client';

import { AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface ErrorStateProps {
    title?: string;
    description?: string;
    onRetry?: () => void;
}

export function ErrorState({
    title = 'Something went wrong',
    description = 'An unexpected error occurred. Please try again.',
    onRetry,
}: ErrorStateProps) {
    return (
        <div className="flex flex-col items-center justify-center p-8 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-destructive/10">
                <AlertCircle className="h-8 w-8 text-destructive" />
            </div>
            <h3 className="mt-4 text-lg font-semibold">{title}</h3>
            <p className="mt-2 text-sm text-muted-foreground max-w-sm">
                {description}
            </p>
            {onRetry && (
                <Button
                    variant="outline"
                    className="mt-6"
                    onClick={onRetry}
                >
                    Try again
                </Button>
            )}
        </div>
    );
}
