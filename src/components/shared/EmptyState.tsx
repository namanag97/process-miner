'use client';

import { LucideIcon, FileQuestion } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface EmptyStateProps {
    icon?: LucideIcon;
    title: string;
    description: string;
    action?: {
        label: string;
        onClick?: () => void;
        href?: string;
    };
}

export function EmptyState({
    icon: Icon = FileQuestion,
    title,
    description,
    action,
}: EmptyStateProps) {
    return (
        <div className="flex flex-col items-center justify-center p-8 text-center">
            <div className="flex h-16 w-16 items-center justify-center rounded-full bg-muted">
                <Icon className="h-8 w-8 text-muted-foreground" />
            </div>
            <h3 className="mt-4 text-lg font-semibold">{title}</h3>
            <p className="mt-2 text-sm text-muted-foreground max-w-sm">
                {description}
            </p>
            {action && (
                <Button
                    className="mt-6"
                    onClick={action.onClick}
                    asChild={!!action.href}
                >
                    {action.href ? (
                        <a href={action.href}>{action.label}</a>
                    ) : (
                        action.label
                    )}
                </Button>
            )}
        </div>
    );
}
