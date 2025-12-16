'use client';

import { FileSpreadsheet, Columns, HardDrive } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import { formatFileSize } from '@/lib/utils';
import type { ParsedData } from '@/lib/stores/useAppStore';

interface DataPreviewProps {
    data: ParsedData;
    fileSize: number;
    onContinue: () => void;
    onReset: () => void;
}

export function DataPreview({
    data,
    fileSize,
    onContinue,
    onReset,
}: DataPreviewProps) {
    const previewRows = data.rows.slice(0, 5);

    const stats = [
        {
            label: 'Total Rows',
            value: data.rowCount.toLocaleString(),
            icon: FileSpreadsheet,
        },
        {
            label: 'Total Columns',
            value: data.headers.length.toString(),
            icon: Columns,
        },
        {
            label: 'File Size',
            value: formatFileSize(fileSize),
            icon: HardDrive,
        },
    ];

    return (
        <div className="space-y-6">
            {/* Stats cards */}
            <div className="grid grid-cols-3 gap-4">
                {stats.map((stat) => (
                    <Card key={stat.label}>
                        <CardContent className="flex items-center gap-3 p-4">
                            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                                <stat.icon className="h-5 w-5 text-primary" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold">{stat.value}</p>
                                <p className="text-xs text-muted-foreground">{stat.label}</p>
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </div>

            {/* Preview table */}
            <Card>
                <CardHeader>
                    <CardTitle className="text-base">Data Preview</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="overflow-x-auto -mx-6 px-6">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    {data.headers.map((header) => (
                                        <TableHead
                                            key={header}
                                            className="whitespace-nowrap font-medium"
                                        >
                                            {header}
                                        </TableHead>
                                    ))}
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {previewRows.map((row, index) => (
                                    <TableRow key={index}>
                                        {data.headers.map((header) => (
                                            <TableCell
                                                key={header}
                                                className="whitespace-nowrap"
                                            >
                                                {(row as Record<string, unknown>)[header] !== undefined
                                                    ? String((row as Record<string, unknown>)[header])
                                                    : '-'}
                                            </TableCell>
                                        ))}
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </div>
                    {data.rowCount > 5 && (
                        <p className="mt-4 text-sm text-muted-foreground text-center">
                            Showing 5 of {data.rowCount.toLocaleString()} rows
                        </p>
                    )}
                </CardContent>
            </Card>

            {/* Action buttons */}
            <div className="flex gap-4 justify-end">
                <Button variant="outline" onClick={onReset}>
                    Upload Different File
                </Button>
                <Button onClick={onContinue}>Continue to Configuration →</Button>
            </div>
        </div>
    );
}
