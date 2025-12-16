'use client';

import { useState } from 'react';
import { Copy, Check, ExternalLink } from 'lucide-react';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { ActivitySequence } from './ActivitySequence';
import type { ProcessVariant } from '@/lib/mining/types';

interface VariantCasesDialogProps {
    variant: ProcessVariant | null;
    open: boolean;
    onOpenChange: (open: boolean) => void;
}

/**
 * Dialog showing case IDs for a specific variant
 */
export function VariantCasesDialog({ variant, open, onOpenChange }: VariantCasesDialogProps) {
    const [copied, setCopied] = useState(false);

    const handleCopyAll = async () => {
        if (!variant) return;

        const caseIdText = variant.caseIds.join('\n');
        await navigator.clipboard.writeText(caseIdText);

        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    if (!variant) return null;

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-lg">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                        Cases for Variant
                        {variant.isHappyPath && (
                            <Badge variant="secondary" className="bg-green-500/20 text-green-700">
                                Happy Path
                            </Badge>
                        )}
                    </DialogTitle>
                    <DialogDescription className="pt-2">
                        <ActivitySequence sequence={variant.sequence} compact />
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-4">
                    {/* Stats */}
                    <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">
                            {variant.caseIds.length} case{variant.caseIds.length !== 1 ? 's' : ''}
                        </span>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={handleCopyAll}
                            className="gap-2"
                        >
                            {copied ? (
                                <>
                                    <Check className="h-4 w-4 text-green-600" />
                                    Copied!
                                </>
                            ) : (
                                <>
                                    <Copy className="h-4 w-4" />
                                    Copy All
                                </>
                            )}
                        </Button>
                    </div>

                    {/* Case ID List */}
                    <ScrollArea className="h-[250px] rounded-md border">
                        <div className="p-4 space-y-2">
                            {variant.caseIds.map((caseId) => (
                                <div
                                    key={caseId}
                                    className="flex items-center justify-between rounded-md bg-muted px-3 py-2"
                                >
                                    <code className="text-sm">{caseId}</code>
                                    <Button
                                        variant="ghost"
                                        size="icon"
                                        className="h-6 w-6"
                                        disabled
                                        title="View case details (coming soon)"
                                    >
                                        <ExternalLink className="h-3 w-3" />
                                    </Button>
                                </div>
                            ))}
                        </div>
                    </ScrollArea>

                    <p className="text-xs text-muted-foreground text-center">
                        Case detail view coming soon
                    </p>
                </div>
            </DialogContent>
        </Dialog>
    );
}
