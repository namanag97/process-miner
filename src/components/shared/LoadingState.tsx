import { Skeleton } from '@/components/ui/skeleton';
import { Loader2 } from 'lucide-react';

interface LoadingStateProps {
    text?: string;
    variant?: 'spinner' | 'skeleton';
}

export function LoadingState({ text, variant = 'spinner' }: LoadingStateProps) {
    if (variant === 'skeleton') {
        return (
            <div className="flex flex-col items-center justify-center p-8 space-y-4">
                <Skeleton className="h-12 w-12 rounded-full" />
                <Skeleton className="h-4 w-48" />
                <Skeleton className="h-4 w-32" />
            </div>
        );
    }

    return (
        <div className="flex flex-col items-center justify-center p-8 space-y-4">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            {text && (
                <p className="text-sm text-muted-foreground">{text}</p>
            )}
        </div>
    );
}
