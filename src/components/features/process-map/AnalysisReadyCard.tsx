'use client';

import { Workflow } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface AnalysisReadyCardProps {
    eventCount: number;
    caseCount: number;
    onRunAnalysis: () => void;
    isLoading?: boolean;
}

export function AnalysisReadyCard({
    eventCount,
    caseCount,
    onRunAnalysis,
    isLoading = false,
}: AnalysisReadyCardProps) {
    return (
        <Card className="w-full max-w-md">
            <CardContent className="flex flex-col items-center justify-center p-8 text-center">
                <div className="mb-6 rounded-full bg-primary/10 p-4">
                    <Workflow className="h-12 w-12 text-primary" />
                </div>

                <h2 className="text-2xl font-semibold mb-2">Ready to Analyze</h2>

                <p className="text-muted-foreground mb-6">
                    {eventCount.toLocaleString()} events across{' '}
                    {caseCount.toLocaleString()} cases
                </p>

                <Button
                    size="lg"
                    onClick={onRunAnalysis}
                    disabled={isLoading}
                    className="w-full"
                >
                    {isLoading ? 'Starting...' : 'Run Process Mining'}
                </Button>
            </CardContent>
        </Card>
    );
}
