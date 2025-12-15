'use client';

import { useCallback } from 'react';
import { useDropzone, type FileRejection } from 'react-dropzone';
import { UploadCloud } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { useAppStore } from '@/lib/stores';
import { formatFileSize } from '@/lib/parsers';

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

interface FileDropzoneProps {
    className?: string;
}

export function FileDropzone({ className }: FileDropzoneProps) {
    const { setFile, addLog } = useAppStore();

    const onDrop = useCallback(
        (acceptedFiles: File[]) => {
            if (acceptedFiles.length > 0) {
                const file = acceptedFiles[0];
                setFile(file);
                addLog(`📁 File selected: ${file.name} (${formatFileSize(file.size)})`, 'info');
            }
        },
        [setFile, addLog]
    );

    const onDropRejected = useCallback(
        (fileRejections: FileRejection[]) => {
            const rejection = fileRejections[0];
            if (!rejection) return;

            const error = rejection.errors[0];
            if (error?.code === 'file-invalid-type') {
                addLog('❌ Invalid file format. Please upload CSV or XES file', 'error');
            } else if (error?.code === 'file-too-large') {
                addLog('❌ File too large. Maximum size is 50MB', 'error');
            } else {
                addLog(`❌ ${error?.message || 'Unknown error'}`, 'error');
            }
        },
        [addLog]
    );

    const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
        onDrop,
        onDropRejected,
        accept: {
            'text/csv': ['.csv'],
            'application/xml': ['.xes'],
            'text/xml': ['.xes'],
        },
        maxSize: MAX_FILE_SIZE,
        multiple: false,
    });

    return (
        <div className={cn('w-full', className)}>
            <div
                {...getRootProps()}
                className={cn(
                    'relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-12 transition-all cursor-pointer',
                    'hover:border-primary/50 hover:bg-primary/5',
                    isDragActive && !isDragReject && 'border-blue-500 bg-blue-50 dark:bg-blue-950/30',
                    isDragReject && 'border-red-500 bg-red-50 dark:bg-red-950/30',
                    !isDragActive && !isDragReject && 'border-slate-300 dark:border-slate-700'
                )}
            >
                <input {...getInputProps()} />

                <div
                    className={cn(
                        'flex h-16 w-16 items-center justify-center rounded-full mb-4',
                        isDragActive && !isDragReject && 'bg-blue-100 dark:bg-blue-900/50',
                        isDragReject && 'bg-red-100 dark:bg-red-900/50',
                        !isDragActive && 'bg-slate-100 dark:bg-slate-800'
                    )}
                >
                    <UploadCloud
                        className={cn(
                            'h-8 w-8',
                            isDragActive && !isDragReject && 'text-blue-600 dark:text-blue-400',
                            isDragReject && 'text-red-600 dark:text-red-400',
                            !isDragActive && 'text-slate-500 dark:text-slate-400'
                        )}
                    />
                </div>

                <h3 className="text-lg font-semibold mb-1">Upload Event Log</h3>
                <p className="text-muted-foreground mb-2">
                    {isDragActive && !isDragReject
                        ? 'Drop your file here...'
                        : isDragReject
                            ? 'Invalid file type'
                            : 'Drag & drop your event log file here'}
                </p>
                <p className="text-sm text-muted-foreground/70">
                    Supports CSV and XES formats • Max 50MB
                </p>

                <Button variant="outline" className="mt-6" type="button">
                    Browse Files
                </Button>
            </div>
        </div>
    );
}
