'use client';

import { AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export interface ErrorStateProps {
    title?: string;
    message: string;
    onRetry?: () => void;
    onBack?: () => void;
    className?: string;
}

export function ErrorState({
    title = 'Something went wrong',
    message,
    onRetry,
    onBack,
    className,
}: ErrorStateProps) {
    return (
        <div
            className={cn(
                'flex flex-col items-center justify-center py-12 px-6 text-center',
                className
            )}
        >
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-destructive/10 mb-4">
                <AlertCircle className="h-8 w-8 text-destructive" />
            </div>
            <h3 className="text-lg font-semibold mb-2">{title}</h3>
            <p className="text-sm text-muted-foreground max-w-sm mb-6">
                {message}
            </p>
            <div className="flex gap-3">
                {onBack && (
                    <Button variant="outline" onClick={onBack}>
                        Go Back
                    </Button>
                )}
                {onRetry && (
                    <Button onClick={onRetry}>Try Again</Button>
                )}
            </div>
        </div>
    );
}
