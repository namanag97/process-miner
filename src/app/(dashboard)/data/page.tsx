'use client';

import { Search, Upload, Filter, Database } from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import { EmptyState } from '@/components/shared/EmptyState';

export default function DataPage() {
    return (
        <div className="flex flex-col">
            <Header title="Data Models" />

            <div className="flex-1 space-y-6 p-4 md:p-6">
                {/* Page header with actions */}
                <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                        <p className="text-muted-foreground">
                            Manage your event log files and data models
                        </p>
                    </div>
                    <Button className="gap-2">
                        <Upload className="h-4 w-4" />
                        Upload Data
                    </Button>
                </div>

                {/* Filter bar */}
                <div className="flex flex-col gap-4 sm:flex-row">
                    <div className="relative flex-1">
                        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                        <Input
                            placeholder="Search data models..."
                            className="pl-9"
                        />
                    </div>
                    <Select defaultValue="all">
                        <SelectTrigger className="w-full sm:w-40">
                            <Filter className="mr-2 h-4 w-4" />
                            <SelectValue placeholder="Status" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">All</SelectItem>
                            <SelectItem value="processing">Processing</SelectItem>
                            <SelectItem value="ready">Ready</SelectItem>
                            <SelectItem value="failed">Failed</SelectItem>
                        </SelectContent>
                    </Select>
                </div>

                {/* Empty state */}
                <div className="flex-1 flex items-center justify-center min-h-[400px]">
                    <EmptyState
                        icon={Database}
                        title="No data models yet"
                        description="Upload your first event log file to create a data model and start analyzing your processes."
                        action={{
                            label: 'Upload Data',
                            href: '#upload',
                        }}
                    />
                </div>
            </div>
        </div>
    );
}
