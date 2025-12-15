'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    LayoutDashboard,
    Database,
    GitBranch,
    Settings,
    Zap,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { useUIStore } from '@/lib/stores/ui-store';

const navigationItems = [
    {
        name: 'Home',
        href: '/',
        icon: LayoutDashboard,
    },
    {
        name: 'Data',
        href: '/data',
        icon: Database,
    },
    {
        name: 'Explore',
        href: '/explore',
        icon: GitBranch,
    },
    {
        name: 'Settings',
        href: '/settings',
        icon: Settings,
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
                'flex h-full w-64 flex-col bg-card border-r',
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

            {/* User section */}
            <div className="border-t p-4">
                <div className="flex items-center gap-3 rounded-lg px-3 py-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-full bg-muted text-sm font-medium">
                        JD
                    </div>
                    <div className="flex-1 overflow-hidden">
                        <p className="truncate text-sm font-medium">John Doe</p>
                        <p className="truncate text-xs text-muted-foreground">
                            john@example.com
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
