'use client';

import { useRouter } from 'next/navigation';
import { Header } from '@/components/layout/Header';
import { NavigationGuard } from '@/components/navigation';
import { InDevState } from '@/components/states';

export default function ProcessMapPage() {
    const router = useRouter();

    return (
        <NavigationGuard>
            <div className="flex flex-col h-full">
                <Header title="Process Map" />

                <div className="flex-1 flex items-center justify-center p-6">
                    <InDevState
                        featureName="Process Map Visualization"
                        description="We're building an interactive process flow visualization with bottleneck detection and variant analysis."
                        onBack={() => router.push('/configure')}
                    />
                </div>
            </div>
        </NavigationGuard>
    );
}
