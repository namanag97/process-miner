'use client';

import { useEffect, useState } from 'react';
import { Loader2 } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';

interface AnalysisProgressCardProps {
    stage: string;
    progress: number;
}

export function AnalysisProgressCard({ stage, progress }: AnalysisProgressCardProps) {
    const isComplete = stage === 'Complete';
    const isFailed = stage === 'Failed';

    // Animated fake progress for better UX since real progress doesn't update during sync work
    const [fakeProgress, setFakeProgress] = useState(0);

    useEffect(() => {
        if (isComplete || isFailed) {
            setFakeProgress(100);
            return;
        }

        // Animate progress smoothly
        const interval = setInterval(() => {
            setFakeProgress(prev => {
                // Slow down as we approach 90% to never reach 100% until complete
                if (prev < 30) return prev + 2;
                if (prev < 60) return prev + 1;
                if (prev < 85) return prev + 0.5;
                if (prev < 95) return prev + 0.1;
                return prev;
            });
        }, 100);

        return () => clearInterval(interval);
    }, [isComplete, isFailed]);

    return (
        <Card className="w-full max-w-md">
            <CardContent className="flex flex-col items-center justify-center p-8 text-center">
                {!isComplete && !isFailed && (
                    <Loader2 className="h-12 w-12 animate-spin text-primary mb-6" />
                )}

                {isComplete && (
                    <div className="h-12 w-12 rounded-full bg-green-500/20 flex items-center justify-center mb-6">
                        <span className="text-2xl">✅</span>
                    </div>
                )}

                {isFailed && (
                    <div className="h-12 w-12 rounded-full bg-red-500/20 flex items-center justify-center mb-6">
                        <span className="text-2xl">❌</span>
                    </div>
                )}

                <h2 className="text-xl font-semibold mb-2">
                    {isComplete ? 'Analysis Complete' : isFailed ? 'Analysis Failed' : 'Analyzing Your Data...'}
                </h2>

                <p className="text-sm text-muted-foreground mb-6">
                    {isComplete
                        ? 'Your process map is ready to explore'
                        : isFailed
                            ? 'Something went wrong during analysis'
                            : 'Building process graph, analyzing variants, and detecting patterns...'}
                </p>

                {/* Animated progress bar */}
                <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                    <div
                        className="h-full bg-gradient-to-r from-primary to-primary/70 transition-all duration-300 ease-out"
                        style={{ width: `${fakeProgress}%` }}
                    />
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                    {Math.round(fakeProgress)}%
                </p>

                {/* Animated dots */}
                {!isComplete && !isFailed && (
                    <div className="flex gap-1 mt-4">
                        {[0, 1, 2].map((i) => (
                            <div
                                key={i}
                                className="w-2 h-2 rounded-full bg-primary animate-pulse"
                                style={{ animationDelay: `${i * 200}ms` }}
                            />
                        ))}
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
