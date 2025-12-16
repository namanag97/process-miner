'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ChevronRight, Check, House } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAppStore } from '@/lib/stores/useAppStore';
import { getRouteAccessibility, getCompletedSteps } from '@/hooks/useNavigationGuard';

interface BreadcrumbStep {
    label: string;
    href: string;
    key: string;
}

const breadcrumbSteps: BreadcrumbStep[] = [
    { label: 'Home', href: '/', key: 'home' },
    { label: 'Upload', href: '/upload', key: 'upload' },
    { label: 'Configure', href: '/configure', key: 'configure' },
    { label: 'Process Map', href: '/process-map', key: 'process-map' },
    { label: 'Insights', href: '/insights', key: 'insights' },
];

export function Breadcrumbs() {
    const pathname = usePathname();
    const { parsedData, columnConfig, miningResults } = useAppStore();

    const accessibility = getRouteAccessibility({ parsedData, columnConfig, miningResults });
    const completed = getCompletedSteps({ parsedData, columnConfig, miningResults });

    // Find current step index
    const currentStepIndex = breadcrumbSteps.findIndex(
        (step) => pathname === step.href || pathname.startsWith(step.href + '/')
    );

    // Don't show breadcrumbs on home page
    if (pathname === '/') {
        return null;
    }

    return (
        <nav className="flex items-center gap-1 text-sm px-4 md:px-6 py-2 bg-muted/30 border-b">
            {breadcrumbSteps.map((step, index) => {
                const isCurrent = pathname === step.href || pathname.startsWith(step.href + '/');
                const isAccessible = accessibility[step.href as keyof typeof accessibility];
                const isCompleted = completed[step.key as keyof typeof completed];
                const isFuture = index > currentStepIndex;

                return (
                    <div key={step.key} className="flex items-center gap-1">
                        {index > 0 && (
                            <ChevronRight className="h-4 w-4 text-muted-foreground/50" />
                        )}
                        {isAccessible && !isCurrent ? (
                            <Link
                                href={step.href}
                                className={cn(
                                    'flex items-center gap-1.5 px-2 py-1 rounded-md transition-colors',
                                    'hover:bg-muted text-muted-foreground hover:text-foreground'
                                )}
                            >
                                {step.key === 'home' ? (
                                    <House className="h-3.5 w-3.5" />
                                ) : isCompleted ? (
                                    <Check className="h-3.5 w-3.5 text-green-600 dark:text-green-400" />
                                ) : null}
                                <span>{step.label}</span>
                            </Link>
                        ) : (
                            <span
                                className={cn(
                                    'flex items-center gap-1.5 px-2 py-1 rounded-md',
                                    isCurrent && 'bg-primary/10 text-primary font-medium',
                                    isFuture && !isAccessible && 'text-muted-foreground/50'
                                )}
                            >
                                {step.key === 'home' ? (
                                    <House className="h-3.5 w-3.5" />
                                ) : isCompleted ? (
                                    <Check className="h-3.5 w-3.5 text-green-600 dark:text-green-400" />
                                ) : null}
                                <span>{step.label}</span>
                            </span>
                        )}
                    </div>
                );
            })}
        </nav>
    );
}
