'use client';

import { Loader2 } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';

export interface LoadingStateProps {
    message?: string;
    progress?: number;
    variant?: 'spinner' | 'skeleton';
    className?: string;
}

export function LoadingState({
    message = 'Loading...',
    progress,
    variant = 'spinner',
    className,
}: LoadingStateProps) {
    if (variant === 'skeleton') {
        return (
            <div className={cn('space-y-4 p-6', className)}>
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
                <Skeleton className="h-4 w-5/6" />
                <Skeleton className="h-4 w-2/3" />
            </div>
        );
    }

    return (
        <div
            className={cn(
                'flex flex-col items-center justify-center py-12 px-6 text-center',
                className
            )}
        >
            <Loader2 className="h-10 w-10 animate-spin text-primary mb-4" />
            <p className="text-sm text-muted-foreground mb-4">{message}</p>
            {progress !== undefined && (
                <div className="w-full max-w-xs">
                    <Progress value={progress} className="h-2" />
                    <p className="text-xs text-muted-foreground mt-2">
                        {Math.round(progress)}%
                    </p>
                </div>
            )}
        </div>
    );
}
