import { defineConfig } from 'orval';

/**
 * Orval configuration for generating React Query hooks from OpenAPI spec.
 * 
 * This generates type-safe React Query hooks that integrate directly with
 * the existing @tanstack/react-query setup.
 * 
 * Usage:
 *   npm run generate:api       # Generate hooks
 *   npx orval --config orval.config.ts  # Direct invocation
 * 
 * Output goes to libs/api-hooks/src/generated/ to keep it separate from
 * the existing openapi-sdk until migration is complete.
 */
export default defineConfig({
    api: {
        input: '../backend/docs/openapi.json',
        output: {
            mode: 'single',
            target: './libs/api-hooks/src/generated/api.ts',
            client: 'react-query',
            clean: true,
            prettier: true,
            override: {
                mutator: {
                    path: './libs/api-hooks/src/axios-instance.ts',
                    name: 'customInstance',
                },
                query: {
                    useQuery: true,
                    useMutation: true,
                    useSuspenseQuery: false,
                    useInfinite: false,
                },
            },
        },
    },
});
