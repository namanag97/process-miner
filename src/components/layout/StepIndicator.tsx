'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAppStore } from '@/lib/stores/useAppStore';
import { getRouteAccessibility, getCompletedSteps } from '@/hooks/useNavigationGuard';

const steps = [
    { number: 1, label: 'Upload', route: '/upload', key: 'upload' },
    { number: 2, label: 'Configure', route: '/configure', key: 'configure' },
    { number: 3, label: 'Analyze', route: '/process-map', key: 'process-map' },
    { number: 4, label: 'Visualize', route: '/insights', key: 'insights' },
];

export function StepIndicator() {
    const pathname = usePathname();
    const { parsedData, columnConfig, miningResults } = useAppStore();

    const accessibility = getRouteAccessibility({ parsedData, columnConfig, miningResults });
    const completed = getCompletedSteps({ parsedData, columnConfig, miningResults });

    // Determine active step based on pathname
    const getActiveStep = () => {
        if (pathname.includes('/upload')) return 1;
        if (pathname.includes('/configure')) return 2;
        if (pathname.includes('/process-map')) return 3;
        if (pathname.includes('/insights')) return 4;
        return 1;
    };

    const activeStep = getActiveStep();

    return (
        <div className="border-b bg-card">
            <div className="mx-auto max-w-4xl px-6 py-4">
                <div className="flex items-center justify-between">
                    {steps.map((step, index) => {
                        const isActive = step.number === activeStep;
                        const isCompleted = completed[step.key as keyof typeof completed];
                        const isAccessible = accessibility[step.route as keyof typeof accessibility];

                        const stepCircle = (
                            <div
                                className={cn(
                                    'flex h-8 w-8 items-center justify-center rounded-full border-2 text-sm font-semibold transition-colors',
                                    isCompleted
                                        ? 'border-green-500 bg-green-500 text-white'
                                        : isActive
                                            ? 'border-primary bg-primary text-primary-foreground'
                                            : 'border-muted-foreground/30 bg-background text-muted-foreground'
                                )}
                            >
                                {isCompleted ? (
                                    <Check className="h-4 w-4" />
                                ) : (
                                    step.number
                                )}
                            </div>
                        );

                        const content = (
                            <div className="flex items-center">
                                {stepCircle}
                                <div className="ml-2">
                                    <div
                                        className={cn(
                                            'text-sm font-medium',
                                            isActive || isCompleted
                                                ? 'text-foreground'
                                                : 'text-muted-foreground'
                                        )}
                                    >
                                        {step.label}
                                    </div>
                                </div>
                            </div>
                        );

                        return (
                            <div key={step.number} className="flex flex-1 items-center">
                                {isAccessible && !isActive ? (
                                    <Link
                                        href={step.route}
                                        className="hover:opacity-80 transition-opacity"
                                    >
                                        {content}
                                    </Link>
                                ) : (
                                    content
                                )}

                                {/* Connector Line */}
                                {index < steps.length - 1 && (
                                    <div
                                        className={cn(
                                            'mx-4 h-0.5 flex-1 transition-colors',
                                            isCompleted
                                                ? 'bg-green-500'
                                                : step.number < activeStep
                                                    ? 'bg-primary'
                                                    : 'bg-muted-foreground/30'
                                        )}
                                    />
                                )}
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
