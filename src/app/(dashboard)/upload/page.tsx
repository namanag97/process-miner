'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Header } from '@/components/layout/Header';
import { LogPanel } from '@/components/shared';
import { useAppStore } from '@/lib/stores/useAppStore';
import { useLogStore } from '@/lib/stores/useLogStore';
import { parseCSV, parseXES } from '@/lib/parsers';
import {
    FileDropzone,
    FilePreviewCard,
    DataPreview,
    HelpCard,
} from '@/components/features/upload';
import { useToast } from '@/hooks/use-toast';

export default function UploadPage() {
    const router = useRouter();
    const { toast } = useToast();
    const addLog = useLogStore((state) => state.addLog);
    const clearLogs = useLogStore((state) => state.clearLogs);
    const { parsedData, setParsedData, setCurrentStep } = useAppStore();

    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [isParsing, setIsParsing] = useState(false);

    const handleFileSelected = useCallback((file: File) => {
        setSelectedFile(file);
    }, []);

    const handleParse = useCallback(async () => {
        if (!selectedFile) return;

        setIsParsing(true);

        const isXES = selectedFile.name.toLowerCase().endsWith('.xes');
        const logCallback = (message: string, type?: 'info' | 'success' | 'error' | 'warning') => {
            addLog(type || 'info', message);
        };

        try {
            let result;

            if (isXES) {
                result = await parseXES(selectedFile, {
                    onLog: logCallback,
                    onProgress: (_current, _total) => {
                        // Progress is logged inside the parser
                    },
                });
            } else {
                result = await parseCSV(selectedFile, {
                    onLog: logCallback,
                    onProgress: (_percent) => {
                        // Progress is logged inside the parser
                    },
                });
            }

            if (result.success && result.data) {
                setParsedData({
                    headers: result.data.headers,
                    rows: result.data.rows as object[],
                    rowCount: result.data.rowCount,
                });
                setCurrentStep(2);
            } else {
                toast({
                    title: 'Parse Error',
                    description: result.error || 'Failed to parse file',
                    variant: 'destructive',
                });
            }
        } catch (error) {
            const message = error instanceof Error ? error.message : 'Unknown error';
            addLog('error', `❌ Parse error: ${message}`);
            toast({
                title: 'Parse Error',
                description: message,
                variant: 'destructive',
            });
        } finally {
            setIsParsing(false);
        }
    }, [selectedFile, addLog, setParsedData, setCurrentStep, toast]);

    const handleRemove = useCallback(() => {
        setSelectedFile(null);
        setParsedData(null);
        clearLogs();
    }, [setParsedData, clearLogs]);

    const handleContinue = useCallback(() => {
        router.push('/configure');
    }, [router]);

    const handleReset = useCallback(() => {
        setSelectedFile(null);
        setParsedData(null);
        clearLogs();
    }, [setParsedData, clearLogs]);

    return (
        <div className="flex flex-col">
            <Header title="Upload Data" />

            <div className="flex-1 p-4 md:p-6">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Main content area */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Upload zone or preview */}
                        {!selectedFile && !parsedData && (
                            <div className="flex justify-center">
                                <FileDropzone
                                    className="w-full max-w-[60%]"
                                    onFileSelected={handleFileSelected}
                                />
                            </div>
                        )}

                        {selectedFile && !parsedData && (
                            <FilePreviewCard
                                file={selectedFile}
                                isParsing={isParsing}
                                onParse={handleParse}
                                onRemove={handleRemove}
                            />
                        )}

                        {parsedData && selectedFile && (
                            <DataPreview
                                data={parsedData}
                                fileSize={selectedFile.size}
                                onContinue={handleContinue}
                                onReset={handleReset}
                            />
                        )}
                    </div>

                    {/* Sidebar */}
                    <div className="space-y-6">
                        <HelpCard />
                        <LogPanel maxHeight="350px" />
                    </div>
                </div>
            </div>
        </div>
    );
}
