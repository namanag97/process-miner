'use client';

import { useState, useEffect, useRef } from 'react';
import { ChevronDown, ChevronUp, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useLogStore, type LogLevel } from '@/lib/stores/useLogStore';
import { cn } from '@/lib/utils';

const LOG_COLORS: Record<LogLevel, string> = {
    info: 'text-blue-600 dark:text-blue-400',
    success: 'text-green-600 dark:text-green-400',
    warning: 'text-yellow-600 dark:text-yellow-400',
    error: 'text-red-600 dark:text-red-400',
};

const LOG_BG_COLORS: Record<LogLevel, string> = {
    info: 'bg-blue-50 dark:bg-blue-950/30',
    success: 'bg-green-50 dark:bg-green-950/30',
    warning: 'bg-yellow-50 dark:bg-yellow-950/30',
    error: 'bg-red-50 dark:bg-red-950/30',
};

export function LogPanel() {
    const [isExpanded, setIsExpanded] = useState(false);
    const [lastViewedCount, setLastViewedCount] = useState(0);
    const { logs, clearLogs } = useLogStore();
    const scrollAreaRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when new logs arrive and panel is expanded
    useEffect(() => {
        if (isExpanded && scrollAreaRef.current) {
            const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
            if (scrollContainer) {
                scrollContainer.scrollTop = scrollContainer.scrollHeight;
            }
        }
    }, [logs, isExpanded]);

    // Update last viewed count when panel is expanded
    useEffect(() => {
        if (isExpanded) {
            setLastViewedCount(logs.length);
        }
    }, [isExpanded, logs.length]);

    const unreadCount = logs.length - lastViewedCount;

    const formatTime = (date: Date) => {
        return date.toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
        });
    };

    const handleToggle = () => {
        setIsExpanded(!isExpanded);
    };

    const handleClear = () => {
        clearLogs();
        setLastViewedCount(0);
    };

    return (
        <div
            className={cn(
                'fixed bottom-0 left-0 right-0 z-50 border-t bg-background transition-all duration-200',
                isExpanded ? 'h-[200px]' : 'h-[40px]'
            )}
        >
            {/* Header */}
            <div className="flex h-[40px] items-center justify-between border-b px-4">
                <div className="flex items-center gap-2">
                    <Button
                        variant="ghost"
                        size="sm"
                        onClick={handleToggle}
                        className="h-7 gap-1 px-2"
                    >
                        {isExpanded ? (
                            <ChevronDown className="h-4 w-4" />
                        ) : (
                            <ChevronUp className="h-4 w-4" />
                        )}
                        <span className="text-sm font-medium">Logs</span>
                    </Button>

                    {!isExpanded && unreadCount > 0 && (
                        <Badge variant="secondary" className="h-5 px-1.5 text-xs">
                            {unreadCount}
                        </Badge>
                    )}

                    <span className="text-xs text-muted-foreground">
                        {logs.length} {logs.length === 1 ? 'entry' : 'entries'}
                    </span>
                </div>

                <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleClear}
                    className="h-7 gap-1 px-2 text-xs"
                >
                    <X className="h-3 w-3" />
                    Clear
                </Button>
            </div>

            {/* Log Content */}
            {isExpanded && (
                <ScrollArea ref={scrollAreaRef} className="h-[calc(200px-40px)]">
                    <div className="space-y-0.5 p-2 font-mono text-xs">
                        {logs.length === 0 ? (
                            <div className="flex h-full items-center justify-center py-8 text-muted-foreground">
                                No logs yet
                            </div>
                        ) : (
                            logs.map((log) => (
                                <div
                                    key={log.id}
                                    className={cn(
                                        'flex gap-3 rounded px-2 py-1',
                                        LOG_BG_COLORS[log.level]
                                    )}
                                >
                                    <span className="text-muted-foreground">
                                        {formatTime(log.timestamp)}
                                    </span>
                                    <span
                                        className={cn(
                                            'w-16 flex-shrink-0 font-semibold uppercase',
                                            LOG_COLORS[log.level]
                                        )}
                                    >
                                        {log.level}
                                    </span>
                                    <span className="flex-1">
                                        {log.message}
                                        {log.details && (
                                            <span className="ml-2 text-muted-foreground">
                                                {JSON.stringify(log.details)}
                                            </span>
                                        )}
                                    </span>
                                </div>
                            ))
                        )}
                    </div>
                </ScrollArea>
            )}
        </div>
    );
}
