'use client';

import { Header } from '@/components/layout/Header';
import { useFileUpload, useToast } from '@/hooks';
import {
    FileDropzone,
    FilePreviewCard,
    DataPreview,
    HelpCard,
} from '@/components/features/upload';

export default function UploadPage() {
    const { toast } = useToast();

    const {
        selectedFile,
        parsedData,
        isParsing,
        handleFileSelected,
        handleParse,
        handleRemove,
        handleReset,
        handleContinue,
    } = useFileUpload({
        onParseError: (error) => {
            toast({
                title: 'Parse Error',
                description: error,
                variant: 'destructive',
            });
        },
    });

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
                            <FilePreviewCard
                                file={selectedFile}
                                isParsing={isParsing}
                                onParse={handleParse}
                                onRemove={handleRemove}
                            />
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
