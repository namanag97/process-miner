'use client';

import { Header } from '@/components/layout/Header';
import { useBackendUpload, useToast } from '@/hooks';
import { useAppStore } from '@/lib/stores/useAppStore';
import {
    FileDropzone,
    DataPreview,
    HelpCard,
} from '@/components/features/upload';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FileText, Loader2, Upload } from 'lucide-react';
import { formatFileSize } from '@/lib/utils';

/**
 * Upload page - Backend processing with PM4Py.
 */
export default function UploadPage() {
    const { toast } = useToast();
    const { parsedData: storeParsedData } = useAppStore();

    const {
        selectedFile,
        isUploading,
        uploadResponse,
        handleFileSelected,
        handleUpload,
        handleRemove,
        handleReset,
        handleContinue,
    } = useBackendUpload({
        onUploadError: (error) => {
            toast({
                title: 'Upload Error',
                description: error,
                variant: 'destructive',
            });
        },
    });

    const parsedData = uploadResponse ? storeParsedData : null;

    return (
        <div className="flex flex-col">
            <Header title="Upload Data" />

            <div className="flex-1 p-4 md:p-6">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Main content area */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Upload zone */}
                        {!selectedFile && !parsedData && (
                            <div className="flex justify-center">
                                <FileDropzone
                                    className="w-full max-w-[60%]"
                                    onFileSelected={handleFileSelected}
                                />
                            </div>
                        )}

                        {/* File preview */}
                        {selectedFile && !parsedData && (
                            <Card className="w-full">
                                <CardContent className="flex items-center gap-4 p-6">
                                    <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                                        <FileText className="h-6 w-6 text-primary" />
                                    </div>

                                    <div className="flex-1 min-w-0">
                                        <p className="font-medium truncate">{selectedFile.name}</p>
                                        <p className="text-sm text-muted-foreground">
                                            {formatFileSize(selectedFile.size)}
                                        </p>
                                    </div>

                                    <div className="flex gap-2 shrink-0">
                                        <Button
                                            variant="ghost"
                                            onClick={handleRemove}
                                            disabled={isUploading}
                                        >
                                            Remove
                                        </Button>
                                        <Button onClick={handleUpload} disabled={isUploading}>
                                            {isUploading ? (
                                                <>
                                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                    Uploading...
                                                </>
                                            ) : (
                                                <>
                                                    <Upload className="mr-2 h-4 w-4" />
                                                    Upload & Analyze
                                                </>
                                            )}
                                        </Button>
                                    </div>
                                </CardContent>
                            </Card>
                        )}

                        {/* Data preview */}
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
                    </div>
                </div>
            </div>
        </div>
    );
}
