
import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { UploadWizardPage } from '../upload-wizard/pages/UploadWizardPage';
import { instrumentedFetch } from '@lumina/design-system';
import { devLog } from '../../../shared/ui/DevConsole';
import * as EnvConfig from 'src/config/env';

// Mock the env configuration to avoid import.meta issues
jest.mock('src/config/env', () => ({
    env: {
        API_BASE_URL: 'http://localhost:3000',
        USE_REAL_AUTH: false,
        ENABLE_DEV_TOOLS: true,
        NODE_ENV: 'test'
    },
    isDevelopment: false,
    isProduction: false,
    isTest: true
}));

// Mock DevConsole
jest.mock('../../../shared/ui/DevConsole', () => ({
    devLog: {
        action: jest.fn(),
        info: jest.fn(),
        error: jest.fn(),
        state: jest.fn(),
    }
}));

// Mock window.matchMedia for Ant Design
Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation(query => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: jest.fn(), // deprecated
        removeListener: jest.fn(), // deprecated
        addEventListener: jest.fn(),
        removeEventListener: jest.fn(),
        dispatchEvent: jest.fn(),
    })),
});

// Mock React Router
jest.mock('react-router-dom', () => {
    const navigate = jest.fn();
    return {
        useParams: () => ({ projectId: 'p1' }),
        useSearchParams: () => [new URLSearchParams()],
        useNavigate: () => navigate,
        // Expose the mock for assertions if needed, but easier to just Mock the hook return
    };
});

// Mock Design System components and utils
jest.mock('@lumina/design-system', () => {
    return {
        instrumentedFetch: jest.fn(),
        logAction: jest.fn(),
        tokens: {
            spacing: { 4: 16, 6: 24, 8: 32 },
            colors: {
                primary: { 500: '#blue' },
                error: { 50: '#red', 500: '#red' },
                neutral: { 50: '#gray' },
            },
            radius: { md: 4 }
        },
        WizardStepper: () => <div>WizardStepper</div>,
    };
});

describe('UploadWizard Integration Tests', () => {
    const mockFetch = instrumentedFetch as jest.Mock;
    const queryClient = new QueryClient({
        defaultOptions: {
            queries: {
                retry: false,
            },
        },
    });

    const renderWithProviders = (ui: React.ReactElement) => {
        return render(
            <QueryClientProvider client={queryClient}>
                {ui}
            </QueryClientProvider>
        );
    };

    beforeEach(() => {
        jest.clearAllMocks();
        queryClient.clear(); // Clear cache between tests

        // Smart mock implementation to handle different endpoints
        mockFetch.mockImplementation(async (url: string, options: any) => {
            if (url.includes('/upload')) {
                return {
                    ok: true,
                    status: 201,
                    json: async () => ({ id: 'd1', name: 'test.csv' }),
                    text: async () => "",
                };
            }
            if (url.includes('/sheets')) {
                return {
                    ok: true,
                    status: 200,
                    json: async () => ({ sheets: [{ name: 'Sheet1' }] }),
                    text: async () => "",
                };
            }
            // Default response
            return {
                ok: true,
                status: 200,
                json: async () => ({}),
                text: async () => "",
            };
        });
    });

    // 1. API Connectivity
    it('should verify API endpoints are reachable', async () => {
        // Setup success response for direct upload
        mockFetch.mockResolvedValueOnce({
            ok: true,
            status: 201,
            json: async () => ({ id: 'd1', name: 'test.csv' })
        });

        renderWithProviders(<UploadWizardPage />);

        // Simulate file upload
        const file = new File(['headers\nr1,r2'], 'test.csv', { type: 'text/csv' });
        const input = document.querySelector('input[type="file"]');
        if (input) {
            fireEvent.change(input, { target: { files: [file] } });
        }

        // Verify API was called with correct base URL (implicit in spy)
        await waitFor(() => {
            expect(mockFetch).toHaveBeenCalledWith(
                expect.stringMatching(/\/api\/v1\/datasets\/upload/),
                expect.objectContaining({ method: 'POST' })
            );
        });
    });

    // 2. Error Handling
    it('should catch network failures and display error with component context', async () => {
        // Mock network error
        mockFetch.mockRejectedValue(new Error('Network Error'));

        renderWithProviders(<UploadWizardPage />);

        // Find and trigger upload to cause the error
        const file = new File(['content'], 'fail.csv', { type: 'text/csv' });
        const input = document.querySelector('input[type="file"]');
        if (input) {
            fireEvent.change(input, { target: { files: [file] } });
        }

        // Verify visible error message
        await waitFor(() => {
            // Use getAllByText because AntD might render the error in multiple places (Alert + text)
            const errors = screen.getAllByText(/Network Error/i);
            expect(errors.length).toBeGreaterThan(0);
        });

        // Verify log contains component context
        expect(devLog.error).toHaveBeenCalledWith(
            expect.stringContaining('Upload'),
            expect.stringContaining('Network Error'),
            expect.anything()
        );
    });

    // 3. Environment Config
    it('should validate API_BASE_URL is configured', () => {
        renderWithProviders(<UploadWizardPage />);
        // ...
    });

    // ... (rest of tests)

    // 7. Logging Coverage
    it('should log to console and DevConsole on error', async () => {
        // Trigger error
        mockFetch.mockRejectedValue(new Error('Logging Test Error'));
        const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => { });

        renderWithProviders(<UploadWizardPage />);
        const file = new File(['c'], 'log.csv', { type: 'text/csv' });
        const input = document.querySelector('input[type="file"]');
        if (input) {
            fireEvent.change(input, { target: { files: [file] } });
        }

        await waitFor(() => {
            const errors = screen.getAllByText(/Logging Test Error/i);
            expect(errors.length).toBeGreaterThan(0);
        });

        // Check Console
        expect(consoleSpy).toHaveBeenCalledWith(
            expect.stringContaining('Upload'),
            expect.anything()
        );

        // Check DevConsole
        expect(devLog.error).toHaveBeenCalled();

        consoleSpy.mockRestore();
    });
});
