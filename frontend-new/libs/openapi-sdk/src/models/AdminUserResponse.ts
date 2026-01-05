/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Admin user response with full details.
 */
export type AdminUserResponse = {
    id: string;
    email: string;
    name: string;
    role: string;
    org_id: (string | null);
    org_name?: (string | null);
    is_active?: boolean;
    created_at: string;
    last_login_at?: (string | null);
};

