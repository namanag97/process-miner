/**
 * MSW Server Setup
 *
 * Creates and configures the MSW server for testing.
 * This server intercepts network requests during tests.
 *
 * @see https://mswjs.io/docs/integrations/node
 */

import { setupServer } from 'msw/node';
import { handlers } from './handlers';

// Create the MSW server with default handlers
export const server = setupServer(...handlers);

// Export for use in tests
export { handlers } from './handlers';
