'use client';

import { Header } from '@/components/layout/Header';
import { NavigationGuard } from '@/components/navigation';
import { ProcessMapPage } from '@/components/features/process-map';
import { useAppStore } from '@/lib/stores/useAppStore';

export default function ProcessMapRoute() {
    const { uploadedFile } = useAppStore();

    return (
        <NavigationGuard>
            <div className="flex flex-col h-full">
                <Header
                    title="Process Analysis"
                    showBackButton
                    backHref="/configure"
                    backLabel="Back to Configure"
                />

                {/* Subtitle with file name */}
                {uploadedFile && (
                    <div className="px-4 md:px-6 pb-2">
                        <p className="text-sm text-muted-foreground">
                            Analyzing: <span className="font-medium">{uploadedFile.name}</span>
                        </p>
                    </div>
                )}

                <ProcessMapPage />
            </div>
        </NavigationGuard>
    );
}
