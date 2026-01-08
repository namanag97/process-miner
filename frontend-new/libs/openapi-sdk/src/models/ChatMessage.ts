/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { MessageRole } from './MessageRole';
/**
 * Single chat message.
 */
export type ChatMessage = {
    role: MessageRole;
    content: string;
    timestamp?: (string | null);
};

