/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ProjectResponse } from './ProjectResponse';
/**
 * Workspace detail with projects.
 */
export type WorkspaceDetailResponse = {
    id: string;
    org_id: string;
    name: string;
    description: (string | null);
    created_at: string;
    updated_at: (string | null);
    projects?: Array<ProjectResponse>;
};

