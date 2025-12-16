'use client';

import { GitBranch } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import type { ProcessModel } from '@/lib/mining/types';
import { formatDuration } from '@/lib/utils';

interface VariantsTabProps {
    model: ProcessModel;
}

export function VariantsTab({ model }: VariantsTabProps) {
    const { variants } = model;

    // Sort variants by case count (descending)
    const sortedVariants = [...variants].sort((a, b) => b.caseCount - a.caseCount);

    return (
        <div className="space-y-4">
            <div className="flex items-center justify-between">
                <div>
                    <h3 className="text-lg font-medium">Process Variants</h3>
                    <p className="text-sm text-muted-foreground">
                        {variants.length} unique process paths discovered
                    </p>
                </div>
            </div>

            <ScrollArea className="h-[500px]">
                <div className="space-y-3 pr-4">
                    {sortedVariants.map((variant, index) => (
                        <Card
                            key={variant.id}
                            className={variant.isHappyPath ? 'border-green-500/50 bg-green-500/5' : ''}
                        >
                            <CardHeader className="pb-2">
                                <div className="flex items-center justify-between">
                                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                                        <GitBranch className="h-4 w-4" />
                                        Variant #{index + 1}
                                        {variant.isHappyPath && (
                                            <Badge variant="secondary" className="bg-green-500/20 text-green-700">
                                                Happy Path
                                            </Badge>
                                        )}
                                    </CardTitle>
                                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                        <span>{variant.caseCount} cases</span>
                                        <span>({variant.percentage.toFixed(1)}%)</span>
                                    </div>
                                </div>
                            </CardHeader>
                            <CardContent>
                                <div className="flex flex-wrap gap-1 mb-2">
                                    {variant.sequence.map((activity, actIdx) => (
                                        <span key={actIdx} className="flex items-center">
                                            <Badge variant="outline" className="text-xs">
                                                {activity}
                                            </Badge>
                                            {actIdx < variant.sequence.length - 1 && (
                                                <span className="mx-1 text-muted-foreground">→</span>
                                            )}
                                        </span>
                                    ))}
                                </div>
                                <p className="text-xs text-muted-foreground">
                                    Avg. duration: {formatDuration(variant.avgDuration)}
                                </p>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </ScrollArea>
        </div>
    );
}
