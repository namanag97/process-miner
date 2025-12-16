'use client';

import { usePathname } from 'next/navigation';
import { Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useUIStore } from '@/lib/stores/ui-store';
import { BackButton } from '@/components/navigation/BackButton';

interface HeaderProps {
    title?: string;
    showBackButton?: boolean;
    backHref?: string;
    backLabel?: string;
}

const backButtonConfig: Record<string, { href: string; label: string }> = {
    '/upload': { href: '/', label: 'Back to Home' },
    '/configure': { href: '/upload', label: 'Back to Upload' },
    '/process-map': { href: '/configure', label: 'Back to Configure' },
    '/insights': { href: '/process-map', label: 'Back to Process Map' },
};

export function Header({ title, showBackButton, backHref, backLabel }: HeaderProps) {
    const { toggleSidebar } = useUIStore();
    const pathname = usePathname();

    // Auto-determine back button config if not provided
    const defaultConfig = backButtonConfig[pathname];
    const shouldShowBack = showBackButton ?? (pathname !== '/' && !!defaultConfig);
    const finalBackHref = backHref ?? defaultConfig?.href;
    const finalBackLabel = backLabel ?? defaultConfig?.label;

    return (
        <header className="sticky top-0 z-40 border-b bg-background">
            <div className="flex h-16 items-center gap-4 px-4 md:px-6">
                {/* Mobile menu button */}
                <Button
                    variant="ghost"
                    size="icon"
                    className="md:hidden"
                    onClick={toggleSidebar}
                >
                    <Menu className="h-5 w-5" />
                    <span className="sr-only">Toggle menu</span>
                </Button>

                {/* Page title */}
                <div className="flex-1">
                    {title && <h1 className="text-xl font-semibold">{title}</h1>}
                </div>
            </div>

            {/* Back button row */}
            {shouldShowBack && finalBackHref && (
                <div className="px-4 md:px-6 pb-2">
                    <BackButton href={finalBackHref} label={finalBackLabel} />
                </div>
            )}
        </header>
    );
}
