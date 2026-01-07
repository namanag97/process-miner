/**
 * MSW Browser Setup
 *
 * Creates and configures the MSW worker for browser-based development.
 * This can be used in Storybook or development mode.
 *
 * @see https://mswjs.io/docs/integrations/browser
 */

import { setupWorker } from 'msw/browser';
import { handlers } from './handlers';

// Create the MSW worker with default handlers
export const worker = setupWorker(...handlers);

// Export for use in development
export { handlers } from './handlers';
