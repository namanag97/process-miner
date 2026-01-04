/**
 * FeatureErrorBoundary
 *
 * Provides crash isolation for feature modules. When a feature crashes,
 * only that feature shows an error - the rest of the app continues working.
 */

import React from 'react';
import { Result, Button } from 'antd';
import { ReloadOutlined } from '@ant-design/icons';

interface Props {
    featureId: string;
    children: React.ReactNode;
}

interface State {
    hasError: boolean;
    error?: Error;
}

export class FeatureErrorBoundary extends React.Component<Props, State> {
    state: State = { hasError: false };

    static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, info: React.ErrorInfo) {
        // Log error for debugging
        console.error(`[FeatureErrorBoundary:${this.props.featureId}] Error:`, error);
        console.error('Component stack:', info.componentStack);

        // Send to dev log endpoint if available
        try {
            fetch('/dev/log', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    level: 'error',
                    category: 'FeatureErrorBoundary',
                    message: `${this.props.featureId} crashed: ${error.message}`,
                    data: {
                        featureId: this.props.featureId,
                        errorMessage: error.message,
                        stack: error.stack,
                        componentStack: info.componentStack,
                    },
                }),
            }).catch(() => {
                // Ignore logging errors
            });
        } catch {
            // Ignore
        }
    }

    handleReset = () => {
        this.setState({ hasError: false, error: undefined });
    };

    render() {
        if (this.state.hasError) {
            return (
                <Result
                    status="error"
                    title={`${this.props.featureId} encountered an error`}
                    subTitle={
                        process.env.NODE_ENV === 'development'
                            ? this.state.error?.message
                            : 'This feature crashed but the rest of the app is still working.'
                    }
                    extra={
                        <Button
                            type="primary"
                            icon={<ReloadOutlined />}
                            onClick={this.handleReset}
                        >
                            Try Again
                        </Button>
                    }
                />
            );
        }
        return this.props.children;
    }
}

export default FeatureErrorBoundary;
