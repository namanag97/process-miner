'use client';

import { X, Clock, Hash, ArrowRight, Play, Square } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import type { ProcessModel } from '@/lib/mining/types';
import { formatDuration } from '@/lib/utils';

interface NodeDetailPanelProps {
    model: ProcessModel;
    selectedNodeId: string | null;
    selectedEdgeId: string | null;
    onClose: () => void;
}

export function NodeDetailPanel({
    model,
    selectedNodeId,
    selectedEdgeId,
    onClose,
}: NodeDetailPanelProps) {
    if (!selectedNodeId && !selectedEdgeId) {
        return null;
    }

    // Find selected activity
    const selectedActivity = selectedNodeId
        ? model.activities.find(a => a.name === selectedNodeId)
        : null;

    // Find selected edge
    const selectedEdge = selectedEdgeId
        ? model.edges.find((_, idx) => `edge-${idx}` === selectedEdgeId)
        : null;

    // Find connected activities for the selected node
    const incomingEdges = selectedNodeId
        ? model.edges.filter(e => e.target === selectedNodeId)
        : [];
    const outgoingEdges = selectedNodeId
        ? model.edges.filter(e => e.source === selectedNodeId)
        : [];

    return (
        <Card className="absolute top-4 left-4 z-10 w-80">
            <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium">
                        {selectedActivity ? 'Activity Details' : 'Transition Details'}
                    </CardTitle>
                    <Button variant="ghost" size="icon" className="h-6 w-6" onClick={onClose}>
                        <X className="h-4 w-4" />
                    </Button>
                </div>
            </CardHeader>

            <CardContent className="space-y-4">
                {selectedActivity && (
                    <>
                        <div>
                            <h3 className="font-semibold text-lg">{selectedActivity.name}</h3>
                            <div className="flex gap-1 mt-1">
                                {selectedActivity.isStart && (
                                    <Badge variant="secondary" className="text-xs bg-green-500/20 text-green-700">
                                        <Play className="h-3 w-3 mr-1" />
                                        Start
                                    </Badge>
                                )}
                                {selectedActivity.isEnd && (
                                    <Badge variant="secondary" className="text-xs bg-red-500/20 text-red-700">
                                        <Square className="h-3 w-3 mr-1" />
                                        End
                                    </Badge>
                                )}
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-3 text-sm">
                            <div className="flex items-center gap-2">
                                <Hash className="h-4 w-4 text-muted-foreground" />
                                <div>
                                    <p className="text-muted-foreground text-xs">Frequency</p>
                                    <p className="font-medium">{selectedActivity.frequency.toLocaleString()}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                <Clock className="h-4 w-4 text-muted-foreground" />
                                <div>
                                    <p className="text-muted-foreground text-xs">Avg Duration</p>
                                    <p className="font-medium">{formatDuration(selectedActivity.avgDuration)}</p>
                                </div>
                            </div>
                        </div>

                        <Separator />

                        {incomingEdges.length > 0 && (
                            <div>
                                <p className="text-xs font-medium text-muted-foreground mb-2">
                                    Incoming from ({incomingEdges.length})
                                </p>
                                <div className="flex flex-wrap gap-1">
                                    {incomingEdges.slice(0, 5).map((edge, idx) => (
                                        <Badge key={idx} variant="outline" className="text-xs">
                                            {edge.source} ({edge.frequency})
                                        </Badge>
                                    ))}
                                    {incomingEdges.length > 5 && (
                                        <Badge variant="outline" className="text-xs">
                                            +{incomingEdges.length - 5} more
                                        </Badge>
                                    )}
                                </div>
                            </div>
                        )}

                        {outgoingEdges.length > 0 && (
                            <div>
                                <p className="text-xs font-medium text-muted-foreground mb-2">
                                    Outgoing to ({outgoingEdges.length})
                                </p>
                                <div className="flex flex-wrap gap-1">
                                    {outgoingEdges.slice(0, 5).map((edge, idx) => (
                                        <Badge key={idx} variant="outline" className="text-xs">
                                            {edge.target} ({edge.frequency})
                                        </Badge>
                                    ))}
                                    {outgoingEdges.length > 5 && (
                                        <Badge variant="outline" className="text-xs">
                                            +{outgoingEdges.length - 5} more
                                        </Badge>
                                    )}
                                </div>
                            </div>
                        )}
                    </>
                )}

                {selectedEdge && (
                    <>
                        <div className="flex items-center gap-2 text-lg font-semibold">
                            <span>{selectedEdge.source}</span>
                            <ArrowRight className="h-5 w-5 text-muted-foreground" />
                            <span>{selectedEdge.target}</span>
                        </div>

                        <div className="grid grid-cols-2 gap-3 text-sm">
                            <div className="flex items-center gap-2">
                                <Hash className="h-4 w-4 text-muted-foreground" />
                                <div>
                                    <p className="text-muted-foreground text-xs">Frequency</p>
                                    <p className="font-medium">{selectedEdge.frequency.toLocaleString()}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                <Clock className="h-4 w-4 text-muted-foreground" />
                                <div>
                                    <p className="text-muted-foreground text-xs">Avg Duration</p>
                                    <p className="font-medium">{formatDuration(selectedEdge.avgDuration)}</p>
                                </div>
                            </div>
                        </div>

                        <Separator />

                        <div>
                            <p className="text-xs font-medium text-muted-foreground mb-2">
                                Cases ({selectedEdge.cases.length})
                            </p>
                            <ScrollArea className="h-24">
                                <div className="flex flex-wrap gap-1">
                                    {selectedEdge.cases.slice(0, 20).map((caseId, idx) => (
                                        <Badge key={idx} variant="outline" className="text-xs">
                                            {caseId}
                                        </Badge>
                                    ))}
                                    {selectedEdge.cases.length > 20 && (
                                        <Badge variant="outline" className="text-xs">
                                            +{selectedEdge.cases.length - 20} more
                                        </Badge>
                                    )}
                                </div>
                            </ScrollArea>
                        </div>
                    </>
                )}
            </CardContent>
        </Card>
    );
}
