'use client';

import { cn } from '@/lib/utils';

interface ActivitySequenceProps {
    sequence: string[];
    className?: string;
    compact?: boolean;
}

/**
 * Horizontal activity flow visualization
 * Displays activities as connected boxes with arrows
 */
export function ActivitySequence({ sequence, className, compact = false }: ActivitySequenceProps) {
    if (sequence.length === 0) return null;

    return (
        <div className={cn('flex flex-wrap items-center gap-1', className)}>
            {sequence.map((activity, index) => (
                <span key={index} className="flex items-center">
                    <span
                        className={cn(
                            'shrink-0 rounded border border-border bg-muted px-2 py-0.5 text-xs font-medium',
                            compact && 'px-1.5 py-0.5 text-[10px]'
                        )}
                    >
                        {activity}
                    </span>
                    {index < sequence.length - 1 && (
                        <span
                            className={cn(
                                'mx-1 text-muted-foreground',
                                compact && 'mx-0.5 text-xs'
                            )}
                        >
                            →
                        </span>
                    )}
                </span>
            ))}
        </div>
    );
}
