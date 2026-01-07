import { defineConfig } from 'orval';

/**
 * Orval configuration for generating React Query hooks from OpenAPI spec.
 * 
 * Output: Single consolidated file at src/api/generated.ts
 * 
 * Usage:
 *   npm run generate:api
 */
export default defineConfig({
    api: {
        input: '../backend/docs/openapi.json',
        output: {
            mode: 'single',
            target: './src/api/generated.ts',
            client: 'react-query',
            clean: false,
            prettier: true,
            override: {
                mutator: {
                    path: './src/api/client.ts',
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

