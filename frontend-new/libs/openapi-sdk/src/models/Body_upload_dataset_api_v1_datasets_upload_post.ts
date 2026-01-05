/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
export type Body_upload_dataset_api_v1_datasets_upload_post = {
    file: Blob;
    name?: (string | null);
    /**
     * Project ID to assign dataset to
     */
    project_id?: (string | null);
    case_id_column?: (string | null);
    activity_column?: (string | null);
    timestamp_column?: (string | null);
    resource_column?: (string | null);
    /**
     * If true, store file only without parsing (deferred ingestion)
     */
    async_store?: boolean;
};

