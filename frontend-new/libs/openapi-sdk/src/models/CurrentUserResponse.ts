/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { src__platform__schemas__OrganizationResponse } from './src__platform__schemas__OrganizationResponse';
import type { UserResponse } from './UserResponse';
import type { WorkspaceResponse } from './WorkspaceResponse';
/**
 * Current user context response (for auth/me endpoint).
 */
export type CurrentUserResponse = {
    user: UserResponse;
    organization?: (src__platform__schemas__OrganizationResponse | null);
    workspaces?: Array<WorkspaceResponse>;
    current_workspace_id?: (string | null);
};

