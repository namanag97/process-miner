'use client';

import { Loader2 } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';

interface AnalysisProgressCardProps {
    stage: string;
    progress: number;
}

const STAGE_LABELS: Record<string, string> = {
    'Starting': 'Initializing...',
    'Transforming data': 'Transforming events...',
    'Building cases': 'Grouping into cases...',
    'Building DFG': 'Building process graph...',
    'Analyzing variants': 'Analyzing variants...',
    'Calculating statistics': 'Calculating statistics...',
    'Complete': 'Analysis complete!',
    'Failed': 'Analysis failed',
};

export function AnalysisProgressCard({ stage, progress }: AnalysisProgressCardProps) {
    const displayLabel = STAGE_LABELS[stage] || stage;
    const isComplete = stage === 'Complete';
    const isFailed = stage === 'Failed';

    return (
        <Card className="w-full max-w-md">
            <CardContent className="flex flex-col items-center justify-center p-8 text-center">
                {!isComplete && !isFailed && (
                    <Loader2 className="h-10 w-10 animate-spin text-primary mb-4" />
                )}

                <h2 className="text-xl font-semibold mb-2">
                    {isComplete ? '✅ Analysis Complete' : isFailed ? '❌ Analysis Failed' : 'Analyzing...'}
                </h2>

                <p className="text-muted-foreground mb-4">{displayLabel}</p>

                <div className="w-full">
                    <Progress value={progress} className="h-2 mb-2" />
                    <p className="text-xs text-muted-foreground">
                        {Math.round(progress)}%
                    </p>
                </div>

                {/* Step indicator dots */}
                <div className="flex gap-2 mt-4">
                    {['Transforming', 'Grouping', 'Building DFG', 'Analyzing', 'Complete'].map((step, idx) => {
                        const stepProgress = (idx + 1) * 20;
                        const isActive = progress >= stepProgress - 20 && progress < stepProgress;
                        const isDone = progress >= stepProgress;

                        return (
                            <div
                                key={step}
                                className={`w-2 h-2 rounded-full transition-colors ${isDone
                                        ? 'bg-primary'
                                        : isActive
                                            ? 'bg-primary/50 animate-pulse'
                                            : 'bg-muted'
                                    }`}
                                title={step}
                            />
                        );
                    })}
                </div>
            </CardContent>
        </Card>
    );
}
