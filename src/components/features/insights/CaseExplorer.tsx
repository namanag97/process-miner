'use client';

import { useState, useMemo, useEffect } from 'react';
import { format } from 'date-fns';
import {
    Search,
    ChevronDown,
    ChevronUp,
    CheckCircle2,
    AlertTriangle,
    FileJson,
    FileSpreadsheet,
    ArrowUpDown,
} from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

import { formatDuration, cn } from '@/lib/utils';
import { createLogger } from '@/lib/debug-logger';
import { exportSingleCaseJSON, exportSingleCaseCSV } from '@/lib/export/exportUtils';
import type { ProcessModel, Deviation } from '@/lib/mining/types';

import { CaseTimeline } from './CaseTimeline';

const logger = createLogger('case-explorer');

interface CaseData {
    caseId: string;
    startTime: Date;
    endTime: Date;
    duration: number;
    eventCount: number;
    variant: string;
    hasDeviation: boolean;
    events: Array<{
        activity: string;
        timestamp: Date;
        resource?: string;
    }>;
}

interface CaseExplorerProps {
    cases: CaseData[];
    model: ProcessModel;
}

type SortField = 'caseId' | 'startTime' | 'duration' | 'eventCount';
type SortDirection = 'asc' | 'desc';

const PAGE_SIZE = 20;

