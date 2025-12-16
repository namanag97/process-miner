'use client';

import { useRouter } from 'next/navigation';
import { Header } from '@/components/layout/Header';
import { NavigationGuard } from '@/components/navigation';
import { InDevState } from '@/components/states';

export default function InsightsPage() {
    const router = useRouter();

    return (
        <NavigationGuard>
            <div className="flex flex-col h-full">
                <Header title="Insights" />

                <div className="flex-1 flex items-center justify-center p-6">
                    <InDevState
                        featureName="Process Insights Dashboard"
                        description="We're building comprehensive analytics with metrics, variants, and bottleneck analysis."
                        onBack={() => router.push('/process-map')}
                    />
                </div>
            </div>
        </NavigationGuard>
    );
}
