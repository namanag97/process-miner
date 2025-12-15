'use client';

import { Menu, Search, Bell } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useUIStore } from '@/lib/stores/ui-store';

interface HeaderProps {
    title: string;
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
                <h1 className="text-xl font-semibold">{title}</h1>
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
                {/* Search button */}
                <Button variant="ghost" size="icon">
                    <Search className="h-5 w-5" />
                    <span className="sr-only">Search</span>
                </Button>

                {/* Notifications button */}
                <Button variant="ghost" size="icon">
                    <Bell className="h-5 w-5" />
                    <span className="sr-only">Notifications</span>
                </Button>

                {/* User dropdown */}
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="relative h-9 w-9 rounded-full">
                            <Avatar className="h-9 w-9">
                                <AvatarImage src="/avatar.jpg" alt="User avatar" />
                                <AvatarFallback>JD</AvatarFallback>
                            </Avatar>
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="w-56" align="end" forceMount>
                        <DropdownMenuLabel className="font-normal">
                            <div className="flex flex-col space-y-1">
                                <p className="text-sm font-medium leading-none">John Doe</p>
                                <p className="text-xs leading-none text-muted-foreground">
                                    john@example.com
                                </p>
                            </div>
                        </DropdownMenuLabel>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem>Profile</DropdownMenuItem>
                        <DropdownMenuItem>Settings</DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem className="text-destructive">
                            Logout
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            </div>
        </header>
    );
}
