'use client';

import { Card, CardContent } from '@/components/ui/card';

export function ProcessMapLegend() {
    return (
        <Card className="absolute top-4 right-4 z-10">
            <CardContent className="p-3 space-y-2">
                <h4 className="text-xs font-semibold uppercase text-muted-foreground">Legend</h4>

                <div className="space-y-1.5 text-xs">
                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded border-l-2 border-l-green-500 bg-card border" />
                        <span>Start Activity</span>
                    </div>

                    <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded border-l-2 border-l-red-500 bg-card border" />
                        <span>End Activity</span>
                    </div>

                    <div className="flex items-center gap-2 pt-1 border-t">
                        <div className="w-6 h-0.5 bg-muted-foreground rounded" />
                        <span>Low frequency</span>
                    </div>

                    <div className="flex items-center gap-2">
                        <div className="w-6 h-1.5 bg-muted-foreground rounded" />
                        <span>High frequency</span>
                    </div>

                    <div className="flex items-center gap-2">
                        <div className="w-6 h-0.5 bg-muted-foreground rounded border-dashed border" style={{ borderStyle: 'dashed' }} />
                        <span>Rare path (&lt;5%)</span>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
