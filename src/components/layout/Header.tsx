'use client';

import { Menu } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useUIStore } from '@/lib/stores/ui-store';

interface HeaderProps {
    title?: string;
}

export function Header({ title }: HeaderProps) {
    const { toggleSidebar } = useUIStore();

    return (
        <header className="sticky top-0 z-40 flex h-16 items-center gap-4 border-b bg-background px-4 md:px-6">
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
        </header>
    );
}
