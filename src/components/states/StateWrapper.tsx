'use client';

import { ReactNode } from 'react';
import { LucideIcon } from 'lucide-react';
import { EmptyState } from './EmptyState';
import { LoadingState, type LoadingStateProps } from './LoadingState';
import { ErrorState, type ErrorStateProps } from './ErrorState';

export interface EmptyConfig {
    icon: LucideIcon;
    title: string;
    description: string;
    actionLabel?: string;
    onAction?: () => void;
}

export interface StateWrapperProps {
    isLoading?: boolean;
    isEmpty?: boolean;
    isError?: boolean;
    error?: string;
    emptyConfig?: EmptyConfig;
    loadingConfig?: Partial<LoadingStateProps>;
    errorConfig?: Partial<ErrorStateProps>;
    onRetry?: () => void;
    onBack?: () => void;
    children: ReactNode;
    className?: string;
}

export function StateWrapper({
    isLoading = false,
    isEmpty = false,
    isError = false,
    error,
    emptyConfig,
    loadingConfig,
    errorConfig,
    onRetry,
    onBack,
    children,
    className,
}: StateWrapperProps) {
    if (isLoading) {
        return (
            <LoadingState
                className={className}
                {...loadingConfig}
            />
        );
    }

    if (isError) {
        return (
            <ErrorState
                message={error || 'An unexpected error occurred'}
                onRetry={onRetry}
                onBack={onBack}
                className={className}
                {...errorConfig}
            />
        );
    }

    if (isEmpty && emptyConfig) {
        return (
            <EmptyState
                icon={emptyConfig.icon}
                title={emptyConfig.title}
                description={emptyConfig.description}
                actionLabel={emptyConfig.actionLabel}
                onAction={emptyConfig.onAction}
                className={className}
            />
        );
    }

    return <>{children}</>;
}
