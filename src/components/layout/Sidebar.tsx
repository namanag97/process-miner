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
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { useUIStore } from '@/lib/stores/ui-store';

const navigationItems = [
    {
        name: 'Home',
        href: '/',
        icon: House,
    },
    {
        name: 'Upload Data',
        href: '/upload',
        icon: Upload,
    },
    {
        name: 'Configure',
        href: '/configure',
        icon: Settings2,
    },
    {
        name: 'Process Map',
        href: '/process-map',
        icon: GitBranch,
    },
    {
        name: 'Insights',
        href: '/insights',
        icon: BarChart3,
    },
];

interface SidebarProps {
    className?: string;
}

export function Sidebar({ className }: SidebarProps) {
    const pathname = usePathname();
    const { closeSidebar } = useUIStore();

    const handleNavClick = () => {
        // Close sidebar on mobile after clicking a link
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
                                <item.icon className="h-4 w-4" />
                                {item.name}
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
