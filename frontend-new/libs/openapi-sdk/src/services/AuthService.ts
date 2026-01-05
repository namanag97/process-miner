/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CurrentUserResponse } from '../models/CurrentUserResponse';
import type { LoginRequest } from '../models/LoginRequest';
import type { RefreshRequest } from '../models/RefreshRequest';
import type { RegisterRequest } from '../models/RegisterRequest';
import type { TokenPair } from '../models/TokenPair';
import type { TokenResponse } from '../models/TokenResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AuthService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Register
     * Register a new user account.
     *
     * Creates user, organization (if name provided), and default workspace.
     * Returns JWT tokens for immediate authentication.
     * @param requestBody
     * @returns TokenResponse Successful Response
     * @throws ApiError
     */
    public registerApiV1AuthRegisterPost(
        requestBody: RegisterRequest,
    ): CancelablePromise<TokenResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/auth/register',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Login
     * Authenticate user and return JWT tokens.
     *
     * For development with AUTH_ENABLED=false, accepts any credentials.
     * @param requestBody
     * @returns TokenResponse Successful Response
     * @throws ApiError
     */
    public loginApiV1AuthLoginPost(
        requestBody: LoginRequest,
    ): CancelablePromise<TokenResponse> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/auth/login',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Refresh Token
     * Refresh access token using refresh token.
     * @param requestBody
     * @returns TokenPair Successful Response
     * @throws ApiError
     */
    public refreshTokenApiV1AuthRefreshPost(
        requestBody: RefreshRequest,
    ): CancelablePromise<TokenPair> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/auth/refresh',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Get Current User Info
     * Get current authenticated user with organization and workspaces.
     * @param xOrgId
     * @returns CurrentUserResponse Successful Response
     * @throws ApiError
     */
    public getCurrentUserInfoApiV1AuthMeGet(
        xOrgId?: (string | null),
    ): CancelablePromise<CurrentUserResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/auth/me',
            headers: {
                'X-Org-Id': xOrgId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Logout
     * Logout endpoint.
     *
     * JWT tokens are stateless - client should discard the token.
     * For additional security, implement token blacklisting in production.
     * @returns string Successful Response
     * @throws ApiError
     */
    public logoutApiV1AuthLogoutPost(): CancelablePromise<Record<string, string>> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/auth/logout',
        });
    }
    /**
     * @deprecated
     * Get Current User Legacy
     * Legacy MVP endpoint - use /auth/me with JWT instead.
     *
     * DEPRECATED: This endpoint bypasses authentication.
     * Only works when AUTH_ENABLED=false.
     * @param email Email to identify user (MVP mode)
     * @returns CurrentUserResponse Successful Response
     * @throws ApiError
     */
    public getCurrentUserLegacyApiV1AuthMeLegacyGet(
        email?: (string | null),
    ): CancelablePromise<CurrentUserResponse> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/auth/me/legacy',
            query: {
                'email': email,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
}
