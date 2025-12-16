'use client';

import { useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';
import { useNavigationGuard } from '@/hooks/useNavigationGuard';
import { useToast } from '@/hooks';

interface NavigationGuardProps {
    children: ReactNode;
}

export function NavigationGuard({ children }: NavigationGuardProps) {
    const router = useRouter();
    const { toast } = useToast();
    const { canAccess, redirectPath, toastMessage } = useNavigationGuard();

    useEffect(() => {
        if (!canAccess && redirectPath) {
            if (toastMessage) {
                toast({
                    title: 'Navigation Required',
                    description: toastMessage,
                    variant: 'default',
                });
            }
            router.replace(redirectPath);
        }
    }, [canAccess, redirectPath, toastMessage, router, toast]);

    // Don't render children if we're about to redirect
    if (!canAccess) {
        return null;
    }

    return <>{children}</>;
}
