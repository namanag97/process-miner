/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Response containing presigned upload URL and tracking info.
 *
 * Client should:
 * 1. PUT file to upload_url with Content-Type header
 * 2. Poll /datasets/{dataset_id} for validation status
 */
export type PresignedUploadResponse = {
    /**
     * Presigned PUT URL for direct S3 upload
     */
    upload_url: string;
    /**
     * S3 object key for tracking
     */
    storage_key: string;
    /**
     * Dataset ID for status polling
     */
    dataset_id: string;
    /**
     * URL expiration in seconds
     */
    expires_in: number;
};

