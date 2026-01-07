/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Registration request for new SaaS users.
 *
 * Password Requirements:
 * - Minimum 8 characters
 * - At least one uppercase letter
 * - At least one lowercase letter
 * - At least one digit
 */
export type RegisterRequest = {
    email: string;
    /**
     * Password (8-128 chars, must include uppercase, lowercase, and digit)
     */
    password: string;
    /**
     * User's display name
     */
    name: string;
    /**
     * Organization name (auto-generated if not provided)
     */
    organization_name?: (string | null);
};

