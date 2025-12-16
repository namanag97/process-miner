'use client';

import { Wrench, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

export interface InDevStateProps {
    featureName: string;
    description?: string;
    onBack?: () => void;
    className?: string;
}

export function InDevState({
    featureName,
    description,
    onBack,
    className,
}: InDevStateProps) {
    return (
        <div
            className={cn(
                'flex flex-col items-center justify-center py-12 px-6 text-center',
                className
            )}
        >
            <div className="relative mb-4">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-orange-100 dark:bg-orange-900/30">
                    <Wrench className="h-8 w-8 text-orange-500" />
                </div>
                <Badge
                    variant="secondary"
                    className="absolute -top-2 -right-2 animate-pulse bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300"
                >
                    Soon
                </Badge>
            </div>
            <h3 className="text-lg font-semibold mb-2">Coming Soon</h3>
            <p className="text-sm text-muted-foreground max-w-sm mb-2">
                <span className="font-medium">{featureName}</span> is currently in development.
            </p>
            {description && (
                <p className="text-sm text-muted-foreground max-w-sm mb-6">
                    {description}
                </p>
            )}
            {onBack && (
                <Button variant="outline" onClick={onBack} className="mt-4">
                    <ArrowLeft className="mr-2 h-4 w-4" />
                    Go Back
                </Button>
            )}
        </div>
    );
}
