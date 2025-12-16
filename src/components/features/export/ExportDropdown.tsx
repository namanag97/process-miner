'use client';

import { Download, FileJson, FileSpreadsheet, BarChart3 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { toast } from 'sonner';
import type { ProcessModel } from '@/lib/mining/types';
import {
    exportProcessModel,
    exportVariants,
    exportDeviations,
    exportStatistics,
    type CaseExportData,
    exportCases,
} from '@/lib/export/exportUtils';

interface ExportDropdownProps {
    model: ProcessModel;
    cases?: CaseExportData[];
    className?: string;
}

export function ExportDropdown({ model, cases, className }: ExportDropdownProps) {
    const handleExportProcessModel = () => {
        try {
            exportProcessModel(model);
            toast.success('Process model exported successfully');
        } catch (error) {
            toast.error('Failed to export process model');
        }
    };

    const handleExportVariants = () => {
        try {
            exportVariants(model.variants);
            toast.success('Variants exported successfully');
        } catch (error) {
            toast.error('Failed to export variants');
        }
    };

    const handleExportDeviations = () => {
        try {
            exportDeviations(model.deviations);
            toast.success('Deviations exported successfully');
        } catch (error) {
            toast.error('Failed to export deviations');
        }
    };

    const handleExportCases = () => {
        if (!cases || cases.length === 0) {
            toast.error('No case data available for export');
            return;
        }
        try {
            exportCases(cases);
            toast.success('Cases exported successfully');
        } catch (error) {
            toast.error('Failed to export cases');
        }
    };

    const handleExportStatistics = () => {
        try {
            exportStatistics(model);
            toast.success('Statistics exported successfully');
        } catch (error) {
            toast.error('Failed to export statistics');
        }
    };

    return (
        <DropdownMenu>
            <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className={className}>
                    <Download className="h-4 w-4 mr-2" />
                    Export
                </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel>Export Options</DropdownMenuLabel>
                <DropdownMenuSeparator />

                <DropdownMenuItem onClick={handleExportProcessModel}>
                    <FileJson className="h-4 w-4 mr-2" />
                    Process Model (JSON)
                </DropdownMenuItem>

                <DropdownMenuItem onClick={handleExportVariants}>
                    <FileSpreadsheet className="h-4 w-4 mr-2" />
                    Variants (CSV)
                </DropdownMenuItem>

                <DropdownMenuItem onClick={handleExportDeviations}>
                    <FileSpreadsheet className="h-4 w-4 mr-2" />
                    Deviations (CSV)
                </DropdownMenuItem>

                {cases && cases.length > 0 && (
                    <DropdownMenuItem onClick={handleExportCases}>
                        <FileSpreadsheet className="h-4 w-4 mr-2" />
                        All Cases (CSV)
                    </DropdownMenuItem>
                )}

                <DropdownMenuSeparator />

                <DropdownMenuItem onClick={handleExportStatistics}>
                    <BarChart3 className="h-4 w-4 mr-2" />
                    Statistics (JSON)
                </DropdownMenuItem>
            </DropdownMenuContent>
        </DropdownMenu>
    );
}
