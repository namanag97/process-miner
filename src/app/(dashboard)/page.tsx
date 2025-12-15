'use client';

import { useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useLogStore } from '@/lib/stores/useLogStore';
import { useAppStore } from '@/lib/stores/useAppStore';

export default function HomePage() {
    const addLog = useLogStore((state) => state.addLog);
    const _reset = useAppStore((state) => state.reset);

    useEffect(() => {
        addLog('info', 'ProcessMiner app initialized');
    }, [addLog]);

    const handleTestLogs = () => {
        addLog('info', 'This is an info message');
        addLog('success', 'Operation completed successfully');
        addLog('warning', 'This is a warning message');
        addLog('error', 'An error occurred');
    };

    return (
        <div className="container mx-auto p-6 space-y-6">
            <div>
                <h1 className="text-3xl font-bold mb-2">Welcome to ProcessMiner</h1>
                <p className="text-muted-foreground">
                    Discover, analyze, and optimize your business processes with powerful process mining capabilities.
                </p>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Quick Start Guide</CardTitle>
                    <CardDescription>Follow these steps to analyze your process data</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div>
                        <h3 className="font-semibold mb-1">1. Upload Data</h3>
                        <p className="text-sm text-muted-foreground">
                            Upload your event log data in CSV or XES format
                        </p>
                    </div>
                    <div>
                        <h3 className="font-semibold mb-1">2. Configure</h3>
                        <p className="text-sm text-muted-foreground">
                            Map columns to case ID, activity, timestamp, and optional fields
                        </p>
                    </div>
                    <div>
                        <h3 className="font-semibold mb-1">3. Analyze</h3>
                        <p className="text-sm text-muted-foreground">
                            View the discovered process map with flows and frequencies
                        </p>
                    </div>
                    <div>
                        <h3 className="font-semibold mb-1">4. Visualize Insights</h3>
                        <p className="text-sm text-muted-foreground">
                            Explore metrics, variants, and bottlenecks in your process
                        </p>
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Test Log Panel</CardTitle>
                    <CardDescription>Click the button to test the logging system</CardDescription>
                </CardHeader>
                <CardContent>
                    <Button onClick={handleTestLogs}>Add Test Logs</Button>
                </CardContent>
            </Card>
        </div>
    );
}
