/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Request for presigned upload URL generation.
 *
 * Client requests a presigned URL, then uploads directly to S3/MinIO.
 * Backend receives upload notification via webhook or polling.
 */
export type PresignedUploadRequest = {
    /**
     * Original filename
     */
    filename: string;
    /**
     * MIME type (text/csv, application/xml)
     */
    content_type?: string;
    /**
     * Expected file size in bytes (for validation)
     */
    file_size_bytes?: (number | null);
    /**
     * Optional project association
     */
    project_id?: (string | null);
};

