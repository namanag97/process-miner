'use client';

import { Sidebar } from '@/components/layout/Sidebar';
import { useUIStore } from '@/lib/stores/ui-store';
import {
    Sheet,
    SheetContent,
} from '@/components/ui/sheet';

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    const { sidebarOpen, closeSidebar } = useUIStore();

    return (
        <div className="flex h-screen overflow-hidden bg-background">
            {/* Desktop sidebar */}
            <aside className="hidden md:flex">
                <Sidebar />
            </aside>

            {/* Mobile sidebar (sheet) */}
            <Sheet open={sidebarOpen} onOpenChange={closeSidebar}>
                <SheetContent side="left" className="w-64 p-0">
                    <Sidebar />
                </SheetContent>
            </Sheet>

            {/* Main content area */}
            <main className="flex-1 overflow-y-auto">
                {children}
            </main>
        </div>
    );
}
