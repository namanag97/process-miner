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
            mode: 'tags-split',
            target: './libs/api-hooks/src/generated',
            schemas: './libs/api-hooks/src/generated/models',
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
                    useSuspenseQuery: true,
                    useInfinite: true,
                    useInfiniteQueryParam: 'page',
                },
            },
        },
    },
});
