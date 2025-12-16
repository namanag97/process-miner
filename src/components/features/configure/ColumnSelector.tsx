'use client';

import { useMemo } from 'react';
import { LucideIcon } from 'lucide-react';
import { Label } from '@/components/ui/label';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { getColumnSamples } from '@/lib/validation';

interface ColumnSelectorProps {
    icon: LucideIcon;
    label: string;
    description: string;
    helperText: string;
    columns: string[];
    selectedColumn: string | null;
    onSelect: (column: string | null) => void;
    rows: Record<string, unknown>[];
    required?: boolean;
    error?: string;
    disabled?: boolean;
}

export function ColumnSelector({
    icon: Icon,
    label,
    description,
    helperText,
    columns,
    selectedColumn,
    onSelect,
    rows,
    required = false,
    error,
    disabled = false,
}: ColumnSelectorProps) {
    const samples = useMemo(() => {
        if (!selectedColumn) return [];
        return getColumnSamples(rows, selectedColumn, 3);
    }, [rows, selectedColumn]);

    return (
        <div className="space-y-2">
            <div className="flex items-center gap-2">
                <Icon className="h-4 w-4 text-primary" />
                <Label className="font-medium">
                    {label}
                    {required && <span className="text-destructive ml-1">*</span>}
                </Label>
            </div>
            <p className="text-sm text-muted-foreground">{description}</p>

            <Select
                value={selectedColumn || ''}
                onValueChange={(value) => onSelect(value === '__none__' ? null : value)}
                disabled={disabled}
            >
                <SelectTrigger className={error ? 'border-destructive' : ''}>
                    <SelectValue placeholder="Select a column..." />
                </SelectTrigger>
                <SelectContent>
                    {!required && (
                        <SelectItem value="__none__">None</SelectItem>
                    )}
                    {columns.map((col) => (
                        <SelectItem key={col} value={col}>
                            {col}
                        </SelectItem>
                    ))}
                </SelectContent>
            </Select>

            {error && (
                <p className="text-sm text-destructive">{error}</p>
            )}

            {selectedColumn && samples.length > 0 && (
                <div className="flex flex-wrap gap-1.5 pt-1">
                    <span className="text-xs text-muted-foreground">Sample values:</span>
                    {samples.map((sample, i) => (
                        <Badge key={i} variant="secondary" className="font-mono text-xs">
                            {sample}
                        </Badge>
                    ))}
                </div>
            )}

            <p className="text-xs text-muted-foreground/70">{helperText}</p>
        </div>
    );
}
