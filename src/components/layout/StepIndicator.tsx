'use client';

import { usePathname } from 'next/navigation';
import { Check } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAppStore } from '@/lib/stores/useAppStore';

const steps = [
    { number: 1, label: 'Upload', route: '/upload' },
    { number: 2, label: 'Configure', route: '/configure' },
    { number: 3, label: 'Analyze', route: '/process-map' },
    { number: 4, label: 'Visualize', route: '/insights' },
];

export function StepIndicator() {
    const pathname = usePathname();
    const _currentStep = useAppStore((state) => state.currentStep);

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
                    {steps.map((step, index) => (
                        <div key={step.number} className="flex flex-1 items-center">
                            {/* Step Circle */}
                            <div className="flex items-center">
                                <div
                                    className={cn(
                                        'flex h-8 w-8 items-center justify-center rounded-full border-2 text-sm font-semibold transition-colors',
                                        step.number < activeStep
                                            ? 'border-primary bg-primary text-primary-foreground'
                                            : step.number === activeStep
                                                ? 'border-primary bg-primary text-primary-foreground'
                                                : 'border-muted-foreground/30 bg-background text-muted-foreground'
                                    )}
                                >
                                    {step.number < activeStep ? (
                                        <Check className="h-4 w-4" />
                                    ) : (
                                        step.number
                                    )}
                                </div>
                                <div className="ml-2">
                                    <div
                                        className={cn(
                                            'text-sm font-medium',
                                            step.number <= activeStep
                                                ? 'text-foreground'
                                                : 'text-muted-foreground'
                                        )}
                                    >
                                        {step.label}
                                    </div>
                                </div>
                            </div>

                            {/* Connector Line */}
                            {index < steps.length - 1 && (
                                <div
                                    className={cn(
                                        'mx-4 h-0.5 flex-1 transition-colors',
                                        step.number < activeStep
                                            ? 'bg-primary'
                                            : 'bg-muted-foreground/30'
                                    )}
                                />
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
