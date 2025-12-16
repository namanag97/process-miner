'use client';

import { useMemo } from 'react';
import { format } from 'date-fns';
import { cn } from '@/lib/utils';
import { formatDuration } from '@/lib/utils';

interface CaseTimelineProps {
    events: Array<{
        activity: string;
        timestamp: Date;
        resource?: string;
    }>;
    reworkActivities?: Set<string>;
    happyPathSequence?: string[];
}

const EVENT_COLORS = {
    start: 'bg-green-500 border-green-600',
    end: 'bg-red-500 border-red-600',
    normal: 'bg-blue-500 border-blue-600',
    rework: 'bg-orange-500 border-orange-600',
};

export function CaseTimeline({ events, reworkActivities = new Set(), happyPathSequence = [] }: CaseTimelineProps) {
    // Prepare events with timing info
    const enrichedEvents = useMemo(() => {
        return events.map((event, idx) => {
            const isStart = idx === 0;
            const isEnd = idx === events.length - 1;
            const isRework = reworkActivities.has(event.activity);

            // Calculate duration to next event
            let durationToNext: number | null = null;
            if (idx < events.length - 1) {
                durationToNext = events[idx + 1].timestamp.getTime() - event.timestamp.getTime();
            }

            let colorClass = EVENT_COLORS.normal;
            if (isStart) colorClass = EVENT_COLORS.start;
            else if (isEnd) colorClass = EVENT_COLORS.end;
            else if (isRework) colorClass = EVENT_COLORS.rework;

            return {
                ...event,
                isStart,
                isEnd,
                isRework,
                durationToNext,
                colorClass,
            };
        });
    }, [events, reworkActivities]);

    if (events.length === 0) {
        return <p className="text-muted-foreground text-sm">No events</p>;
    }

    return (
        <div className="overflow-x-auto pb-2">
            <div className="flex items-start min-w-max">
                {enrichedEvents.map((event, idx) => (
                    <div key={idx} className="flex items-start">
                        {/* Event Node */}
                        <div className="flex flex-col items-center">
                            {/* Circle */}
                            <div
                                className={cn(
                                    'w-4 h-4 rounded-full border-2 shrink-0',
                                    event.colorClass
                                )}
                                title={`${event.isStart ? 'Start: ' : event.isEnd ? 'End: ' : ''}${event.activity}`}
                            />

                            {/* Activity details */}
                            <div className="mt-2 text-center max-w-[120px]">
                                <p className="text-xs font-medium truncate" title={event.activity}>
                                    {event.activity}
                                </p>
                                <p className="text-[10px] text-muted-foreground">
                                    {format(event.timestamp, 'HH:mm:ss')}
                                </p>
                                {event.resource && (
                                    <p className="text-[10px] text-muted-foreground truncate" title={event.resource}>
                                        {event.resource}
                                    </p>
                                )}
                            </div>
                        </div>

                        {/* Connector line with duration */}
                        {idx < enrichedEvents.length - 1 && (
                            <div className="flex flex-col items-center mx-1">
                                <div className="relative w-16 h-4 flex items-center">
                                    <div className="absolute inset-x-0 top-1/2 h-0.5 bg-muted-foreground/40" />
                                    {event.durationToNext !== null && event.durationToNext > 0 && (
                                        <span className="relative mx-auto px-1 text-[9px] text-muted-foreground bg-background">
                                            {formatDuration(event.durationToNext)}
                                        </span>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {/* Legend */}
            <div className="flex items-center gap-3 mt-4 text-xs text-muted-foreground">
                <div className="flex items-center gap-1">
                    <div className={cn('w-2.5 h-2.5 rounded-full', EVENT_COLORS.start)} />
                    <span>Start</span>
                </div>
                <div className="flex items-center gap-1">
                    <div className={cn('w-2.5 h-2.5 rounded-full', EVENT_COLORS.end)} />
                    <span>End</span>
                </div>
                <div className="flex items-center gap-1">
                    <div className={cn('w-2.5 h-2.5 rounded-full', EVENT_COLORS.normal)} />
                    <span>Normal</span>
                </div>
                <div className="flex items-center gap-1">
                    <div className={cn('w-2.5 h-2.5 rounded-full', EVENT_COLORS.rework)} />
                    <span>Rework</span>
                </div>
            </div>
        </div>
    );
}
