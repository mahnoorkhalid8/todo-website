// API client for the Todo Web Application
// Centralized error handling and request management

interface TokenResponse {
  access_token: string;
  token_type: string;
  user?: {
    id: string;
    email: string;
    name?: string;
  };
}

interface TaskResponse {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
  user_id: string;
  due_date?: string | null;
}

interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

class ApiClient {
  private baseUrl: string;
  private token: string | null;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    this.token = null;
  }

  // Set authentication token
  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  // Get authentication token
  getToken(): string | null {
    // First try to get from localStorage (client-side)
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('auth_token');
      if (token) {
        return token;
      }
    }

    // Fallback to instance variable
    return this.token;
  }

  // Remove authentication token
  removeToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  // Generic request method
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;

    // Build headers safely to avoid type conflicts
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    // Copy headers from options if they exist
    if (options.headers) {
      const optionHeaders = options.headers;
      if (optionHeaders instanceof Headers) {
        optionHeaders.forEach((value, key) => {
          headers[key] = value;
        });
      } else if (Array.isArray(optionHeaders)) {
        optionHeaders.forEach(([key, value]) => {
          if (typeof key === 'string' && typeof value === 'string') {
            headers[key] = value;
          }
        });
      } else if (typeof optionHeaders === 'object') {
        Object.entries(optionHeaders).forEach(([key, value]) => {
          if (typeof key === 'string' && typeof value === 'string') {
            headers[key] = value;
          }
        });
      }
    }

    // Add authorization header if token exists
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      // Construct fetch options to avoid type conflicts
      const fetchOptions: RequestInit = {};

      // Copy allowed properties from options individually to avoid type issues
      if (options.method) fetchOptions.method = options.method;
      if (options.body) fetchOptions.body = options.body;
      if (options.mode) fetchOptions.mode = options.mode;
      if (options.cache) fetchOptions.cache = options.cache;
      if (options.credentials) fetchOptions.credentials = options.credentials;
      if (options.redirect) fetchOptions.redirect = options.redirect;
      if (options.referrer) fetchOptions.referrer = options.referrer;
      if (options.integrity) fetchOptions.integrity = options.integrity;
      if (options.keepalive) fetchOptions.keepalive = options.keepalive;
      if (options.signal) fetchOptions.signal = options.signal;
      if (options.referrerPolicy) fetchOptions.referrerPolicy = options.referrerPolicy;

      // Always use our computed headers
      fetchOptions.headers = headers;

      const response = await fetch(url, fetchOptions);

      let data;
      try {
        data = await response.json();
      } catch (parseError) {
        // If response is not JSON, return a generic error
        if (!response.ok) {
          return {
            success: false,
            error: {
              code: `HTTP_${response.status}`,
              message: `HTTP Error ${response.status}`,
              details: null,
            },
          };
        }
        // If it's a successful non-JSON response, return success
        return {
          success: true,
          data: undefined,
        };
      }

      if (!response.ok) {
        return {
          success: false,
          error: {
            code: `HTTP_${response.status}`,
            message: data?.message || response.statusText,
            details: data?.details || null,
          },
        };
      }

      return {
        success: true,
        data,
      };
    } catch (error: any) {
      return {
        success: false,
        error: {
          code: 'NETWORK_ERROR',
          message: error.message || 'Network error occurred',
        },
      };
    }
  }

  // Authentication methods
  async register(email: string, password: string, name?: string) {
    const response = await this.request<TokenResponse>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
    });

    // If registration is successful, store the token
    if (response.success && response.data?.access_token) {
      this.setToken(response.data.access_token);
    }

    return response;
  }

  async login(email: string, password: string) {
    const response = await this.request<TokenResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    // If login is successful, store the token
    if (response.success && response.data?.access_token) {
      this.setToken(response.data.access_token);
    }

    return response;
  }

  async logout() {
    const result = await this.request('/api/auth/logout', {
      method: 'POST',
    });

    if (result.success) {
      this.removeToken();
    }

    return result;
  }

  // Task methods
  async getTasks(status: string = 'all', sort: string = 'created', page: number = 1, limit: number = 10) {
    const params = new URLSearchParams({
      status,
      sort,
      page: page.toString(),
      limit: limit.toString(),
    });

    return this.request(`/api/tasks?${params}`);
  }

  async createTask(title: string, description?: string, dueDate?: string) {
    return this.request('/api/tasks', {
      method: 'POST',
      body: JSON.stringify({ title, description, due_date: dueDate }),
    });
  }

  async getTask(id: number) {
    return this.request(`/api/tasks/${id}`);
  }

  async updateTask(id: number, title?: string, description?: string, dueDate?: string) {
    return this.request(`/api/tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ title, description, due_date: dueDate }),
    });
  }

  async deleteTask(id: number) {
    return this.request(`/api/tasks/${id}`, {
      method: 'DELETE',
    });
  }

  async toggleTaskCompletion(id: number, completed: boolean) {
    return this.request(`/api/tasks/${id}/complete`, {
      method: 'PATCH',
      body: JSON.stringify({ completed }),
    });
  }
}

// Export a singleton instance
export const api = new ApiClient();