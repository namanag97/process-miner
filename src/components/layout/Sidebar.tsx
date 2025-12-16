'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    House,
    Upload,
    Settings2,
    GitBranch,
    BarChart3,
    Zap,
    Check,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import {
    Tooltip,
    TooltipContent,
    TooltipTrigger,
} from '@/components/ui/tooltip';
import { useUIStore } from '@/lib/stores/ui-store';
import { useAppStore } from '@/lib/stores/useAppStore';
import { getRouteAccessibility, getCompletedSteps } from '@/hooks/useNavigationGuard';

const navigationItems = [
    {
        name: 'Home',
        href: '/',
        icon: House,
        key: 'home',
    },
    {
        name: 'Upload Data',
        href: '/upload',
        icon: Upload,
        key: 'upload',
    },
    {
        name: 'Configure',
        href: '/configure',
        icon: Settings2,
        key: 'configure',
    },
    {
        name: 'Process Map',
        href: '/process-map',
        icon: GitBranch,
        key: 'process-map',
    },
    {
        name: 'Insights',
        href: '/insights',
        icon: BarChart3,
        key: 'insights',
    },
];

interface SidebarProps {
    className?: string;
}

export function Sidebar({ className }: SidebarProps) {
    const pathname = usePathname();
    const { closeSidebar } = useUIStore();
    const { parsedData, columnConfig, miningResults } = useAppStore();

    const accessibility = getRouteAccessibility({ parsedData, columnConfig, miningResults });
    const completed = getCompletedSteps({ parsedData, columnConfig, miningResults });

    const handleNavClick = () => {
        closeSidebar();
    };

    return (
        <div
            className={cn(
                'flex h-full w-[250px] flex-col bg-card border-r',
                className
            )}
        >
            {/* Brand */}
            <div className="flex h-16 items-center gap-2 border-b px-6">
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
                    <Zap className="h-4 w-4 text-primary-foreground" />
                </div>
                <span className="text-lg font-semibold">ProcessMiner</span>
            </div>

            {/* Navigation */}
            <nav className="flex-1 space-y-1 p-4">
                {navigationItems.map((item) => {
                    const isActive = pathname === item.href;
                    const isAccessible = accessibility[item.href as keyof typeof accessibility];
                    const isCompleted = completed[item.key as keyof typeof completed];

                    const buttonContent = (
                        <span className="flex items-center gap-3 w-full">
                            <item.icon className="h-4 w-4" />
                            <span className="flex-1 text-left">{item.name}</span>
                            {isCompleted && (
                                <Check className="h-4 w-4 text-green-600 dark:text-green-400" />
                            )}
                        </span>
                    );

                    if (!isAccessible) {
                        return (
                            <Tooltip key={item.href}>
                                <TooltipTrigger asChild>
                                    <Button
                                        variant="ghost"
                                        className={cn(
                                            'w-full justify-start gap-3 h-10',
                                            'opacity-50 cursor-not-allowed'
                                        )}
                                        disabled
                                    >
                                        {buttonContent}
                                    </Button>
                                </TooltipTrigger>
                                <TooltipContent side="right">
                                    Complete previous steps first
                                </TooltipContent>
                            </Tooltip>
                        );
                    }

                    return (
                        <Button
                            key={item.href}
                            variant="ghost"
                            className={cn(
                                'w-full justify-start gap-3 h-10',
                                isActive && 'bg-accent text-accent-foreground'
                            )}
                            asChild
                            onClick={handleNavClick}
                        >
                            <Link href={item.href}>
                                {buttonContent}
                            </Link>
                        </Button>
                    );
                })}
            </nav>

            {/* Footer */}
            <div className="border-t p-4">
                <p className="text-xs text-muted-foreground text-center">
                    Process Mining Tool
                </p>
            </div>
        </div>
    );
}
