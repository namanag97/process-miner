/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ChangePasswordRequest } from '../models/ChangePasswordRequest';
import type { CurrentUserResponse } from '../models/CurrentUserResponse';
import type { ForgotPasswordRequest } from '../models/ForgotPasswordRequest';
import type { LoginRequest } from '../models/LoginRequest';
import type { RefreshRequest } from '../models/RefreshRequest';
import type { RegisterRequest } from '../models/RegisterRequest';
import type { ResetPasswordRequest } from '../models/ResetPasswordRequest';
import type { TokenPair } from '../models/TokenPair';
import type { TokenResponse } from '../models/TokenResponse';
import type { UserResponse } from '../models/UserResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AuthService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * Register
     * Register a new user account for the process mining SaaS platform.
     *
     * Creates:
     * - User account with hashed password
     * - Organization (auto-named if not provided)
     * - Default workspace for collaboration
     * - Workspace membership with owner role
     *
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
     * Update Current User
     * Update current user's profile (name, etc.).
     * @param name
     * @param xOrgId
     * @returns UserResponse Successful Response
     * @throws ApiError
     */
    public updateCurrentUserApiV1AuthMePut(
        name?: (string | null),
        xOrgId?: (string | null),
    ): CancelablePromise<UserResponse> {
        return this.httpRequest.request({
            method: 'PUT',
            url: '/api/v1/auth/me',
            headers: {
                'X-Org-Id': xOrgId,
            },
            query: {
                'name': name,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Change Password
     * Change password for logged in user.
     * @param requestBody
     * @param xOrgId
     * @returns string Successful Response
     * @throws ApiError
     */
    public changePasswordApiV1AuthChangePasswordPost(
        requestBody: ChangePasswordRequest,
        xOrgId?: (string | null),
    ): CancelablePromise<Record<string, string>> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/auth/change-password',
            headers: {
                'X-Org-Id': xOrgId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Forgot Password
     * Request password reset email.
     *
     * Always returns success to prevent email enumeration.
     * @param requestBody
     * @returns string Successful Response
     * @throws ApiError
     */
    public forgotPasswordApiV1AuthForgotPasswordPost(
        requestBody: ForgotPasswordRequest,
    ): CancelablePromise<Record<string, string>> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/auth/forgot-password',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Reset Password
     * Set new password with reset token.
     *
     * Note: Token validation not implemented - placeholder.
     * @param requestBody
     * @returns string Successful Response
     * @throws ApiError
     */
    public resetPasswordApiV1AuthResetPasswordPost(
        requestBody: ResetPasswordRequest,
    ): CancelablePromise<Record<string, string>> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/v1/auth/reset-password',
            body: requestBody,
            mediaType: 'application/json',
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
     * Oauth Google Init
     * Initiate Google OAuth flow.
     *
     * Note: OAuth integration not yet implemented.
     * @returns any Successful Response
     * @throws ApiError
     */
    public oauthGoogleInitApiV1AuthOauthGoogleGet(): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/auth/oauth/google',
        });
    }
    /**
     * Oauth Google Callback
     * Google OAuth callback.
     *
     * Note: OAuth integration not yet implemented.
     * @param code
     * @param state
     * @returns any Successful Response
     * @throws ApiError
     */
    public oauthGoogleCallbackApiV1AuthOauthGoogleCallbackGet(
        code?: (string | null),
        state?: (string | null),
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/auth/oauth/google/callback',
            query: {
                'code': code,
                'state': state,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }
    /**
     * Oauth Github Init
     * Initiate GitHub OAuth flow.
     *
     * Note: OAuth integration not yet implemented.
     * @returns any Successful Response
     * @throws ApiError
     */
    public oauthGithubInitApiV1AuthOauthGithubGet(): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/auth/oauth/github',
        });
    }
    /**
     * Oauth Github Callback
     * GitHub OAuth callback.
     *
     * Note: OAuth integration not yet implemented.
     * @param code
     * @param state
     * @returns any Successful Response
     * @throws ApiError
     */
    public oauthGithubCallbackApiV1AuthOauthGithubCallbackGet(
        code?: (string | null),
        state?: (string | null),
    ): CancelablePromise<Record<string, any>> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/v1/auth/oauth/github/callback',
            query: {
                'code': code,
                'state': state,
            },
            errors: {
                422: `Validation Error`,
            },
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
