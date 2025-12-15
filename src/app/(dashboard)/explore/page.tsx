'use client';

import { GitBranch } from 'lucide-react';
import { Header } from '@/components/layout/Header';
import { EmptyState } from '@/components/shared/EmptyState';

export default function ExplorePage() {
    return (
        <div className="flex flex-col">
            <Header title="Process Explorer" />

            <div className="flex-1 flex items-center justify-center p-4 md:p-6 min-h-[calc(100vh-4rem)]">
                <EmptyState
                    icon={GitBranch}
                    title="No process to explore"
                    description="Upload a data file first, then come back to explore the process map and discover insights."
                    action={{
                        label: 'Go to Data',
                        href: '/data',
                    }}
                />
            </div>
        </div>
    );
}
