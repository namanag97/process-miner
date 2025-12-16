'use client';

import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface BackButtonProps {
    href?: string;
    label?: string;
    className?: string;
}

export function BackButton({ href, label, className }: BackButtonProps) {
    const router = useRouter();

    const handleClick = () => {
        if (href) {
            router.push(href);
        } else {
            router.back();
        }
    };

    return (
        <Button
            variant="ghost"
            size="sm"
            onClick={handleClick}
            className={cn('gap-2 text-muted-foreground hover:text-foreground', className)}
        >
            <ArrowLeft className="h-4 w-4" />
            {label || 'Back'}
        </Button>
    );
}
