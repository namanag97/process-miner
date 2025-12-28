/**
 * Auth Client - Authentication Operations
 * 
 * Business verbs:
 * - signIn() - Authenticate user and start session
 * - signOut() - End session
 * - whoAmI() - Get current user profile
 */

import { HttpClient } from '../client.js';
import { AuthToken, LoginCredentials, UserProfile } from '../types/auth.js';

export class AuthClient {
  constructor(private readonly http: HttpClient) {}

  /**
   * Sign in with email and password.
   * Returns access token for authenticated requests.
   */
  async signIn(credentials: LoginCredentials): Promise<AuthToken> {
    const response = await this.http.post<{
      access_token: string;
      token_type: string;
    }>('/auth/login', credentials);

    // Store token in client
    this.http.setAuth(response.access_token, response.token_type);

    return {
      accessToken: response.access_token,
      tokenType: response.token_type,
    };
  }

  /**
   * Sign out and clear session.
   */
  async signOut(): Promise<void> {
    await this.http.post('/auth/logout');
    this.http.clearAuth();
  }

  /**
   * Get the current authenticated user's profile.
   */
  async whoAmI(): Promise<UserProfile> {
    return this.http.get<UserProfile>('/auth/me');
  }

  /**
   * Check if user is currently authenticated.
   */
  isAuthenticated(): boolean {
    return this.http.isAuthenticated();
  }
}
