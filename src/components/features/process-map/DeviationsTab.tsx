'use client';

import { AlertTriangle, RefreshCw, SkipForward, Route } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import type { ProcessModel, Deviation } from '@/lib/mining/types';

interface DeviationsTabProps {
    model: ProcessModel;
}

const DEVIATION_ICONS: Record<Deviation['type'], React.ReactNode> = {
    rework: <RefreshCw className="h-4 w-4" />,
    skip: <SkipForward className="h-4 w-4" />,
    unusual_path: <Route className="h-4 w-4" />,
};

const DEVIATION_COLORS: Record<Deviation['type'], string> = {
    rework: 'bg-orange-500/20 text-orange-700 border-orange-500/50',
    skip: 'bg-red-500/20 text-red-700 border-red-500/50',
    unusual_path: 'bg-yellow-500/20 text-yellow-700 border-yellow-500/50',
};

const DEVIATION_LABELS: Record<Deviation['type'], string> = {
    rework: 'Rework',
    skip: 'Skip',
    unusual_path: 'Unusual Path',
};

export function DeviationsTab({ model }: DeviationsTabProps) {
    const { deviations } = model;

    // Sort by frequency (descending)
    const sortedDeviations = [...deviations].sort((a, b) => b.frequency - a.frequency);

    if (deviations.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center py-12 text-center">
                <div className="rounded-full bg-green-500/10 p-4 mb-4">
                    <AlertTriangle className="h-8 w-8 text-green-600" />
                </div>
                <h3 className="text-lg font-medium">No Deviations Detected</h3>
                <p className="text-sm text-muted-foreground mt-1">
                    All cases follow expected process patterns
                </p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <div>
                    <h3 className="text-lg font-medium">Process Deviations</h3>
                    <p className="text-sm text-muted-foreground">
                        {deviations.length} deviation patterns detected
                    </p>
                </div>
            </div>

            <ScrollArea className="h-[500px]">
                <div className="space-y-3 pr-4">
                    {sortedDeviations.map((deviation, index) => (
                        <Card key={index} className={DEVIATION_COLORS[deviation.type]}>
                            <CardHeader className="pb-2">
                                <div className="flex items-center justify-between">
                                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                                        {DEVIATION_ICONS[deviation.type]}
                                        <Badge variant="outline" className={DEVIATION_COLORS[deviation.type]}>
                                            {DEVIATION_LABELS[deviation.type]}
                                        </Badge>
                                    </CardTitle>
                                    <span className="text-sm text-muted-foreground">
                                        {deviation.frequency} occurrences
                                    </span>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <p className="text-sm mb-2">{deviation.description}</p>
                                <p className="text-xs text-muted-foreground">
                                    Affects {deviation.affectedCases.length} case{deviation.affectedCases.length !== 1 ? 's' : ''}
                                </p>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </ScrollArea>
        </div>
    );
}
