'use client';

import { FileText, Loader2 } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { formatFileSize } from '@/lib/utils';

interface FilePreviewCardProps {
    file: File;
    isParsing: boolean;
    onParse: () => void;
    onRemove: () => void;
}

export function FilePreviewCard({
    file,
    isParsing,
    onParse,
    onRemove,
}: FilePreviewCardProps) {
    return (
        <Card className="w-full">
            <CardContent className="flex items-center gap-4 p-6">
                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                    <FileText className="h-6 w-6 text-primary" />
                </div>

                <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{file.name}</p>
                    <p className="text-sm text-muted-foreground">
                        {formatFileSize(file.size)}
                    </p>
                </div>

                <div className="flex gap-2 shrink-0">
                    <Button
                        variant="ghost"
                        onClick={onRemove}
                        disabled={isParsing}
                    >
                        Remove
                    </Button>
                    <Button onClick={onParse} disabled={isParsing}>
                        {isParsing ? (
                            <>
                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                Parsing...
                            </>
                        ) : (
                            'Parse File'
                        )}
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
}
