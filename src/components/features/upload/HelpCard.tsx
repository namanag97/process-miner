'use client';

import { HelpCircle, FileSpreadsheet, ExternalLink } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';

export function HelpCard() {
    return (
        <Card>
            <CardHeader className="pb-3">
                <CardTitle className="flex items-center gap-2 text-base">
                    <HelpCircle className="h-4 w-4" />
                    What is an Event Log?
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                <p className="text-sm text-muted-foreground">
                    An event log is a record of activities that happened in your business
                    process. Each row represents a single event with at least three key
                    pieces of information.
                </p>

                <Separator />

                <div className="space-y-3">
                    <h4 className="text-sm font-medium flex items-center gap-2">
                        <FileSpreadsheet className="h-4 w-4 text-primary" />
                        Required Columns
                    </h4>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                        <li className="flex gap-2">
                            <span className="font-mono text-xs bg-muted px-1.5 py-0.5 rounded">
                                Case ID
                            </span>
                            <span>Unique identifier for each process instance</span>
                        </li>
                        <li className="flex gap-2">
                            <span className="font-mono text-xs bg-muted px-1.5 py-0.5 rounded">
                                Activity
                            </span>
                            <span>Name of the activity that was performed</span>
                        </li>
                        <li className="flex gap-2">
                            <span className="font-mono text-xs bg-muted px-1.5 py-0.5 rounded">
                                Timestamp
                            </span>
                            <span>When the activity occurred</span>
                        </li>
                    </ul>
                </div>

                <Separator />

                <div>
                    <a
                        href="#"
                        className="inline-flex items-center gap-1 text-sm text-primary hover:underline"
                    >
                        <ExternalLink className="h-3 w-3" />
                        Download sample data
                    </a>
                </div>
            </CardContent>
        </Card>
    );
}
