'use client';

import { CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export interface SuccessStateAction {
    label: string;
    onClick: () => void;
    variant?: 'default' | 'outline' | 'secondary';
}

export interface SuccessStateProps {
    title?: string;
    message: string;
    primaryAction?: SuccessStateAction;
    secondaryAction?: SuccessStateAction;
    className?: string;
}

export function SuccessState({
    title = 'Success!',
    message,
    primaryAction,
    secondaryAction,
    className,
}: SuccessStateProps) {
    return (
        <div
            className={cn(
                'flex flex-col items-center justify-center py-12 px-6 text-center',
                className
            )}
        >
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/30 mb-4">
                <CheckCircle className="h-8 w-8 text-green-600 dark:text-green-400" />
            </div>
            <h3 className="text-lg font-semibold mb-2">{title}</h3>
            <p className="text-sm text-muted-foreground max-w-sm mb-6">
                {message}
            </p>
            <div className="flex gap-3">
                {secondaryAction && (
                    <Button
                        variant={secondaryAction.variant || 'outline'}
                        onClick={secondaryAction.onClick}
                    >
                        {secondaryAction.label}
                    </Button>
                )}
                {primaryAction && (
                    <Button
                        variant={primaryAction.variant || 'default'}
                        onClick={primaryAction.onClick}
                    >
                        {primaryAction.label}
                    </Button>
                )}
            </div>
        </div>
    );
}
