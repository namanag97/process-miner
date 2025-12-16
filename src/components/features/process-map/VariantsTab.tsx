'use client';

import { useState, useMemo, useEffect } from 'react';
import { Star, ArrowUpDown, Eye } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { Slider } from '@/components/ui/slider';
import { Label } from '@/components/ui/label';
import type { ProcessModel, ProcessVariant } from '@/lib/mining/types';
import { formatDuration } from '@/lib/utils';
import { createLogger } from '@/lib/debug-logger';
import { ActivitySequence } from './ActivitySequence';
import { VariantCasesDialog } from './VariantCasesDialog';

const logger = createLogger('variants-tab');

interface VariantsTabProps {
    model: ProcessModel;
}

type SortOption = 'frequency' | 'duration' | 'activityCount';

// Colors for pie chart
const CHART_COLORS = [
    '#6366f1', // indigo
    '#8b5cf6', // violet
    '#a855f7', // purple
    '#d946ef', // fuchsia
    '#ec4899', // pink
    '#94a3b8', // slate (for "Other")
];

export function VariantsTab({ model }: VariantsTabProps) {
    const { variants, stats } = model;

    // State
    const [sortBy, setSortBy] = useState<SortOption>('frequency');
    const [minCaseCount, setMinCaseCount] = useState(0);
    const [selectedVariant, setSelectedVariant] = useState<ProcessVariant | null>(null);
    const [dialogOpen, setDialogOpen] = useState(false);

    // Calculate max case count for slider
    const maxCaseCount = useMemo(() => {
        if (variants.length === 0) return 10;
        return Math.max(...variants.map((v) => v.caseCount));
    }, [variants]);

    // Sort and filter variants
    const filteredVariants = useMemo(() => {
        let result = variants.filter((v) => v.caseCount >= minCaseCount);

        switch (sortBy) {
            case 'frequency':
                result = [...result].sort((a, b) => b.caseCount - a.caseCount);
                break;
            case 'duration':
                result = [...result].sort((a, b) => b.avgDuration - a.avgDuration);
                break;
            case 'activityCount':
                result = [...result].sort((a, b) => b.sequence.length - a.sequence.length);
                break;
        }

        return result;
    }, [variants, sortBy, minCaseCount]);

    // Prepare pie chart data (top 5 + Other)
    const pieChartData = useMemo(() => {
        const sortedByFreq = [...variants].sort((a, b) => b.caseCount - a.caseCount);
        const top5 = sortedByFreq.slice(0, 5);
        const otherCount = sortedByFreq.slice(5).reduce((sum, v) => sum + v.caseCount, 0);

        const data = top5.map((v, i) => ({
            name: `Variant #${i + 1}`,
            value: v.caseCount,
            percentage: v.percentage,
        }));

        if (otherCount > 0) {
            const otherPercentage = sortedByFreq
                .slice(5)
                .reduce((sum, v) => sum + v.percentage, 0);
            data.push({
                name: 'Other',
                value: otherCount,
                percentage: otherPercentage,
            });
        }

        return data;
    }, [variants]);

    // Calculate happy path coverage
    const happyPathCoverage = useMemo(() => {
        const happyPath = variants.find((v) => v.isHappyPath);
        return happyPath?.percentage || 0;
    }, [variants]);

    // Log on mount
    useEffect(() => {
        logger.info(`📊 Displaying ${variants.length} variants, happy path covers ${happyPathCoverage.toFixed(1)}%`);
    }, [variants.length, happyPathCoverage]);

    const handleViewCases = (variant: ProcessVariant) => {
        setSelectedVariant(variant);
        setDialogOpen(true);
    };

    // Get rank with original order preserved
    const getRank = (variant: ProcessVariant): number => {
        const sortedByFreq = [...variants].sort((a, b) => b.caseCount - a.caseCount);
        return sortedByFreq.findIndex((v) => v.id === variant.id) + 1;
    };

    return (
        <div className="space-y-6">
            {/* Summary Section */}
            <div className="flex flex-col lg:flex-row gap-6">
                {/* Stats Card */}
                <Card className="flex-1">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-lg">Process Variants</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold">
                            {variants.length}
                        </div>
                        <p className="text-sm text-muted-foreground">
                            unique process paths discovered
                        </p>
                        <div className="mt-4 flex items-center gap-2">
                            <Star className="h-4 w-4 text-green-600" />
                            <span className="text-sm">
                                Happy path covers <strong>{happyPathCoverage.toFixed(1)}%</strong> of cases
                            </span>
                        </div>
                    </CardContent>
                </Card>

                {/* Pie Chart */}
                <Card className="flex-1">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-lg">Variant Distribution</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="h-[180px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={pieChartData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={40}
                                        outerRadius={70}
                                        paddingAngle={2}
                                        dataKey="value"
                                    >
                                        {pieChartData.map((_, index) => (
                                            <Cell
                                                key={`cell-${index}`}
                                                fill={CHART_COLORS[index % CHART_COLORS.length]}
                                            />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        formatter={(value, name) => [
                                            `${value} cases`,
                                            name,
                                        ]}
                                    />
                                    <Legend
                                        layout="vertical"
                                        align="right"
                                        verticalAlign="middle"
                                        iconSize={10}
                                        wrapperStyle={{ fontSize: '12px' }}
                                    />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Sorting and Filtering Controls */}
            <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-end">
                <div className="space-y-2">
                    <Label htmlFor="sort-select" className="text-sm flex items-center gap-1">
                        <ArrowUpDown className="h-3 w-3" />
                        Sort by
                    </Label>
                    <Select value={sortBy} onValueChange={(v) => setSortBy(v as SortOption)}>
                        <SelectTrigger id="sort-select" className="w-[180px]">
                            <SelectValue placeholder="Sort by..." />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="frequency">Frequency</SelectItem>
                            <SelectItem value="duration">Duration</SelectItem>
                            <SelectItem value="activityCount">Activity Count</SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                <div className="space-y-2 flex-1 max-w-xs">
                    <Label className="text-sm">
                        Minimum case count: <strong>{minCaseCount}</strong>
                    </Label>
                    <Slider
                        value={[minCaseCount]}
                        onValueChange={([value]) => setMinCaseCount(value)}
                        max={maxCaseCount}
                        min={0}
                        step={1}
                        className="w-full"
                    />
                </div>

                <div className="text-sm text-muted-foreground">
                    Showing {filteredVariants.length} of {variants.length} variants
                </div>
            </div>

            {/* Variants List */}
            <ScrollArea className="h-[500px]">
                <div className="space-y-3 pr-4">
                    {filteredVariants.map((variant) => {
                        const rank = getRank(variant);
                        const isHappyPath = variant.isHappyPath;

                        return (
                            <Card
                                key={variant.id}
                                className={
                                    isHappyPath
                                        ? 'border-green-500/50 bg-gradient-to-r from-green-500/5 to-transparent'
                                        : ''
                                }
                            >
                                <CardContent className="pt-4">
                                    <div className="flex items-start justify-between gap-4">
                                        {/* Left: Rank and Info */}
                                        <div className="flex items-start gap-3 flex-1">
                                            {/* Rank Badge */}
                                            <div
                                                className={`shrink-0 flex items-center justify-center w-8 h-8 rounded-full font-bold text-sm ${isHappyPath
                                                    ? 'bg-green-500/20 text-green-700'
                                                    : 'bg-muted text-muted-foreground'
                                                    }`}
                                            >
                                                #{rank}
                                            </div>

                                            <div className="flex-1 space-y-2">
                                                {/* Title Row */}
                                                <div className="flex items-center gap-2 flex-wrap">
                                                    {isHappyPath && (
                                                        <Badge
                                                            variant="secondary"
                                                            className="bg-green-500/20 text-green-700 gap-1"
                                                        >
                                                            <Star className="h-3 w-3" />
                                                            Happy Path
                                                        </Badge>
                                                    )}
                                                    <span className="text-xs text-muted-foreground">
                                                        {variant.sequence.length} activities
                                                    </span>
                                                </div>

                                                {/* Activity Sequence */}
                                                <ActivitySequence
                                                    sequence={variant.sequence}
                                                    compact
                                                />

                                                {/* Stats Row */}
                                                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                                                    <span>
                                                        <strong className="text-foreground">
                                                            {variant.caseCount}
                                                        </strong>{' '}
                                                        cases
                                                    </span>
                                                    <span>({variant.percentage.toFixed(1)}%)</span>
                                                    <span>
                                                        Avg: {formatDuration(variant.avgDuration)}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>

                                        {/* Right: View Cases Button */}
                                        <Button
                                            variant="outline"
                                            size="sm"
                                            onClick={() => handleViewCases(variant)}
                                            className="shrink-0 gap-1"
                                        >
                                            <Eye className="h-3 w-3" />
                                            View Cases
                                        </Button>
                                    </div>
                                </CardContent>
                            </Card>
                        );
                    })}

                    {filteredVariants.length === 0 && (
                        <div className="flex flex-col items-center justify-center py-12 text-center">
                            <p className="text-muted-foreground">
                                No variants match the current filter.
                            </p>
                            <Button
                                variant="link"
                                size="sm"
                                onClick={() => setMinCaseCount(0)}
                            >
                                Reset filter
                            </Button>
                        </div>
                    )}
                </div>
            </ScrollArea>

            {/* Cases Dialog */}
            <VariantCasesDialog
                variant={selectedVariant}
                open={dialogOpen}
                onOpenChange={setDialogOpen}
            />
        </div>
    );
}
