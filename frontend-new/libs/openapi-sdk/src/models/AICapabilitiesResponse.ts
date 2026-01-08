/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Response describing AI capabilities.
 */
export type AICapabilitiesResponse = {
    capabilities: Array<string>;
    supported_analysis_types: Array<string>;
    max_message_length: number;
    max_history_length: number;
    model_info: Record<string, any>;
};