export function CaseExplorer({ cases, model }: CaseExplorerProps) {
    const [search, setSearch] = useState('');
    const [sortField, setSortField] = useState<SortField>('startTime');
    const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
    const [page, setPage] = useState(0);
    const [expandedCaseId, setExpandedCaseId] = useState<string | null>(null);

    // Get rework activities for highlighting
    const reworkActivities = useMemo(() => {
        const activities = new Set<string>();
        model.deviations
            .filter((d) => d.type === 'rework')
            .forEach((d) => {
                const match = d.description.match(/Activity '([^']+)'/);
                if (match) activities.add(match[1]);
            });
        return activities;
    }, [model.deviations]);

    // Get happy path sequence
    const happyPathSequence = useMemo(() => {
        const happyPath = model.variants.find((v) => v.isHappyPath);
        return happyPath?.sequence || [];
    }, [model.variants]);

    // Filter and sort cases
    const filteredCases = useMemo(() => {
        let result = cases;

        // Search filter
        if (search.trim()) {
            const searchLower = search.toLowerCase();
            result = result.filter((c) =>
                c.caseId.toLowerCase().includes(searchLower)
            );
        }

        // Sort
        result = [...result].sort((a, b) => {
            let comparison = 0;
            switch (sortField) {
                case 'caseId':
                    comparison = a.caseId.localeCompare(b.caseId);
                    break;
                case 'startTime':
                    comparison = a.startTime.getTime() - b.startTime.getTime();
                    break;
                case 'duration':
                    comparison = a.duration - b.duration;
                    break;
                case 'eventCount':
                    comparison = a.eventCount - b.eventCount;
                    break;
            }
            return sortDirection === 'asc' ? comparison : -comparison;
        });

        return result;
    }, [cases, search, sortField, sortDirection]);

    // Pagination
    const totalPages = Math.ceil(filteredCases.length / PAGE_SIZE);
    const paginatedCases = filteredCases.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

    // Reset page when search changes
    useEffect(() => {
        setPage(0);
    }, [search]);

    // Log on mount
    useEffect(() => {
        logger.info(`📋 Loaded case explorer with ${cases.length} cases`);
    }, [cases.length]);

    const handleSort = (field: SortField) => {
        if (sortField === field) {
            setSortDirection((d) => (d === 'asc' ? 'desc' : 'asc'));
        } else {
            setSortField(field);
            setSortDirection('desc');
        }
    };

    const toggleExpand = (caseId: string) => {
        setExpandedCaseId((prev) => (prev === caseId ? null : caseId));
    };

    const handleExportJSON = (caseData: CaseData) => {
        exportSingleCaseJSON({
            caseId: caseData.caseId,
            startTime: caseData.startTime,
            endTime: caseData.endTime,
            duration: caseData.duration,
            variant: caseData.variant,
            events: caseData.events,
        });
    };

    const handleExportCSV = (caseData: CaseData) => {
        exportSingleCaseCSV({
            caseId: caseData.caseId,
            events: caseData.events,
        });
    };

    const SortButton = ({ field, children }: { field: SortField; children: React.ReactNode }) => (
        <Button
            variant="ghost"
            size="sm"
            className="h-8 -ml-3 font-medium"
            onClick={() => handleSort(field)}
        >
            {children}
            <ArrowUpDown className="ml-1 h-3 w-3" />
        </Button>
    );

    return (
        <Card>
            <CardHeader className="pb-4">
                <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">Case Explorer</CardTitle>
                    <div className="relative w-64">
                        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                        <Input
                            placeholder="Search by Case ID..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="pl-9"
                        />
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                <div className="rounded-md border">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead className="w-[50px]" />
                                <TableHead>
                                    <SortButton field="caseId">Case ID</SortButton>
                                </TableHead>
                                <TableHead>
                                    <SortButton field="startTime">Start Time</SortButton>
                                </TableHead>
                                <TableHead>End Time</TableHead>
                                <TableHead>
                                    <SortButton field="duration">Duration</SortButton>
                                </TableHead>
                                <TableHead>
                                    <SortButton field="eventCount">Events</SortButton>
                                </TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead className="w-[100px]">Actions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {paginatedCases.map((c) => (
                                <>
                                    <TableRow
                                        key={c.caseId}
                                        className={cn(
                                            'cursor-pointer',
                                            expandedCaseId === c.caseId && 'bg-muted/50'
                                        )}
                                        onClick={() => toggleExpand(c.caseId)}
                                    >
                                        <TableCell>
                                            {expandedCaseId === c.caseId ? (
                                                <ChevronUp className="h-4 w-4" />
                                            ) : (
                                                <ChevronDown className="h-4 w-4" />
                                            )}
                                        </TableCell>
                                        <TableCell className="font-mono text-sm">
                                            {c.caseId}
                                        </TableCell>
                                        <TableCell className="text-sm">
                                            {format(c.startTime, 'PPp')}
                                        </TableCell>
                                        <TableCell className="text-sm">
                                            {format(c.endTime, 'PPp')}
                                        </TableCell>
                                        <TableCell className="text-sm">
                                            {formatDuration(c.duration)}
                                        </TableCell>
                                        <TableCell className="text-sm">{c.eventCount}</TableCell>
                                        <TableCell>
                                            {c.hasDeviation ? (
                                                <Badge
                                                    variant="secondary"
                                                    className="bg-yellow-500/20 text-yellow-700 gap-1"
                                                >
                                                    <AlertTriangle className="h-3 w-3" />
                                                    Deviation
                                                </Badge>
                                            ) : (
                                                <Badge
                                                    variant="secondary"
                                                    className="bg-green-500/20 text-green-700 gap-1"
                                                >
                                                    <CheckCircle2 className="h-3 w-3" />
                                                    Happy Path
                                                </Badge>
                                            )}
                                        </TableCell>
                                        <TableCell onClick={(e) => e.stopPropagation()}>
                                            <DropdownMenu>
                                                <DropdownMenuTrigger asChild>
                                                    <Button variant="ghost" size="sm">
                                                        Export
                                                    </Button>
                                                </DropdownMenuTrigger>
                                                <DropdownMenuContent align="end">
                                                    <DropdownMenuItem onClick={() => handleExportJSON(c)}>
                                                        <FileJson className="h-4 w-4 mr-2" />
                                                        Export as JSON
                                                    </DropdownMenuItem>
                                                    <DropdownMenuItem onClick={() => handleExportCSV(c)}>
                                                        <FileSpreadsheet className="h-4 w-4 mr-2" />
                                                        Export as CSV
                                                    </DropdownMenuItem>
                                                </DropdownMenuContent>
                                            </DropdownMenu>
                                        </TableCell>
                                    </TableRow>

                                    {/* Expanded Detail */}
                                    {expandedCaseId === c.caseId && (
                                        <TableRow>
                                            <TableCell colSpan={8} className="bg-muted/30 p-4">
                                                <div className="space-y-4">
                                                    <div className="flex items-center gap-4 text-sm">
                                                        <span className="text-muted-foreground">Variant:</span>
                                                        <span className="font-mono text-xs truncate max-w-[500px]" title={c.variant}>
                                                            {c.variant}
                                                        </span>
                                                    </div>
                                                    <div>
                                                        <h4 className="text-sm font-medium mb-3">Event Timeline</h4>
                                                        <CaseTimeline
                                                            events={c.events}
                                                            reworkActivities={reworkActivities}
                                                            happyPathSequence={happyPathSequence}
                                                        />
                                                    </div>
                                                </div>
                                            </TableCell>
                                        </TableRow>
                                    )}
                                </>
                            ))}
                            {paginatedCases.length === 0 && (
                                <TableRow>
                                    <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                                        {search ? 'No cases match your search' : 'No cases available'}
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                    <div className="flex items-center justify-between mt-4">
                        <p className="text-sm text-muted-foreground">
                            Showing {page * PAGE_SIZE + 1}-{Math.min((page + 1) * PAGE_SIZE, filteredCases.length)} of{' '}
                            {filteredCases.length} cases
                        </p>
                        <div className="flex items-center gap-2">
                            <Button
                                variant="outline"
                                size="sm"
                                disabled={page === 0}
                                onClick={() => setPage((p) => p - 1)}
                            >
                                Previous
                            </Button>
                            <span className="text-sm text-muted-foreground">
                                Page {page + 1} of {totalPages}
                            </span>
                            <Button
                                variant="outline"
                                size="sm"
                                disabled={page >= totalPages - 1}
                                onClick={() => setPage((p) => p + 1)}
                            >
                                Next
                            </Button>
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
