'use client';

import { useEffect, useRef } from 'react';
import { format } from 'date-fns';
import { ScrollText } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useLogStore, type LogLevel } from '@/lib/stores/useLogStore';

interface LogPanelProps {
    className?: string;
    maxHeight?: string;
}

const getLogColor = (level: LogLevel) => {
    switch (level) {
        case 'success':
            return 'text-green-600 dark:text-green-400';
        case 'error':
            return 'text-red-600 dark:text-red-400';
        case 'warning':
            return 'text-yellow-600 dark:text-yellow-400';
        default:
            return 'text-muted-foreground';
    }
};

export function LogPanel({ className, maxHeight = '300px' }: LogPanelProps) {
    const { logs } = useLogStore();
    const scrollRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when new logs are added
    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    return (
        <div className={cn('rounded-lg border bg-card', className)}>
            <div className="flex items-center gap-2 border-b px-4 py-3">
                <ScrollText className="h-4 w-4 text-muted-foreground" />
                <h3 className="text-sm font-medium">Activity Log</h3>
                <span className="ml-auto text-xs text-muted-foreground">
                    {logs.length} entries
                </span>
            </div>
            <div
                ref={scrollRef}
                className="overflow-y-auto p-4 font-mono text-xs"
                style={{ maxHeight }}
            >
                {logs.length === 0 ? (
                    <p className="text-muted-foreground italic">
                        No activity yet. Upload a file to get started.
                    </p>
                ) : (
                    <div className="space-y-1">
                        {logs.map((log) => (
                            <div
                                key={log.id}
                                className={cn('flex gap-2', getLogColor(log.level))}
                            >
                                <span className="shrink-0 text-muted-foreground">
                                    [{format(log.timestamp, 'HH:mm:ss')}]
                                </span>
                                <span>{log.message}</span>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
