import { withSentryConfig } from "@sentry/nextjs";

/** @type {import('next').NextConfig} */
const nextConfig = {
    // Your existing config...
};

// Sentry config - only wraps if DSN is provided
const sentryConfig = {
    // For all available options, see:
    // https://github.com/getsentry/sentry-webpack-plugin#options

    // Suppresses source map uploading logs during build
    silent: true,
    org: process.env.SENTRY_ORG,
    project: process.env.SENTRY_PROJECT,
};

const sentryOptions = {
    // Hides source maps from generated client bundles
    hideSourceMaps: true,

    // Automatically tree-shake Sentry logger statements to reduce bundle size
    disableLogger: true,

    // Enable component annotations for better error context
    reactComponentAnnotation: {
        enabled: true,
    },
};

// Only apply Sentry wrapper if DSN is configured
const finalConfig = process.env.NEXT_PUBLIC_SENTRY_DSN
    ? withSentryConfig(nextConfig, sentryConfig, sentryOptions)
    : nextConfig;

export default finalConfig;
