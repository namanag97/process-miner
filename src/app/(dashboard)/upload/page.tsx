'use client';

import { Header } from '@/components/layout/Header';
import { useBackendUpload, useFileUpload, useToast } from '@/hooks';
import { useAppStore } from '@/lib/stores/useAppStore';
import {
    FileDropzone,
    FilePreviewCard,
    DataPreview,
    HelpCard,
} from '@/components/features/upload';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FileText, Loader2, Upload, Wifi, WifiOff } from 'lucide-react';
import { formatFileSize } from '@/lib/utils';

/**
 * Upload page that supports both backend and client-side processing.
 * 
 * Backend mode (default): Uploads file to FastAPI server for PM4Py processing
 * Client mode (fallback): Parses file locally in browser
 */
export default function UploadPage() {
    const { toast } = useToast();
    const { useBackend, setUseBackend, parsedData: storeParsedData } = useAppStore();

    // Backend upload hook
    const {
        selectedFile: backendFile,
        isUploading,
        uploadResponse,
        handleFileSelected: handleBackendFileSelected,
        handleUpload,
        handleRemove: handleBackendRemove,
        handleReset: handleBackendReset,
        handleContinue: handleBackendContinue,
    } = useBackendUpload({
        onUploadError: (error) => {
            toast({
                title: 'Upload Error',
                description: error,
                variant: 'destructive',
            });
        },
    });

    // Client-side upload hook (fallback)
    const {
        selectedFile: clientFile,
        parsedData: clientParsedData,
        isParsing,
        handleFileSelected: handleClientFileSelected,
        handleParse,
        handleRemove: handleClientRemove,
        handleReset: handleClientReset,
        handleContinue: handleClientContinue,
    } = useFileUpload({
        onParseError: (error) => {
            toast({
                title: 'Parse Error',
                description: error,
                variant: 'destructive',
            });
        },
    });

    // Use appropriate hook based on mode
    const selectedFile = useBackend ? backendFile : clientFile;
    const parsedData = useBackend ? (uploadResponse ? storeParsedData : null) : clientParsedData;
    const isProcessing = useBackend ? isUploading : isParsing;
    const handleFileSelected = useBackend ? handleBackendFileSelected : handleClientFileSelected;
    const handleProcess = useBackend ? handleUpload : handleParse;
    const handleRemove = useBackend ? handleBackendRemove : handleClientRemove;
    const handleReset = useBackend ? handleBackendReset : handleClientReset;
    const handleContinue = useBackend ? handleBackendContinue : handleClientContinue;
    const processButtonText = useBackend ? 'Upload & Analyze' : 'Parse File';
    const processingText = useBackend ? 'Uploading...' : 'Parsing...';

    return (
        <div className="flex flex-col">
            <Header title="Upload Data" />

            <div className="flex-1 p-4 md:p-6">
                {/* Mode toggle */}
                <div className="flex justify-end mb-4">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setUseBackend(!useBackend)}
                        className="gap-2"
                    >
                        {useBackend ? (
                            <>
                                <Wifi className="h-4 w-4 text-green-500" />
                                <span>Backend Mode</span>
                            </>
                        ) : (
                            <>
                                <WifiOff className="h-4 w-4 text-orange-500" />
                                <span>Offline Mode</span>
                            </>
                        )}
                    </Button>
                </div>

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

                        {/* File preview - custom for backend mode */}
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
                                            {useBackend && (
                                                <span className="ml-2 text-green-600">• Backend processing</span>
                                            )}
                                        </p>
                                    </div>

                                    <div className="flex gap-2 shrink-0">
                                        <Button
                                            variant="ghost"
                                            onClick={handleRemove}
                                            disabled={isProcessing}
                                        >
                                            Remove
                                        </Button>
                                        <Button onClick={handleProcess} disabled={isProcessing}>
                                            {isProcessing ? (
                                                <>
                                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                                    {processingText}
                                                </>
                                            ) : (
                                                <>
                                                    {useBackend && <Upload className="mr-2 h-4 w-4" />}
                                                    {processButtonText}
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

                        {/* Backend status */}
                        {useBackend && (
                            <Card>
                                <CardContent className="p-4">
                                    <h3 className="font-semibold mb-2 flex items-center gap-2">
                                        <Wifi className="h-4 w-4 text-green-500" />
                                        Backend Mode
                                    </h3>
                                    <p className="text-sm text-muted-foreground">
                                        Files are uploaded to the server for processing with PM4Py.
                                        This enables advanced process mining algorithms and handles
                                        larger files.
                                    </p>
                                </CardContent>
                            </Card>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
