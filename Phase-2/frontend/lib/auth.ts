// Authentication utilities for the Todo Web Application

import { api } from './api';

interface User {
  id: string;
  email: string;
  name?: string;
}

class AuthUtils {
  // Check if user is authenticated
  isAuthenticated(): boolean {
    const token = this.getToken();
    return token !== null && token !== undefined && token !== '';
  }

  // Get token from localStorage
  getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token');
    }
    return null;
  }

  // Set token in localStorage
  setToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  // Remove token from localStorage
  removeToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  // Get user info from localStorage or return null
  getUser(): User | null {
    if (typeof window !== 'undefined') {
      const userStr = localStorage.getItem('user');
      if (userStr) {
        try {
          return JSON.parse(userStr);
        } catch (error) {
          console.error('Error parsing user data:', error);
          return null;
        }
      }
    }
    return null;
  }

  // Set user info in localStorage
  setUser(user: User): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('user', JSON.stringify(user));
    }
  }

  // Remove user info from localStorage
  removeUser(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('user');
    }
  }

  // Login user
  async login(email: string, password: string): Promise<{ success: boolean; user?: User; error?: string }> {
    const response = await api.login(email, password);

    if (response.success && response.data) {
      // Store the token (in access_token field)
      this.setToken(response.data.access_token);

      // Store user info (in user field if available)
      if (response.data.user) {
        this.setUser(response.data.user);
      } else {
        // For login, we may need to fetch user info separately if not included
        // For now, we'll create a basic user object from the token
        const token = response.data.access_token;
        if (token) {
          try {
            const payload = JSON.parse(atob(token.split('.')[1]));
            const basicUser: User = {
              id: payload.sub,
              email: payload.email
            };
            this.setUser(basicUser);
          } catch (e) {
            console.error('Error extracting user info from token:', e);
          }
        }
      }

      return { success: true, user: response.data.user || this.getUser() };
    } else {
      return { success: false, error: response.error?.message || 'Login failed' };
    }
  }

  // Register user
  async register(email: string, password: string, name?: string): Promise<{ success: boolean; user?: User; error?: string }> {
    const response = await api.register(email, password, name);

    if (response.success && response.data) {
      // Store the token (now in access_token field)
      this.setToken(response.data.access_token);

      // Store user info (now in user field)
      this.setUser(response.data.user);

      return { success: true, user: response.data.user };
    } else {
      return { success: false, error: response.error?.message || 'Registration failed' };
    }
  }

  // Logout user
  async logout(): Promise<{ success: boolean; error?: string }> {
    // Call the API to invalidate the session
    const response = await api.logout();

    // Remove local storage
    this.removeToken();
    this.removeUser();

    return response.success
      ? { success: true }
      : { success: false, error: response.error?.message || 'Logout failed' };
  }

  // Check if token is expired
  isTokenExpired(): boolean {
    const token = this.getToken();
    if (!token) return true;

    try {
      // Decode the token to check expiration
      const payload = JSON.parse(atob(token.split('.')[1]));
      const exp = payload.exp;
      const now = Math.floor(Date.now() / 1000);

      return now >= exp;
    } catch (error) {
      console.error('Error decoding token:', error);
      return true;
    }
  }
}

// Export a singleton instance
export const auth = new AuthUtils();